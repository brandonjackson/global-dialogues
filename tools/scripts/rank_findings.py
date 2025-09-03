#!/usr/bin/env python3
"""
Rank investigation findings using LLM judges.

This script uses multiple LLM judges to rank random samples of findings
from investigation answers based on interestingness, surprisingness, and impactfulness.
"""

import argparse
import asyncio
import csv
import json
import os
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math

import aiohttp
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Finding:
    """Represents a single finding from the investigation."""
    section_id: str
    question: str
    finding: str
    details: str
    
    def to_dict(self):
        return {
            'section_id': self.section_id,
            'question': self.question,
            'finding': self.finding,
            'details': self.details
        }


@dataclass 
class RankedFinding(Finding):
    """Finding with aggregate ranking score."""
    score: float = 0.0
    rank_positions: List[int] = field(default_factory=list)
    
    def to_dict(self):
        d = super().to_dict()
        d.update({
            'score': self.score,
            'avg_rank': sum(self.rank_positions) / len(self.rank_positions) if self.rank_positions else None,
            'num_rankings': len(self.rank_positions)
        })
        return d


class RankingResponse(BaseModel):
    """Pydantic model for LLM ranking response."""
    rankings: List[str] = Field(..., description="Ordered list of section IDs from most to least interesting")
    reasoning: Optional[str] = Field(None, description="Optional reasoning for the rankings")


class FindingParser:
    """Parse findings from investigation markdown files."""
    
    def __init__(self, gd_number: int):
        self.gd_number = gd_number
        self.base_path = Path(f"analysis_output/GD{gd_number}/research")
        self.questions_file = self.base_path / f"GD{gd_number}_investigation_questions.md"
        self.answers_file = self.base_path / f"GD{gd_number}_investigation_answers.md"
        
    def parse_questions(self) -> Dict[str, str]:
        """Parse questions from the questions file."""
        if not self.questions_file.exists():
            raise FileNotFoundError(f"Questions file not found: {self.questions_file}")
            
        questions = {}
        with open(self.questions_file, 'r') as f:
            content = f.read()
            
        # Parse sections and questions
        pattern = r'\* \*\*(\d+\.\d+)\.[^:]+:\*\* ([^*\n]+)'
        matches = re.findall(pattern, content)
        
        for section_id, question_text in matches:
            questions[section_id] = question_text.strip()
            
        return questions
    
    def parse_findings(self) -> List[Finding]:
        """Parse all findings from the answers file."""
        if not self.answers_file.exists():
            raise FileNotFoundError(f"Answers file not found: {self.answers_file}")
            
        questions = self.parse_questions()
        findings = []
        
        with open(self.answers_file, 'r') as f:
            content = f.read()
            
        # Split by sections
        sections = re.split(r'^#{1,3} Question (\d+\.\d+):', content, flags=re.MULTILINE)
        
        # Process each section (skip first element which is header)
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_id = sections[i]
                section_content = sections[i + 1]
                
                # Extract finding
                finding_match = re.search(r'\*\*Finding:\*\* (.+?)(?=\n\*\*|$)', section_content, re.DOTALL)
                if not finding_match:
                    continue
                    
                finding_text = finding_match.group(1).strip()
                
                # Extract details - everything after **Details:** up to next section or Summary
                details_match = re.search(r'\*\*Details:\*\*(.+?)(?=^#{1,3} |^## Summary Insights|$)', 
                                        section_content, re.DOTALL | re.MULTILINE)
                if not details_match:
                    continue
                    
                details_text = details_match.group(1).strip()
                
                # Get question text
                question_text = questions.get(section_id, f"Question {section_id}")
                
                findings.append(Finding(
                    section_id=section_id,
                    question=question_text,
                    finding=finding_text,
                    details=details_text
                ))
                
        return findings


