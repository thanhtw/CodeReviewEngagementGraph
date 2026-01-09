"""
Homework Label Distribution Chart
=================================
This script generates a grouped bar chart showing the distribution of 
peer review quality labels (Relevance, Concreteness, Constructive) 
across different homework assignments (HW1-HW7).

Author: Research Team
Date: 2025
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Set publication-quality defaults
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})


def calculate_3label_percentages():
    """
    Calculate the three label percentages (Relevance, Concreteness, Constructive)
    per homework assignment from the pre-processed 3labeled data file.
    """
    # Load the pre-processed 3-label data file
    with open('function/3labeled_processed_totalData.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = {}
    
    for hw in ['HW1', 'HW2', 'HW3', 'HW4', 'HW5', 'HW6', 'HW7']:
        if hw not in data:
            results[hw] = {'relevance': 0, 'concreteness': 0, 'constructive': 0, 'total': 0}
            continue
        
        hw_data = data[hw]
        
        # Collect all feedback rounds across all review pairs
        all_feedbacks = []
        for review_pair in hw_data:
            if 'Round' in review_pair:
                for round_data in review_pair['Round']:
                    all_feedbacks.append({
                        'relevance': round_data.get('Relevance', 0),
                        'concreteness': round_data.get('Concreteness', 0),
                        'constructive': round_data.get('Constructive', 0)
                    })
        
        total = len(all_feedbacks)
        
        if total > 0:
            relevance_count = sum(1 for f in all_feedbacks if f['relevance'] == 1)
            concreteness_count = sum(1 for f in all_feedbacks if f['concreteness'] == 1)
            constructive_count = sum(1 for f in all_feedbacks if f['constructive'] == 1)
            
            results[hw] = {
                'relevance': (relevance_count / total) * 100,
                'concreteness': (concreteness_count / total) * 100,
                'constructive': (constructive_count / total) * 100,
                'total': total,
                'relevance_count': relevance_count,
                'concreteness_count': concreteness_count,
                'constructive_count': constructive_count
            }
        else:
            results[hw] = {'relevance': 0, 'concreteness': 0, 'constructive': 0, 'total': 0}
    
    return results


def create_hw_label_chart(output_path='figures/hw_label_distribution.png'):
    """
    Create a grouped bar chart showing label distribution across homework assignments.
    """
    # Calculate label percentages from 3labeled data
    hw_data = calculate_3label_percentages()
    
    # Prepare data for plotting
    homeworks = ['HW1', 'HW2', 'HW3', 'HW4', 'HW5', 'HW6', 'HW7']
    relevance = [hw_data[hw]['relevance'] for hw in homeworks]
    concreteness = [hw_data[hw]['concreteness'] for hw in homeworks]
    constructive = [hw_data[hw]['constructive'] for hw in homeworks]
    
    # Print the data
    print("\nLabel Distribution per Homework:")
    print("-" * 70)
    print(f"{'HW':<6} {'Relevance':<12} {'Concreteness':<14} {'Constructive':<14} {'Total':<8}")
    print("-" * 70)
    for hw in homeworks:
        print(f"{hw:<6} {hw_data[hw]['relevance']:<12.1f} {hw_data[hw]['concreteness']:<14.1f} {hw_data[hw]['constructive']:<14.1f} {hw_data[hw]['total']:<8}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set bar positions
    x = np.arange(len(homeworks))
    width = 0.25
    
    # Create bars with colors matching the image
    bars1 = ax.bar(x - width, relevance, width, label='Relevance', 
                   color='#FFD166', edgecolor='white', linewidth=0.5)  # Yellow/Orange
    bars2 = ax.bar(x, concreteness, width, label='Concreteness', 
                   color='#90EE90', edgecolor='white', linewidth=0.5)  # Light Green
    bars3 = ax.bar(x + width, constructive, width, label='Constructive', 
                   color='#DDA0DD', edgecolor='white', linewidth=0.5)  # Light Purple
    
    # Customize the chart
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'])
    
    ax.set_xticks(x)
    ax.set_xticklabels(homeworks)
    
    # Add legend at bottom
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add subtle grid
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # Save figure
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"\nSaved: {output_path}")
    plt.close()
    
    return hw_data


def create_hw_label_chart_detailed(output_path='figures/hw_label_distribution_detailed.png'):
    """
    Create a more detailed version with value labels on bars.
    """
    hw_data = calculate_3label_percentages()
    
    homeworks = ['HW1', 'HW2', 'HW3', 'HW4', 'HW5', 'HW6', 'HW7']
    relevance = [hw_data[hw]['relevance'] for hw in homeworks]
    concreteness = [hw_data[hw]['concreteness'] for hw in homeworks]
    constructive = [hw_data[hw]['constructive'] for hw in homeworks]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(homeworks))
    width = 0.25
    
    bars1 = ax.bar(x - width, relevance, width, label='Relevance', 
                   color='#FFD166', edgecolor='#333', linewidth=0.5)
    bars2 = ax.bar(x, concreteness, width, label='Specificity', 
                   color='#90EE90', edgecolor='#333', linewidth=0.5)
    bars3 = ax.bar(x + width, constructive, width, label='Constructiveness', 
                   color='#DDA0DD', edgecolor='#333', linewidth=0.5)
    
    # Add value labels on bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
    
    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    
    ax.set_xlabel('Homework Assignment', fontsize=12)
    ax.set_ylabel('Percentage of Reviews with Label (%)', fontsize=12)
    ax.set_title('Distribution of Peer Review Quality Labels Across Homework Assignments', 
                 fontweight='bold', fontsize=14, pad=15)
    ax.set_ylim(0, 50)
    ax.set_xticks(x)
    ax.set_xticklabels(homeworks)
    
    ax.legend(loc='upper right', frameon=True)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_individual_hw_charts(output_dir='figures/individual_hw'):
    """
    Create individual bar charts for each homework assignment.
    """
    hw_data = calculate_3label_percentages()
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for hw in ['HW1', 'HW2', 'HW3', 'HW4', 'HW5', 'HW6', 'HW7']:
        fig, ax = plt.subplots(figsize=(6, 5))
        
        labels = ['Relevance', 'Concreteness', 'Constructive']
        values = [hw_data[hw]['relevance'], hw_data[hw]['concreteness'], hw_data[hw]['constructive']]
        colors = ['#FFD166', '#90EE90', '#DDA0DD']
        
        bars = ax.bar(labels, values, color=colors, edgecolor='#333', linewidth=0.5)
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax.annotate(f'{val:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, val),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)
        
        ax.set_ylabel('Percentage (%)', fontsize=11)
        ax.set_title(f'{hw} - Label Distribution', fontweight='bold', fontsize=12)
        ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        plt.savefig(f'{output_dir}/{hw.lower()}_labels.png')
        plt.savefig(f'{output_dir}/{hw.lower()}_labels.pdf')
        plt.close()
    
    print(f"Saved: {output_dir}/ (7 individual charts)")


def main():
    """
    Main function to generate all homework label distribution charts.
    """
    print("=" * 60)
    print("Homework Label Distribution Chart Generator")
    print("=" * 60)
    print()
    
    # Create output directory
    Path('figures').mkdir(parents=True, exist_ok=True)
    
    # 1. Main grouped bar chart (matching the image style)
    print("1. Creating main label distribution chart...")
    hw_data = create_hw_label_chart()
    
    # 2. Detailed version with value labels
    print("\n2. Creating detailed chart with value labels...")
    create_hw_label_chart_detailed()
    
    # 3. Individual charts per homework
    print("\n3. Creating individual homework charts...")
    create_individual_hw_charts()
    
    print()
    print("=" * 60)
    print("All charts generated successfully!")
    print("Output files:")
    print("  - figures/hw_label_distribution.png/pdf")
    print("  - figures/hw_label_distribution_detailed.png/pdf")
    print("  - figures/individual_hw/ (7 charts)")
    print("=" * 60)


if __name__ == '__main__':
    main()
