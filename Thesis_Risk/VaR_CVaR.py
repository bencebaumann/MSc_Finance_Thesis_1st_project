import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
import os
import configparser

# === Load configuration from config.ini ===
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Load configuration
config = load_config('config.ini')

# Retrieve paths from the configuration file
local_dir_base = config['Paths']['local_dir_base']
price_path = os.path.join(local_dir_base, config['Paths']['price_file'])

output_path = local_dir_base + 'Thesis_Risk/VaR_CVaR/'  # Output directory for saved files
confidence_level = 0.975  # Confidence level for VaR and CVaR
lookback_q = 4  # Number of quarters to look back for VaR calculation

# Ensure output directory exists
os.makedirs(output_path, exist_ok=True)

# VaR function assuming normally distributed returns (parametric approach)
def calculate_var(returns, confidence_level=0.975):
    """
    Calculate the Value at Risk (VaR) assuming normally distributed returns.
    """
    mean_val = returns.mean()
    std_val = returns.std(ddof=1)
    var = norm.ppf(1 - confidence_level, loc=mean_val, scale=std_val)
    return var


# CVaR function for normally distributed returns
def calculate_cvar(returns, confidence_level=0.975):
    """
    Calculate the Conditional Value at Risk (CVaR) using the Normal assumptions.
    """
    mean_val = returns.mean()
    std_val = returns.std(ddof=1)
    alpha = 1 - confidence_level  # tail probability, e.g., 0.025 for 97.5% confidence
    z = norm.ppf(alpha)
    pdf_z = norm.pdf(z)
    cvar = mean_val - std_val * (pdf_z / alpha)
    return cvar


# Read the data from the Excel file
df = pd.read_excel(price_path)
df['time'] = pd.to_datetime(df['time'])

# Create new date-related columns: year, month, and quarter
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['quarter'] = df['time'].dt.quarter

# Calculate returns based on the 'close' column
df['long_return'] = df['close'].pct_change()
df['short_return'] = -df['close'].pct_change()

# Create quarter identifiers for lookback calculation
df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
df['date_index'] = pd.to_datetime(df['year'].astype(str) + '-' +
                                  ((df['quarter'] * 3) - 2).astype(str) + '-01')

# Sort by date
df = df.sort_values('time')

# Save the basis data to Excel
df.to_excel(output_path + 'basis.xlsx', index=False)

# Group data by year and quarter to prepare for lookback analysis
results = []
grouped = df.groupby(['year', 'quarter'])

for (year, quarter), group in grouped:
    # Current quarter identifier
    current_yq = f"{year}-Q{quarter}"

    # Get the current quarter's end date
    current_date = group['time'].max()

    # Filter data for the lookback period (current quarter and previous lookback_q-1 quarters)
    lookback_data = df[df['time'] <= current_date].tail(lookback_q * len(group))

    # Extract returns for risk calculation
    long_returns = lookback_data['long_return'].dropna()
    short_returns = lookback_data['short_return'].dropna()

    # Skip if not enough data
    if len(long_returns) < 20:  # Minimum sample size
        continue

    # Basic statistics
    n = len(long_returns)
    std_s = long_returns.std(ddof=1)
    mean_val = long_returns.mean()

    # Compute risk metrics
    long_var = calculate_var(long_returns, confidence_level)
    short_var = calculate_var(short_returns, confidence_level)
    long_cvar = calculate_cvar(long_returns, confidence_level)
    short_cvar = calculate_cvar(short_returns, confidence_level)

    # Store results
    results.append({
        'year': year,
        'quarter': quarter,
        'n': n,
        'std.s': std_s,
        'mean': mean_val,
        'long_var': long_var,
        'short_var': short_var,
        'long_cvar': long_cvar,
        'short_cvar': short_cvar,
        'year_quarter': current_yq,
        'plot_date': pd.to_datetime(f"{year}-{3 * quarter - 2}-15")  # Mid-quarter date for plotting
    })

# Create a results DataFrame and order columns
results_df = pd.DataFrame(results)
results_df = results_df[['year', 'quarter', 'plot_date', 'n', 'std.s', 'mean',
                         'long_var', 'short_var', 'long_cvar', 'short_cvar']]

# Add the VaR spread
results_df['var_spread'] = results_df['long_var'] - results_df['short_var']

# Calculate the absolute ratio: ABS(var_spread) / ABS(mean)
results_df['abs_ratio'] = results_df['var_spread'].abs() / results_df['mean'].abs()

# Sort by date for plotting
results_df = results_df.sort_values('plot_date')

# Save the results to Excel
results_df.to_excel(output_path + 'result.xlsx', index=False)

# Print the abs_ratio for verification
print("VaR spread to mean ratio by quarter:")
print(results_df[['year', 'quarter', 'abs_ratio']])

# Get the dummy variable from the original data
# Merge with results_df based on year and quarter
dummy_data = df[['year', 'quarter', 'Dummy']].drop_duplicates()
dummy_data = dummy_data.sort_values(['year', 'quarter'])
results_df = pd.merge(results_df, dummy_data, on=['year', 'quarter'], how='left')
results_df['Dummy'] = results_df['Dummy'].fillna(0)

# First Plot: Risk Metrics Over Time (VaR and CVaR)
plt.figure(figsize=(12, 8))
plt.plot(results_df['plot_date'], results_df['long_var'], marker='o', label='Long VaR', linewidth=2)
plt.plot(results_df['plot_date'], results_df['short_var'], marker='o', label='Short VaR', linewidth=2)
plt.plot(results_df['plot_date'], results_df['long_cvar'], marker='o', label='Long CVaR', linewidth=2)
plt.plot(results_df['plot_date'], results_df['short_cvar'], marker='o', label='Short CVaR', linewidth=2)

# Use the exact date when dummy turns to 1
dummy_change_date = pd.to_datetime('2022-02-24')  # The exact date from your data

# Then when plotting the vertical line
plt.axvline(x=dummy_change_date, color='red', linestyle='-', linewidth=2,
           label='Dummy = 1')

plt.xlabel('Idő', fontsize=12)
plt.ylabel('Várható veszteség alpha = 97.5%', fontsize=12)
plt.title('VaR és CVaR (lookback = 1y)', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True)
plt.gca().invert_yaxis()  # Invert Y-axis as requested
plt.tight_layout()
plt.savefig(output_path + 'risk_metrics_over_time.png')
plt.show()

# Second Plot: VaR Spread and Mean Return Over Time
plt.figure(figsize=(12, 8))
plt.plot(results_df['plot_date'], results_df['var_spread'], marker='o', label='VaR Spread (Long - Short)', linewidth=2)
plt.plot(results_df['plot_date'], results_df['mean'], marker='o', label='Mean Return', linewidth=2)

# Draw a horizontal thick black line at Y = 0
plt.axhline(y=0, color='black', linestyle='-', linewidth=3,
           label='Y = 0')

plt.xlabel('Idő', fontsize=12)
plt.ylabel('Hányad', fontsize=12)
plt.title('long short VaR spread és az átlagos hozam', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True)
plt.gca().invert_yaxis()  # Invert Y-axis as requested
plt.tight_layout()
plt.savefig(output_path + 'var_spread_and_mean.png')
plt.show()