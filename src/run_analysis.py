
import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from scipy import stats
from datetime import datetime


def load_processed_data(processed_dir: str = "data/processed") -> Tuple[pd.DataFrame, Dict]:
    """
    Load processed data files for analysis.
    

    Returns:
        Tuple: (DataFrame of time-series data, summary statistics dict)
    """
    # Load time-series data
    ts_file = os.path.join(processed_dir, "price_time_series.csv")
    df = pd.read_csv(ts_file, parse_dates=["date"])
    
    # Load summary statistics
    stats_file = os.path.join(processed_dir, "summary_statistics.json")
    with open(stats_file, 'r') as f:
        summary = json.load(f)
    
    print(f"Loaded {len(df)} observations from {df['date'].nunique()} days")
    print(f"Categories: {df['category'].unique().tolist()}")
    
    return df, summary


def analyze_category_discounts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze discount patterns by category.
    
    Research Question 1: Which product categories show the most frequent 
    and significant discounts?
    
    Args:
        df: Time-series DataFrame.
    
    Returns:
        pd.DataFrame: Category discount analysis results.
    """
    print("\n" + "=" * 60)
    print("ANALYSIS 1: Category Discount Patterns")
    print("=" * 60)
    
    # Calculate metrics by category
    category_analysis = df.groupby('category').agg({
        'discount_percentage': ['mean', 'median', 'max', 'std'],
        'sku': 'nunique',
        'savings_amount': 'mean'
    }).round(2)
    
    # Flatten column names
    category_analysis.columns = ['avg_discount', 'median_discount', 'max_discount',
                                  'discount_std', 'unique_products', 'avg_savings']
    
    # Calculate percentage of products on sale per category
    on_sale_pct = df.groupby('category').apply(
        lambda x: (x['discount_percentage'] > 0).sum() / len(x) * 100
    ).round(2)
    category_analysis['on_sale_pct'] = on_sale_pct
    
    # Calculate discount frequency (how often discounts change)
    discount_volatility = df.groupby('category')['discount_percentage'].apply(
        lambda x: x.diff().abs().mean()
    ).round(2)
    category_analysis['discount_volatility'] = discount_volatility
    
    # Sort by average discount
    category_analysis = category_analysis.sort_values('avg_discount', ascending=False)
    
    print("\nCategory Discount Summary:")
    print("-" * 60)
    for cat in category_analysis.index:
        row = category_analysis.loc[cat]
        print(f"\n{cat.upper()}:")
        print(f"  - Average discount: {row['avg_discount']:.1f}%")
        print(f"  - Products on sale: {row['on_sale_pct']:.1f}%")
        print(f"  - Max discount observed: {row['max_discount']:.0f}%")
        print(f"  - Average savings: ${row['avg_savings']:.2f}")
        print(f"  - Discount volatility: {row['discount_volatility']:.2f}")
    
    return category_analysis.reset_index()


def analyze_price_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze how prices change over time.
    
    Research Question 2: How do product prices change over time?
    
    Args:
        df: Time-series DataFrame.
    
    Returns:
        pd.DataFrame: Daily price trend analysis.
    """
    print("\n" + "=" * 60)
    print("ANALYSIS 2: Price Trends Over Time")
    print("=" * 60)
    
    # Daily aggregations
    daily_stats = df.groupby('date').agg({
        'original_price': 'mean',
        'sale_price': 'mean',
        'discount_percentage': 'mean',
        'savings_amount': 'sum',
        'sku': 'count'
    }).reset_index()
    
    daily_stats.columns = ['date', 'avg_original_price', 'avg_sale_price',
                           'avg_discount', 'total_savings', 'product_count']
    
    # Calculate day-over-day changes
    daily_stats['discount_change'] = daily_stats['avg_discount'].diff()
    daily_stats['price_change'] = daily_stats['avg_sale_price'].diff()
    
    # Calculate overall trend
    days_numeric = (daily_stats['date'] - daily_stats['date'].min()).dt.days
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        days_numeric, daily_stats['avg_discount']
    )
    
    print(f"\nDaily Price Statistics:")
    print("-" * 60)
    print(f"Date range: {daily_stats['date'].min().date()} to {daily_stats['date'].max().date()}")
    print(f"\nAverage original price: ${daily_stats['avg_original_price'].mean():.2f}")
    print(f"Average sale price: ${daily_stats['avg_sale_price'].mean():.2f}")
    print(f"Average discount: {daily_stats['avg_discount'].mean():.1f}%")
    
    print(f"\nDiscount Trend Analysis:")
    print(f"  - Trend direction: {'Increasing' if slope > 0 else 'Decreasing'}")
    print(f"  - Daily change rate: {slope:.3f}% per day")
    print(f"  - R-squared: {r_value**2:.3f}")
    print(f"  - Trend significance (p-value): {p_value:.4f}")
    
    # Day of week analysis
    daily_stats['day_of_week'] = daily_stats['date'].dt.day_name()
    dow_stats = daily_stats.groupby('day_of_week')['avg_discount'].mean()
    
    print(f"\nBest discount day: {dow_stats.idxmax()} ({dow_stats.max():.1f}%)")
    print(f"Worst discount day: {dow_stats.idxmin()} ({dow_stats.min():.1f}%)")
    
    return daily_stats


