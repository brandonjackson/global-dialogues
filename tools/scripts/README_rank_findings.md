# Finding Ranking System

## Overview

The `rank_findings.py` script implements an LLM-based ranking system for investigation findings from the Global Dialogues survey analysis. It uses multiple LLM judges to evaluate and rank findings based on their interestingness, surprisingness, and potential impact.

## How It Works

1. **Parsing**: Extracts findings from investigation markdown files, including section IDs, questions, findings, and detailed results
2. **Sampling**: Randomly selects N findings for each ranking round
3. **Parallel Judging**: Uses 3 different LLM models (Claude Haiku, Gemini Flash, GPT-4o-mini) via OpenRouter API
4. **Robust Parsing**: Uses Pydantic models with retry logic for reliable response parsing
5. **Statistical Aggregation**: Applies Borda count method to aggregate rankings into scores (0.0-1.0)
6. **Output**: Generates CSV with all findings ranked by aggregate score

## Setup

### API Key Configuration

Create a `.env` file with your OpenRouter API key:
```bash
OPENROUTER_API_KEY=your_key_here
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Rank findings from GD5 with default settings
python tools/scripts/rank_findings.py 5
```

### Advanced Options

```bash
# Customize sample size and number of rounds
python tools/scripts/rank_findings.py 5 -n 15 -r 20

# Specify custom output path
python tools/scripts/rank_findings.py 5 -o custom_rankings.csv
```

### Parameters

- `gd_number`: Global Dialogue number (required)
- `-n, --sample-size`: Number of findings per ranking round (default: 10)
- `-r, --rounds`: Total number of ranking rounds (default: auto-calculated based on coverage)
- `-o, --output`: Custom output file path (default: `analysis_output/GD{N}/research/GD{N}_ranked_findings.csv`)

## Algorithm Details

### Sampling Strategy
- Each round randomly samples N findings from the complete set
- Auto-calculation ensures each finding is ranked approximately 5 times for statistical reliability
- Maximum of 30 rounds to control API costs

### Ranking Method
- **Borda Count**: Classic voting method where rankings are converted to points
  - 1st place = N points, 2nd place = N-1 points, etc.
  - Scores normalized to 0.0-1.0 scale
  - Higher scores indicate more interesting/impactful findings

### LLM Diversity
- Rotates through 3 different models to reduce bias:
  - Anthropic Claude 3 Haiku
  - Google Gemini Flash 1.5 8B  
  - OpenAI GPT-4o-mini
- All models use temperature=0.3 for consistency
- JSON response format enforced for reliable parsing

## Output Format

The CSV output includes:
- `rank`: Final ranking position (1 = most interesting)
- `score`: Aggregate Borda score (0.0-1.0)
- `section_id`: Finding identifier (e.g., "1.5", "3.2")
- `question`: Research question text
- `finding`: Main finding statement
- `avg_rank_position`: Average position across all rankings
- `num_rankings`: Total times this finding was ranked
- `details`: Supporting details (truncated to 500 chars in CSV)

## Cost Estimation

- Approximate cost: $0.01-0.03 per run (depending on settings)
- Each round uses ~2-3K tokens per model
- Default auto-calculated rounds optimize for coverage vs cost

## Error Handling

- Automatic retry (3 attempts) with exponential backoff for API failures
- Continues processing even if individual rounds fail
- Reports successful vs total rounds in output
- Validates JSON responses using Pydantic models