#!/usr/bin/env python3
"""
Section manager for GD parallel analysis
Handles claiming, completing, and reviewing sections
"""
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

TRACKER_FILE = "tracker.csv"
TIMEOUT_MINUTES = 60

def claim_next_section():
    """Find and claim the next available section"""
    rows = []
    claimed_section = None
    
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for timed-out claims
            if row['status'] == 'in_progress' and row['claimed_at']:
                claimed_time = datetime.fromisoformat(row['claimed_at'])
                if datetime.now() - claimed_time > timedelta(minutes=TIMEOUT_MINUTES):
                    row['status'] = 'available'
                    row['claimed_at'] = ''
            
            # Claim first available section
            if row['status'] == 'available' and not claimed_section:
                row['status'] = 'in_progress'
                row['claimed_at'] = datetime.now().isoformat()
                claimed_section = row['section_num']
            
            rows.append(row)
    
    # Write back
    if rows:
        with open(TRACKER_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    if claimed_section:
        print(f"CLAIMED: Section {claimed_section}")
    else:
        print("NO_SECTIONS_AVAILABLE")

def complete_section(section_num):
    """Mark a section as completed"""
    rows = []
    
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['section_num'] == section_num:
                row['status'] = 'completed'
                row['completed_at'] = datetime.now().isoformat()
            rows.append(row)
    
    with open(TRACKER_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"COMPLETED: Section {section_num}")

def mark_for_review(section_num):
    """Mark a section as needing review"""
    rows = []
    
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['section_num'] == section_num:
                row['review_status'] = 'needs_review'
            rows.append(row)
    
    with open(TRACKER_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"MARKED_FOR_REVIEW: Section {section_num}")

def complete_review(section_num):
    """Mark a section review as completed"""
    rows = []
    
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['section_num'] == section_num:
                row['review_status'] = 'reviewed'
            rows.append(row)
    
    with open(TRACKER_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"REVIEW_COMPLETED: Section {section_num}")

def status():
    """Show current status of all sections"""
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total = len(rows)
    completed = sum(1 for r in rows if r['status'] == 'completed')
    in_progress = sum(1 for r in rows if r['status'] == 'in_progress')
    available = sum(1 for r in rows if r['status'] == 'available')
    reviewed = sum(1 for r in rows if r['review_status'] == 'reviewed')
    
    print(f"Total sections: {total}")
    print(f"  Completed: {completed}")
    print(f"  In progress: {in_progress}")
    print(f"  Available: {available}")
    print(f"  Reviewed: {reviewed}")
    
    if in_progress > 0:
        print("\nSections in progress:")
        for row in rows:
            if row['status'] == 'in_progress':
                print(f"  Section {row['section_num']}: {row['section_title'][:50]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python section_manager.py [claim|complete|review|complete_review|status] [section_num]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "claim":
        claim_next_section()
    elif action == "complete" and len(sys.argv) == 3:
        complete_section(sys.argv[2])
    elif action == "review" and len(sys.argv) == 3:
        mark_for_review(sys.argv[2])
    elif action == "complete_review" and len(sys.argv) == 3:
        complete_review(sys.argv[2])
    elif action == "status":
        status()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)