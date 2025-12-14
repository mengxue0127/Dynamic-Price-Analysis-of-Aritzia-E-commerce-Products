import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


def load_raw_data(raw_dir: str = "data/raw") -> Dict[str, List[Dict]]:
    """
    Load all raw JSON data files from the specified directory.
    
    Args:
        raw_dir: Path to the directory containing raw data files.
    
    Returns:
        Dict: A dictionary with dates as keys and product lists as values.
    """
    print(f"Loading raw data from: {raw_dir}")
    
    # Load the combined file if it exists
    combined_file = os.path.join(raw_dir, "aritzia_all_days.json")
    
    if os.path.exists(combined_file):
        with open(combined_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded combined data file with {len(data)} days")
        return data
    
    # Otherwise, load individual daily files
    all_data = {}
    for filename in sorted(os.listdir(raw_dir)):
        if filename.startswith("aritzia_products_") and filename.endswith(".json"):
            filepath = os.path.join(raw_dir, filename)
            date_str = filename.replace("aritzia_products_", "").replace(".json", "")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                all_data[date_str] = json.load(f)
            
            print(f"  Loaded: {filename} ({len(all_data[date_str])} products)")
    
    return all_data


def remove_duplicates(products: List[Dict]) -> List[Dict]:
    """
    Remove duplicate products based on SKU.
    
    Args:
        products: List of product dictionaries.
    
    Returns:
        List[Dict]: Deduplicated product list.
    """
    seen_skus = set()
    unique_products = []
    
    for product in products:
        if product["sku"] not in seen_skus:
            seen_skus.add(product["sku"])
            unique_products.append(product)
    
    removed = len(products) - len(unique_products)
    if removed > 0:
        print(f"  Removed {removed} duplicate products")
    
    return unique_products


def validate_and_clean_prices(product: Dict) -> Dict:
    """
    Validate and clean price data for a single product.
    
    Args:
        product: A product dictionary.
    
    Returns:
        Dict: The cleaned product dictionary.
    """
    cleaned = product.copy()
    
    # Ensure original_price is valid
    if cleaned.get("original_price") is None or cleaned["original_price"] <= 0:
        cleaned["original_price"] = None
        cleaned["is_valid"] = False
        return cleaned
    
    # Round prices to 2 decimal places
    cleaned["original_price"] = round(float(cleaned["original_price"]), 2)
    
    # Validate sale_price
    if cleaned.get("sale_price") is not None:
        cleaned["sale_price"] = round(float(cleaned["sale_price"]), 2)
        
        # Sale price should not exceed original price
        if cleaned["sale_price"] > cleaned["original_price"]:
            cleaned["sale_price"] = cleaned["original_price"]
            cleaned["discount_percentage"] = 0
    
    # Recalculate discount percentage for accuracy
    if cleaned["sale_price"] and cleaned["sale_price"] < cleaned["original_price"]:
        actual_discount = (1 - cleaned["sale_price"] / cleaned["original_price"]) * 100
        cleaned["discount_percentage"] = round(actual_discount, 1)
    else:
        cleaned["discount_percentage"] = 0
    
    cleaned["is_valid"] = True
    return cleaned


def standardize_category(category: str) -> str:
    """
    Standardize category names to lowercase.
    
    Args:
        category: Raw category name.
    
    Returns:
        str: Standardized category name.
    """
    if not category:
        return "uncategorized"
    return category.lower().strip()


def clean_product_name(name: str) -> str:
    """
    Clean and standardize product names.
    
    Args:
        name: Raw product name.
    
    Returns:
        str: Cleaned product name.
    """
    if not name:
        return "Unknown Product"
    
    # Remove extra whitespace
    cleaned = " ".join(name.split())
    # Title case
    cleaned = cleaned.title()
    return cleaned


def add_derived_features(product: Dict) -> Dict:
    """
    Add derived features useful for analysis.
    
    Args:
        product: A cleaned product dictionary.
    
    Returns:
        Dict: Product with additional derived features.
    """
    enhanced = product.copy()
    
    # Add price tier based on original price
    price = enhanced.get("original_price", 0)
    if price > 0:
        if price < 50:
            enhanced["price_tier"] = "budget"
        elif price < 100:
            enhanced["price_tier"] = "mid-range"
        elif price < 200:
            enhanced["price_tier"] = "premium"
        else:
            enhanced["price_tier"] = "luxury"
    else:
        enhanced["price_tier"] = "unknown"
    
    # Add discount tier
    discount = enhanced.get("discount_percentage", 0)
    if discount == 0:
        enhanced["discount_tier"] = "none"
    elif discount <= 20:
        enhanced["discount_tier"] = "small"
    elif discount <= 40:
        enhanced["discount_tier"] = "medium"
    else:
        enhanced["discount_tier"] = "large"
    
    # Add number of color options
    enhanced["num_colors"] = len(enhanced.get("colors", []))
    
    # Calculate savings amount
    if enhanced.get("original_price") and enhanced.get("sale_price"):
        enhanced["savings_amount"] = round(
            enhanced["original_price"] - enhanced["sale_price"], 2
        )
    else:
        enhanced["savings_amount"] = 0
    
    return enhanced


def clean_daily_data(products: List[Dict], date: str) -> List[Dict]:
    """
    Clean a single day's product data.
    
    Args:
        products: List of product dictionaries for one day.
        date: The date string for the data.
    
    Returns:
        List[Dict]: Cleaned product list.
    """
    print(f"\nCleaning data for {date}...")
    
    # Step 1: Remove duplicates
    products = remove_duplicates(products)
    
    cleaned_products = []
    invalid_count = 0
    
    for product in products:
        # Step 2: Clean product name
        product["name"] = clean_product_name(product.get("name", ""))
        
        # Step 3: Standardize category
        product["category"] = standardize_category(product.get("category", ""))
        
        # Step 4: Validate and clean prices
        product = validate_and_clean_prices(product)
        
        if not product.get("is_valid", True):
            invalid_count += 1
            continue
        
        # Step 5: Add derived features
        product = add_derived_features(product)
        
        # Remove internal validation flag
        if "is_valid" in product:
            del product["is_valid"]
        
        cleaned_products.append(product)
    
    if invalid_count > 0:
        print(f"  Removed {invalid_count} invalid products")
    
    print(f"  Cleaned products: {len(cleaned_products)}")
    
    return cleaned_products


def create_time_series_data(all_data: Dict[str, List[Dict]]) -> pd.DataFrame:
    """
    Create a time-series DataFrame tracking product prices over time.
    
    Args:
        all_data: Dictionary of all daily data.
    
    Returns:
        pd.DataFrame: Time-series price data.
    """
    records = []
    
    for date, products in sorted(all_data.items()):
        for product in products:
            record = {
                "date": date,
                "sku": product["sku"],
                "name": product["name"],
                "category": product["category"],
                "original_price": product["original_price"],
                "sale_price": product["sale_price"],
                "discount_percentage": product["discount_percentage"],
                "price_tier": product.get("price_tier", "unknown"),
                "discount_tier": product.get("discount_tier", "none"),
                "in_stock": product.get("in_stock", True),
                "savings_amount": product.get("savings_amount", 0)
            }
            records.append(record)
    
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    
    return df


def create_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics from the cleaned data.
    
    Args:
        df: Cleaned DataFrame.
    
    Returns:
        Dict: Summary statistics.
    """
    stats = {
        "total_products": df["sku"].nunique(),
        "total_observations": len(df),
        "date_range": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
            "num_days": df["date"].nunique()
        },
        "categories": df["category"].unique().tolist(),
        "price_statistics": {
            "mean_original_price": round(df["original_price"].mean(), 2),
            "median_original_price": round(df["original_price"].median(), 2),
            "min_price": round(df["original_price"].min(), 2),
            "max_price": round(df["original_price"].max(), 2)
        },
        "discount_statistics": {
            "products_on_sale_pct": round(
                (df["discount_percentage"] > 0).sum() / len(df) * 100, 2
            ),
            "mean_discount": round(
                df[df["discount_percentage"] > 0]["discount_percentage"].mean(), 2
            ),
            "max_discount": df["discount_percentage"].max()
        }
    }
    
    return stats


def save_cleaned_data(
    all_cleaned_data: Dict[str, List[Dict]],
    time_series_df: pd.DataFrame,
    summary_stats: Dict,
    output_dir: str = "data/processed"
) -> None:
    """
    Save all cleaned data to the processed directory.
    
    Args:
        all_cleaned_data: Dictionary of cleaned daily data.
        time_series_df: Time-series DataFrame.
        summary_stats: Summary statistics dictionary.
        output_dir: Output directory path.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save cleaned JSON data
    json_output = os.path.join(output_dir, "cleaned_products.json")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(all_cleaned_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved cleaned JSON: {json_output}")
    
    # Save time-series CSV
    csv_output = os.path.join(output_dir, "price_time_series.csv")
    time_series_df.to_csv(csv_output, index=False)
    print(f"Saved time-series CSV: {csv_output}")
    
    # Save summary statistics
    stats_output = os.path.join(output_dir, "summary_statistics.json")
    with open(stats_output, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, indent=2)
    print(f"Saved summary statistics: {stats_output}")
    
    # Save category-level aggregation
    category_stats = time_series_df.groupby(['category', 'date']).agg({
        'original_price': 'mean',
        'sale_price': 'mean',
        'discount_percentage': 'mean',
        'sku': 'count',
        'savings_amount': 'sum'
    }).reset_index()
    category_stats.columns = ['category', 'date', 'avg_original_price', 
                              'avg_sale_price', 'avg_discount', 'product_count',
                              'total_savings']
    
    category_output = os.path.join(output_dir, "category_daily_stats.csv")
    category_stats.to_csv(category_output, index=False)
    print(f"Saved category statistics: {category_output}")


def clean_data(raw_dir: str = "data/raw", output_dir: str = "data/processed") -> None:
    """
    Main function to orchestrate the data cleaning process.
    
    Args:
        raw_dir: Directory containing raw data.
        output_dir: Directory for cleaned output data.
    """
    print("=" * 60)
    print("ARITZIA DATA CLEANING PROCESS")
    print("=" * 60)
    
    # Load raw data
    raw_data = load_raw_data(raw_dir)
    
    if not raw_data:
        print("ERROR: No data found in raw directory!")
        return
    
    # Clean each day's data
    all_cleaned_data = {}
    for date, products in sorted(raw_data.items()):
        cleaned = clean_daily_data(products, date)
        all_cleaned_data[date] = cleaned
    
    # Create time-series DataFrame
    print("\nCreating time-series data...")
    ts_df = create_time_series_data(all_cleaned_data)
    
    # Generate summary statistics
    print("Generating summary statistics...")
    summary = create_summary_statistics(ts_df)
    
    # Save all cleaned data
    save_cleaned_data(all_cleaned_data, ts_df, summary, output_dir)
    
    # Print summary
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)
    print(f"Total unique products: {summary['total_products']}")
    print(f"Total observations: {summary['total_observations']}")
    print(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"Categories: {', '.join(summary['categories'])}")
    print(f"Average price: ${summary['price_statistics']['mean_original_price']}")
    print(f"Products on sale: {summary['discount_statistics']['products_on_sale_pct']}%")
    print(f"Average discount: {summary['discount_statistics']['mean_discount']}%")
    print("=" * 60)


if __name__ == "__main__":
    clean_data(raw_dir="data/raw", output_dir="data/processed")
