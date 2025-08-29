#!/usr/bin/env python3
"""
Generate human-readable survey documentation and question ID mappings for Global Dialogues.

This script performs a two-step pipeline:
1. Generates a human-readable markdown version of the survey from the discussion guide
2. Creates a question ID mapping CSV that links human-readable IDs to UUIDs

Usage:
    python generate_survey_documentation.py --gd_number <ID>
"""

import argparse
import csv
import logging
import re
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple, Optional
from lib.analysis_utils import parse_gd_identifier, validate_gd_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_discussion_guide(file_path: Path) -> List[Dict]:
    """Parse the discussion guide CSV to extract questions and options."""
    questions = []
    question_num = 1
    
    try:
        # Read the CSV with many columns
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            # Skip empty lines at the beginning
            headers = next(reader)
            while not any(headers):
                headers = next(reader)
            
            # Find relevant column indices
            item_type_idx = None
            content_idx = None
            
            for i, header in enumerate(headers):
                if 'Item type' in header or 'item type' in header.lower():
                    item_type_idx = i
                if header == 'Content' or 'content' in header.lower():
                    content_idx = i
            
            if item_type_idx is None or content_idx is None:
                logger.warning(f"Could not find required columns in discussion guide. Headers: {headers[:10]}")
                return questions
            
            # Find indices for poll options (look for "Poll or Category Option" columns)
            option_indices = []
            for i, header in enumerate(headers):
                if 'Poll or Category Option' in header or header.startswith('Poll Option'):
                    option_indices.append(i)
            
            # If no option columns found, use columns after 'Content'
            if not option_indices:
                option_indices = list(range(content_idx + 5, min(len(headers), content_idx + 25)))
            
            for row in reader:
                if len(row) <= content_idx:
                    continue
                    
                item_type = row[item_type_idx] if item_type_idx < len(row) else ''
                content = row[content_idx] if content_idx < len(row) else ''
                
                if not content or not content.strip():
                    continue
                
                # Extract options from option columns
                options = []
                for idx in option_indices:
                    if idx < len(row):
                        opt = row[idx]
                        if opt and opt.strip() and opt.strip() not in ['', 'Randomize']:
                            options.append(opt.strip())
                
                # Determine question type
                is_select = 'select' in item_type.lower()
                is_speak = 'speak' in item_type.lower()
                is_open = 'open' in item_type.lower() or 'ask' in item_type.lower()
                
                if content and (is_select or is_speak or is_open):
                    question_data = {
                        'number': question_num,
                        'type': item_type,
                        'content': content.strip(),
                        'options': options if is_select else []
                    }
                    questions.append(question_data)
                    question_num += 1
                    
    except Exception as e:
        logger.error(f"Error reading discussion guide: {e}")
        
    return questions


def generate_human_readable_survey(questions: List[Dict], output_path: Path):
    """Generate a markdown file with the human-readable survey."""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Survey Questions\n\n")
        
        for q in questions:
            # Write question number and text
            f.write(f"{q['number']}. {q['content']}\n")
            
            # Write options if present (and not a country list)
            if q['options']:
                # Check if this is a country question
                if any(country in q['options'] for country in ['Afghanistan', 'United States', 'China', 'India']):
                    # It's likely a country list, just indicate it
                    f.write("   - Afghanistan\n")
                    f.write("   - Albania\n")
                    f.write("   - Algeria\n")
                    f.write("   - Andorra\n")
                    f.write("   - … etc\n")
                else:
                    # Regular options, list them all
                    for option in q['options']:
                        f.write(f"   - {option}\n")
            
            f.write("\n")
    
    logger.info(f"Generated human-readable survey at {output_path}")


