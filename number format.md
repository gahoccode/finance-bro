# Financial Number Formatting in Finance Bro

## Overview

Financial applications face the fundamental challenge of presenting large numerical values in a human-readable format. In the Vietnamese stock market context, values often range from thousands to billions of VND, making raw numbers difficult to comprehend at a glance. Effective number formatting is crucial for user experience, enabling quick comprehension of financial metrics without losing precision or context.

This documentatation implements a sophisticated number formatting system that transforms large numerical values into abbreviated, human-readable formats while maintaining financial accuracy and consistency across all displays.

## Problem Statement

### Readability Challenges
Large financial numbers present significant usability issues:

**Raw Values (Difficult to Read)**:
- Company revenue: `25000000000`
- Stock price: `45500`
- Portfolio value: `1250000000`
- Market capitalization: `45000000000000`

**User Experience Issues**:
- Mental calculation required to understand scale
- Error-prone digit counting
- Inconsistent presentation across different views
- Difficulty quickly comparing values of different magnitudes

### Currency Identification
Financial data requires clear currency context:
- Vietnamese Dong (VND) needs explicit identification
- International users may not recognize VND formatting
- Currency symbols improve data comprehension
- Consistent currency presentation builds user trust

### Precision Management
Different financial metrics require different precision levels:
- Currency values need appropriate decimal places
- Percentages require consistent formatting
- Ratios need specific precision standards
- Technical indicators have unique formatting needs

## Solution Architecture

### Dual Formatting Strategy

The application implements a dual formatting approach to handle different display contexts:

1. **Currency Formatting**: For monetary values with VND identification
2. **Default Formatting**: For general numerical values without currency

### Large Number Abbreviation System

**Abbreviation Scale**:
- **K** = Thousands (1,000)
- **M** = Millions (1,000,000)
- **B** = Billions (1,000,000,000)
- **T** = Trillions (1,000,000,000,000)

**Precision Standards**:
- Currency: 2 decimal places
- Default values: 2 decimal places
- Consistent rounding behavior
- Preserve financial accuracy

### Implementation Philosophy

- **Human-First**: Prioritize readability over raw numerical precision
- **Context-Aware**: Different formatting for different use cases
- **Consistent**: Uniform formatting across all application modules
- **Scalable**: Handle values from thousands to trillions

## Implementation Details

### 1. Currency Formatting Implementation

**Transformation Pattern**:
```
Input: 1,500,000,000
Output: "1.50B VND"
```

**Core Implementation** (`src/services/data_service.py`):

```python
def format_financial_metrics(value: Any, metric_type: str = "default") -> str:
    """
    Format financial metrics for display with appropriate scaling and currency.

    Args:
        value: Value to format
        metric_type: Type of metric ('currency', 'percentage', 'ratio', 'default')

    Returns:
        Formatted string with appropriate abbreviations and currency
    """
    try:
        if value is None or (isinstance(value, float) and (value != value)):  # NaN check
            return "N/A"

        if metric_type == "currency":
            # Currency formatting with VND suffix
            if abs(value) >= 1_000_000_000_000:  # Trillions
                return f"{value/1_000_000_000_000:.2f}T VND"
            elif abs(value) >= 1_000_000_000:  # Billions
                return f"{value/1_000_000_000:.2f}B VND"
            elif abs(value) >= 1_000_000:  # Millions
                return f"{value/1_000_000:.2f}M VND"
            elif abs(value) >= 1_000:  # Thousands
                return f"{value/1_000:.2f}K VND"
            else:
                return f"{value:.2f} VND"

        elif metric_type == "default":
            # Default formatting without currency suffix
            if abs(value) >= 1_000_000_000_000:  # Trillions
                return f"{value/1_000_000_000_000:.2f}T"
            elif abs(value) >= 1_000_000_000:  # Billions
                return f"{value/1_000_000_000:.2f}B"
            elif abs(value) >= 1_000_000:  # Millions
                return f"{value/1_000_000:.2f}M"
            elif abs(value) >= 1_000:  # Thousands
                return f"{value/1_000:.2f}K"
            else:
                return f"{value:.2f}"

        # Handle other metric types (percentage, ratio, etc.)
        # ... additional formatting logic

    except (ValueError, TypeError):
        return "N/A"
```

**Step-by-Step Transformation Logic**:

1. **Value Validation**: Check for None, NaN, or invalid values
2. **Scale Determination**: Identify appropriate abbreviation tier
3. **Division & Rounding**: Apply mathematical transformation
4. **String Formatting**: Create final formatted string
5. **Currency Suffix**: Add "VND" for currency formatting

