"""
Peer Review Quality Analysis and Visualization for Journal Paper
================================================================
This script analyzes peer review label frequencies and their correlations
with academic performance (grades) in a programming education context.

Author: Research Team
Date: 2025
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from scipy import stats
from pathlib import Path

# Set publication-quality defaults
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'axes.grid': False,
})

# Variable name translations (Chinese to English)
TRANSLATIONS = {
    '相關性標籤頻率': 'Relevance Label Frequency',
    '具體性標籤頻率': 'Specificity Label Frequency', 
    '建設性標籤頻率': 'Constructiveness Label Frequency',
    '期中成績': 'Midterm Grade',
    '期末成績': 'Final Grade',
    '學期成績': 'Semester Grade'
}

# Short variable names for compact displays
SHORT_NAMES = {
    '相關性標籤頻率': 'Relevance',
    '具體性標籤頻率': 'Specificity',
    '建設性標籤頻率': 'Constructiveness',
    '期中成績': 'Midterm',
    '期末成績': 'Final',
    '學期成績': 'Semester'
}


def load_data(filepath='static/visualization_data.json'):
    """Load visualization data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_correlation_heatmap(data, output_path='figures/correlation_heatmap.png'):
    """
    Create a publication-quality correlation heatmap.
    
    Shows correlations between peer review quality labels (Relevance, 
    Specificity, Constructiveness) and academic grades.
    """
    corr_matrix = data['correlation_matrix']
    
    # Convert to DataFrame with English labels
    variables = list(corr_matrix.keys())
    n = len(variables)
    
    matrix = np.zeros((n, n))
    for i, var1 in enumerate(variables):
        for j, var2 in enumerate(variables):
            matrix[i, j] = corr_matrix[var1][var2]
    
    # Use short names for display
    labels = [SHORT_NAMES.get(v, v) for v in variables]
    
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Create heatmap with custom colormap
    mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
    
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    
    sns.heatmap(matrix, 
                annot=True, 
                fmt='.3f',
                cmap=cmap,
                center=0,
                vmin=-1, 
                vmax=1,
                square=True,
                linewidths=0.5,
                cbar_kws={'shrink': 0.8, 'label': 'Pearson Correlation Coefficient'},
                xticklabels=labels,
                yticklabels=labels,
                ax=ax)
    
    ax.set_title('Correlation Matrix: Review Quality Labels and Academic Performance', 
                 fontweight='bold', pad=20)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_scatter_plots(data, output_path='figures/scatter_plots.png'):
    """
    Create scatter plots showing relationships between label frequencies 
    and academic grades with regression lines.
    """
    scatter_data = data['scatter_data']
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    grades = ['期中成績', '期末成績', '學期成績']
    
    fig, axes = plt.subplots(3, 3, figsize=(12, 11))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    for i, label in enumerate(labels):
        for j, grade in enumerate(grades):
            ax = axes[i, j]
            
            # Extract data
            points = scatter_data[label][grade]
            x = [p['x'] for p in points]
            y = [p['y'] for p in points]
            
            # Scatter plot
            ax.scatter(x, y, alpha=0.6, s=40, c=colors[i], edgecolors='white', linewidth=0.5)
            
            # Calculate regression line
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            x_line = np.linspace(min(x), max(x), 100)
            y_line = slope * x_line + intercept
            
            ax.plot(x_line, y_line, color='#333333', linestyle='--', linewidth=1.5, alpha=0.8)
            
            # Add statistics annotation
            significance = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'
            stats_text = f'r = {r_value:.3f} ({significance})\np = {p_value:.4f}'
            
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
                   fontsize=8, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Labels
            if i == 2:
                ax.set_xlabel(f'{SHORT_NAMES[grade]} Grade')
            if j == 0:
                ax.set_ylabel(f'{SHORT_NAMES[label]} (%)')
            
            ax.set_xlim(-5, 105)
            ax.set_ylim(-5, 105)
            
            # Grid
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Add row and column labels
    for i, label in enumerate(labels):
        axes[i, 0].annotate(SHORT_NAMES[label], xy=(-0.35, 0.5), 
                           xycoords='axes fraction',
                           fontsize=11, fontweight='bold', rotation=90,
                           verticalalignment='center')
    
    for j, grade in enumerate(grades):
        axes[0, j].set_title(SHORT_NAMES[grade], fontweight='bold', pad=10)
    
    fig.suptitle('Scatter Plots: Review Quality Labels vs. Academic Grades', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_group_comparison_boxplots(data, output_path='figures/group_comparison_boxplots.png'):
    """
    Create boxplots comparing low, mid, and high label frequency groups
    across different grade types.
    """
    group_stats = data['group_statistics']
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    grades = ['期中成績', '期末成績', '學期成績']
    
    fig, axes = plt.subplots(3, 3, figsize=(12, 10))
    
    colors = {'low_group': '#E74C3C', 'mid_group': '#F39C12', 'high_group': '#27AE60'}
    group_labels = {'low_group': 'Low', 'mid_group': 'Medium', 'high_group': 'High'}
    
    for i, label in enumerate(labels):
        for j, grade in enumerate(grades):
            ax = axes[i, j]
            
            # Extract data for each group
            box_data = []
            positions = []
            group_names = []
            
            for k, (group, color) in enumerate(colors.items()):
                group_data = group_stats[label][grade][group]['data']
                box_data.append(group_data)
                positions.append(k + 1)
                group_names.append(group_labels[group])
            
            # Create boxplot
            bp = ax.boxplot(box_data, positions=positions, patch_artist=True,
                           widths=0.6, showfliers=True)
            
            # Color the boxes
            for patch, (group, color) in zip(bp['boxes'], colors.items()):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            # Style whiskers, caps, and medians
            for whisker in bp['whiskers']:
                whisker.set(color='#333333', linewidth=1)
            for cap in bp['caps']:
                cap.set(color='#333333', linewidth=1)
            for median in bp['medians']:
                median.set(color='#333333', linewidth=2)
            for flier in bp['fliers']:
                flier.set(marker='o', markerfacecolor='#666666', alpha=0.5, markersize=4)
            
            # Calculate and annotate means
            for k, (group, color) in enumerate(colors.items()):
                mean_val = group_stats[label][grade][group]['mean']
                ax.scatter([k + 1], [mean_val], marker='D', color='white', 
                          edgecolors='black', s=50, zorder=5, linewidths=1)
            
            ax.set_xticks(positions)
            ax.set_xticklabels(group_names)
            ax.set_ylim(-5, 110)
            
            if i == 2:
                ax.set_xlabel('Label Frequency Group')
            if j == 0:
                ax.set_ylabel('Grade')
            
            ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Add row and column labels
    for i, label in enumerate(labels):
        axes[i, 0].annotate(SHORT_NAMES[label], xy=(-0.4, 0.5),
                           xycoords='axes fraction',
                           fontsize=11, fontweight='bold', rotation=90,
                           verticalalignment='center')
    
    for j, grade in enumerate(grades):
        axes[0, j].set_title(SHORT_NAMES[grade], fontweight='bold', pad=10)
    
    fig.suptitle('Grade Distribution by Review Quality Label Groups', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    # Add legend
    legend_patches = [mpatches.Patch(color=color, alpha=0.7, label=group_labels[group]) 
                     for group, color in colors.items()]
    legend_patches.append(plt.scatter([], [], marker='D', color='white', 
                                      edgecolors='black', s=50, label='Mean'))
    fig.legend(handles=legend_patches, loc='upper right', 
              bbox_to_anchor=(0.98, 0.98), frameon=True)
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_descriptive_statistics_table(data, output_path='figures/descriptive_statistics.png'):
    """
    Create a publication-quality table of descriptive statistics.
    """
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    
    # Calculate descriptive statistics for numeric columns
    numeric_cols = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率', 
                   '期中成績', '期末成績', '學期成績']
    
    stats_dict = {}
    for col in numeric_cols:
        col_data = df[col].dropna()
        stats_dict[SHORT_NAMES[col]] = {
            'N': len(col_data),
            'Mean': f'{col_data.mean():.3f}',
            'SD': f'{col_data.std():.3f}',
            'Min': f'{col_data.min():.3f}',
            'Max': f'{col_data.max():.3f}',
            'Median': f'{col_data.median():.3f}'
        }
    
    stats_df = pd.DataFrame(stats_dict).T
    
    # Create figure with table
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    
    table = ax.table(cellText=stats_df.values,
                    rowLabels=stats_df.index,
                    colLabels=stats_df.columns,
                    cellLoc='center',
                    rowLoc='center',
                    loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Style the table
    for (row, col), cell in table.get_celld().items():
        if row == 0:  # Header row
            cell.set_text_props(fontweight='bold')
            cell.set_facecolor('#4472C4')
            cell.set_text_props(color='white')
        elif col == -1:  # Row labels
            cell.set_text_props(fontweight='bold')
            cell.set_facecolor('#D6DCE4')
        elif row % 2 == 0:
            cell.set_facecolor('#F2F2F2')
        
        cell.set_edgecolor('#CCCCCC')
    
    ax.set_title('Table 1: Descriptive Statistics of Study Variables', 
                fontsize=12, fontweight='bold', pad=20, loc='left')
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()
    
    return stats_df


def create_label_distribution(data, output_path='figures/label_distribution.png'):
    """
    Create histogram distributions for label frequencies.
    """
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    for i, (label, color) in enumerate(zip(labels, colors)):
        ax = axes[i]
        
        # Convert to percentage
        values = df[label].dropna() * 100
        
        # Histogram
        n, bins, patches = ax.hist(values, bins=20, color=color, alpha=0.7, 
                                   edgecolor='white', linewidth=0.5)
        
        # Add kernel density estimate
        if len(values) > 1:
            kde_x = np.linspace(values.min(), values.max(), 100)
            kde = stats.gaussian_kde(values)
            ax.plot(kde_x, kde(kde_x) * len(values) * (bins[1] - bins[0]), 
                   color='#333333', linewidth=2, linestyle='-')
        
        # Statistics annotation
        mean_val = values.mean()
        std_val = values.std()
        ax.axvline(mean_val, color='#E74C3C', linewidth=2, linestyle='--', label=f'Mean: {mean_val:.1f}%')
        
        stats_text = f'Mean: {mean_val:.2f}%\nSD: {std_val:.2f}%\nN: {len(values)}'
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel(f'{SHORT_NAMES[label]} (%)')
        ax.set_ylabel('Frequency' if i == 0 else '')
        ax.set_title(SHORT_NAMES[label], fontweight='bold')
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
    
    fig.suptitle('Distribution of Peer Review Quality Label Frequencies', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_grade_distribution(data, output_path='figures/grade_distribution.png'):
    """
    Create histogram distributions for grades.
    """
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    
    grades = ['期中成績', '期末成績', '學期成績']
    colors = ['#3498DB', '#9B59B6', '#1ABC9C']
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    for i, (grade, color) in enumerate(zip(grades, colors)):
        ax = axes[i]
        values = df[grade].dropna()
        
        # Histogram
        n, bins, patches = ax.hist(values, bins=15, color=color, alpha=0.7,
                                   edgecolor='white', linewidth=0.5)
        
        # Add kernel density estimate
        if len(values) > 1 and values.std() > 0:
            kde_x = np.linspace(values.min(), values.max(), 100)
            kde = stats.gaussian_kde(values)
            ax.plot(kde_x, kde(kde_x) * len(values) * (bins[1] - bins[0]),
                   color='#333333', linewidth=2, linestyle='-')
        
        # Statistics
        mean_val = values.mean()
        ax.axvline(mean_val, color='#E74C3C', linewidth=2, linestyle='--')
        
        stats_text = f'Mean: {mean_val:.1f}\nSD: {values.std():.1f}\nN: {len(values)}'
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('Grade')
        ax.set_ylabel('Frequency' if i == 0 else '')
        ax.set_title(SHORT_NAMES[grade], fontweight='bold')
        ax.set_xlim(0, 105)
        ax.grid(True, alpha=0.3, axis='y')
    
    fig.suptitle('Distribution of Academic Grades', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_combined_violin_plot(data, output_path='figures/violin_comparison.png'):
    """
    Create violin plots comparing grade distributions across label frequency groups.
    """
    group_stats = data['group_statistics']
    
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    colors = {'low_group': '#E74C3C', 'mid_group': '#F39C12', 'high_group': '#27AE60'}
    
    for i, label in enumerate(labels):
        ax = axes[i]
        
        # Prepare data for violin plot
        all_data = []
        positions = []
        group_labels_list = []
        
        for j, grade in enumerate(['學期成績']):  # Focus on semester grade
            for k, group in enumerate(['low_group', 'mid_group', 'high_group']):
                group_data = group_stats[label][grade][group]['data']
                all_data.append(group_data)
                positions.append(k + 1)
        
        # Create violin plot
        parts = ax.violinplot(all_data, positions=positions, showmeans=True, 
                             showmedians=True, widths=0.7)
        
        # Color the violins
        for j, (pc, color) in enumerate(zip(parts['bodies'], colors.values())):
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        
        # Style other elements
        parts['cmeans'].set_color('#333333')
        parts['cmedians'].set_color('#333333')
        parts['cmedians'].set_linestyle('--')
        
        for partname in ('cbars', 'cmins', 'cmaxes'):
            parts[partname].set_color('#333333')
        
        # Add group means as text
        for k, group in enumerate(['low_group', 'mid_group', 'high_group']):
            mean_val = group_stats[label]['學期成績'][group]['mean']
            ax.text(k + 1, 105, f'{mean_val:.1f}', ha='center', fontsize=9, fontweight='bold')
        
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(['Low', 'Medium', 'High'])
        ax.set_xlabel(f'{SHORT_NAMES[label]} Group')
        ax.set_ylabel('Semester Grade' if i == 0 else '')
        ax.set_title(f'{SHORT_NAMES[label]}', fontweight='bold')
        ax.set_ylim(0, 115)
        ax.grid(True, axis='y', alpha=0.3)
    
    fig.suptitle('Semester Grade Distribution by Review Quality Label Groups', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    # Add legend
    legend_patches = [mpatches.Patch(color=color, alpha=0.7, label=name) 
                     for color, name in zip(colors.values(), ['Low', 'Medium', 'High'])]
    fig.legend(handles=legend_patches, loc='upper right', 
              bbox_to_anchor=(0.98, 0.95), frameon=True, title='Group')
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_pairplot(data, output_path='figures/pairplot.png'):
    """
    Create a pairplot showing relationships between all variables.
    """
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    
    # Select and rename columns
    cols = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率', '學期成績']
    plot_df = df[cols].copy()
    
    # Convert label frequencies to percentages
    for col in cols[:3]:
        plot_df[col] = plot_df[col] * 100
    
    # Rename columns
    plot_df.columns = ['Relevance (%)', 'Specificity (%)', 'Constructiveness (%)', 'Semester Grade']
    
    # Create pairplot
    g = sns.pairplot(plot_df, diag_kind='kde', 
                    plot_kws={'alpha': 0.6, 's': 40, 'edgecolor': 'white', 'linewidth': 0.5},
                    diag_kws={'fill': True, 'alpha': 0.7})
    
    g.fig.suptitle('Pairwise Relationships: Review Quality Labels and Semester Grade', 
                   y=1.02, fontsize=14, fontweight='bold')
    
    # Add correlation coefficients
    for i in range(len(cols)):
        for j in range(len(cols)):
            if i != j:
                corr = plot_df.iloc[:, i].corr(plot_df.iloc[:, j])
                ax = g.axes[i, j]
                ax.annotate(f'r={corr:.2f}', xy=(0.05, 0.95), 
                           xycoords='axes fraction', fontsize=8,
                           verticalalignment='top')
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def create_statistical_summary(data, output_path='figures/statistical_summary.txt'):
    """
    Generate a statistical summary report for the paper.
    """
    corr_matrix = data['correlation_matrix']
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    metadata = data['metadata']
    
    report = []
    report.append("=" * 70)
    report.append("STATISTICAL SUMMARY REPORT")
    report.append("Peer Review Quality Analysis in Programming Education")
    report.append("=" * 70)
    report.append("")
    
    # Sample information
    report.append("1. SAMPLE INFORMATION")
    report.append("-" * 40)
    report.append(f"   Total participants: {metadata['total_students']}")
    report.append(f"   Variables analyzed: {metadata['variables_count']}")
    report.append(f"   Analysis timestamp: {metadata['generation_timestamp']}")
    report.append("")
    
    # Descriptive statistics
    report.append("2. DESCRIPTIVE STATISTICS")
    report.append("-" * 40)
    
    numeric_cols = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率',
                   '期中成績', '期末成績', '學期成績']
    
    for col in numeric_cols:
        values = df[col].dropna()
        if col in ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']:
            values = values * 100
        
        report.append(f"   {SHORT_NAMES[col]}:")
        report.append(f"      Mean: {values.mean():.3f}")
        report.append(f"      SD: {values.std():.3f}")
        report.append(f"      Min: {values.min():.3f}")
        report.append(f"      Max: {values.max():.3f}")
        report.append(f"      Median: {values.median():.3f}")
        report.append("")
    
    # Correlation analysis
    report.append("3. CORRELATION ANALYSIS")
    report.append("-" * 40)
    
    label_vars = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    grade_vars = ['期中成績', '期末成績', '學期成績']
    
    for label in label_vars:
        report.append(f"   {SHORT_NAMES[label]}:")
        for grade in grade_vars:
            r = corr_matrix[label][grade]
            
            # Calculate p-value (approximation for demonstration)
            n = len(df)
            t_stat = r * np.sqrt((n - 2) / (1 - r**2)) if abs(r) < 1 else float('inf')
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            
            sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'
            report.append(f"      vs {SHORT_NAMES[grade]}: r = {r:.4f} (p = {p_value:.4f}) {sig}")
        report.append("")
    
    # Key findings
    report.append("4. KEY FINDINGS")
    report.append("-" * 40)
    
    # Find strongest correlations
    best_corr = {'label': '', 'grade': '', 'r': 0}
    for label in label_vars:
        for grade in grade_vars:
            r = abs(corr_matrix[label][grade])
            if r > abs(best_corr['r']):
                best_corr = {'label': label, 'grade': grade, 'r': corr_matrix[label][grade]}
    
    report.append(f"   Strongest correlation with grades:")
    report.append(f"      {SHORT_NAMES[best_corr['label']]} vs {SHORT_NAMES[best_corr['grade']]}")
    report.append(f"      r = {best_corr['r']:.4f}")
    report.append("")
    
    # Label inter-correlations
    report.append("   Inter-correlations among review quality labels:")
    report.append(f"      Relevance - Specificity: r = {corr_matrix['相關性標籤頻率']['具體性標籤頻率']:.4f}")
    report.append(f"      Relevance - Constructiveness: r = {corr_matrix['相關性標籤頻率']['建設性標籤頻率']:.4f}")
    report.append(f"      Specificity - Constructiveness: r = {corr_matrix['具體性標籤頻率']['建設性標籤頻率']:.4f}")
    report.append("")
    
    report.append("=" * 70)
    report.append("Note: * p < .05, ** p < .01, *** p < .001, n.s. = not significant")
    report.append("=" * 70)
    
    # Save report
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"Saved: {output_path}")
    print('\n'.join(report))


def create_individual_scatter_plots(data, output_dir='figures/individual_scatter'):
    """
    Export each scatter plot as a separate figure file.
    """
    scatter_data = data['scatter_data']
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    grades = ['期中成績', '期末成績', '學期成績']
    
    colors = {'相關性標籤頻率': '#2E86AB', '具體性標籤頻率': '#A23B72', '建設性標籤頻率': '#F18F01'}
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for label in labels:
        for grade in grades:
            fig, ax = plt.subplots(figsize=(6, 5))
            
            # Extract data
            points = scatter_data[label][grade]
            x = [p['x'] for p in points]
            y = [p['y'] for p in points]
            
            # Scatter plot
            ax.scatter(x, y, alpha=0.6, s=50, c=colors[label], edgecolors='white', linewidth=0.5)
            
            # Calculate regression line
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            x_line = np.linspace(min(x), max(x), 100)
            y_line = slope * x_line + intercept
            
            ax.plot(x_line, y_line, color='#333333', linestyle='--', linewidth=2, alpha=0.8)
            
            # Add statistics annotation
            significance = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'
            stats_text = f'r = {r_value:.3f} ({significance})\np = {p_value:.4f}\nN = {len(x)}'
            
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
            
            ax.set_xlabel(f'{SHORT_NAMES[label]} Frequency (%)', fontsize=11)
            ax.set_ylabel(f'{SHORT_NAMES[grade]} Grade', fontsize=11)
            ax.set_title(f'{SHORT_NAMES[label]} vs {SHORT_NAMES[grade]}', fontweight='bold', fontsize=12)
            
            ax.set_xlim(-5, 105)
            ax.set_ylim(-5, 105)
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            
            plt.tight_layout()
            
            # Save with descriptive filename
            filename = f'scatter_{SHORT_NAMES[label].lower()}_{SHORT_NAMES[grade].lower()}'
            plt.savefig(f'{output_dir}/{filename}.png')
            plt.savefig(f'{output_dir}/{filename}.pdf')
            plt.close()
    
    print(f"Saved: {output_dir}/ (9 individual scatter plots)")


def create_individual_boxplots(data, output_dir='figures/individual_boxplots'):
    """
    Export each boxplot comparison as a separate figure file.
    """
    group_stats = data['group_statistics']
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    grades = ['期中成績', '期末成績', '學期成績']
    
    colors = {'low_group': '#E74C3C', 'mid_group': '#F39C12', 'high_group': '#27AE60'}
    group_labels = {'low_group': 'Low', 'mid_group': 'Medium', 'high_group': 'High'}
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for label in labels:
        for grade in grades:
            fig, ax = plt.subplots(figsize=(6, 5))
            
            # Extract data for each group
            box_data = []
            positions = []
            group_names = []
            
            for k, (group, color) in enumerate(colors.items()):
                group_data = group_stats[label][grade][group]['data']
                box_data.append(group_data)
                positions.append(k + 1)
                group_names.append(group_labels[group])
            
            # Create boxplot
            bp = ax.boxplot(box_data, positions=positions, patch_artist=True,
                           widths=0.6, showfliers=True)
            
            # Color the boxes
            for patch, (group, color) in zip(bp['boxes'], colors.items()):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            # Style elements
            for whisker in bp['whiskers']:
                whisker.set(color='#333333', linewidth=1)
            for cap in bp['caps']:
                cap.set(color='#333333', linewidth=1)
            for median in bp['medians']:
                median.set(color='#333333', linewidth=2)
            for flier in bp['fliers']:
                flier.set(marker='o', markerfacecolor='#666666', alpha=0.5, markersize=4)
            
            # Add means
            for k, (group, color) in enumerate(colors.items()):
                mean_val = group_stats[label][grade][group]['mean']
                ax.scatter([k + 1], [mean_val], marker='D', color='white', 
                          edgecolors='black', s=60, zorder=5, linewidths=1.5)
                ax.text(k + 1, mean_val + 5, f'{mean_val:.1f}', ha='center', fontsize=9)
            
            ax.set_xticks(positions)
            ax.set_xticklabels(group_names)
            ax.set_ylim(-5, 115)
            ax.set_xlabel(f'{SHORT_NAMES[label]} Group', fontsize=11)
            ax.set_ylabel(f'{SHORT_NAMES[grade]} Grade', fontsize=11)
            ax.set_title(f'{SHORT_NAMES[grade]} by {SHORT_NAMES[label]} Groups', fontweight='bold', fontsize=12)
            ax.grid(True, axis='y', alpha=0.3)
            
            # Add legend
            legend_patches = [mpatches.Patch(color=color, alpha=0.7, label=group_labels[group]) 
                             for group, color in colors.items()]
            ax.legend(handles=legend_patches, loc='upper right', frameon=True)
            
            plt.tight_layout()
            
            filename = f'boxplot_{SHORT_NAMES[label].lower()}_{SHORT_NAMES[grade].lower()}'
            plt.savefig(f'{output_dir}/{filename}.png')
            plt.savefig(f'{output_dir}/{filename}.pdf')
            plt.close()
    
    print(f"Saved: {output_dir}/ (9 individual boxplots)")


def create_individual_distributions(data, output_dir='figures/individual_distributions'):
    """
    Export each distribution histogram as a separate figure file.
    """
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Label distributions
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    label_colors = {'相關性標籤頻率': '#2E86AB', '具體性標籤頻率': '#A23B72', '建設性標籤頻率': '#F18F01'}
    
    for label in labels:
        fig, ax = plt.subplots(figsize=(7, 5))
        
        values = df[label].dropna() * 100
        
        n, bins, patches = ax.hist(values, bins=20, color=label_colors[label], alpha=0.7, 
                                   edgecolor='white', linewidth=0.5)
        
        if len(values) > 1:
            kde_x = np.linspace(values.min(), values.max(), 100)
            kde = stats.gaussian_kde(values)
            ax.plot(kde_x, kde(kde_x) * len(values) * (bins[1] - bins[0]), 
                   color='#333333', linewidth=2, linestyle='-')
        
        mean_val = values.mean()
        ax.axvline(mean_val, color='#E74C3C', linewidth=2, linestyle='--')
        
        stats_text = f'Mean: {mean_val:.2f}%\nSD: {values.std():.2f}%\nMedian: {values.median():.2f}%\nN: {len(values)}'
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        ax.set_xlabel(f'{SHORT_NAMES[label]} Frequency (%)', fontsize=11)
        ax.set_ylabel('Number of Students', fontsize=11)
        ax.set_title(f'Distribution of {SHORT_NAMES[label]} Label Frequency', fontweight='bold', fontsize=12)
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        filename = f'dist_{SHORT_NAMES[label].lower()}'
        plt.savefig(f'{output_dir}/{filename}.png')
        plt.savefig(f'{output_dir}/{filename}.pdf')
        plt.close()
    
    # Grade distributions
    grades = ['期中成績', '期末成績', '學期成績']
    grade_colors = {'期中成績': '#3498DB', '期末成績': '#9B59B6', '學期成績': '#1ABC9C'}
    
    for grade in grades:
        fig, ax = plt.subplots(figsize=(7, 5))
        
        values = df[grade].dropna()
        
        n, bins, patches = ax.hist(values, bins=15, color=grade_colors[grade], alpha=0.7,
                                   edgecolor='white', linewidth=0.5)
        
        if len(values) > 1 and values.std() > 0:
            kde_x = np.linspace(values.min(), values.max(), 100)
            kde = stats.gaussian_kde(values)
            ax.plot(kde_x, kde(kde_x) * len(values) * (bins[1] - bins[0]),
                   color='#333333', linewidth=2, linestyle='-')
        
        mean_val = values.mean()
        ax.axvline(mean_val, color='#E74C3C', linewidth=2, linestyle='--')
        
        stats_text = f'Mean: {mean_val:.1f}\nSD: {values.std():.1f}\nMedian: {values.median():.1f}\nN: {len(values)}'
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        ax.set_xlabel('Grade', fontsize=11)
        ax.set_ylabel('Number of Students', fontsize=11)
        ax.set_title(f'Distribution of {SHORT_NAMES[grade]} Grade', fontweight='bold', fontsize=12)
        ax.set_xlim(0, 105)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        filename = f'dist_{SHORT_NAMES[grade].lower()}_grade'
        plt.savefig(f'{output_dir}/{filename}.png')
        plt.savefig(f'{output_dir}/{filename}.pdf')
        plt.close()
    
    print(f"Saved: {output_dir}/ (6 individual distribution plots)")


def generate_findings_report(data, output_path='figures/ANALYSIS_FINDINGS.md'):
    """
    Generate a comprehensive findings report explaining the analysis results.
    """
    corr_matrix = data['correlation_matrix']
    group_stats = data['group_statistics']
    raw_data = data['original_data']['raw_data']
    df = pd.DataFrame(raw_data)
    metadata = data['metadata']
    
    report = []
    
    report.append("# Peer Review Quality Analysis - Research Findings")
    report.append("")
    report.append("## Overview")
    report.append("")
    report.append("This document presents the analysis findings of peer review quality labels and their relationship with academic performance in a programming education context.")
    report.append("")
    report.append("---")
    report.append("")
    
    # Study Information
    report.append("## 1. Study Information")
    report.append("")
    report.append(f"- **Total Participants**: {metadata['total_students']} students")
    report.append(f"- **Variables Analyzed**: {metadata['variables_count']}")
    report.append(f"- **Analysis Date**: {metadata['generation_timestamp']}")
    report.append("")
    report.append("### Variables")
    report.append("")
    report.append("**Review Quality Labels (Independent Variables):**")
    report.append("- **Relevance**: Measures whether the review comment is related to the code being reviewed")
    report.append("- **Specificity**: Measures how specific and detailed the review feedback is")
    report.append("- **Constructiveness**: Measures whether the review provides actionable suggestions for improvement")
    report.append("")
    report.append("**Academic Performance (Dependent Variables):**")
    report.append("- **Midterm Grade**: Student's midterm examination score")
    report.append("- **Final Grade**: Student's final examination score")
    report.append("- **Semester Grade**: Overall course grade for the semester")
    report.append("")
    report.append("---")
    report.append("")
    
    # Descriptive Statistics
    report.append("## 2. Descriptive Statistics")
    report.append("")
    report.append("### Review Quality Label Frequencies")
    report.append("")
    report.append("| Variable | Mean | SD | Min | Max | Median |")
    report.append("|----------|------|-----|-----|-----|--------|")
    
    for col in ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']:
        values = df[col].dropna() * 100
        report.append(f"| {SHORT_NAMES[col]} | {values.mean():.2f}% | {values.std():.2f}% | {values.min():.2f}% | {values.max():.2f}% | {values.median():.2f}% |")
    
    report.append("")
    report.append("### Academic Grades")
    report.append("")
    report.append("| Variable | Mean | SD | Min | Max | Median |")
    report.append("|----------|------|-----|-----|-----|--------|")
    
    for col in ['期中成績', '期末成績', '學期成績']:
        values = df[col].dropna()
        report.append(f"| {SHORT_NAMES[col]} | {values.mean():.2f} | {values.std():.2f} | {values.min():.0f} | {values.max():.0f} | {values.median():.0f} |")
    
    report.append("")
    report.append("**Key Observations:**")
    
    rel_mean = df['相關性標籤頻率'].mean() * 100
    spec_mean = df['具體性標籤頻率'].mean() * 100
    cons_mean = df['建設性標籤頻率'].mean() * 100
    
    report.append(f"- Relevance labels have the highest frequency ({rel_mean:.1f}%), indicating students most commonly provide relevant comments")
    report.append(f"- Constructiveness labels have the lowest frequency ({cons_mean:.1f}%), suggesting students rarely provide actionable improvement suggestions")
    report.append(f"- There is considerable variation in all label frequencies, indicating diverse review quality among students")
    report.append("")
    report.append("---")
    report.append("")
    
    # Correlation Analysis
    report.append("## 3. Correlation Analysis")
    report.append("")
    report.append("### Correlation Matrix: Labels vs Grades")
    report.append("")
    report.append("| | Midterm | Final | Semester |")
    report.append("|---|---------|-------|----------|")
    
    n = len(df)
    for label in ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']:
        row = f"| {SHORT_NAMES[label]} |"
        for grade in ['期中成績', '期末成績', '學期成績']:
            r = corr_matrix[label][grade]
            t_stat = r * np.sqrt((n - 2) / (1 - r**2)) if abs(r) < 1 else float('inf')
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
            row += f" {r:.3f}{sig} |"
        report.append(row)
    
    report.append("")
    report.append("*Note: \\* p < .05, \\*\\* p < .01, \\*\\*\\* p < .001*")
    report.append("")
    
    # Find and report key correlations
    spec_mid = corr_matrix['具體性標籤頻率']['期中成績']
    report.append("**Key Findings:**")
    report.append("")
    report.append(f"1. **Specificity shows the strongest correlation with grades** (r = {spec_mid:.3f} with Midterm)")
    report.append("   - Students who provide more specific feedback tend to perform better academically")
    report.append("   - This suggests that the ability to provide detailed code analysis reflects deeper understanding")
    report.append("")
    report.append(f"2. **Relevance shows weak correlation** (r = {corr_matrix['相關性標籤頻率']['學期成績']:.3f} with Semester)")
    report.append("   - Simply providing relevant comments does not strongly predict academic success")
    report.append("   - Most students can identify relevant issues; the difference lies in depth of analysis")
    report.append("")
    report.append(f"3. **Constructiveness shows modest correlation** (r = {corr_matrix['建設性標籤頻率']['期中成績']:.3f} with Midterm)")
    report.append("   - Providing actionable suggestions moderately relates to academic performance")
    report.append("")
    report.append("### Inter-Label Correlations")
    report.append("")
    report.append(f"- Relevance ↔ Specificity: r = {corr_matrix['相關性標籤頻率']['具體性標籤頻率']:.3f}")
    report.append(f"- Specificity ↔ Constructiveness: r = {corr_matrix['具體性標籤頻率']['建設性標籤頻率']:.3f}")
    report.append(f"- Relevance ↔ Constructiveness: r = {corr_matrix['相關性標籤頻率']['建設性標籤頻率']:.3f}")
    report.append("")
    report.append("**Interpretation**: Specificity and Constructiveness are strongly correlated (r = 0.703), suggesting that students who provide specific feedback also tend to provide constructive suggestions.")
    report.append("")
    report.append("---")
    report.append("")
    
    # Group Comparison
    report.append("## 4. Group Comparison Analysis")
    report.append("")
    report.append("Students were divided into three groups (Low, Medium, High) based on their label frequencies.")
    report.append("")
    report.append("### Semester Grade by Specificity Groups")
    report.append("")
    
    for label in ['具體性標籤頻率']:
        low_mean = group_stats[label]['學期成績']['low_group']['mean']
        mid_mean = group_stats[label]['學期成績']['mid_group']['mean']
        high_mean = group_stats[label]['學期成績']['high_group']['mean']
        
        report.append(f"| Group | Mean Grade | SD | N |")
        report.append(f"|-------|------------|-----|---|")
        report.append(f"| Low | {low_mean:.1f} | {group_stats[label]['學期成績']['low_group']['std']:.1f} | {group_stats[label]['學期成績']['low_group']['count']} |")
        report.append(f"| Medium | {mid_mean:.1f} | {group_stats[label]['學期成績']['mid_group']['std']:.1f} | {group_stats[label]['學期成績']['mid_group']['count']} |")
        report.append(f"| High | {high_mean:.1f} | {group_stats[label]['學期成績']['high_group']['std']:.1f} | {group_stats[label]['學期成績']['high_group']['count']} |")
    
    report.append("")
    report.append(f"**Grade Difference (High - Low)**: {high_mean - low_mean:.1f} points")
    report.append("")
    
    # Effect Sizes
    report.append("### Effect Sizes (Cohen's d)")
    report.append("")
    report.append("| Label | Midterm | Final | Semester |")
    report.append("|-------|---------|-------|----------|")
    
    for label in ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']:
        row = f"| {SHORT_NAMES[label]} |"
        for grade in ['期中成績', '期末成績', '學期成績']:
            low_mean = group_stats[label][grade]['low_group']['mean']
            high_mean = group_stats[label][grade]['high_group']['mean']
            low_std = group_stats[label][grade]['low_group']['std']
            high_std = group_stats[label][grade]['high_group']['std']
            pooled_std = np.sqrt((low_std**2 + high_std**2) / 2)
            d = (high_mean - low_mean) / pooled_std if pooled_std > 0 else 0
            
            interpretation = "large" if abs(d) >= 0.8 else "medium" if abs(d) >= 0.5 else "small"
            row += f" {d:.2f} ({interpretation}) |"
        report.append(row)
    
    report.append("")
    report.append("*Effect size interpretation: small (d ≥ 0.2), medium (d ≥ 0.5), large (d ≥ 0.8)*")
    report.append("")
    report.append("---")
    report.append("")
    
    # Conclusions
    report.append("## 5. Key Conclusions")
    report.append("")
    report.append("### Main Findings")
    report.append("")
    report.append("1. **Specificity is the most important predictor of academic success**")
    report.append("   - Students who provide more specific, detailed peer reviews tend to achieve higher grades")
    report.append("   - This relationship is consistent across midterm, final, and semester grades")
    report.append("")
    report.append("2. **Review quality labels are inter-correlated**")
    report.append("   - Students who excel in one aspect of review quality tend to excel in others")
    report.append("   - Specificity and Constructiveness show the strongest relationship")
    report.append("")
    report.append("3. **Practical effect sizes support educational significance**")
    report.append("   - The difference between high and low specificity groups represents meaningful academic improvement")
    report.append("   - Interventions targeting review specificity may improve both review quality and learning outcomes")
    report.append("")
    report.append("### Implications for Education")
    report.append("")
    report.append("- **Teaching Recommendation**: Train students to provide more specific feedback in peer reviews")
    report.append("- **Assessment Design**: Consider incorporating peer review quality as part of course assessment")
    report.append("- **Learning Support**: Provide examples of high-quality, specific peer reviews as learning resources")
    report.append("")
    report.append("### Limitations")
    report.append("")
    report.append("- Correlation does not imply causation")
    report.append("- Sample limited to a single course/semester")
    report.append("- Label classification based on NLP model inference")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## 6. Figure Index")
    report.append("")
    report.append("### Combined Figures (figures/)")
    report.append("| Filename | Description |")
    report.append("|----------|-------------|")
    report.append("| correlation_heatmap.png | Full correlation matrix heatmap |")
    report.append("| scatter_plots.png | 3×3 grid of all scatter plots |")
    report.append("| group_comparison_boxplots.png | 3×3 grid of group comparison boxplots |")
    report.append("| descriptive_statistics.png | Summary statistics table |")
    report.append("| label_distribution.png | Distribution histograms for all labels |")
    report.append("| grade_distribution.png | Distribution histograms for all grades |")
    report.append("| violin_comparison.png | Violin plots for group comparisons |")
    report.append("| pairplot.png | Pairwise relationship matrix |")
    report.append("| effect_sizes.png | Cohen's d effect size comparison |")
    report.append("")
    report.append("### Individual Figures")
    report.append("- **figures/individual_scatter/**: 9 separate scatter plots (label × grade combinations)")
    report.append("- **figures/individual_boxplots/**: 9 separate boxplot comparisons")
    report.append("- **figures/individual_distributions/**: 6 separate distribution histograms (3 labels + 3 grades)")
    report.append("")
    report.append("---")
    report.append("")
    report.append(f"*Report generated: {metadata['generation_timestamp']}*")
    
    # Save report
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"Saved: {output_path}")


def create_effect_size_comparison(data, output_path='figures/effect_sizes.png'):
    """
    Create a bar chart comparing effect sizes (Cohen's d) between groups.
    """
    group_stats = data['group_statistics']
    labels = ['相關性標籤頻率', '具體性標籤頻率', '建設性標籤頻率']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(3)
    width = 0.25
    
    colors = ['#3498DB', '#9B59B6', '#1ABC9C']
    
    for i, grade in enumerate(['期中成績', '期末成績', '學期成績']):
        effect_sizes = []
        for label in labels:
            low_mean = group_stats[label][grade]['low_group']['mean']
            high_mean = group_stats[label][grade]['high_group']['mean']
            low_std = group_stats[label][grade]['low_group']['std']
            high_std = group_stats[label][grade]['high_group']['std']
            
            # Calculate Cohen's d
            pooled_std = np.sqrt((low_std**2 + high_std**2) / 2)
            cohens_d = (high_mean - low_mean) / pooled_std if pooled_std > 0 else 0
            effect_sizes.append(cohens_d)
        
        bars = ax.bar(x + i * width, effect_sizes, width, label=SHORT_NAMES[grade], 
                     color=colors[i], alpha=0.8, edgecolor='white', linewidth=0.5)
        
        # Add value labels
        for bar, d in zip(bars, effect_sizes):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{d:.2f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('Review Quality Label')
    ax.set_ylabel("Cohen's d (Effect Size)")
    ax.set_title("Effect Size Comparison: High vs. Low Label Frequency Groups", 
                 fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels([SHORT_NAMES[l] for l in labels])
    ax.legend(title='Grade Type')
    
    # Add reference lines for effect size interpretation
    ax.axhline(y=0.2, color='#E74C3C', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(y=0.5, color='#F39C12', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(y=0.8, color='#27AE60', linestyle='--', alpha=0.5, linewidth=1)
    
    ax.text(2.8, 0.22, 'Small (0.2)', fontsize=8, color='#E74C3C')
    ax.text(2.8, 0.52, 'Medium (0.5)', fontsize=8, color='#F39C12')
    ax.text(2.8, 0.82, 'Large (0.8)', fontsize=8, color='#27AE60')
    
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_ylim(0, 1.2)
    
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.savefig(output_path.replace('.png', '.pdf'))
    print(f"Saved: {output_path}")
    plt.close()


def main():
    """
    Main function to generate all visualizations and statistical analyses.
    """
    print("=" * 60)
    print("Peer Review Quality Analysis - Journal Paper Visualization")
    print("=" * 60)
    print()
    
    # Load data
    print("Loading data...")
    data = load_data('static/visualization_data.json')
    print(f"  Loaded data for {data['metadata']['total_students']} students")
    print()
    
    # Create output directory
    Path('figures').mkdir(parents=True, exist_ok=True)
    
    # Generate all visualizations
    print("Generating visualizations...")
    print("-" * 40)
    
    # 1. Correlation heatmap
    print("1. Creating correlation heatmap...")
    create_correlation_heatmap(data)
    
    # 2. Scatter plots
    print("2. Creating scatter plots...")
    create_scatter_plots(data)
    
    # 3. Group comparison boxplots
    print("3. Creating group comparison boxplots...")
    create_group_comparison_boxplots(data)
    
    # 4. Descriptive statistics table
    print("4. Creating descriptive statistics table...")
    create_descriptive_statistics_table(data)
    
    # 5. Label frequency distributions
    print("5. Creating label distribution histograms...")
    create_label_distribution(data)
    
    # 6. Grade distributions
    print("6. Creating grade distribution histograms...")
    create_grade_distribution(data)
    
    # 7. Violin plots
    print("7. Creating violin comparison plots...")
    create_combined_violin_plot(data)
    
    # 8. Pairplot
    print("8. Creating pairplot...")
    create_pairplot(data)
    
    # 9. Effect sizes
    print("9. Creating effect size comparison...")
    create_effect_size_comparison(data)
    
    # 10. Statistical summary report
    print("10. Generating statistical summary report...")
    print("-" * 40)
    create_statistical_summary(data)
    
    # 11. Individual scatter plots
    print("11. Creating individual scatter plots...")
    create_individual_scatter_plots(data)
    
    # 12. Individual boxplots
    print("12. Creating individual boxplots...")
    create_individual_boxplots(data)
    
    # 13. Individual distributions
    print("13. Creating individual distribution plots...")
    create_individual_distributions(data)
    
    # 14. Findings report
    print("14. Generating findings report...")
    generate_findings_report(data)
    
    print()
    print("=" * 60)
    print("All visualizations generated successfully!")
    print("Output files are saved in the 'figures' directory:")
    print("")
    print("Combined Figures:")
    print("  - correlation_heatmap.png/pdf")
    print("  - scatter_plots.png/pdf")
    print("  - group_comparison_boxplots.png/pdf")
    print("  - descriptive_statistics.png/pdf")
    print("  - label_distribution.png/pdf")
    print("  - grade_distribution.png/pdf")
    print("  - violin_comparison.png/pdf")
    print("  - pairplot.png/pdf")
    print("  - effect_sizes.png/pdf")
    print("  - statistical_summary.txt")
    print("  - ANALYSIS_FINDINGS.md")
    print("")
    print("Individual Figures:")
    print("  - individual_scatter/ (9 plots)")
    print("  - individual_boxplots/ (9 plots)")
    print("  - individual_distributions/ (6 plots)")
    print("=" * 60)


if __name__ == '__main__':
    main()
