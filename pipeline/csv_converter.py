#!/usr/bin/env python3
"""
CSV to JSON Converter for Review Data Pipeline
Converts CSV format to JSON format for further processing.

Expected CSV format (based on 1131test_64.csv):
Author_ID,Reviewer_ID,Author_Name,Reviewer_Name,Feedback,Label,Time,Assignment,Metrics,Category,Round
"""

import csv
import json
import os
from typing import Dict, List


def create_id_mapping(names: List[str]) -> Dict[str, int]:
    """Create a mapping from unique names to sequential IDs."""
    valid_names = [name for name in names if name and name.strip() and name.upper() != 'NULL']
    unique_names = sorted(set(valid_names))
    return {name: idx + 1 for idx, name in enumerate(unique_names)}


def calculate_score(feedback: str) -> int:
    """Calculate score based on feedback content length."""
    if not feedback or feedback.strip() == '' or feedback.upper() == 'NULL':
        return 0
    if len(feedback.strip()) > 5:
        return 2
    return 1


def calculate_label(feedback: str) -> int:
    """Calculate label based on feedback meaningfulness."""
    if not feedback or feedback.strip() == '' or feedback.upper() == 'NULL':
        return 0
    simple_responses = ['是', '否', '有', '無', '可', '好', '0', '1', '?', 'yes', 'no', 'YES', 'NO']
    if feedback.strip() in simple_responses:
        return 0
    if len(feedback.strip()) > 3:
        return 1
    return 0


def detect_column_names(reader_fieldnames: List[str]) -> dict:
    """
    Detect the correct column names from CSV header.
    Returns a mapping of standard names to actual column names.
    """
    fieldnames = [f.strip() if f else '' for f in reader_fieldnames]
    fieldnames_lower = [f.lower() for f in fieldnames]
    
    mapping = {
        'author_id': None,
        'reviewer_id': None,
        'author_name': None,
        'reviewer_name': None,
        'feedback': None,
        'label': None,
        'time': None,
        'assignment': None,
        'metrics': None,
        'category': None,
        'round': None
    }
    
    # Map variations to standard names
    variations = {
        'author_id': ['author_id', 'authorid', 'owner_id', 'ownerid'],
        'reviewer_id': ['reviewer_id', 'reviewerid'],
        'author_name': ['author_name', 'authorname', 'owner_name', 'ownername', 'author'],
        'reviewer_name': ['reviewer_name', 'reviewername', 'reviewer'],
        'feedback': ['feedback', 'comment', 'review', 'text'],
        'label': ['label', 'rating', 'score'],
        'time': ['time', 'timestamp', 'date', 'datetime', 'created_at'],
        'assignment': ['assignment', 'hw', 'homework', 'task'],
        'metrics': ['metrics', 'metric'],
        'category': ['category', 'pmetric', 'cat'],
        'round': ['round', 'iteration', 'attempt']
    }
    
    for standard, variants in variations.items():
        for variant in variants:
            if variant in fieldnames_lower:
                idx = fieldnames_lower.index(variant)
                mapping[standard] = fieldnames[idx]
                break
    
    return mapping


def convert_csv_to_json(csv_path: str, json_path: str) -> dict:
    """
    Convert CSV file to JSON format.
    
    Expected CSV columns (flexible naming):
    - Author_Name / Owner_name: The student being reviewed
    - Reviewer_Name / Reviewer_name: The student doing the review
    - Feedback: Review text
    - Assignment: HW1, HW2, etc.
    - Round: Review round number
    
    Returns:
        dict with conversion statistics
    """
    records = []
    all_authors = []
    all_reviewers = []
    
    print(f"Reading CSV file: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        print(f"CSV columns found: {fieldnames}")
        
        # Detect column mappings
        col_map = detect_column_names(fieldnames)
        print(f"Column mapping: {col_map}")
        
        rows = list(reader)
    
    print(f"Found {len(rows)} rows in CSV")
    
    # Get column names
    author_col = col_map['author_name']
    reviewer_col = col_map['reviewer_name']
    feedback_col = col_map['feedback']
    assignment_col = col_map['assignment']
    round_col = col_map['round']
    time_col = col_map['time']
    metrics_col = col_map['metrics']
    category_col = col_map['category']
    label_col = col_map['label']
    
    if not author_col or not reviewer_col:
        print(f"WARNING: Could not find author/reviewer columns!")
        print(f"  Looking for Author_Name or Owner_name")
        print(f"  Looking for Reviewer_Name or Reviewer_name")
    
    # Collect unique names
    for row in rows:
        author = row.get(author_col, '') if author_col else ''
        reviewer = row.get(reviewer_col, '') if reviewer_col else ''
        
        if author and author.strip() and author.upper() != 'NULL':
            all_authors.append(author.strip())
        if reviewer and reviewer.strip() and reviewer.upper() != 'NULL':
            all_reviewers.append(reviewer.strip())
    
    # Create ID mappings
    author_id_map = create_id_mapping(all_authors)
    reviewer_id_map = create_id_mapping(all_reviewers)
    
    print(f"Found {len(author_id_map)} unique authors, {len(reviewer_id_map)} unique reviewers")
    
    # Convert rows to records
    for row in rows:
        author_name = (row.get(author_col, '') if author_col else '') or ''
        reviewer_name = (row.get(reviewer_col, '') if reviewer_col else '') or ''
        
        # Skip rows with invalid reviewer (reviewer is required)
        if not reviewer_name.strip() or reviewer_name.upper() == 'NULL':
            continue
        
        # Handle NULL author (keep as NULL, visualization will handle it)
        if not author_name.strip() or author_name.upper() == 'NULL':
            author_name = 'NULL'
        
        feedback = (row.get(feedback_col, '') if feedback_col else '') or ''
        if feedback.upper() == 'NULL':
            feedback = ''
        
        # Parse numeric fields
        try:
            metrics = int(row.get(metrics_col, '') or '0') if metrics_col else 0
        except (ValueError, TypeError):
            metrics = 0
        
        try:
            category = int(row.get(category_col, '') or '0') if category_col else 0
        except (ValueError, TypeError):
            category = 0
        
        try:
            round_num = int(row.get(round_col, '') or '1') if round_col else 1
        except (ValueError, TypeError):
            round_num = 1
        
        # Use existing label if present, otherwise calculate
        try:
            label = int(row.get(label_col, '') or '') if label_col else None
            if label is None or (isinstance(label, str) and label.upper() == 'NULL'):
                label = calculate_label(feedback)
        except (ValueError, TypeError):
            label = calculate_label(feedback)
        
        record = {
            "Author_ID": author_id_map.get(author_name, 0),
            "Reviewer_ID": reviewer_id_map.get(reviewer_name, 0),
            "Author_Name": author_name,
            "Reviewer_Name": reviewer_name,
            "Feedback": feedback,
            "Score": calculate_score(feedback),
            "Label": label,
            "Time": (row.get(time_col, '') if time_col else '') or '',
            "Assignment": (row.get(assignment_col, '') if assignment_col else '') or '',
            "Metrics": metrics,
            "Category": category,
            "Round": round_num
        }
        records.append(record)
    
    # Write JSON output
    print(f"Writing JSON file: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(records, json_file, ensure_ascii=False, indent=2)
    
    stats = {
        "total_rows": len(rows),
        "converted_records": len(records),
        "unique_authors": len(author_id_map),
        "unique_reviewers": len(reviewer_id_map)
    }
    
    print(f"Successfully converted {len(records)} records")
    return stats


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        convert_csv_to_json(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python csv_converter.py <input.csv> <output.json>")
