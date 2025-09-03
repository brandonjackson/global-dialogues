#!/usr/bin/env python3
"""
GD Investigation Infrastructure Factory
Creates the parallel analysis infrastructure for any GD[N] survey
"""

import sys
import csv
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import re
from jinja2 import Template

def render_template(template_path, **kwargs):
    """Render a Jinja2 template with given variables"""
    with open(template_path) as f:
        template = Template(f.read())
    return template.render(**kwargs)

def parse_investigation_questions(gd_num, base_dir):
    """Parse the investigation questions file to extract sections"""
    questions_file = base_dir / f"analysis_output/GD{gd_num}/research/GD{gd_num}_investigation_questions.md"
    
    if not questions_file.exists():
        print(f"Error: {questions_file} not found")
        print("Please ensure GD{gd_num}_investigation_questions.md exists before running this script")
        return []
    
    sections = []
    
    with open(questions_file) as f:
        content = f.read()
        
        # Find all section headers - handles both "## Section X:" and "## **Section X:**" formats
        section_pattern = r'^##\s+\*{0,2}Section\s+(\d+):\s*(.+?)(?:\*{0,2})\s*$'
        
        for match in re.finditer(section_pattern, content, re.MULTILINE):
            section_num = match.group(1)
            section_title = match.group(2).strip().rstrip('*').strip()
            
            sections.append({
                'section_num': section_num,
                'section_title': section_title,
                'status': 'available',
                'claimed_at': '',
                'completed_at': '',
                'review_status': 'pending'
            })
    
    return sections

def create_tracker_csv(output_dir, sections):
    """Create the tracker.csv file"""
    tracker_path = output_dir / "tracker.csv"
    
    if not sections:
        print("Warning: No sections found to track")
        # Create empty tracker with headers
        with open(tracker_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['section_num', 'section_title', 'status', 
                                                   'claimed_at', 'completed_at', 'review_status'])
            writer.writeheader()
    else:
        with open(tracker_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sections[0].keys())
            writer.writeheader()
            writer.writerows(sections)
    
    print(f"✓ Created: {tracker_path} with {len(sections)} sections")
    return tracker_path

def copy_section_manager(output_dir):
    """Copy the section_manager.py script"""
    template_path = Path(__file__).parent.parent / "templates/gd_investigation/section_manager.py"
    dest_path = output_dir / "section_manager.py"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return None
    
    shutil.copy2(template_path, dest_path)
    dest_path.chmod(0o755)
    print(f"✓ Created: {dest_path}")
    return dest_path

def create_assembly_script(output_dir, gd_num):
    """Create the assembly script from template"""
    template_path = Path(__file__).parent.parent / "templates/gd_investigation/assemble_report.py.j2"
    dest_path = output_dir / "assemble_report.py"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return None
    
    content = render_template(template_path, gd_num=gd_num)
    dest_path.write_text(content)
    dest_path.chmod(0o755)
    print(f"✓ Created: {dest_path}")
    return dest_path

def create_analysis_prompt(output_dir, gd_num):
    """Create the analysis prompt from template"""
    template_path = Path(__file__).parent.parent / "templates/gd_investigation/ANALYSIS_PROMPT.md.j2"
    dest_path = output_dir / f"ANALYSIS_PROMPT_GD{gd_num}.md"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return None
    
    content = render_template(template_path, gd_num=gd_num)
    dest_path.write_text(content)
    print(f"✓ Created: {dest_path}")
    return dest_path

def create_review_prompt(output_dir, gd_num):
    """Create the review prompt from template"""
    template_path = Path(__file__).parent.parent / "templates/gd_investigation/REVIEW_PROMPT.md.j2"
    dest_path = output_dir / f"REVIEW_PROMPT_GD{gd_num}.md"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return None
    
    content = render_template(template_path, gd_num=gd_num)
    dest_path.write_text(content)
    print(f"✓ Created: {dest_path}")
    return dest_path

def validate_prerequisites(gd_num, base_dir):
    """Check that required files and directories exist"""
    issues = []
    
    # Check for investigation questions file
    questions_file = base_dir / f"analysis_output/GD{gd_num}/research/GD{gd_num}_investigation_questions.md"
    if not questions_file.exists():
        issues.append(f"Missing: {questions_file}")
    
    # Check for research guide
    guide_file = base_dir / "docs/gd_research_guide.md"
    if not guide_file.exists():
        issues.append(f"Missing: {guide_file} (needed for analysis guidance)")
    
    # Check for templates
    template_dir = base_dir / "templates/gd_investigation"
    if not template_dir.exists():
        issues.append(f"Missing: {template_dir} directory")
    
    return issues

def main():
    parser = argparse.ArgumentParser(
        description='Create GD investigation infrastructure for parallel analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_investigation_infrastructure.py 5
  python scripts/create_investigation_infrastructure.py 6 --base-dir /path/to/project
        """
    )
    parser.add_argument('gd_num', type=int, help='GD number (e.g., 5 for GD5)')
    parser.add_argument('--base-dir', type=Path, default=Path.cwd(), 
                       help='Base directory of the project (default: current directory)')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing infrastructure')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Creating GD{args.gd_num} Investigation Infrastructure")
    print(f"{'='*60}\n")
    
    # Validate prerequisites
    issues = validate_prerequisites(args.gd_num, args.base_dir)
    if issues:
        print("⚠️  Prerequisites not met:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease resolve these issues before proceeding.")
        sys.exit(1)
    
    # Create output directory structure
    output_dir = args.base_dir / f"analysis_output/GD{args.gd_num}/research"
    sections_dir = output_dir / "sections"
    
    # Check if infrastructure already exists
    if (output_dir / "tracker.csv").exists() and not args.force:
        print(f"⚠️  Infrastructure already exists in {output_dir}")
        print("   Use --force to overwrite")
        sys.exit(1)
    
    sections_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {sections_dir}")
    
    # Parse investigation questions to get sections
    print(f"\nParsing investigation questions...")
    sections = parse_investigation_questions(args.gd_num, args.base_dir)
    
    if not sections:
        print("⚠️  No sections found in investigation questions file")
        print("   Please check the formatting of section headers")
        print("   Expected format: ## Section N: Title")
    else:
        print(f"✓ Found {len(sections)} sections to analyze")
    
    # Create all components
    print(f"\nCreating infrastructure files...")
    
    tracker = create_tracker_csv(output_dir, sections)
    manager = copy_section_manager(output_dir)
    assembly = create_assembly_script(output_dir, args.gd_num)
    analysis = create_analysis_prompt(output_dir, args.gd_num)
    review = create_review_prompt(output_dir, args.gd_num)
    
    # Check if all files were created successfully
    if all([tracker, manager, assembly, analysis, review]):
        print(f"\n{'='*60}")
        print(f"✅ Infrastructure Created Successfully")
        print(f"{'='*60}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Navigate to: cd {output_dir}")
        print(f"2. Open multiple terminal windows (5-8 recommended)")
        print(f"3. In each terminal, provide Claude Code with:")
        print(f"   {output_dir}/ANALYSIS_PROMPT_GD{args.gd_num}.md")
        print(f"4. Monitor progress: python section_manager.py status")
        print(f"5. After completion, run review with:")
        print(f"   {output_dir}/REVIEW_PROMPT_GD{args.gd_num}.md")
        print(f"6. Assemble final report: python assemble_report.py")
    else:
        print(f"\n❌ Some files failed to create. Please check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()