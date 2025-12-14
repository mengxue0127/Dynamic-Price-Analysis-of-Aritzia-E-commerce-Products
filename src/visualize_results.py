
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Optional, Dict


def setup_style() -> None:
    """Configure matplotlib style for consistent, professional visualizations."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'figure.figsize': (10, 6),
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.dpi': 100,
        'savefig.dpi': 150,
        'savefig.bbox': 'tight'
    })


def load_data(processed_dir: str = "data/processed") -> Dict[str, pd.DataFrame]:
    """
    Load all processed data files.
    
    Args:
        processed_dir: Path to processed data directory.
    
    Returns:
        Dict: Dictionary of DataFrames.
    """
    data = {}
    
    # Load main time series
    data['time_series'] = pd.read_csv(
        os.path.join(processed_dir, "price_time_series.csv"),
        parse_dates=['date']
    )
    
    # Load category analysis
    data['category'] = pd.read_csv(
        os.path.join(processed_dir, "category_analysis.csv")
    )
    
    # Load daily trends
    data['daily'] = pd.read_csv(
        os.path.join(processed_dir, "daily_price_trends.csv"),
        parse_dates=['date']
    )
    
    # Load correlation matrix
    data['correlation'] = pd.read_csv(
        os.path.join(processed_dir, "correlation_matrix.csv"),
        index_col=0
    )
    
    return data


def plot_daily_price_trajectory(
    df: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create line chart showing daily average prices and discounts over time.
    
    Args:
        df: Daily statistics DataFrame.
        output_dir: Directory to save the plot.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot 1: Prices over time
    ax1 = axes[0]
    ax1.plot(df['date'], df['avg_original_price'], 
             marker='o', linewidth=2, markersize=6,
             label='Original Price', color='#2C3E50')
    ax1.plot(df['date'], df['avg_sale_price'], 
             marker='s', linewidth=2, markersize=6,
             label='Sale Price', color='#E74C3C')
    
    ax1.fill_between(df['date'], df['avg_sale_price'], df['avg_original_price'],
                     alpha=0.3, color='#27AE60', label='Savings')
    
    ax1.set_ylabel('Average Price ($)')
    ax1.set_title('Daily Average Prices Over Time', fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Discount percentage over time
    ax2 = axes[1]
    ax2.plot(df['date'], df['avg_discount'], 
             marker='D', linewidth=2, markersize=6,
             color='#9B59B6', label='Average Discount')
    ax2.fill_between(df['date'], 0, df['avg_discount'], alpha=0.3, color='#9B59B6')
    
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Average Discount (%)')
    ax2.set_title('Daily Average Discount Percentage', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'daily_price_trajectory.png'))
    plt.close()
    print(f"Saved: daily_price_trajectory.png")


def plot_category_discounts(
    df: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create bar chart comparing average discounts by category.
    
    Args:
        df: Category analysis DataFrame.
        output_dir: Directory to save the plot.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Sort by average discount
    df_sorted = df.sort_values('avg_discount', ascending=True)
    
    # Color palette
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(df_sorted)))[::-1]
    
    # Plot 1: Average Discount by Category
    ax1 = axes[0]
    bars1 = ax1.barh(df_sorted['category'].str.title(), 
                     df_sorted['avg_discount'], 
                     color=colors, edgecolor='white', linewidth=1.5)
    ax1.set_xlabel('Average Discount (%)')
    ax1.set_title('Average Discount by Category', fontweight='bold')
    
    # Add value labels
    for bar, val in zip(bars1, df_sorted['avg_discount']):
        ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{val:.1f}%', va='center', fontsize=10)
    
    # Plot 2: Products on Sale Percentage
    ax2 = axes[1]
    df_sorted2 = df.sort_values('on_sale_pct', ascending=True)
    colors2 = plt.cm.Blues(np.linspace(0.3, 0.9, len(df_sorted2)))
    
    bars2 = ax2.barh(df_sorted2['category'].str.title(), 
                     df_sorted2['on_sale_pct'], 
                     color=colors2, edgecolor='white', linewidth=1.5)
    ax2.set_xlabel('Percentage of Products on Sale (%)')
    ax2.set_title('Discount Frequency by Category', fontweight='bold')
    
    # Add value labels
    for bar, val in zip(bars2, df_sorted2['on_sale_pct']):
        ax2.text(val + 1, bar.get_y() + bar.get_height()/2, 
                f'{val:.1f}%', va='center', fontsize=10)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'category_discounts.png'))
    plt.close()
    print(f"Saved: category_discounts.png")


def plot_price_distribution_boxplot(
    df: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create box plots showing price and discount distributions by category.
    
    Args:
        df: Time series DataFrame.
        output_dir: Directory to save the plot.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Custom color palette
    palette = {'outerwear': '#E74C3C', 'dresses': '#9B59B6', 
               'tops': '#3498DB', 'pants': '#27AE60', 'accessories': '#F39C12'}
    
    # Plot 1: Original Price Distribution
    ax1 = axes[0]
    categories_order = df.groupby('category')['original_price'].median().sort_values().index
    
    sns.boxplot(x='category', y='original_price', data=df, 
                order=categories_order, palette=palette, ax=ax1)
    ax1.set_xlabel('Category')
    ax1.set_ylabel('Original Price ($)')
    ax1.set_title('Price Distribution by Category', fontweight='bold')
    ax1.set_xticklabels([cat.title() for cat in categories_order], rotation=45)
    
    # Plot 2: Discount Distribution (only for products on sale)
    ax2 = axes[1]
    df_on_sale = df[df['discount_percentage'] > 0]
    categories_order2 = df_on_sale.groupby('category')['discount_percentage'].median().sort_values().index
    
    sns.boxplot(x='category', y='discount_percentage', data=df_on_sale,
                order=categories_order2, palette=palette, ax=ax2)
    ax2.set_xlabel('Category')
    ax2.set_ylabel('Discount Percentage (%)')
    ax2.set_title('Discount Distribution by Category (Items on Sale)', fontweight='bold')
    ax2.set_xticklabels([cat.title() for cat in categories_order2], rotation=45)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'distribution_boxplots.png'))
    plt.close()
    print(f"Saved: distribution_boxplots.png")


def plot_category_heatmap(
    df: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create heatmap showing discount patterns across categories and days.
    
    Args:
        df: Time series DataFrame.
        output_dir: Directory to save the plot.
    """
    # Pivot data for heatmap
    pivot_data = df.pivot_table(
        values='discount_percentage',
        index='category',
        columns='date',
        aggfunc='mean'
    )
    
    # Format column labels to show just day
    pivot_data.columns = [d.strftime('%b %d') for d in pivot_data.columns]
    
    # Rename rows for display
    pivot_data.index = [cat.title() for cat in pivot_data.index]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn',
                center=pivot_data.values.mean(),
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'Avg Discount (%)'}, ax=ax)
    
    ax.set_title('Category Discount Heatmap Across Days', fontweight='bold', pad=20)
    ax.set_xlabel('Date')
    ax.set_ylabel('Category')
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'category_heatmap.png'))
    plt.close()
    print(f"Saved: category_heatmap.png")