class LLMJudge:
    """Interface to LLM judges via OpenRouter API."""
    
    MODELS = [
        "anthropic/claude-3-haiku-20240307",
        "google/gemini-flash-1.5-8b",
        "openai/gpt-4o-mini"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def _create_prompt(self, findings: List[Finding]) -> str:
        """Create the prompt for ranking findings."""
        prompt = """You are an expert research evaluator tasked with ranking survey findings based on their interestingness, surprisingness, and potential impact.

You will be given a list of findings from a Global Dialogues survey about AI and human-animal communication. Each finding has:
- A section ID (e.g., 1.5, 3.2)
- The research question being addressed
- The main finding
- Supporting details

Please rank these findings from MOST interesting/surprising/impactful to LEAST interesting/surprising/impactful.

Consider these criteria:
- Interestingness: How engaging or thought-provoking is the finding?
- Surprisingness: Does it reveal unexpected patterns or counterintuitive results?
- Impactfulness: Could this finding influence policy, behavior, or understanding?

FINDINGS TO RANK:

"""
        for finding in findings:
            prompt += f"""
**[{finding.section_id}]**
Question: {finding.question}
Finding: {finding.finding}
Details: {finding.details}

---
"""
        
        prompt += """

Respond with ONLY a JSON object in this exact format:
{
    "rankings": ["section_id_1", "section_id_2", ...],
    "reasoning": "Brief explanation of top choices"
}

The "rankings" array should list all section IDs in order from MOST interesting (first) to LEAST interesting (last).
"""
        return prompt
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_ranking(self, findings: List[Finding], model: str, session: aiohttp.ClientSession) -> RankingResponse:
        """Get ranking from a single LLM judge."""
        prompt = self._create_prompt(findings)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        async with session.post(self.base_url, headers=headers, json=data) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"API request failed with status {response.status}: {text}")
                
            result = await response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON response
            try:
                parsed = json.loads(content)
                return RankingResponse(**parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                # Retry with a different approach if JSON parsing fails
                raise Exception(f"Failed to parse response from {model}: {e}")


class RankingAggregator:
    """Aggregate rankings from multiple judges."""
    
    def __init__(self, findings: List[Finding]):
        self.findings = {f.section_id: f for f in findings}
        self.rankings: Dict[str, List[int]] = defaultdict(list)
        
    def add_ranking(self, ranking: List[str]):
        """Add a single ranking from a judge."""
        for position, section_id in enumerate(ranking, 1):
            if section_id in self.findings:
                self.rankings[section_id].append(position)
    
    def calculate_scores(self) -> List[RankedFinding]:
        """Calculate aggregate scores using Borda count method."""
        ranked_findings = []
        n = len(self.findings)
        
        for section_id, finding in self.findings.items():
            positions = self.rankings.get(section_id, [])
            
            if positions:
                # Borda score: higher is better (n points for 1st place, 1 point for last)
                borda_scores = [n - pos + 1 for pos in positions]
                avg_borda = sum(borda_scores) / len(borda_scores)
                # Normalize to 0-1 scale
                score = avg_borda / n
            else:
                score = 0.0
                
            ranked = RankedFinding(
                section_id=finding.section_id,
                question=finding.question,
                finding=finding.finding,
                details=finding.details,
                score=score,
                rank_positions=positions
            )
            ranked_findings.append(ranked)
            
        # Sort by score descending
        ranked_findings.sort(key=lambda x: x.score, reverse=True)
        return ranked_findings


async def run_parallel_rankings(findings: List[Finding], judge: LLMJudge, num_rounds: int) -> List[RankingResponse]:
    """Run multiple ranking rounds in parallel."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for round_num in range(num_rounds):
            # Rotate through models for diversity
            model = LLMJudge.MODELS[round_num % len(LLMJudge.MODELS)]
            task = judge.get_ranking(findings, model, session)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Warning: Round {i+1} failed: {result}", file=sys.stderr)
            else:
                valid_results.append(result)
                
        return valid_results


def calculate_num_rounds(n_findings: int, n_sample: int, total_findings: int) -> int:
    """Calculate recommended number of rounds based on sampling parameters."""
    # Ensure good coverage: each finding should be ranked at least 5 times on average
    coverage_factor = 5
    rounds = math.ceil((total_findings * coverage_factor) / n_sample)
    
    # But cap at a reasonable maximum
    return min(rounds, 30)


def save_results(ranked_findings: List[RankedFinding], output_path: Path):
    """Save ranked findings to CSV."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['rank', 'score', 'section_id', 'question', 'finding', 
                     'avg_rank_position', 'num_rankings', 'details']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for rank, finding in enumerate(ranked_findings, 1):
            row = finding.to_dict()
            writer.writerow({
                'rank': rank,
                'score': f"{row['score']:.4f}",
                'section_id': row['section_id'],
                'question': row['question'],
                'finding': row['finding'],
                'avg_rank_position': f"{row['avg_rank']:.2f}" if row['avg_rank'] else 'N/A',
                'num_rankings': row['num_rankings'],
                'details': row['details'][:500] + '...' if len(row['details']) > 500 else row['details']
            })


