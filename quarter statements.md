# Quarterly Financial Statements Data Transformation

## Overview

This document explains the core data transformation process for quarterly financial statements, focusing on converting raw VnStock API data into a user-friendly wide format for improved clarity and readability.

## Problem: Original VnStock Data Format

### 1. Long Format Structure Issues

**Original Data Structure from VnStock**:
| ticker | yearReport | lengthReport | Total_Revenue | Net_Income | Total_Assets |
|--------|------------|--------------|---------------|------------|--------------|
| VCB    | 2024       | 1            | 25000000      | 5000000    | 450000000    |
| VCB    | 2024       | 2            | 26000000      | 5200000    | 455000000    |
| VCB    | 2024       | 3            | 25500000      | 5100000    | 452000000    |
| VCB    | 2024       | 4            | 27000000      | 5400000    | 460000000    |

**Readability Problems**:
- **Vertical Layout**: Quarterly data spread across multiple rows
- **Poor Comparison**: Difficult to compare Q1 vs Q2 vs Q3 vs Q4 at a glance
- **Complex Analysis**: Requires mental calculation to identify trends
- **Space Inefficient**: Repeated ticker and year information
- **Non-Intuitive**: Financial professionals expect wide format for period comparisons

### 2. Column Naming Confusion

**Technical vs. User-Friendly Names**:
- `lengthReport`: Technical term unclear to users
- Values 1,2,3,4: Require interpretation as quarters (Q1-Q4)
- Missing Period Context: No clear quarterly identification

## Solution: Data Transformation Process

### Core Transformation Function

```python
def transpose_financial_dataframe(df, name, period):
    """Transpose financial dataframes from long to wide format"""
```

### Step-by-Step Transformation Process

#### Step 1: Data Cleaning
```python
df_clean = df.drop("ticker", axis=1, errors="ignore")
```
- Removes redundant ticker information for cleaner display

#### Step 2: Column Renaming
```python
df_clean = df_clean.rename(columns={"lengthReport": "Quarter"})
```
- Replaces technical term `lengthReport` with user-friendly `Quarter`

#### Step 3: Period ID Creation
```python
df_clean["period_id"] = (
    df_clean["yearReport"].astype(str) + "-Q" + df_clean["Quarter"].astype(str)
)
```
- Creates human-readable period identifiers (e.g., "2024-Q1", "2024-Q2")

#### Step 4: Data Transposition
```python
df_wide = df_clean.set_index("period_id").T
```
- **Key Transformation**: Converts from long format (quarters in rows) to wide format (quarters in columns)

#### Step 5: Metadata Cleanup
```python
df_wide = df_wide.drop(["yearReport", "Quarter"], axis=0, errors="ignore")
```
- Removes helper columns used in transformation

#### Step 6: Final Formatting
```python
df_wide = df_wide.reset_index()
df_wide = df_wide.rename(columns={"index": "Metric"})
```
- Creates clean, readable column structure

## Statement-Specific Transformations

### 1. Income Statement Transformation

**Original Format**:
| ticker | yearReport | lengthReport | Total_Revenue | Net_Income | Operating_Income |
|--------|------------|--------------|---------------|------------|------------------|
| VCB    | 2024       | 1            | 25000000      | 5000000    | 7500000          |
| VCB    | 2024       | 2            | 26000000      | 5200000    | 7800000          |
| VCB    | 2024       | 3            | 25500000      | 5100000    | 7650000          |
| VCB    | 2024       | 4            | 27000000      | 5400000    | 8100000          |

**Transformed Format**:
| Metric            | 2024-Q1   | 2024-Q2   | 2024-Q3   | 2024-Q4   |
|-------------------|-----------|-----------|-----------|-----------|
| Total_Revenue     | 25000000  | 26000000  | 25500000  | 27000000  |
| Net_Income        | 5000000   | 5200000   | 5100000   | 5400000   |
| Operating_Income  | 7500000   | 7800000   | 7650000   | 8100000   |

**Benefits**:
- Immediate quarter-over-quarter comparison
- Clear trend identification across periods
- Professional financial analysis layout

### 2. Balance Sheet Transformation

**Original Format**:
| ticker | yearReport | lengthReport | Total_Assets | Total_Liabilities | Shareholders_Equity |
|--------|------------|--------------|--------------|-------------------|-------------------|
| VCB    | 2024       | 1            | 450000000    | 315000000         | 135000000         |
| VCB    | 2024       | 2            | 455000000    | 318500000         | 136500000         |
| VCB    | 2024       | 3            | 452000000    | 316400000         | 135600000         |
| VCB    | 2024       | 4            | 460000000    | 322000000         | 138000000         |

**Transformed Format**:
| Metric               | 2024-Q1   | 2024-Q2   | 2024-Q3   | 2024-Q4   |
|----------------------|-----------|-----------|-----------|-----------|
| Total_Assets         | 450000000 | 455000000 | 452000000 | 460000000 |
| Total_Liabilities    | 315000000 | 318500000 | 316400000 | 322000000 |
| Shareholders_Equity  | 135000000 | 136500000 | 135600000 | 138000000 |