def analyze_price_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identify patterns to help consumers find the best time to buy.
    
    Research Question 3: Are there identifiable patterns that can help 
    consumers determine the best time to buy?
    
    Args:
        df: Time-series DataFrame.
    
    Returns:
        Dict: Pattern analysis results.
    """
    print("\n" + "=" * 60)
    print("ANALYSIS 3: Consumer Buying Patterns")
    print("=" * 60)
    
    patterns = {}
    
    # 1. Best category to find deals
    category_value = df.groupby('category').agg({
        'discount_percentage': 'mean',
        'savings_amount': 'mean'
    })
    best_deal_category = category_value['savings_amount'].idxmax()
    patterns['best_deal_category'] = {
        'category': best_deal_category,
        'avg_savings': category_value.loc[best_deal_category, 'savings_amount'],
        'avg_discount': category_value.loc[best_deal_category, 'discount_percentage']
    }
    
    print(f"\n1. Best Category for Deals: {best_deal_category.upper()}")
    print(f"   Average savings: ${patterns['best_deal_category']['avg_savings']:.2f}")
    
    # 2. Price tier analysis - which tier has best discounts?
    tier_analysis = df.groupby('price_tier').agg({
        'discount_percentage': ['mean', 'count'],
        'savings_amount': 'mean'
    })
    tier_analysis.columns = ['avg_discount', 'count', 'avg_savings']
    patterns['price_tier_analysis'] = tier_analysis.to_dict()
    
    best_tier = tier_analysis['avg_discount'].idxmax()
    print(f"\n2. Best Price Tier for Discounts: {best_tier.upper()}")
    print(f"   Average discount: {tier_analysis.loc[best_tier, 'avg_discount']:.1f}%")
    
    # 3. Correlation between original price and discount
    correlation = df['original_price'].corr(df['discount_percentage'])
    patterns['price_discount_correlation'] = correlation
    
    print(f"\n3. Price-Discount Correlation: {correlation:.3f}")
    if correlation > 0.3:
        print("   Interpretation: Higher-priced items tend to have larger discounts")
    elif correlation < -0.3:
        print("   Interpretation: Lower-priced items tend to have larger discounts")
    else:
        print("   Interpretation: No strong relationship between price and discount")
    
    # 4. Discount size distribution
    discount_dist = df[df['discount_percentage'] > 0]['discount_tier'].value_counts(normalize=True)
    patterns['discount_distribution'] = discount_dist.to_dict()
    
    print(f"\n4. Discount Size Distribution (of items on sale):")
    for tier, pct in discount_dist.items():
        print(f"   {tier}: {pct*100:.1f}%")
    
    # 5. Category-specific timing recommendations
    print(f"\n5. Category-Specific Recommendations:")
    
    category_daily = df.groupby(['category', 'date'])['discount_percentage'].mean().reset_index()
    
    for category in df['category'].unique():
        cat_data = category_daily[category_daily['category'] == category]
        best_day = cat_data.loc[cat_data['discount_percentage'].idxmax()]
        print(f"   {category.upper()}: Best day was {best_day['date'].strftime('%A, %b %d')} "
              f"({best_day['discount_percentage']:.1f}% avg discount)")
    
    # 6. Products with consistent discounts
    consistent_sales = df.groupby('sku').agg({
        'discount_percentage': ['mean', 'std', 'min'],
        'name': 'first',
        'category': 'first'
    })
    consistent_sales.columns = ['avg_discount', 'discount_std', 'min_discount', 'name', 'category']
    
    # Products always on sale (min discount > 0) with consistent discount
    always_on_sale = consistent_sales[
        (consistent_sales['min_discount'] > 0) & 
        (consistent_sales['discount_std'] < 5)
    ].sort_values('avg_discount', ascending=False)
    
    patterns['consistently_discounted'] = len(always_on_sale)
    
    print(f"\n6. Consistently Discounted Products: {len(always_on_sale)}")
    if len(always_on_sale) > 0:
        print("   Top 5 products with stable discounts:")
        for idx, row in always_on_sale.head(5).iterrows():
            print(f"   - {row['name']} ({row['category']}): {row['avg_discount']:.0f}% off")
    
    return patterns


def analyze_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create correlation analysis between numeric variables.
    
    Args:
        df: Time-series DataFrame.
    
    Returns:
        pd.DataFrame: Correlation matrix.
    """
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS")
    print("=" * 60)
    
    numeric_cols = ['original_price', 'sale_price', 'discount_percentage', 'savings_amount']
    corr_matrix = df[numeric_cols].corr().round(3)
    
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    return corr_matrix


