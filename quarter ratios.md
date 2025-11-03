# Quarterly Ratios Column Naming Strategy in Finance Bro

## Column Naming Strategy Overview

The Finance Bro application implements a sophisticated dual-column naming strategy to optimize quarterly ratios data for both human display and AI query processing. This approach ensures data integrity while enhancing natural language interaction capabilities.

## VnStock Data Structure and Column Flattening

### Raw Data from VnStock API

When fetching quarterly ratios data from VnStock, the raw data comes with **multi-index column structure**:

```python
# Raw data structure from VnStock
Ratio_raw = stock.finance.ratio(period=period, lang="en", dropna=True)
```

**Raw Multi-Index Structure Example**:
```
Columns:
Level 0: ['Liquidity', 'Profitability', 'Solvency']
Level 1: ['Current_Ratio', 'ROE', 'Debt_to_Equity']
```

### Column Flattening Process

**Implementation**: Uses VnStock's built-in flattening utility

```python
# Use vnstock's built-in flatten_hierarchical_index function
Ratio = flatten_hierarchical_index(
    Ratio_raw, separator="_", handle_duplicates=True, drop_levels=0
)
```

**Flattening Transformation**:
- **Input**: Multi-level column headers (Liquidity > Current_Ratio)
- **Output**: Single-level column names (Liquidity_Current_Ratio)
- **Separator**: Underscore "_" connects hierarchical levels
- **Duplicate Handling**: `handle_duplicates=True` ensures unique column names

**Flattened Column Structure**:
| ticker | yearReport | lengthReport | Liquidity_Current_Ratio | Profitability_ROE | Solvency_Debt_to_Equity |
|--------|------------|--------------|-------------------------|-------------------|-------------------------|
| VCB    | 2024       | 1            | 0.85                    | 0.152             | 0.68                    |

### lengthReport Column: Quarter Representation

**Critical Understanding**: The `lengthReport` column contains **numeric values that represent quarters**:

- **Value 1**: Quarter 1 (Q1) - January to March
- **Value 2**: Quarter 2 (Q2) - April to June
- **Value 3**: Quarter 3 (Q3) - July to September
- **Value 4**: Quarter 4 (Q4) - October to December

**Quarter Detection Logic**:
```python
# Check for quarterly data pattern
if df["lengthReport"].isin([1, 2, 3, 4]).any():
    # This confirms quarterly data structure
    # Values 1,2,3,4 represent Q1,Q2,Q3,Q4 respectively
```

**Example Quarterly Data**:
| yearReport | lengthReport | Quarter Interpretation |
|------------|--------------|----------------------|
| 2024       | 1            | 2024-Q1 (Jan-Mar)    |
| 2024       | 2            | 2024-Q2 (Apr-Jun)    |
| 2024       | 3            | 2024-Q3 (Jul-Sep)    |
| 2024       | 4            | 2024-Q4 (Oct-Dec)    |

## Dual Data Storage Architecture

### 1. Display Version (Original Column Names)

**Purpose**: Maintains data integrity and accurate presentation
**Column Naming**: Preserves original VnStock API column names

**Characteristics**:
- Maintains original column names from VnStock API
- Uses `lengthReport` column with numeric values [1,2,3,4] for quarter identification
- Preserves `yearReport` for annual context
- Keeps `ticker` column for stock identification

**Display Structure**:
| ticker | yearReport | lengthReport | Liquidity_Current_Ratio | Profitability_ROE |
|--------|------------|--------------|-------------------------|-------------------|
| VCB    | 2024       | 1            | 0.85                    | 0.152             |
| VCB    | 2024       | 2            | 0.87                    | 0.148             |

### 2. AI-Optimized Version (Enhanced Column Names)

**Purpose**: Improves natural language query processing for AI systems
**Column Naming**: Enhanced for more intuitive AI interactions

**Column Renaming Process**:
```python
# AI-Optimized Version - Enhanced for Queries
Ratio_AI = Ratio.copy()

if period == "quarter":
    # Rename columns in AI copies for better query compatibility
    if "lengthReport" in Ratio_AI.columns and Ratio_AI["lengthReport"].isin([1, 2, 3, 4]).any():
        Ratio_AI = Ratio_AI.rename(columns={"lengthReport": "Quarter"})
```

**Characteristics**:
- Renames `lengthReport` → `Quarter` (maintains numeric values 1,2,3,4)
- Maintains all other columns for data consistency
- Optimized for AI query interpretation

**AI-Optimized Structure**:
| ticker | yearReport | Quarter | Liquidity_Current_Ratio | Profitability_ROE |
|--------|------------|---------|-------------------------|-------------------|
| VCB    | 2024       | 1       | 0.85                    | 0.152             |
| VCB    | 2024       | 2       | 0.87                    | 0.148             |

## Column Naming Transformation Logic

### Quarterly Data Detection and Renaming
```python
# Detect quarterly data pattern
if (
    "lengthReport" in Ratio_AI.columns  # Column exists
    and Ratio_AI["lengthReport"].isin([1, 2, 3, 4]).any()  # Contains quarter values
):
    # Confirm quarterly data and proceed with column renaming
    Ratio_AI = Ratio_AI.rename(columns={"lengthReport": "Quarter"})
```

### Column Mapping Strategy

