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
from datetime import datetime

import aiohttp
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# API Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_TEMPERATURE = 0.3

# LLM Models for ranking (models that support structured output)
LLM_MODELS = [
    "x-ai/grok-code-fast-1",
    "google/gemini-2.5-flash", 
    "openai/gpt-4.1",
    "deepseek/deepseek-chat-v3-0324"
]

# Ranking Configuration
DEFAULT_SAMPLE_SIZE = 10
DEFAULT_COVERAGE_FACTOR = 5  # Each finding should be ranked this many times on average
MAX_ROUNDS = 40  # Maximum number of ranking rounds
BATCH_SIZE = 10   # Number of parallel ranking tasks to run simultaneously

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_MIN_WAIT = 2
RETRY_MAX_WAIT = 10

# Output Configuration
MAX_DETAILS_LENGTH = 4000  # Truncate details in CSV output
INCLUDE_PER_MODEL_SCORES = True  # Toggle to include individual model scores (set to False to disable)
# Base CSV fields
BASE_CSV_FIELDS = ['rank', 'score', 'section_id', 'question', 'finding', 
                   'avg_rank_position', 'num_rankings', 'details']

# Add model columns if per-model scoring is enabled
if INCLUDE_PER_MODEL_SCORES:
    CSV_FIELDS = BASE_CSV_FIELDS + [f'model_{model.replace("/", "_").replace("-", "_")}' for model in LLM_MODELS]
else:
    CSV_FIELDS = BASE_CSV_FIELDS

# =============================================================================
# USAGE
# =============================================================================
# Usage:
#  # Quick dry run (parse findings only, no LLM calls)
#  python tools/scripts/rank_findings.py 5 --dry-run
#
#  # Basic usage for GD5 (default: 10 findings per round, auto-calculated rounds)
#  python tools/scripts/rank_findings.py 5
#
#  # Custom settings with more findings per round
#  python tools/scripts/rank_findings.py 5 -n 15 -r 20
#
#  # Specify custom output path
#  python tools/scripts/rank_findings.py 5 -o custom_rankings.csv
#
#  # Minimal run for testing (1 round, 5 findings)
#  python tools/scripts/rank_findings.py 5 -n 5 -r 1


# =============================================================================
# CLASS DEFINITIONS
# =============================================================================


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
    model_scores: Dict[str, List[float]] = field(default_factory=dict)  # Model name -> list of scores
    
    def to_dict(self):
        d = super().to_dict()
        d.update({
            'score': self.score,
            'avg_rank': sum(self.rank_positions) / len(self.rank_positions) if self.rank_positions else None,
            'num_rankings': len(self.rank_positions)
        })
        
        # Add per-model scores if enabled
        if INCLUDE_PER_MODEL_SCORES:
            for model_name in LLM_MODELS:
                scores = self.model_scores.get(model_name, [])
                if scores:
                    # Calculate average score for this model (Borda count normalized to 0-1)
                    avg_model_score = sum(scores) / len(scores)
                    d[f'model_{model_name.replace("/", "_").replace("-", "_")}'] = f"{avg_model_score:.4f}"
                else:
                    d[f'model_{model_name.replace("/", "_").replace("-", "_")}'] = 'N/A'
        
        return d


