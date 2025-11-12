#!/usr/bin/env python3
"""
Script to compile verbatims into a human-readable markdown file.

This script processes Global Dialogues survey data to create a formatted markdown
document that combines survey questions/statements with their corresponding
verbatim responses from participants.

The script:
1. Reads the survey structure from the human-readable markdown file
2. Maps question numbers to their UUIDs using the question_id_mapping.csv
3. Loads verbatim responses from the verbatim_map.csv
4. Generates a formatted markdown output with questions and their verbatims

Output files are saved to analysis_output/GD<NUMBER>/verbatims/ with filenames
that include the question range if specified.

Usage Examples:
    # Generate verbatims for all questions in GD3
    python analyze_verbatims.py GD3

    # Generate verbatims for questions 51-53 in GD3
    python analyze_verbatims.py GD3 --start-question 51 --end-question 53

    # Generate verbatims from question 38 onwards in GD3
    python analyze_verbatims.py GD3 --start-question 38

    # Generate verbatims up to question 20 in GD3
    python analyze_verbatims.py GD3 --end-question 20

    # Specify a custom output file
    python analyze_verbatims.py GD3 --start-question 38 --end-question 40 --output custom_output.md

Input Files Required:
    - GD<NUMBER>_survey_human_readable.md: Survey structure with numbered items
    - GD<NUMBER>_question_id_mapping.csv: Maps item numbers to question UUIDs
    - GD<NUMBER>_verbatim_map.csv: Contains verbatim responses indexed by question UUID

Output Format:
    For each item in the survey:
    - H2 header with item number and UUID (if it's a question)
    - H3 "Item Text" section with the original question/statement text
    - For questions only:
      - H3 "Analysis of Responses" section (placeholder for future analysis)
      - H3 "Full Verbatims" section with bullet points of all responses
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

# Add parent directory to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.analysis_utils import parse_gd_identifier, validate_gd_directory


def parse_numbered_items(markdown_content):
    """
    Parse numbered items from the survey markdown file.
    
    Extracts items that start with a number followed by a period (e.g., "1.", "2.").
    Each item includes all text until the next numbered item is encountered.
    
    Args:
        markdown_content (str): The full content of the survey markdown file
        
    Returns:
        list: List of tuples where each tuple is (item_number, item_text)
              - item_number (int): The numeric identifier of the item
              - item_text (str): The full text content of the item including
                                any sub-items, options, or formatting
              
    Example:
        Input markdown with "1. Question text\\n   - Option A\\n2. Next question"
        Returns: [(1, "Question text\\n   - Option A"), (2, "Next question")]
    """
    items = []
    lines = markdown_content.split('\n')
    current_item = None
    current_text = []
    
    for line in lines:
        # Match numbered items like "1.", "2.", etc.
        match = re.match(r'^(\d+)\.\s*(.*)$', line)
        if match:
            # Save previous item if exists
            if current_item is not None:
                items.append((current_item, '\n'.join(current_text).strip()))
            
            # Start new item
            current_item = int(match.group(1))
            current_text = [match.group(2)] if match.group(2) else []
        elif current_item is not None:
            # Continue current item
            current_text.append(line)
    
    # Don't forget the last item
    if current_item is not None:
        items.append((current_item, '\n'.join(current_text).strip()))
    
    return items


def load_question_mapping(mapping_file):
    """
    Load question ID mapping from CSV file.
    
    The mapping file connects human-readable item numbers to their UUIDs.
    Items that appear in this mapping are considered "questions" (as opposed
    to statements/instructions which don't have UUIDs).
    
    Args:
        mapping_file (Path): Path to the question_id_mapping.csv file
        
    Returns:
        dict: Dictionary mapping human_readable_id (int) -> (uuid, question_text)
              - uuid (str): The unique identifier for the question
              - question_text (str): The text of the question
              
    Note:
        Only items that have entries in this file are considered questions.
        Items without entries are treated as statements/instructions.
    """
    mapping = {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_num = int(row['human_readable_id'])
            uuid = row['uuid']
            question_text = row['question_text']
            mapping[item_num] = (uuid, question_text)
    return mapping


def load_verbatims(verbatim_file):
    """
    Load verbatim responses from CSV file.
    
    Processes the verbatim map CSV which contains participant responses
    (thoughts) indexed by question UUID. Each response is normalized by
    removing line breaks and normalizing whitespace.
    
    Args:
        verbatim_file (Path): Path to the verbatim_map.csv file
        
    Returns:
        dict: Dictionary mapping question_id (str) -> list of verbatim texts
              Each verbatim is a single-line string with normalized whitespace.
              
    Note:
        - Empty verbatims are skipped
        - Line breaks within verbatims are converted to spaces
        - Multiple spaces are collapsed to single spaces
    """
    verbatims = {}
    with open(verbatim_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_id = row['Question ID']
            thought_text = row['Thought Text'].strip()
            
            if question_id not in verbatims:
                verbatims[question_id] = []
            
            if thought_text:  # Only add non-empty verbatims
                # Strip line breaks and normalize whitespace
                normalized_text = ' '.join(thought_text.split())
                verbatims[question_id].append(normalized_text)
    
    return verbatims


def filter_items_by_range(items, start_question, end_question):
    """
    Filter items to only include those within the specified question range.
    
    Args:
        items (list): List of (item_number, item_text) tuples
        start_question (int, optional): Starting question number (inclusive).
                                        If None, no lower bound is applied.
        end_question (int, optional): Ending question number (inclusive).
                                     If None, no upper bound is applied.
        
    Returns:
        list: Filtered list of (item_number, item_text) tuples containing
              only items within the specified range.
              
    Example:
        filter_items_by_range([(1, "A"), (5, "B"), (10, "C")], 3, 8)
        Returns: [(5, "B")]
    """
    if start_question is None and end_question is None:
        return items
    
    filtered = []
    for item_num, item_text in items:
        if start_question is not None and item_num < start_question:
            continue
        if end_question is not None and item_num > end_question:
            continue
        filtered.append((item_num, item_text))
    
    return filtered


def generate_output_markdown(items, question_mapping, verbatims, output_file):
    """
    Generate the output markdown file with formatted verbatims.
    
    Creates a structured markdown document with:
    - H2 headers for each item (with UUID for questions)
    - Item text sections
    - Analysis placeholder sections (for questions only)
    - Full verbatims sections with bullet points (for questions only)
    
    Args:
        items (list): List of (item_number, item_text) tuples to include
        question_mapping (dict): Dictionary mapping item numbers to (uuid, question_text)
        verbatims (dict): Dictionary mapping question UUIDs to lists of verbatim texts
        output_file (Path): Path where the output markdown file should be written
        
    Note:
        - Statements (items without UUIDs) only get item number and text
        - Questions get additional "Analysis of Responses" and "Full Verbatims" sections
        - If no verbatims exist for a question, a placeholder message is included
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Survey Questions with Verbatims\n\n")
        
        for item_num, item_text in items:
            # Check if this is a question (has mapping) or statement
            is_question = item_num in question_mapping
            
            if is_question:
                uuid, question_text = question_mapping[item_num]
                # Write H2 header
                f.write(f"## Item {item_num} (id: {uuid})\n\n")
            else:
                # For statements, just use the item number
                f.write(f"## Item {item_num}\n\n")
            
            # Write Item Text section
            f.write("### Item Text\n\n")
            f.write(f"{item_text}\n\n")
            
            # For questions, add Analysis and Verbatims sections
            if is_question:
                uuid, _ = question_mapping[item_num]
                
                # Analysis of Responses section
                f.write("### Analysis of Responses\n\n")
                f.write("_Analysis section to be populated_\n\n")
                
                # Full Verbatims section
                f.write("### Full Verbatims\n\n")
                
                if uuid in verbatims and verbatims[uuid]:
                    for verbatim in verbatims[uuid]:
                        f.write(f"- {verbatim}\n")
                else:
                    f.write("_No verbatims available for this question._\n")
                
                f.write("\n")


def main():
    """
    Main entry point for the script.
    
    Parses command-line arguments, validates input files, processes survey data,
    and generates the output markdown file with verbatims.
    """
    parser = argparse.ArgumentParser(
        description='Compile verbatims into a human-readable markdown file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s GD3
  %(prog)s GD3 --start-question 51 --end-question 53
  %(prog)s GD3 --start-question 38
  %(prog)s GD3 --end-question 20
  %(prog)s GD3 --start-question 38 --end-question 40 --output custom.md
        """
    )
    parser.add_argument(
        'gd_number',
        type=str,
        help='GD number (e.g., GD3, 3, etc.)'
    )
    parser.add_argument(
        '--start-question',
        type=int,
        default=None,
        help='Starting question number (inclusive)'
    )
    parser.add_argument(
        '--end-question',
        type=int,
        default=None,
        help='Ending question number (inclusive)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: analysis_output/GD<NUMBER>/verbatims/GD<NUMBER>_verbatims_analysis[_range].md)'
    )
    
    args = parser.parse_args()
    
    # Parse and validate GD identifier (handles formats like "3", "GD3", "6UK", etc.)
    gd_identifier = parse_gd_identifier(args.gd_number)
    data_dir = Path(validate_gd_directory(gd_identifier))
    
    # Construct file paths for required input files
    survey_file = data_dir / f"{gd_identifier}_survey_human_readable.md"
    mapping_file = data_dir / f"{gd_identifier}_question_id_mapping.csv"
    verbatim_file = data_dir / f"{gd_identifier}_verbatim_map.csv"
    
    # Check if files exist
    if not survey_file.exists():
        print(f"Error: Survey file not found: {survey_file}")
        sys.exit(1)
    if not mapping_file.exists():
        print(f"Error: Mapping file not found: {mapping_file}")
        sys.exit(1)
    if not verbatim_file.exists():
        print(f"Error: Verbatim file not found: {verbatim_file}")
        sys.exit(1)
    
    # Determine output file location
    if args.output:
        # Use custom output path if provided
        output_file = Path(args.output)
    else:
        # Default: analysis_output/GD<NUMBER>/verbatims/
        output_dir = Path("analysis_output") / gd_identifier / "verbatims"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build filename with optional range suffix for better organization
        # Examples: GD3_verbatims_analysis_51-53.md, GD3_verbatims_analysis_38-end.md
        if args.start_question is not None or args.end_question is not None:
            range_suffix = ""
            if args.start_question is not None and args.end_question is not None:
                range_suffix = f"_{args.start_question}-{args.end_question}"
            elif args.start_question is not None:
                range_suffix = f"_{args.start_question}-end"
            elif args.end_question is not None:
                range_suffix = f"_start-{args.end_question}"
            output_file = output_dir / f"{gd_identifier}_verbatims_analysis{range_suffix}.md"
        else:
            # No range specified - include all questions
            output_file = output_dir / f"{gd_identifier}_verbatims_analysis.md"
    
    # Read survey markdown
    print(f"Reading survey file: {survey_file}")
    with open(survey_file, 'r', encoding='utf-8') as f:
        survey_content = f.read()
    
    # Parse numbered items
    print("Parsing numbered items from survey...")
    items = parse_numbered_items(survey_content)
    print(f"Found {len(items)} items")
    
    # Filter by range if provided
    if args.start_question or args.end_question:
        items = filter_items_by_range(items, args.start_question, args.end_question)
        print(f"Filtered to {len(items)} items in range")
    
    # Load question mapping
    print(f"Loading question mapping: {mapping_file}")
    question_mapping = load_question_mapping(mapping_file)
    print(f"Found {len(question_mapping)} question mappings")
    
    # Load verbatims
    print(f"Loading verbatims: {verbatim_file}")
    verbatims = load_verbatims(verbatim_file)
    print(f"Found verbatims for {len(verbatims)} questions")
    
    # Generate output
    print(f"Generating output markdown: {output_file}")
    generate_output_markdown(items, question_mapping, verbatims, output_file)
    
    print(f"Done! Output written to: {output_file}")


if __name__ == '__main__':
    main()