**Benefits**:
- Balance sheet evolution tracking
- Capital structure analysis across quarters
- Asset growth assessment

### 3. Cash Flow Statement Transformation

**Original Format**:
| ticker | yearReport | lengthReport | Operating_Cash_Flow | Investing_Cash_Flow | Financing_Cash_Flow |
|--------|------------|--------------|---------------------|---------------------|---------------------|
| VCB    | 2024       | 1            | 8000000            | -2000000           | 1000000            |
| VCB    | 2024       | 2            | 8500000            | -1500000           | 500000             |
| VCB    | 2024       | 3            | 8200000            | -1800000           | 800000             |
| VCB    | 2024       | 4            | 9000000            | -1200000           | -200000            |

**Transformed Format**:
| Metric                | 2024-Q1   | 2024-Q2   | 2024-Q3   | 2024-Q4   |
|-----------------------|-----------|-----------|-----------|-----------|
| Operating_Cash_Flow   | 8000000   | 8500000   | 8200000   | 9000000   |
| Investing_Cash_Flow   | -2000000  | -1500000  | -1800000  | -1200000  |
| Financing_Cash_Flow   | 1000000   | 500000    | 800000    | -200000   |

**Benefits**:
- Cash generation pattern analysis
- Investment activity tracking
- Financing strategy assessment

## Column Naming Strategy Improvements

### Original Column Names
- `lengthReport`: Technical term requiring interpretation
- `yearReport`: Clear but could be more contextual
- Metric names: Already descriptive (Total_Revenue, Net_Income, etc.)

### Enhanced Column Names
- `Quarter`: Intuitive quarterly identification
- `period_id`: Combined year-quarter for clear timeline
- Metric names: Preserved for consistency

### Value Mapping
| lengthReport Value | Quarter Interpretation | Period ID   |
|-------------------|-----------------------|-------------|
| 1                 | Q1                    | 2024-Q1     |
| 2                 | Q2                    | 2024-Q2     |
| 3                 | Q3                    | 2024-Q3     |
| 4                 | Q4                    | 2024-Q4     |

## Readability and Clarity Improvements

### 1. Enhanced Visual Comparison

**Before Transformation**:
- Requires vertical scanning across multiple rows
- Mental calculations needed for trend identification
- Difficult to spot patterns quickly

**After Transformation**:
- Horizontal scanning across single row
- Immediate visual pattern recognition
- Easy quarter-over-quarter comparison

### 2. Improved Financial Analysis

**Trend Analysis**:
- Revenue growth: 25000000 → 26000000 → 25500000 → 27000000
- Net income trend: 5000000 → 5200000 → 5100000 → 5400000
- Seasonal patterns immediately visible

**Comparative Analysis**:
- Metric performance comparison across quarters
- Identification of best/worst performing periods
- Consistency assessment across different statement items

### 3. Professional Presentation

**Industry Standard Format**:
- Matches financial analyst expectations
- Consistent with professional reporting tools
- Suitable for analysis and presentation

**Data Organization**:
- Clear metric categorization
- Logical time series presentation
- Efficient use of display space

## Data Integrity Preservation

### 1. Value Conservation
- All numerical values remain unchanged
- Only data structure and column names are modified
- No information loss during transformation

### 2. Validation Mechanisms
```python
# Quarter validation
if df["lengthReport"].isin([1, 2, 3, 4]).any():
    # Confirm valid quarterly data structure
    # Proceed with transformation
```

### 3. Error Handling
- Original dataframe returned if transformation fails
- Graceful handling of edge cases and data anomalies
- Robust fallback mechanisms

## Performance Considerations

### 1. Computational Efficiency
- Transformation uses pandas built-in operations
- Minimal memory overhead during processing
- Fast execution for typical dataset sizes

### 2. Scalability
- Handles multiple years of quarterly data
- Supports various statement types (Income Statement, Balance Sheet, Cash Flow)
- Efficient processing of large financial datasets

## Usage Benefits

### 1. For Financial Analysis
- Quick identification of performance trends
- Easy comparison of key metrics across periods
- Professional presentation of quarterly results

### 2. For Decision Making
- Clear visibility into business performance
- Rapid assessment of quarterly changes
- Data-driven insights extraction

### 3. For Reporting
- Presentation-ready format for stakeholders
- Easy integration into reports and dashboards
- Standardized financial data layout

## Conclusion

The quarterly financial statements data transformation addresses critical usability issues in the original VnStock long format data. By converting to wide format and implementing user-friendly column naming, the transformation significantly improves:

- **Readability**: Clear horizontal layout for easy comparison
- **Clarity**: Intuitive quarterly identification and professional presentation
- **Analysis Efficiency**: Immediate trend identification and pattern recognition
- **Data Integrity**: Preserved numerical accuracy with enhanced structure

This transformation enables efficient quarterly financial analysis while maintaining data precision, making complex financial data accessible and understandable for users across different skill levels.