def extract_questions_from_aggregate(file_path: Path) -> pd.DataFrame:
    """Extract unique questions from the aggregate standardized CSV."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
        
        # Get unique questions
        questions_df = df[['Question ID', 'Question Type', 'Question']].drop_duplicates()
        
        # Find branch columns
        branch_cols = [col for col in df.columns if col.startswith('Branches (')]
        
        return questions_df, df, branch_cols
    except Exception as e:
        logger.error(f"Error reading aggregate standardized file: {e}")
        return pd.DataFrame(), pd.DataFrame(), []


def fuzzy_match_question(question1: str, question2: str) -> bool:
    """Check if two questions are essentially the same, accounting for formatting differences."""
    # Normalize both questions
    def normalize(text):
        # Remove extra whitespace, newlines, and punctuation differences
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().lower()
        # Remove special characters for comparison
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    norm1 = normalize(question1)
    norm2 = normalize(question2)
    
    # Check exact match
    if norm1 == norm2:
        return True
    
    # Check if one is contained in the other (for partial matches)
    if len(norm1) > 20 and len(norm2) > 20:
        if norm1 in norm2 or norm2 in norm1:
            return True
    
    # Check similarity ratio (for very similar questions)
    from difflib import SequenceMatcher
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    return similarity > 0.9


def create_question_id_mapping(
    survey_questions: List[Dict],
    aggregate_questions_df: pd.DataFrame,
    aggregate_df: pd.DataFrame,
    branch_cols: List[str],
    output_path: Path
):
    """Create a CSV mapping human-readable IDs to UUIDs."""
    
    mappings = []
    
    for q in survey_questions:
        question_text = q['content']
        human_id = str(q['number'])
        
        # Find matching question in aggregate
        matched = False
        for _, row in aggregate_questions_df.iterrows():
            if fuzzy_match_question(question_text, row['Question']):
                mappings.append({
                    'human_readable_id': human_id,
                    'uuid': row['Question ID'],
                    'question_text': row['Question']
                })
                matched = True
                
                # Check for branch questions
                check_for_branches(
                    human_id, 
                    row['Question'], 
                    aggregate_questions_df, 
                    aggregate_df,
                    branch_cols,
                    mappings
                )
                break
        
        if not matched:
            logger.warning(f"Could not find UUID for question {human_id}: {question_text[:50]}...")
    
    # Write to CSV
    df = pd.DataFrame(mappings)
    df.to_csv(output_path, index=False)
    logger.info(f"Created question ID mapping at {output_path}")
    
    return df


def check_for_branches(
    parent_human_id: str,
    parent_question: str,
    aggregate_questions_df: pd.DataFrame,
    aggregate_df: pd.DataFrame,
    branch_cols: List[str],
    mappings: List[Dict]
):
    """Check for and add branch questions to the mapping."""
    
    # Find the relevant branch column
    relevant_branch_col = None
    for col in branch_cols:
        # Extract question text from column name
        col_question = col.replace('Branches (', '').rstrip(')')
        if fuzzy_match_question(parent_question, col_question):
            relevant_branch_col = col
            break
    
    if not relevant_branch_col:
        return
    
    # Find branch questions
    branch_questions = aggregate_questions_df[
        aggregate_questions_df['Question'].str.contains('^Branch [A-C] - ', regex=True, na=False)
    ]
    
    for _, branch_row in branch_questions.iterrows():
        branch_text = branch_row['Question']
        
        # Check if this branch belongs to our parent question
        branch_df = aggregate_df[aggregate_df['Question ID'] == branch_row['Question ID']]
        if not branch_df.empty:
            branch_values = branch_df[relevant_branch_col].dropna().unique()
            
            # Determine branch letter
            branch_match = re.match(r'^Branch ([A-C]) - ', branch_text)
            if branch_match:
                branch_letter = branch_match.group(1).lower()
                
                # Check if this branch is associated with our parent
                if any(f'Branch {branch_letter.upper()}' in str(val) for val in branch_values):
                    branch_human_id = f"{parent_human_id}_branch_{branch_letter}"
                    
                    # Add to mappings if not already present
                    if not any(m['human_readable_id'] == branch_human_id for m in mappings):
                        mappings.append({
                            'human_readable_id': branch_human_id,
                            'uuid': branch_row['Question ID'],
                            'question_text': branch_text
                        })


def update_survey_with_branches(
    survey_path: Path,
    mapping_df: pd.DataFrame
):
    """Update the survey markdown with any missing branch questions."""
    
    # Read current survey
    with open(survey_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find branch questions in mapping
    branch_questions = mapping_df[mapping_df['human_readable_id'].str.contains('_branch_', na=False)]
    
    if branch_questions.empty:
        logger.info("No branch questions to add to survey")
        return
    
    # Group branches by parent
    branches_by_parent = {}
    for _, row in branch_questions.iterrows():
        parent_id = row['human_readable_id'].split('_branch_')[0]
        if parent_id not in branches_by_parent:
            branches_by_parent[parent_id] = []
        branches_by_parent[parent_id].append(row)
    
    # Insert branches after their parent questions
    new_lines = []
    for line in lines:
        new_lines.append(line)
        
        # Check if this line starts a question that has branches
        for parent_id, branches in branches_by_parent.items():
            if line.strip().startswith(f"{parent_id}. "):
                # Skip to next non-option line
                current_idx = lines.index(line)
                while current_idx + 1 < len(lines) and lines[current_idx + 1].strip().startswith('-'):
                    current_idx += 1
                
                # Add branch questions
                for branch in branches:
                    branch_id = branch['human_readable_id']
                    branch_text = branch['question_text']
                    new_lines.append(f"\n{branch_id}. {branch_text}\n")
                
                # Remove from dict so we don't add again
                del branches_by_parent[parent_id]
                break
    
    # Write updated survey
    with open(survey_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    logger.info(f"Updated survey with {len(branch_questions)} branch questions")


def main():
    parser = argparse.ArgumentParser(
        description='Generate human-readable survey documentation and question ID mappings'
    )
    parser.add_argument(
        '--gd_number',
        type=str,
        required=True,
        help='Global Dialogue identifier (e.g., "3", "6UK")'
    )
    
    args = parser.parse_args()
    
    # Parse and validate GD identifier
    gd_identifier = parse_gd_identifier(args.gd_number)
    try:
        data_dir = Path(validate_gd_directory(gd_identifier))
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Define file paths
    discussion_guide_path = data_dir / f"{gd_identifier}_discussion_guide.csv"
    aggregate_std_path = data_dir / f"{gd_identifier}_aggregate_standardized.csv"
    survey_output_path = data_dir / f"{gd_identifier}_survey_human_readable.md"
    mapping_output_path = data_dir / f"{gd_identifier}_question_id_mapping.csv"
    
    # Check prerequisites
    if not discussion_guide_path.exists():
        logger.error(f"Discussion guide not found: {discussion_guide_path}")
        sys.exit(1)
    
    if not aggregate_std_path.exists():
        logger.error(f"Aggregate standardized file not found: {aggregate_std_path}")
        logger.info("Please run preprocessing first: make preprocess GD=<ID>")
        sys.exit(1)
    
    logger.info(f"Generating survey documentation for {gd_identifier}")
    
    # Step 1: Generate human-readable survey
    logger.info("Step 1: Parsing discussion guide and generating human-readable survey")
    questions = parse_discussion_guide(discussion_guide_path)
    
    if not questions:
        logger.error("No questions found in discussion guide")
        sys.exit(1)
    
    generate_human_readable_survey(questions, survey_output_path)
    
    # Step 2: Create question ID mapping
    logger.info("Step 2: Creating question ID mapping")
    aggregate_questions_df, aggregate_df, branch_cols = extract_questions_from_aggregate(aggregate_std_path)
    
    if aggregate_questions_df.empty:
        logger.error("Could not extract questions from aggregate standardized file")
        sys.exit(1)
    
    mapping_df = create_question_id_mapping(
        questions,
        aggregate_questions_df,
        aggregate_df,
        branch_cols,
        mapping_output_path
    )
    
    # Step 3: Update survey with branch questions
    logger.info("Step 3: Updating survey with branch questions")
    update_survey_with_branches(survey_output_path, mapping_df)
    
    logger.info(f"Successfully generated survey documentation for {gd_identifier}")
    logger.info(f"  - Human-readable survey: {survey_output_path}")
    logger.info(f"  - Question ID mapping: {mapping_output_path}")


if __name__ == "__main__":
    main()