def plot_price_vs_discount_scatter(
    df: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create scatter plot showing relationship between price and discount.
    
    Args:
        df: Time series DataFrame.
        output_dir: Directory to save the plot.
    """
    # Filter to products on sale
    df_on_sale = df[df['discount_percentage'] > 0].copy()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Color by category
    palette = {'outerwear': '#E74C3C', 'dresses': '#9B59B6', 
               'tops': '#3498DB', 'pants': '#27AE60', 'accessories': '#F39C12'}
    
    for category in df_on_sale['category'].unique():
        cat_data = df_on_sale[df_on_sale['category'] == category]
        ax.scatter(cat_data['original_price'], cat_data['discount_percentage'],
                  alpha=0.6, s=50, label=category.title(),
                  c=palette.get(category, '#95A5A6'))
    
    # Add trend line
    z = np.polyfit(df_on_sale['original_price'], df_on_sale['discount_percentage'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df_on_sale['original_price'].min(), 
                         df_on_sale['original_price'].max(), 100)
    ax.plot(x_line, p(x_line), "k--", alpha=0.8, linewidth=2, label='Trend Line')
    
    # Calculate correlation
    corr = df_on_sale['original_price'].corr(df_on_sale['discount_percentage'])
    
    ax.set_xlabel('Original Price ($)')
    ax.set_ylabel('Discount Percentage (%)')
    ax.set_title(f'Original Price vs. Discount Rate (r = {corr:.3f})', fontweight='bold')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'price_vs_discount_scatter.png'))
    plt.close()
    print(f"Saved: price_vs_discount_scatter.png")


def plot_correlation_heatmap(
    corr_matrix: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create correlation matrix heatmap.
    
    Args:
        corr_matrix: Correlation matrix DataFrame.
        output_dir: Directory to save the plot.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create mask for upper triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Rename labels for clarity
    labels = {
        'original_price': 'Original\nPrice',
        'sale_price': 'Sale\nPrice',
        'discount_percentage': 'Discount\n%',
        'savings_amount': 'Savings\nAmount'
    }
    
    corr_display = corr_matrix.rename(index=labels, columns=labels)
    
    sns.heatmap(corr_display, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, vmin=-1, vmax=1,
                linewidths=0.5, linecolor='white',
                square=True, ax=ax)
    
    ax.set_title('Correlation Matrix of Price Variables', fontweight='bold', pad=15)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()
    print(f"Saved: correlation_heatmap.png")


def plot_discount_tier_distribution(
    df: pd.DataFrame, 
    output_dir: str = "results"
) -> None:
    """
    Create pie chart showing discount tier distribution.
    
    Args:
        df: Time series DataFrame.
        output_dir: Directory to save the plot.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Overall discount tier distribution
    ax1 = axes[0]
    tier_counts = df['discount_tier'].value_counts()
    colors = {'none': '#BDC3C7', 'small': '#F1C40F', 
              'medium': '#E67E22', 'large': '#C0392B'}
    pie_colors = [colors.get(tier, '#95A5A6') for tier in tier_counts.index]
    
    wedges, texts, autotexts = ax1.pie(tier_counts, labels=tier_counts.index.str.title(),
                                        autopct='%1.1f%%', colors=pie_colors,
                                        explode=[0.02] * len(tier_counts),
                                        startangle=90)
    ax1.set_title('Distribution of Discount Tiers\n(All Products)', fontweight='bold')
    
    # Plot 2: Discount tier by category (stacked bar)
    ax2 = axes[1]
    tier_by_cat = pd.crosstab(df['category'], df['discount_tier'], normalize='index') * 100
    tier_by_cat = tier_by_cat.reindex(columns=['none', 'small', 'medium', 'large'])
    
    tier_by_cat.plot(kind='bar', stacked=True, ax=ax2, 
                     color=[colors['none'], colors['small'], 
                            colors['medium'], colors['large']],
                     edgecolor='white', linewidth=0.5)
    
    ax2.set_xlabel('Category')
    ax2.set_ylabel('Percentage (%)')
    ax2.set_title('Discount Tier Distribution by Category', fontweight='bold')
    ax2.set_xticklabels([cat.title() for cat in tier_by_cat.index], rotation=45)
    ax2.legend(title='Discount Tier', loc='upper right',
               labels=['None', 'Small (1-20%)', 'Medium (21-40%)', 'Large (41%+)'])
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'discount_tier_distribution.png'))
    plt.close()
    print(f"Saved: discount_tier_distribution.png")


def create_all_visualizations(
    processed_dir: str = "data/processed",
    output_dir: str = "results"
) -> None:
    """
    Generate all visualizations for the analysis.
    
    Args:
        processed_dir: Directory containing processed data.
        output_dir: Directory to save visualizations.
    """
    print("=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    
    # Setup style
    setup_style()
    
    # Load data
    print("\nLoading data...")
    data = load_data(processed_dir)
    
    print("\nCreating visualizations...")
    print("-" * 40)
    
    # Generate each visualization
    plot_daily_price_trajectory(data['daily'], output_dir)
    plot_category_discounts(data['category'], output_dir)
    plot_price_distribution_boxplot(data['time_series'], output_dir)
    plot_category_heatmap(data['time_series'], output_dir)
    plot_price_vs_discount_scatter(data['time_series'], output_dir)
    plot_correlation_heatmap(data['correlation'], output_dir)
    plot_discount_tier_distribution(data['time_series'], output_dir)
    
    print("-" * 40)
    print(f"\nAll visualizations saved to: {os.path.abspath(output_dir)}")
    print("=" * 60)


if __name__ == "__main__":
    create_all_visualizations(
        processed_dir="data/processed",
        output_dir="results"
    )