def generate_analysis_report(
    category_analysis: pd.DataFrame,
    daily_stats: pd.DataFrame,
    patterns: Dict,
    corr_matrix: pd.DataFrame,
    output_dir: str = "data/processed"
) -> None:
    """
    Save all analysis results to files.
    
    Args:
        category_analysis: Category discount analysis.
        daily_stats: Daily price trends.
        patterns: Pattern analysis results.
        corr_matrix: Correlation matrix.
        output_dir: Output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save category analysis
    category_analysis.to_csv(
        os.path.join(output_dir, "category_analysis.csv"), 
        index=False
    )
    
    # Save daily stats
    daily_stats.to_csv(
        os.path.join(output_dir, "daily_price_trends.csv"), 
        index=False
    )
    
    # Save correlation matrix
    corr_matrix.to_csv(os.path.join(output_dir, "correlation_matrix.csv"))
    
    # Save patterns as JSON
    # Convert non-serializable types
    patterns_serializable = {}
    for key, value in patterns.items():
        if isinstance(value, dict):
            patterns_serializable[key] = {
                str(k): float(v) if isinstance(v, (np.float64, np.int64)) else v 
                for k, v in value.items()
            }
        elif isinstance(value, (np.float64, np.int64)):
            patterns_serializable[key] = float(value)
        else:
            patterns_serializable[key] = value
    
    with open(os.path.join(output_dir, "consumer_patterns.json"), 'w') as f:
        json.dump(patterns_serializable, f, indent=2, default=str)
    
    print(f"\nAnalysis results saved to: {output_dir}")


def run_analysis(processed_dir: str = "data/processed") -> Dict[str, Any]:
    """
    Main function to run all analyses.
    
    Args:
        processed_dir: Directory containing processed data.
    
    Returns:
        Dict: All analysis results.
    """
    print("=" * 60)
    print("ARITZIA PRICE ANALYSIS")
    print("=" * 60)
    
    # Load data
    df, summary = load_processed_data(processed_dir)
    
    # Run analyses
    category_analysis = analyze_category_discounts(df)
    daily_stats = analyze_price_trends(df)
    patterns = analyze_price_patterns(df)
    corr_matrix = analyze_correlation_matrix(df)
    
    # Save results
    generate_analysis_report(
        category_analysis, 
        daily_stats, 
        patterns, 
        corr_matrix,
        processed_dir
    )
    
    # Print conclusions
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    
    print("\n1. DISCOUNT FREQUENCY BY CATEGORY:")
    top_category = category_analysis.loc[
        category_analysis['on_sale_pct'].idxmax()
    ]
    print(f"   Most frequently discounted: {top_category['category'].upper()} "
          f"({top_category['on_sale_pct']:.1f}% of products on sale)")
    
    print("\n2. PRICE VOLATILITY:")
    most_volatile = category_analysis.loc[
        category_analysis['discount_volatility'].idxmax()
    ]
    print(f"   Most volatile category: {most_volatile['category'].upper()} "
          f"(volatility index: {most_volatile['discount_volatility']:.2f})")
    
    print("\n3. CONSUMER RECOMMENDATIONS:")
    print(f"   - Best category for savings: {patterns['best_deal_category']['category'].upper()}")
    print(f"   - Products consistently on sale: {patterns['consistently_discounted']}")
    
    print("\n" + "=" * 60)
    
    return {
        'category_analysis': category_analysis,
        'daily_stats': daily_stats,
        'patterns': patterns,
        'correlation': corr_matrix
    }


if __name__ == "__main__":
    results = run_analysis(processed_dir="data/processed")