async def main():
    parser = argparse.ArgumentParser(description='Rank investigation findings using LLM judges')
    parser.add_argument('gd_number', type=int, help='Global Dialogue number (e.g., 5 for GD5)')
    parser.add_argument('-n', '--sample-size', type=int, default=10,
                       help='Number of findings per sample (default: 10)')
    parser.add_argument('-r', '--rounds', type=int, default=None,
                       help='Number of ranking rounds (default: auto-calculated)')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Parse findings
    print(f"Parsing findings from GD{args.gd_number}...")
    parser = FindingParser(args.gd_number)
    all_findings = parser.parse_findings()
    print(f"Found {len(all_findings)} total findings")
    
    if len(all_findings) < args.sample_size:
        print(f"Warning: Only {len(all_findings)} findings available, using all of them")
        args.sample_size = len(all_findings)
    
    # Calculate number of rounds if not specified
    if args.rounds is None:
        args.rounds = calculate_num_rounds(args.sample_size, args.sample_size, len(all_findings))
    
    print(f"Running {args.rounds} ranking rounds with {args.sample_size} findings per round...")
    
    # Initialize aggregator
    aggregator = RankingAggregator(all_findings)
    judge = LLMJudge()
    
    # Run ranking rounds
    successful_rounds = 0
    for batch in range(0, args.rounds, 3):  # Process in batches of 3 for parallel execution
        batch_size = min(3, args.rounds - batch)
        
        # Sample findings for this batch
        batch_samples = []
        for _ in range(batch_size):
            sample = random.sample(all_findings, args.sample_size)
            batch_samples.append(sample)
        
        # Run rankings in parallel for this batch
        batch_results = []
        for sample in batch_samples:
            results = await run_parallel_rankings(sample, judge, 1)
            batch_results.extend(results)
        
        # Add results to aggregator
        for result in batch_results:
            if result and result.rankings:
                aggregator.add_ranking(result.rankings)
                successful_rounds += 1
                
        print(f"Completed {min(batch + 3, args.rounds)}/{args.rounds} rounds...")
    
    print(f"Successfully completed {successful_rounds}/{args.rounds} rounds")
    
    # Calculate final scores
    ranked_findings = aggregator.calculate_scores()
    
    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(f"analysis_output/GD{args.gd_number}/research")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"GD{args.gd_number}_ranked_findings.csv"
    
    save_results(ranked_findings, output_path)
    print(f"Results saved to {output_path}")
    
    # Print top 5 findings
    print("\nTop 5 Most Interesting/Surprising/Impactful Findings:")
    print("-" * 80)
    for i, finding in enumerate(ranked_findings[:5], 1):
        print(f"\n{i}. [{finding.section_id}] Score: {finding.score:.4f}")
        print(f"   Question: {finding.question}")
        print(f"   Finding: {finding.finding[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())