### 2. Default Formatting Implementation

**Transformation Pattern**:
```
Input: 2,500,000
Output: "2.50M"
```

**Implementation within the same function**:

```python
elif metric_type == "default":
    # Default formatting without currency suffix
    if abs(value) >= 1_000_000_000_000:  # Trillions
        return f"{value/1_000_000_000_000:.2f}T"
    elif abs(value) >= 1_000_000_000:  # Billions
        return f"{value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:  # Millions
        return f"{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:  # Thousands
        return f"{value/1_000:.2f}K"
    else:
        return f"{value:.2f}"
```

**Key Differences from Currency Formatting**:

1. **No Currency Suffix**: Omits "VND" identifier
2. **Same Scaling Logic**: Uses identical abbreviation tiers
3. **Consistent Precision**: Maintains 2 decimal places
4. **Cleaner Display**: Suitable for non-monetary metrics

**Real-World Usage Examples**:

```python
# Trading volume
volume = 2500000
formatted_volume = format_financial_metrics(volume, "default")
# Result: "2.50M"

# Company metrics (non-monetary)
employee_count = 15000
formatted_employees = format_financial_metrics(employee_count, "default")
# Result: "15.00K"

# Technical indicators
rsi_value = 75.5
formatted_rsi = format_financial_metrics(rsi_value, "default")
# Result: "75.50"
```

### 3. Application-Wide Usage Patterns

**Portfolio Allocation Formatting**:

```python
def format_allocation_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format portfolio allocation data for display"""
    df_copy = df.copy()

    # Apply currency formatting to monetary values
    df_copy["Total Value (VND)"] = df_copy["Total Value (VND)"].apply(
        lambda x: format_financial_metrics(x, "currency")
    )

    # Apply default formatting to share quantities
    df_copy["Shares"] = df_copy["Shares"].apply(
        lambda x: format_financial_metrics(x, "default")
    )

    return df_copy
```

**Data Processing and Analysis**:

```python
# Apply formatting to financial datasets
def process_financial_data(raw_data):
    formatted_data = raw_data.copy()

    # Currency columns
    currency_columns = ['revenue', 'profit', 'assets', 'market_cap']
    for col in currency_columns:
        formatted_data[col] = formatted_data[col].apply(
            lambda x: format_financial_metrics(x, "currency")
        )

    # Non-currency columns
    numeric_columns = ['volume', 'employees', 'transactions']
    for col in numeric_columns:
        formatted_data[col] = formatted_data[col].apply(
            lambda x: format_financial_metrics(x, "default")
        )

    return formatted_data

# Custom tooltip formatting for financial data
def format_chart_tooltip(value, metric_type):
    if metric_type == "currency":
        return format_financial_metrics(value, "currency")
    else:
        return format_financial_metrics(value, "default")
```

### 4. Edge Case Handling

**Null and Invalid Values**:

```python
# Handle None values
format_financial_metrics(None, "currency")  # Returns: "N/A"

# Handle NaN values
format_financial_metrics(float('nan'), "default")  # Returns: "N/A"

# Handle invalid types
format_financial_metrics("invalid", "currency")  # Returns: "N/A"
```

**Negative Values**:

```python
# Handle negative financial values
loss = -5000000
format_financial_metrics(loss, "currency")  # Returns: "-5.00M VND"

negative_growth = -0.15
format_financial_metrics(negative_growth, "default")  # Returns: "-0.15"
```

**Small Values**:

```python
# Values less than 1,000
small_amount = 500
format_financial_metrics(small_amount, "currency")  # Returns: "500.00 VND"

tiny_value = 0.05
format_financial_metrics(tiny_value, "default")  # Returns: "0.05"
```

## Benefits of the Implementation

### 1. Enhanced User Experience
- **Immediate Comprehension**: Users can instantly understand value scales
- **Reduced Cognitive Load**: No need to count digits or calculate magnitudes
- **Consistent Presentation**: Uniform formatting across all application areas

### 2. Financial Accuracy
- **Preserved Precision**: 2 decimal places maintain financial accuracy
- **Appropriate Scaling**: Values are displayed at meaningful scales
- **Error Handling**: Graceful handling of edge cases and invalid data

### 3. International Readiness
- **Clear Currency Identification**: VND suffix provides context
- **Standard Abbreviations**: K, M, B, T conventions are internationally recognized
- **Flexible Architecture**: Easy to extend for other currencies or regions

### 4. Development Efficiency
- **Centralized Logic**: Single function handles all formatting needs
- **Consistent Behavior**: Uniform formatting across all modules
- **Easy Maintenance**: Changes to formatting logic propagate automatically