class RankingResponse(BaseModel):
    """Pydantic model for LLM ranking response."""
    rankings: List[str] = Field(..., description="Ordered list of section IDs from most to least interesting")
    reasoning: Optional[str] = Field(None, description="Optional reasoning for the rankings")
    model_used: Optional[str] = None  # Track which model was used for this ranking


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
            
        # Parse sections and questions - improved regex to capture full question text
        # Look for pattern: * **X.Y. Title:** Question text (until next * or end of line)
        pattern = r'\* \*\*(\d+\.\d+)\.[^:]+:\*\* ([^*\n]+(?:\n(?!\*)[^*\n]*)*)'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for section_id, question_text in matches:
            # Clean up the question text - remove extra whitespace and newlines
            cleaned_text = re.sub(r'\s+\n\s+', ' ', question_text.strip())
            questions[section_id] = cleaned_text
            
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
    
    def __init__(self, api_key: Optional[str] = None, log_file: Optional[Path] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")
        
        self.base_url = OPENROUTER_BASE_URL
        self.log_file = log_file
        
    def _create_prompt(self, findings: List[Finding]) -> str:
        """Create the prompt for ranking findings."""
        prompt = """You are an expert research evaluator tasked with ranking survey findings based on their interestingness, surprisingness, and potential impact.

You will be given a list of findings from a digital survey of a globally representative sample of people about a particular topic area regarding people's attitudes and beliefs about Artificial Intelligence. Each finding has:
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
    
    def _log_interaction(self, round_num: int, model: str, findings: List[Finding], 
                        prompt: str, response_data: dict, parsed_response: Optional[RankingResponse] = None, 
                        error: Optional[str] = None):
        """Log the full interaction for debugging and validation."""
        if not self.log_file:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "round": round_num,
            "model": model,
            "findings_count": len(findings),
            "findings": [f.to_dict() for f in findings],
            "prompt": prompt,
            "api_response": response_data,
            "parsed_response": parsed_response.model_dump() if parsed_response else None,
            "error": error
        }
        
        # Append to log file with proper formatting
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n=== ROUND {round_num} - {model} ===\n")
            f.write(json.dumps(log_entry, indent=2, ensure_ascii=False))
            f.write("\n" + "="*80 + "\n")
    
    @retry(stop=stop_after_attempt(MAX_RETRY_ATTEMPTS), wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT))
    async def get_ranking(self, findings: List[Finding], model: str, session: aiohttp.ClientSession, 
                         round_num: int = 0) -> RankingResponse:
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
            "temperature": DEFAULT_TEMPERATURE,
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with session.post(self.base_url, headers=headers, json=data) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    error_msg = f"API request failed with status {response.status}: {response_text}"
                    self._log_interaction(round_num, model, findings, prompt, 
                                        {"status": response.status, "text": response_text}, 
                                        error=error_msg)
                    raise Exception(error_msg)
                    
                result = json.loads(response_text)
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    parsed = json.loads(content)
                    ranking_response = RankingResponse(**parsed)
                    
                    # Log successful interaction
                    self._log_interaction(round_num, model, findings, prompt, result, ranking_response)
                    
                    return ranking_response
                except (json.JSONDecodeError, ValidationError) as e:
                    error_msg = f"Failed to parse response from {model}: {e}"
                    self._log_interaction(round_num, model, findings, prompt, result, error=error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            # Log any other errors
            self._log_interaction(round_num, model, findings, prompt, {}, error=str(e))
            raise


class RankingAggregator:
    """Aggregate rankings from multiple judges."""
    
    def __init__(self, findings: List[Finding]):
        self.findings = {f.section_id: f for f in findings}
        self.rankings: Dict[str, List[int]] = defaultdict(list)
        self.model_rankings: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))  # Model -> section_id -> positions
        
    def add_ranking(self, ranking: List[str], model_name: str):
        """Add a single ranking from a judge."""
        for position, section_id in enumerate(ranking, 1):
            if section_id in self.findings:
                self.rankings[section_id].append(position)
                self.model_rankings[model_name][section_id].append(position)
    
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
                
            # Calculate per-model scores
            model_scores = {}
            if INCLUDE_PER_MODEL_SCORES:
                for model_name in LLM_MODELS:
                    model_positions = self.model_rankings[model_name].get(section_id, [])
                    if model_positions:
                        # Borda score: higher is better (n points for 1st place, 1 point for last)
                        n = len(self.findings)
                        borda_scores = [n - pos + 1 for pos in model_positions]
                        avg_borda = sum(borda_scores) / len(borda_scores)
                        # Normalize to 0-1 scale
                        model_scores[model_name] = [avg_borda / n]
                    else:
                        model_scores[model_name] = []
            
            ranked = RankedFinding(
                section_id=finding.section_id,
                question=finding.question,
                finding=finding.finding,
                details=finding.details,
                score=score,
                rank_positions=positions,
                model_scores=model_scores
            )
            ranked_findings.append(ranked)
            
        # Sort by score descending
        ranked_findings.sort(key=lambda x: x.score, reverse=True)
        return ranked_findings


async def run_parallel_rankings(findings: List[Finding], judge: LLMJudge, round_num: int = 0) -> List[RankingResponse]:
    """Run ranking of the same findings by all models in parallel."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Send the same findings to all models for direct comparison
        for model in LLM_MODELS:
            task = judge.get_ranking(findings, model, session, round_num)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and add model info
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Warning: Model {LLM_MODELS[i]} failed: {result}", file=sys.stderr)
            else:
                result.model_used = LLM_MODELS[i]  # Track which model was used
                valid_results.append(result)
                
        return valid_results


def calculate_num_rounds(n_findings: int, n_sample: int, total_findings: int) -> int:
    """Calculate recommended number of rounds based on sampling parameters."""
    # Ensure good coverage: each finding should be ranked at least DEFAULT_COVERAGE_FACTOR times on average
    # Since each round now uses all models, we need fewer rounds
    rounds = math.ceil((total_findings * DEFAULT_COVERAGE_FACTOR) / (n_sample * len(LLM_MODELS)))
    
    # But cap at a reasonable maximum
    return min(rounds, MAX_ROUNDS)


def save_results(ranked_findings: List[RankedFinding], output_path: Path):
    """Save ranked findings to CSV with full question text."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        
        for rank, finding in enumerate(ranked_findings, 1):
            row = finding.to_dict()
            
            # Ensure full question text is saved (no truncation)
            full_question = row['question']
            
            writer.writerow({
                'rank': rank,
                'score': f"{row['score']:.4f}",
                'section_id': row['section_id'],
                'question': full_question,  # Full question text preserved
                'finding': row['finding'],
                'avg_rank_position': f"{row['avg_rank']:.2f}" if row['avg_rank'] else 'N/A',
                'num_rankings': row['num_rankings'],
                'details': row['details'][:MAX_DETAILS_LENGTH] + '...' if len(row['details']) > MAX_DETAILS_LENGTH else row['details']
            })


async def main():
    parser = argparse.ArgumentParser(description='Rank investigation findings using LLM judges')
    parser.add_argument('gd_number', type=int, help='Global Dialogue number (e.g., 5 for GD5)')
    parser.add_argument('-n', '--sample-size', type=int, default=DEFAULT_SAMPLE_SIZE,
                       help=f'Number of findings per sample (default: {DEFAULT_SAMPLE_SIZE})')
    parser.add_argument('-r', '--rounds', type=int, default=None,
                       help='Number of ranking rounds (default: auto-calculated)')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output CSV file path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse findings and show sample prompts without making LLM API calls')
    
    args = parser.parse_args()
    
    # Parse findings
    print(f"Parsing findings from GD{args.gd_number}...")
    parser = FindingParser(args.gd_number)
    all_findings = parser.parse_findings()
    print(f"Found {len(all_findings)} total findings")
    
    if len(all_findings) < args.sample_size:
        print(f"Warning: Only {len(all_findings)} findings available, using all of them")
        args.sample_size = len(all_findings)
    
    # Dry run mode - show sample findings and prompts without making API calls
    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
        print(f"Sample of {min(3, len(all_findings))} findings:")
        for i, finding in enumerate(all_findings[:3]):
            print(f"\n{i+1}. [{finding.section_id}]")
            print(f"   Question: {finding.question[:100]}...")
            print(f"   Finding: {finding.finding[:100]}...")
        
        # Show sample prompt
        print(f"\n=== SAMPLE PROMPT (first {min(args.sample_size, len(all_findings))} findings) ===")
        sample_findings = all_findings[:args.sample_size]
        judge = LLMJudge()
        sample_prompt = judge._create_prompt(sample_findings)
        print(sample_prompt[:1000] + "..." if len(sample_prompt) > 1000 else sample_prompt)
        
        print(f"\n=== CONFIGURATION ===")
        print(f"Total findings: {len(all_findings)}")
        print(f"Sample size: {args.sample_size}")
        if args.rounds:
            print(f"Rounds: {args.rounds}")
        else:
            calculated_rounds = calculate_num_rounds(args.sample_size, args.sample_size, len(all_findings))
            print(f"Rounds: {calculated_rounds} (auto-calculated)")
        print(f"Models: {', '.join(LLM_MODELS)}")
        print(f"Estimated API calls: {len(LLM_MODELS) * (args.rounds or calculate_num_rounds(args.sample_size, args.sample_size, len(all_findings)))}")
        print("\nDry run complete. Remove --dry-run to execute actual ranking.")
        return
    
    # Calculate number of rounds if not specified
    if args.rounds is None:
        args.rounds = calculate_num_rounds(args.sample_size, args.sample_size, len(all_findings))
    
    print(f"Running {args.rounds} ranking rounds with {args.sample_size} findings per round...")
    print(f"Each round will be evaluated by all {len(LLM_MODELS)} models for direct comparison.")
    
    # Initialize aggregator and judge with logging
    aggregator = RankingAggregator(all_findings)
    
    # Set up logging file
    log_dir = Path(f"analysis_output/GD{args.gd_number}/research")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"GD{args.gd_number}_ranking_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    judge = LLMJudge(log_file=log_file)
    
    # Initialize log file with metadata
    with open(log_file, 'w', encoding='utf-8') as f:
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "gd_number": args.gd_number,
            "total_findings": len(all_findings),
            "sample_size": args.sample_size,
            "rounds": args.rounds,
            "models": LLM_MODELS,
            "settings": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_retry_attempts": MAX_RETRY_ATTEMPTS,
                "coverage_factor": DEFAULT_COVERAGE_FACTOR
            }
        }
        f.write(json.dumps({"metadata": metadata}, indent=2, ensure_ascii=False))
        f.write("\n" + "="*80 + "\n")
    
    print(f"Logging all interactions to: {log_file}")
    
    # Run ranking rounds
    successful_rounds = 0
    for round_num in range(args.rounds):
        # Sample findings for this round
        sample = random.sample(all_findings, args.sample_size)
        
        # Run rankings by all models in parallel for this sample
        results = await run_parallel_rankings(sample, judge, round_num + 1)
        
        # Add results to aggregator
        for result in results:
            if result and result.rankings:
                aggregator.add_ranking(result.rankings, result.model_used)
                successful_rounds += 1
                
        print(f"Completed round {round_num + 1}/{args.rounds} (sample size: {len(sample)})...")
    
    print(f"Successfully completed {successful_rounds}/{args.rounds * len(LLM_MODELS)} model evaluations across {args.rounds} rounds")
    print(f"Full interaction log saved to: {log_file}")
    
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
    print(f"Note: Full question text is now preserved in the CSV output")
    
    # Print top 5 findings
    print("\nTop 5 Most Interesting/Surprising/Impactful Findings:")
    print("-" * 80)
    for i, finding in enumerate(ranked_findings[:5], 1):
        print(f"\n{i}. [{finding.section_id}] Score: {finding.score:.4f}")
        print(f"   Question: {finding.question}")
        print(f"   Finding: {finding.finding[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())