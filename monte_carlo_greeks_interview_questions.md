# Monte Carlo Greeks Implementation - Interview Questions

## Overview
This question assesses the candidate's ability to implement Greeks calculations using Monte Carlo methods. The candidate should demonstrate understanding of numerical differentiation, simulation techniques, and performance optimization for derivatives risk management.

---

## Question 1: Basic Monte Carlo Delta Implementation
**Difficulty: Medium**

Looking at the existing `monte_carlo_option_pricing_basic` function in the codebase, implement a Monte Carlo method to calculate **Delta** (∂V/∂S) for a European option.

**Requirements:**
- Use finite difference approximation with a small bump in spot price (e.g., 1% or $1)
- Compare computational efficiency vs analytical Black-Scholes delta
- Handle both call and put options

**Follow-up:** How would you choose the optimal bump size? What are the trade-offs between accuracy and numerical stability?

---

## Solution

```python
import numpy as np
import math
import time
from scipy.stats import norm

def monte_carlo_delta(S, K, T, r, sigma, n_simulations=100000, option_type='call', bump_size=1.0):
    """
    Calculate Delta using Monte Carlo simulation with finite difference method.
    
    Parameters:
    S: Current stock price
    K: Strike price
    T: Time to maturity
    r: Risk-free rate
    sigma: Volatility
    n_simulations: Number of Monte Carlo simulations
    option_type: 'call' or 'put'
    bump_size: Size of spot price bump for finite difference
    
    Returns:
    dict: Contains delta, option prices, and computation time
    """
    np.random.seed(42)  # For reproducible results
    
    start_time = time.time()
    
    # Generate common random numbers for variance reduction
    dW = np.random.normal(0, math.sqrt(T), n_simulations)
    
    # Calculate option prices for S, S+h, and S-h using same random paths
    S_up = S + bump_size
    S_down = S - bump_size
    
    # Stock prices at maturity for each scenario
    ST_base = S * np.exp((r - 0.5 * sigma**2) * T + sigma * dW)
    ST_up = S_up * np.exp((r - 0.5 * sigma**2) * T + sigma * dW)
    ST_down = S_down * np.exp((r - 0.5 * sigma**2) * T + sigma * dW)
    
    # Calculate payoffs
    if option_type == 'call':
        payoffs_base = np.maximum(ST_base - K, 0)
        payoffs_up = np.maximum(ST_up - K, 0)
        payoffs_down = np.maximum(ST_down - K, 0)
    else:  # put
        payoffs_base = np.maximum(K - ST_base, 0)
        payoffs_up = np.maximum(K - ST_up, 0)
        payoffs_down = np.maximum(K - ST_down, 0)
    
    # Discount to present value
    discount_factor = math.exp(-r * T)
    price_base = discount_factor * np.mean(payoffs_base)
    price_up = discount_factor * np.mean(payoffs_up)
    price_down = discount_factor * np.mean(payoffs_down)
    
    # Calculate delta using central difference
    delta_central = (price_up - price_down) / (2 * bump_size)
    
    # Alternative: forward difference (less accurate but sometimes used)
    delta_forward = (price_up - price_base) / bump_size
    
    computation_time = time.time() - start_time
    
    return {
        'delta_central': delta_central,
        'delta_forward': delta_forward,
        'price_base': price_base,
        'price_up': price_up,
        'price_down': price_down,
        'computation_time': computation_time,
        'n_simulations': n_simulations
    }

def analytical_delta(S, K, T, r, sigma, option_type='call'):
    """
    Calculate analytical Delta using Black-Scholes formula for comparison.
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    
    if option_type == 'call':
        return norm.cdf(d1)
    else:  # put
        return norm.cdf(d1) - 1

def compare_delta_methods():
    """
    Compare Monte Carlo delta with analytical delta.
    """
    # Test parameters
    S = 100.0
    K = 105.0
    T = 0.25
    r = 0.05
    sigma = 0.2
    option_type = 'call'
    
    print("=== Delta Calculation Comparison ===")
    print(f"Parameters: S=${S}, K=${K}, T={T}, r={r}, σ={sigma}")
    print(f"Option type: {option_type}")
    print()
    
    # Analytical delta
    analytical = analytical_delta(S, K, T, r, sigma, option_type)
    print(f"Analytical Delta: {analytical:.6f}")
    
    # Test different simulation sizes
    simulation_sizes = [10000, 50000, 100000, 500000]
    bump_sizes = [0.01, 0.1, 1.0]
    
    print("\nMonte Carlo Delta Results:")
    print("Simulations | Bump Size | Delta (Central) | Delta (Forward) | Error (Central) | Time (s)")
    print("-" * 85)
    
    for n_sims in simulation_sizes:
        for bump in bump_sizes:
            mc_result = monte_carlo_delta(S, K, T, r, sigma, n_sims, option_type, bump)
            error_central = abs(mc_result['delta_central'] - analytical)
            
            print(f"{n_sims:>10} | {bump:>8} | {mc_result['delta_central']:>14.6f} | "
                  f"{mc_result['delta_forward']:>14.6f} | {error_central:>14.6f} | "
                  f"{mc_result['computation_time']:>8.4f}")
    
    # Test convergence with different bump sizes
    print(f"\n=== Bump Size Analysis (100k simulations) ===")
    bump_range = [0.001, 0.01, 0.1, 1.0, 5.0, 10.0]
    
    for bump in bump_range:
        mc_result = monte_carlo_delta(S, K, T, r, sigma, 100000, option_type, bump)
        error = abs(mc_result['delta_central'] - analytical)
        print(f"Bump: {bump:>6.3f} | Delta: {mc_result['delta_central']:>8.6f} | "
              f"Error: {error:>8.6f}")

if __name__ == "__main__":
    compare_delta_methods()
```

## Key Implementation Points

### 1. **Finite Difference Method**
- Uses central difference: `Δ = (V(S+h) - V(S-h)) / (2h)`
- More accurate than forward difference: `Δ = (V(S+h) - V(S)) / h`

### 2. **Variance Reduction**
- Uses same random paths for all price scenarios
- Significantly reduces Monte Carlo error
- Critical for accurate Greeks calculation

### 3. **Bump Size Selection**
- Too small: numerical precision errors
- Too large: discretization errors
- Optimal range typically 0.1% to 1% of spot price

### 4. **Performance Considerations**
- Vectorized numpy operations
- Single random number generation
- Reused calculations across scenarios

## Expected Discussion Points

1. **Accuracy vs Efficiency Trade-off**
2. **Optimal bump size selection**
3. **Variance reduction techniques**
4. **Comparison with analytical methods**
5. **Extension to other Greeks**