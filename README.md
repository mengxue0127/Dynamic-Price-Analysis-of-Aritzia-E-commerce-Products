# Dynamic Price Analysis of Aritzia E-commerce Products

## Project Overview

This project analyzes temporal price changes in Aritzia's online product catalog to uncover discount patterns, cross-category price behaviors, and potential pricing cycles. The goal is to provide data-driven insights into Aritzia's pricing behavior and empower consumers with better purchasing strategies.

### Research Questions
1. Which product categories show the most frequent and significant discounts?
2. How do product prices change over time?
3. Are there identifiable patterns that can help consumers determine the best time to buy?

## Team Members

| Name | USC Email | USC ID |
|------|-----------|--------|
|Mengxue Li|mengxue@usc.edu|6724826910|
## Project Structure

```
aritzia_project/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── project_proposal.pdf         # Original project proposal
├── data/
│   ├── raw/                     # Raw data files (JSON)
│   └── processed/               # Cleaned and processed data
├── results/
│   ├── final_report.pdf         # Final project report
│   └── *.png                    # Visualization outputs
└── src/
    ├── get_data.py              # Data collection script
    ├── clean_data.py            # Data cleaning script
    ├── run_analysis.py          # Analysis script
    ├── visualize_results.py     # Visualization script
    └── utils/                   # Utility functions
```

## Setup Instructions

### 1. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Scripts

Execute the scripts in the following order:

### Step 1: Data Collection

```bash
python src/get_data.py
```

This script simulates collecting product data from Aritzia's website. It generates realistic data for 10 consecutive days, including:
- Product information (name, SKU, URL)
- Pricing data (original price, sale price, discount percentage)
- Product metadata (category, colors, availability)

Output: `data/raw/aritzia_products_YYYY-MM-DD.json` files

### Step 2: Data Cleaning

```bash
python src/clean_data.py
```

This script processes the raw data:
- Removes duplicate entries
- Validates and standardizes price formats
- Adds derived features (price tier, discount tier)
- Creates time-series structured data

Output: 
- `data/processed/cleaned_products.json`
- `data/processed/price_time_series.csv`
- `data/processed/summary_statistics.json`
- `data/processed/category_daily_stats.csv`

### Step 3: Data Analysis

```bash
python src/run_analysis.py
```

This script performs comprehensive analysis:
- Category discount pattern analysis
- Time-series price trend analysis
- Consumer pattern identification
- Correlation analysis

Output:
- `data/processed/category_analysis.csv`
- `data/processed/daily_price_trends.csv`
- `data/processed/consumer_patterns.json`
- `data/processed/correlation_matrix.csv`

### Step 4: Visualization

```bash
python src/visualize_results.py
```

This script generates all visualizations:
- Daily price trajectory charts
- Category discount comparison bar charts
- Price/discount distribution box plots
- Category-day discount heatmap
- Price vs. discount scatter plot
- Correlation matrix heatmap
- Discount tier distribution charts

Output: `results/*.png` visualization files

## Running All Steps at Once

You can run all steps sequentially:

```bash
cd src
python get_data.py && python clean_data.py && python run_analysis.py && python visualize_results.py
```

## Data Description

### Raw Data Fields
| Field | Type | Description |
|-------|------|-------------|
| id | int | Product unique identifier |
| sku | str | Stock Keeping Unit code |
| name | str | Product name |
| category | str | Product category |
| url | str | Product page URL |
| original_price | float | Original retail price |
| sale_price | float | Current sale price |
| discount_percentage | int | Discount as percentage |
| colors | list | Available color options |
| in_stock | bool | Stock availability |
| collection_timestamp | str | Data collection timestamp |
| collection_date | str | Data collection date |

### Processed Data (Additional Fields)
| Field | Type | Description |
|-------|------|-------------|
| price_tier | str | Price category (budget/mid-range/premium/luxury) |
| discount_tier | str | Discount category (none/small/medium/large) |
| num_colors | int | Number of color options |
| savings_amount | float | Dollar amount saved |

## Key Findings

After running the analysis, you will find:

1. **Category Insights**: Accessories category shows the highest discount frequency, while outerwear has the largest absolute savings.

2. **Temporal Patterns**: Discount rates fluctuate throughout the collection period with identifiable trends.

3. **Consumer Recommendations**: 
   - Best categories for deals identified
   - Products with consistent discounts highlighted
   - Optimal shopping timing suggested

## Dependencies

- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- scipy >= 1.10.0

## Notes

- **Data Simulation**: Due to web scraping limitations, this project uses simulated data that mimics real Aritzia product data patterns.
- **Reproducibility**: The data generation uses seeded random values for reproducible results.
- **File Size**: All individual files are under 100MB as required.

## License

This project is for educational purposes (DSCI 510 Final Project, USC).

## Acknowledgments

- DSCI 510 Course Staff
- University of Southern California
