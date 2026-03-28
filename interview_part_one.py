"""
INTERVIEW PART ONE
========================================================
"""

import pandas as pd
import numpy as np
import datetime as dt
import time
import pytz
from typing import List, Dict, Optional
from sqlalchemy import create_engine, text

def process_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process market data and add derived columns"""
    print("Processing market data...")
    
    processed_data = []
    for index, row in df.iterrows():
        if row['price'] > 100:
            new_row = row.copy()
            new_row['price_category'] = 'High'
            new_row['adjusted_price'] = row['price'] * 1.1
        else:
            new_row = row.copy()
            new_row['price_category'] = 'Low'
            new_row['adjusted_price'] = row['price'] * 0.9
        
        processed_data.append(new_row)
    
    result_df = pd.DataFrame(processed_data)
    copy1 = result_df.copy()
    copy2 = copy1.copy()
    copy3 = copy2.copy()
    
    return copy3



def calculate_regional_stats(large_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate statistics by region"""
    df1 = large_df.copy()
    df2 = large_df.copy() 
    df3 = large_df.copy()
    df4 = large_df.copy()
    
    result1 = df1.groupby('region')['price'].mean()
    result2 = df2.groupby('region')['price'].std()
    result3 = df3.groupby('region')['volume'].sum()
    result4 = df4.groupby('region')['volume'].mean()
    
    combined = pd.DataFrame()
    combined['avg_price'] = result1
    combined['std_price'] = result2
    combined['total_volume'] = result3
    combined['avg_volume'] = result4
    
    return combined

def handle_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Handle timestamp conversions"""
    df['timestamp_utc'] = pd.to_datetime(df['date']).dt.tz_localize('UTC')
    df['timestamp_local'] = pd.to_datetime(df['date'])
    
    try:
        df['time_diff'] = df['timestamp_utc'] - df['timestamp_local']
    except TypeError as e:
        print(f"Timezone error: {e}")
        df['time_diff'] = pd.NaT
    
    return df

def filter_and_enrich_data(df: pd.DataFrame, regions: List[str]) -> pd.DataFrame:
    """Filter data by regions and add enrichment"""
    result_data = []
    
    for region in regions:
        for index, row in df.iterrows():
            if row['region'] == region:
                filtered_df = df[df['region'] == region]
                avg_price = filtered_df['price'].mean()
                
                new_row = {
                    'region': region,
                    'date': row['date'],
                    'price': row['price'],
                    'regional_avg': avg_price,
                    'price_vs_avg': row['price'] - avg_price
                }
                result_data.append(new_row)
    
    return pd.DataFrame(result_data)

def save_to_database(engine, df: pd.DataFrame, schema: str):
    """Save data to database"""
    for index, row in df.iterrows():
        query = f"""
        INSERT INTO {schema}.ce_gas (date, price, volume, region)
        VALUES ('{row['date']}', {row['price']}, {row['volume']}, '{row['region']}')
        """
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()

def format_region_data(df: pd.DataFrame) -> pd.DataFrame:
    """Format region information"""
    df['region_upper'] = df['region'].apply(lambda x: x.upper())
    df['region_formatted'] = df['region'].apply(lambda x: f"Region_{x}")
    
    for idx in df.index:
        if df.loc[idx, 'region'] == 'NWE':
            df.loc[idx, 'region_code'] = 'NW001'
        elif df.loc[idx, 'region'] == 'Asia':
            df.loc[idx, 'region_code'] = 'AS001'
        else:
            df.loc[idx, 'region_code'] = 'OT001'
    
    return df

def parse_date_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date strings to datetime objects"""
    dates = []
    for date_str in df['date_string']:
        try:
            parsed_date = dt.datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(parsed_date)
        except:
            dates.append(None)
    
    df['parsed_date'] = dates
    
    df['date_cet'] = df['parsed_date'].apply(
        lambda x: pytz.timezone('CET').localize(x) if x else None
    )
    
    return df

def calculate_correlations(df: pd.DataFrame, regions: List[str]) -> Dict:
    """Calculate price correlations between regions"""
    correlations = {}
    
    for region1 in regions:
        correlations[region1] = {}
        for region2 in regions:
            data1 = []
            data2 = []
            
            for idx, row in df.iterrows():
                if row['region'] == region1:
                    data1.append(row['price'])
                if row['region'] == region2:
                    data2.append(row['price'])
            
            if len(data1) > 0 and len(data2) > 0:
                correlations[region1][region2] = np.corrcoef(data1, data2)[0,1]
    
    return correlations
