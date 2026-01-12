#!/usr/bin/env python3
"""
Data Summarizer - Creates a compact summary of final_result.json for faster loading.
Reduces 14MB+ file to ~100KB summary with pre-computed statistics.
"""

import json
from pathlib import Path
from collections import defaultdict

def summarize_data(input_file: Path, output_file: Path):
    """
    Create a compact summary from the full labeled data.
    
    Summary structure:
    {
        "HW1": {
            "reviewers": {
                "D1051683": {
                    "assignments": 5,
                    "validFeedbacks": 48,
                    "relevance": 30,
                    "concreteness": 25,
                    "constructive": 20,
                    "authors": ["D1051234", "D1051567", ...]
                },
                ...
            },
            "edges": [
                {"from": "D1051683", "to": "D1051234", "rounds": 48, "completedAll": true},
                ...
            ],
            "stats": {
                "totalAssignments": 100,
                "totalFeedbacks": 5000,
                ...
            }
        },
        ...
    }
    """
    print(f"📖 Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    summary = {}
    
    for hw_name, assignments in data.items():
        print(f"  Processing {hw_name}...")
        
        reviewers = defaultdict(lambda: {
            "assignments": 0,
            "validFeedbacks": 0,
            "relevance": 0,
            "concreteness": 0,
            "constructive": 0,
            "authors": set(),
            "feedbackTexts": []  # Store sample feedbacks for display
        })
        
        edges = []  # Store actual edges from the data
        
        hw_stats = {
            "totalAssignments": len(assignments),
            "totalFeedbacks": 0,
            "totalRelevance": 0,
            "totalConcreteness": 0,
            "totalConstructive": 0
        }
        
        for assignment in assignments:
            reviewer = assignment.get("Reviewer_Name", "Unknown")
            author = assignment.get("Author_Name", "NULL")
            rounds = assignment.get("Round", [])
            
            reviewers[reviewer]["assignments"] += 1
            
            # Track valid authors for edges
            if author and author != "NULL" and author.strip():
                reviewers[reviewer]["authors"].add(author)
                # Create edge record
                edges.append({
                    "from": reviewer,
                    "to": author,
                    "rounds": len(rounds),
                    "completedAll": len(rounds) >= 3
                })
            
            for round_data in rounds:
                feedback = round_data.get("Feedback", "")
                if feedback and feedback.strip():
                    reviewers[reviewer]["validFeedbacks"] += 1
                    hw_stats["totalFeedbacks"] += 1
                    
                    # Collect label counts
                    if round_data.get("Relevance", 0) == 1:
                        reviewers[reviewer]["relevance"] += 1
                        hw_stats["totalRelevance"] += 1
                    if round_data.get("Concreteness", 0) == 1:
                        reviewers[reviewer]["concreteness"] += 1
                        hw_stats["totalConcreteness"] += 1
                    if round_data.get("Constructive", 0) == 1:
                        reviewers[reviewer]["constructive"] += 1
                        hw_stats["totalConstructive"] += 1
                    
                    # Store sample feedbacks (max 3 per reviewer per HW)
                    if len(reviewers[reviewer]["feedbackTexts"]) < 3:
                        reviewers[reviewer]["feedbackTexts"].append({
                            "feedback": feedback[:200],  # Truncate long feedbacks
                            "author": author,
                            "relevance": round_data.get("Relevance", 0),
                            "concreteness": round_data.get("Concreteness", 0),
                            "constructive": round_data.get("Constructive", 0)
                        })
        
        # Convert sets to lists for JSON serialization
        summary_reviewers = {}
        for reviewer_id, reviewer_data in reviewers.items():
            summary_reviewers[reviewer_id] = {
                "assignments": reviewer_data["assignments"],
                "validFeedbacks": reviewer_data["validFeedbacks"],
                "relevance": reviewer_data["relevance"],
                "concreteness": reviewer_data["concreteness"],
                "constructive": reviewer_data["constructive"],
                "authors": list(reviewer_data["authors"]),
                "sampleFeedbacks": reviewer_data["feedbackTexts"]
            }
        
        summary[hw_name] = {
            "reviewers": summary_reviewers,
            "edges": edges,  # Include actual edges
            "stats": hw_stats
        }
    
    # Write summary
    print(f"💾 Writing summary to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Report size reduction
    input_size = input_file.stat().st_size / 1024 / 1024
    output_size = output_file.stat().st_size / 1024
    
    print(f"\n✅ Summary created!")
    print(f"   Original: {input_size:.2f} MB")
    print(f"   Summary:  {output_size:.2f} KB")
    print(f"   Reduction: {(1 - output_size/1024/input_size)*100:.1f}%")
    
    # Report edge statistics
    total_edges = sum(len(hw.get("edges", [])) for hw in summary.values())
    print(f"   Total edges preserved: {total_edges}")
    
    return summary

def main():
    pipeline_dir = Path(__file__).parent
    input_file = pipeline_dir / "output" / "final_result.json"
    output_file = pipeline_dir / "output" / "data_summary.json"
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    summarize_data(input_file, output_file)

if __name__ == "__main__":
    main()
