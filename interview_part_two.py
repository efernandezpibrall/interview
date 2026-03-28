"""
OPTIONS PRICING INTERVIEW - QUANTITATIVE DEVELOPER
================================================

Based on real options trading and valuation pipeline.
Tests understanding of options theory, numerical methods, and performance optimization.
"""

import pandas as pd
import numpy as np
import math
import time
from scipy.stats import norm
from typing import Dict, List, Tuple, Optional

def black_scholes_basic(S, K, T, r, sigma, option_type='call'):
    """
    Basic Black-Scholes option pricing implementation
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = -norm.cdf(-d1)
    
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2)
    vega = S * norm.pdf(d1) * math.sqrt(T)
    
    return {
        'price': price,
        'delta': delta, 
        'gamma': gamma,
        'theta': theta,
        'vega': vega
    }

def newton_raphson_ivol(market_price, S, K, T, r, option_type='call', max_iterations=50):
    """
    Implied volatility calculation using Newton-Raphson method
    """
    # Initial guess
    sigma = 0.2
    
    for i in range(max_iterations):
        bs_result = black_scholes_basic(S, K, T, r, sigma, option_type)
        
        price_diff = bs_result['price'] - market_price
        vega = bs_result['vega']
        
        if abs(price_diff) < 1e-6 or vega == 0:
            return sigma
            
        # Newton-Raphson step
        sigma = sigma - price_diff / vega
        
        if sigma <= 0:
            sigma = 0.001
    
    return sigma

def kirk_spread_option_slow(S1, S2, K, sigma1, sigma2, rho, T, option_type='call'):
    """
    Kirk approximation for spread options - inefficient implementation
    """
    # Calculate effective volatility
    F2_plus_K = S2 + K
    beta = S2 / F2_plus_K
    
    sigma_eff_squared = sigma1**2 + (beta * sigma2)**2 - 2 * rho * sigma1 * beta * sigma2
    sigma_eff = math.sqrt(sigma_eff_squared)
    
    # Calculate d1 and d2
    d1 = math.log(S1 / F2_plus_K) / (sigma_eff * math.sqrt(T)) + 0.5 * sigma_eff * math.sqrt(T)
    d2 = d1 - sigma_eff * math.sqrt(T)
    
    if option_type == 'call':
        price = S1 * norm.cdf(d1) - F2_plus_K * norm.cdf(d2)
    else:
        price = F2_plus_K * norm.cdf(-d2) - S1 * norm.cdf(-d1)
    
    return price

def process_options_portfolio(options_data):
    """
    Process a portfolio of options with performance issues
    """
    results = []
    
    # Performance issue: Processing one by one instead of vectorization
    for index, option in options_data.iterrows():
        if option['model'] == 'black_scholes':
            result = black_scholes_basic(
                option['spot'], option['strike'], option['time_to_expiry'],
                option['rate'], option['volatility'], option['option_type']
            )
        elif option['model'] == 'kirk':
            result = {'price': kirk_spread_option_slow(
                option['S1'], option['S2'], option['strike'], 
                option['vol1'], option['vol2'], option['correlation'],
                option['time_to_expiry'], option['option_type']
            )}
        
        # Create a copy for each result (memory inefficient)
        option_copy = option.copy()
        option_copy.update(result)
        results.append(option_copy)
    
    return pd.DataFrame(results)

def calculate_portfolio_greeks_inefficient(portfolio_df):
    """
    Calculate portfolio Greeks with performance issues
    """
    portfolio_greeks = {
        'total_delta': 0,
        'total_gamma': 0,
        'total_vega': 0,
        'total_theta': 0
    }
    
    # Inefficient: Looping through DataFrame rows
    for idx, row in portfolio_df.iterrows():
        if 'delta' in row:
            portfolio_greeks['total_delta'] += row['quantity'] * row['delta']
        if 'gamma' in row:
            portfolio_greeks['total_gamma'] += row['quantity'] * row['gamma']
        if 'vega' in row:
            portfolio_greeks['total_vega'] += row['quantity'] * row['vega']
        if 'theta' in row:
            portfolio_greeks['total_theta'] += row['quantity'] * row['theta']
    
    return portfolio_greeks

def volatility_surface_interpolation_basic(vol_data, target_strike, target_expiry):
    """
    Basic volatility surface interpolation - no error handling
    """
    # Find closest points (no bounds checking)
    strikes = sorted(vol_data['strike'].unique())
    expiries = sorted(vol_data['expiry'].unique())
    
    # Linear interpolation without boundary checks
    strike_idx = 0
    for i, strike in enumerate(strikes):
        if strike >= target_strike:
            strike_idx = i
            break
    
    expiry_idx = 0
    for i, expiry in enumerate(expiries):
        if expiry >= target_expiry:
            expiry_idx = i
            break
    
    # Get four corner points for bilinear interpolation
    s1, s2 = strikes[strike_idx-1], strikes[strike_idx]
    t1, t2 = expiries[expiry_idx-1], expiries[expiry_idx]
    
    vol_11 = vol_data[(vol_data['strike'] == s1) & (vol_data['expiry'] == t1)]['volatility'].iloc[0]
    vol_12 = vol_data[(vol_data['strike'] == s1) & (vol_data['expiry'] == t2)]['volatility'].iloc[0]
    vol_21 = vol_data[(vol_data['strike'] == s2) & (vol_data['expiry'] == t1)]['volatility'].iloc[0]
    vol_22 = vol_data[(vol_data['strike'] == s2) & (vol_data['expiry'] == t2)]['volatility'].iloc[0]
    
    # Bilinear interpolation
    w1 = (s2 - target_strike) / (s2 - s1)
    w2 = (target_strike - s1) / (s2 - s1)
    
    vol_t1 = w1 * vol_11 + w2 * vol_21
    vol_t2 = w1 * vol_12 + w2 * vol_22
    
    w3 = (t2 - target_expiry) / (t2 - t1)
    w4 = (target_expiry - t1) / (t2 - t1)
    
    interpolated_vol = w3 * vol_t1 + w4 * vol_t2
    
    return interpolated_vol

def monte_carlo_option_pricing_basic(S, K, T, r, sigma, n_simulations=10000, option_type='call'):
    """
    Monte Carlo option pricing - basic implementation
    """
    np.random.seed(42)
    
    # Generate random paths
    dt = T
    dW = np.random.normal(0, math.sqrt(dt), n_simulations)
    
    # Final stock prices
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * dW)
    
    # Calculate payoffs
    if option_type == 'call':
        payoffs = np.maximum(ST - K, 0)
    else:
        payoffs = np.maximum(K - ST, 0)
    
    # Discount to present value
    option_price = math.exp(-r * T) * np.mean(payoffs)
    
    return option_price

def risk_management_var_calculation(portfolio_returns, confidence_level=0.05):
    """
    Value at Risk calculation with basic implementation
    """
    # Sort returns
    sorted_returns = sorted(portfolio_returns)
    
    # Calculate VaR
    var_index = int(confidence_level * len(sorted_returns))
    var = abs(sorted_returns[var_index])
    
    # Calculate Expected Shortfall (CVaR)
    tail_returns = sorted_returns[:var_index]
    expected_shortfall = abs(np.mean(tail_returns))
    
    return {
        'VaR_95': var,
        'Expected_Shortfall': expected_shortfall,
        'Max_Loss': abs(min(sorted_returns))
    }

def main_options_analysis():
    """
    Main function demonstrating options pricing and risk analysis
    """
    print("Starting options pricing analysis...")
    
    # Create sample options portfolio
    options_data = pd.DataFrame({
        'option_id': range(1, 1001),
        'model': ['black_scholes'] * 500 + ['kirk'] * 500,
        'spot': np.random.uniform(90, 110, 1000),
        'strike': np.random.uniform(95, 105, 1000),
        'time_to_expiry': np.random.uniform(0.1, 2.0, 1000),
        'rate': [0.05] * 1000,
        'volatility': np.random.uniform(0.15, 0.35, 1000),
        'option_type': np.random.choice(['call', 'put'], 1000),
        'quantity': np.random.randint(-100, 100, 1000),
        'S1': np.random.uniform(90, 110, 1000),
        'S2': np.random.uniform(85, 105, 1000),
        'vol1': np.random.uniform(0.2, 0.4, 1000),
        'vol2': np.random.uniform(0.18, 0.38, 1000),
        'correlation': np.random.uniform(0.3, 0.8, 1000)
    })
    
    print(f"Portfolio size: {len(options_data)} options")
    
    # Phase 1: Option Pricing
    print("\n=== PHASE 1: OPTION PRICING ===")
    
    # Test Black-Scholes pricing
    print("Testing Black-Scholes pricing...")
    bs_example = black_scholes_basic(100, 105, 0.25, 0.05, 0.2, 'call')
    print(f"Call option price: ${bs_example['price']:.4f}")
    print(f"Delta: {bs_example['delta']:.4f}")
    
    # Test implied volatility
    print("Testing implied volatility calculation...")
    market_price = 3.5
    start_time = time.time()
    implied_vol = newton_raphson_ivol(market_price, 100, 105, 0.25, 0.05, 'call')
    print(f"Implied volatility: {implied_vol:.4f} ({time.time() - start_time:.4f} seconds)")
    
    # Phase 2: Portfolio Processing
    print("\n=== PHASE 2: PORTFOLIO PROCESSING ===")
    
    print("Processing options portfolio...")
    start_time = time.time()
    portfolio_results = process_options_portfolio(options_data.head(100))  # Only first 100 for speed
    print(f"Portfolio processing took: {time.time() - start_time:.4f} seconds")
    
    # Phase 3: Greeks Calculation
    print("\n=== PHASE 3: GREEKS CALCULATION ===")
    
    print("Calculating portfolio Greeks...")
    start_time = time.time()
    portfolio_greeks = calculate_portfolio_greeks_inefficient(portfolio_results)
    print(f"Greeks calculation took: {time.time() - start_time:.4f} seconds")
    print(f"Portfolio Greeks: {portfolio_greeks}")
    
    # Phase 4: Volatility Surface
    print("\n=== PHASE 4: VOLATILITY SURFACE ===")
    
    # Create sample volatility surface data
    vol_surface_data = pd.DataFrame({
        'strike': [95, 95, 95, 100, 100, 100, 105, 105, 105],
        'expiry': [0.25, 0.5, 1.0, 0.25, 0.5, 1.0, 0.25, 0.5, 1.0],
        'volatility': [0.22, 0.21, 0.20, 0.20, 0.19, 0.18, 0.23, 0.22, 0.21]
    })
    
    print("Testing volatility interpolation...")
    try:
        interpolated_vol = volatility_surface_interpolation_basic(vol_surface_data, 102, 0.75)
        print(f"Interpolated volatility: {interpolated_vol:.4f}")
    except Exception as e:
        print(f"Volatility interpolation failed: {e}")
    
    # Phase 5: Monte Carlo Pricing
    print("\n=== PHASE 5: MONTE CARLO PRICING ===")
    
    print("Testing Monte Carlo option pricing...")
    start_time = time.time()
    mc_price = monte_carlo_option_pricing_basic(100, 105, 0.25, 0.05, 0.2, 10000, 'call')
    print(f"Monte Carlo price: ${mc_price:.4f} ({time.time() - start_time:.4f} seconds)")
    
    # Phase 6: Risk Management
    print("\n=== PHASE 6: RISK MANAGEMENT ===")
    
    # Generate sample portfolio returns
    portfolio_returns = np.random.normal(0.001, 0.02, 1000)  # Daily returns
    
    print("Calculating Value at Risk...")
    var_results = risk_management_var_calculation(portfolio_returns)
    print(f"Portfolio VaR (95%): {var_results['VaR_95']:.4f}")
    print(f"Expected Shortfall: {var_results['Expected_Shortfall']:.4f}")
    
    print("\nOptions analysis complete!")
    return {
        'portfolio_results': portfolio_results,
        'portfolio_greeks': portfolio_greeks,
        'var_results': var_results
    }

if __name__ == "__main__":
    results = main_options_analysis()