| Original Column | AI-Optimized Column | Data Values | Purpose |
|-----------------|-------------------|-------------|---------|
| `lengthReport`  | `Quarter`          | [1, 2, 3, 4] | Natural language queries ("Q1", "quarter 1", etc.) |
| `yearReport`    | `yearReport`       | [2024, 2023] | Annual context (unchanged) |
| `ticker`        | `ticker`           | ['VCB', 'VIC'] | Stock identification (unchanged) |
| `*_Ratio`       | `*_Ratio`          | [0.85, 0.152] | Metric names (unchanged) |

### lengthReport to Quarter Interpretation

**Display Version (lengthReport)**:
- Technical representation: Numeric values 1,2,3,4
- Purpose: Data processing and API compatibility
- Usage: Internal calculations and data storage

**AI-Optimized Version (Quarter)**:
- Natural representation: Same numeric values 1,2,3,4 but with semantic column name
- Purpose: Enhanced AI query understanding
- Usage: Natural language processing and user queries

## Quarterly Data Transformation for Display

### Period ID Creation Process
```python
# Create human-readable quarterly identifiers
df_clean["period_id"] = (
    df_clean["yearReport"].astype(str) + "-Q" + df_clean["Quarter"].astype(str)
)
```

**Transformation Example**:
| yearReport | Quarter (lengthReport) | period_id |
|------------|------------------------|-----------|
| 2024       | 1                      | 2024-Q1   |
| 2024       | 2                      | 2024-Q2   |
| 2024       | 3                      | 2024-Q3   |
| 2024       | 4                      | 2024-Q4   |

## AI Query Enhancement Benefits

### Query Interpretation Comparison

**Query Examples with Original lengthReport Column**:
- User Query: "What was the ROE in lengthReport 2?"
- AI Challenge: Technical term "lengthReport" not intuitive
- Success Rate: Lower

**Query Examples with Enhanced Quarter Column**:
- User Query: "What was the ROE in Q2?" or "What was the ROE in quarter 2?"
- AI Advantage: Clear understanding of quarterly concepts
- Success Rate: Higher

**Enhanced Query Examples**:
- "Show me Q2 profitability metrics" → Interprets Quarter = 2
- "Compare quarter 1 vs quarter 3 ROE" → Interprets Quarter = 1 vs 3
- "What's the debt ratio in Q4?" → Interprets Quarter = 4
- "Display all quarterly liquidity ratios" → Processes all Quarter values

## Data Integrity and Validation

### Quarter Value Validation Process
Data validation ensures the `lengthReport` column contains valid quarter values:
- Values [1, 2, 3, 4] confirm valid quarterly data structure
- Values outside this range indicate non-quarterly data
- Validation occurs before column renaming transformation

### Data Consistency Assurance
- **Numerical Preservation**: Quarter values (1,2,3,4) remain identical across both versions
- **Column Name Change**: Only the column header changes from `lengthReport` to `Quarter`
- **Data Structure**: All other columns and relationships remain unchanged

## Technical Implementation Details

### Column Renaming Conditions
Column renaming occurs only when ALL conditions are met:
1. Period parameter equals "quarter"
2. DataFrame contains "lengthReport" column
3. Column contains valid quarter values [1, 2, 3, 4]

### VnStock Integration Details
- **Data Source**: VnStock API multi-index financial ratios data
- **Flattening Process**: Built-in `flatten_hierarchical_index()` utility
- **Quarter Encoding**: Numeric values 1-4 represent Q1-Q4 in `lengthReport` column
- **Data Sources**: Supports both VCI and TCBS data sources

## Benefits of Dual Naming Strategy

### 1. Enhanced User Experience
- **Natural Queries**: Users can reference quarters intuitively (Q1, Q2, etc.)
- **Accurate Display**: Financial data shows with proper industry-standard column names
- **Technical Accuracy**: Original `lengthReport` maintains API compatibility

### 2. Improved AI Performance
- **Better Parsing**: "Quarter" more recognizable than "lengthReport"
- **Context Understanding**: AI comprehends temporal quarterly concepts
- **Query Accuracy**: Higher success rate for quarterly financial analysis

### 3. Data Integrity
- **Original Preservation**: Display data maintains API-accurate column names
- **No Information Loss**: All numerical quarter values preserved
- **Audit Trail**: Original structure maintained for compliance

## Quarterly Value Mapping Reference

| lengthReport Value | Quarter Name | Period ID | Common Months |
|-------------------|--------------|-----------|---------------|
| 1                 | Q1 / Quarter 1 | 2024-Q1   | Jan, Feb, Mar  |
| 2                 | Q2 / Quarter 2 | 2024-Q2   | Apr, May, Jun  |
| 3                 | Q3 / Quarter 3 | 2024-Q3   | Jul, Aug, Sep  |
| 4                 | Q4 / Quarter 4 | 2024-Q4   | Oct, Nov, Dec  |

## Conclusion

The dual column naming strategy, combined with VnStock's built-in column flattening, creates a robust system for handling quarterly financial ratios data. By understanding that `lengthReport` values 1-4 represent quarters Q1-Q4, the system effectively transforms technical API responses into user-friendly quarterly formats while maintaining data integrity and enhancing AI query capabilities.

This approach successfully bridges the gap between raw financial API data and intuitive user interaction, making complex quarterly financial analysis accessible through natural language queries.