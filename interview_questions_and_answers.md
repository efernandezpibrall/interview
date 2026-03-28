# Python Interview Questions & Answers - Quantitative Developer


## Phase 2: Vectorization & Performance (8-10 minutes)

### Question 2.1: Iterrows Performance Issue
**Q:** Analyze the `process_market_data()` function. What's the main performance issue?

**A:**
- Using `iterrows()` is extremely slow - 100x+ slower than vectorized operations
- **Fixed version:**
```python
def process_market_data_fixed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['price_category'] = np.where(df['price'] > 100, 'High', 'Low')
    df['adjusted_price'] = np.where(df['price'] > 100, df['price'] * 1.1, df['price'] * 0.9)
    return df
```

### Question 2.2: Memory Inefficiency
**Q:** What's inefficient about the `calculate_regional_stats()` function?

**A:**
- Creates 4 unnecessary DataFrame copies
- Performs 4 separate groupby operations
- **Fixed version:**
```python
def calculate_regional_stats_fixed(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('region').agg({
        'price': ['mean', 'std'],
        'volume': ['sum', 'mean']
    }).round(2)
```

### Question 2.3: String Operations
**Q:** How would you optimize the `format_region_data()` function?

**A:**
- Use vectorized string operations instead of `apply()`
- Use `np.select()` for conditional logic
- **Fixed version:**
```python
def format_region_data_fixed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['region_upper'] = df['region'].str.upper()
    df['region_formatted'] = 'Region_' + df['region']
    
    conditions = [df['region'] == 'NWE', df['region'] == 'Asia']
    choices = ['NW001', 'AS001']
    df['region_code'] = np.select(conditions, choices, default='OT001')
    return df
```

## Phase 3: Debugging & Error Handling (8-10 minutes)

### Question 3.1: Timezone Handling
**Q:** What's the issue in `handle_timestamps()` and how do you fix it?

**A:**
- Mixing timezone-aware and timezone-naive datetimes causes TypeError
- **Problem:** Cannot subtract timezone-aware from timezone-naive
- **Fix:** Ensure both timestamps have consistent timezone handling
```python
def handle_timestamps_fixed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['timestamp_utc'] = pd.to_datetime(df['date']).dt.tz_localize('UTC')
    df['timestamp_local'] = pd.to_datetime(df['date']).dt.tz_localize('UTC').dt.tz_convert('CET')
    df['time_diff'] = df['timestamp_utc'] - df['timestamp_local']
    return df
```


### Question 3.3: Database Operations
**Q:** What are the critical issues in `save_to_database()`?

**A:**
- Row-by-row INSERT is extremely slow
- No transaction management
- No error handling
- SQL injection vulnerability
- **Fixed version:**
```python
def save_to_database_fixed(engine, df: pd.DataFrame, schema: str):
    try:
        df.to_sql('ce_gas', engine, schema=schema, if_exists='append', 
                 index=False, chunksize=10000)
    except Exception as e:
        logger.error(f"Database write failed: {e}")
        raise
```

### Question 3.4: Nested Loop Performance
**Q:** Why is `filter_and_enrich_data()` so slow?

**A:**
- Nested loops with repeated DataFrame filtering
- Inefficient data extraction
- **Fixed version:**
```python
def filter_and_enrich_data_fixed(df: pd.DataFrame, regions: List[str]) -> pd.DataFrame:
    filtered_df = df[df['region'].isin(regions)]
    regional_avgs = filtered_df.groupby('region')['price'].mean()
    
    result = filtered_df.copy()
    result['regional_avg'] = result['region'].map(regional_avgs)
    result['price_vs_avg'] = result['price'] - result['regional_avg']
    
    return result
```

### Question 3.5: Correlation Calculation
**Q:** How would you optimize `calculate_correlations()`?

**A:**
- Use pandas pivot and corr() methods
- Avoid nested loops and manual data extraction
- **Fixed version:**
```python
def calculate_correlations_fixed(df: pd.DataFrame, regions: List[str]) -> pd.DataFrame:
    pivot_data = df.pivot_table(index='date', columns='region', values='price', aggfunc='mean')
    return pivot_data[regions].corr()
```