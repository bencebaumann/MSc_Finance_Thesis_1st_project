import os
import configparser
import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

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


output_path = os.path.join(local_dir_base, 'Thesis_Risk/Vizualizációk/')
print(output_path)

# Hardcoded parameter
confidence_level = 0.975  # Confidence level for VaR and CVaR


# Ensure the output directory exists
os.makedirs(output_path, exist_ok=True)

# Define major events with labels, colors, and descriptions in Hungarian
major_events = {
    '2022-02-24': {
        'label': 'Ukrajna invázió',
        'color': 'darkred',
        'description': 'Ukrajna invázió kezdete\n(azonnali ellátási félelmek)'
    },
    '2022-03-15': {
        'label': 'Szankciók',
        'color': 'darkorange',
        'description': 'Szankciók bejelentése\n(gázellátási bizonytalanság)'
    },
    '2022-09-26': {
        'label': 'Nord Stream',
        'color': 'purple',
        'description': 'Nord Stream szabotázs\n(akut ellátási válság)'
    }
}

# VaR and CVaR functions assuming normally distributed returns
def calculate_var(returns, confidence_level=0.975):
    mean_val = returns.mean()
    std_val = returns.std(ddof=1)
    return norm.ppf(1 - confidence_level, loc=mean_val, scale=std_val)

def calculate_cvar(returns, confidence_level=0.975):
    mean_val = returns.mean()
    std_val = returns.std(ddof=1)
    alpha = 1 - confidence_level  # tail probability (e.g., 0.025)
    z = norm.ppf(alpha)
    return mean_val - std_val * (norm.pdf(z) / alpha)

# Read data from the Excel file
df = pd.read_excel(price_path)
df['time'] = pd.to_datetime(df['time'])

# Create date-related columns
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['quarter'] = df['time'].dt.quarter

# Calculate returns based on the 'close' column
df['long_return'] = df['close'].pct_change()
df['short_return'] = -df['close'].pct_change()

# Group data by year and quarter to calculate statistics and risk metrics
results = []
grouped = df.groupby(['year', 'quarter'])
for (year, quarter), group in grouped:
    long_returns = group['long_return'].dropna()
    short_returns = group['short_return'].dropna()

    n = len(long_returns)
    std_s = long_returns.std(ddof=1)
    mean_val = long_returns.mean()

    long_var = calculate_var(long_returns, confidence_level)
    short_var = calculate_var(short_returns, confidence_level)
    long_cvar = calculate_cvar(long_returns, confidence_level)
    short_cvar = calculate_cvar(short_returns, confidence_level)

    results.append({
        'year': year,
        'quarter': quarter,
        'n': n,
        'std.s': std_s,
        'mean': mean_val,
        'long_var': long_var,
        'short_var': short_var,
        'long_cvar': long_cvar,
        'short_cvar': short_cvar
    })

results_df = pd.DataFrame(results)
results_df = results_df[['year', 'quarter', 'n', 'std.s', 'mean', 'long_var', 'short_var', 'long_cvar', 'short_cvar']]


# Create a plot_date column by mapping each quarter to a mid-quarter month
quarter_to_month = {1: 2, 2: 5, 3: 8, 4: 11}
results_df['plot_date'] = pd.to_datetime(
    results_df['year'].astype(str) + '-' +
    results_df['quarter'].map(quarter_to_month).astype(str) + '-01'
)
results_df.sort_values('plot_date', inplace=True)

# ------------------------------
# First Plot: Risk Metrics Over Time with modifications
# ------------------------------

plt.figure(figsize=(10, 6))
plt.plot(results_df['plot_date'], results_df['long_var'], marker='o', label='long VaR')
plt.plot(results_df['plot_date'], results_df['short_var'], marker='o', label='short VaR')
plt.plot(results_df['plot_date'], results_df['long_cvar'], marker='o', label='long CVaR')
plt.plot(results_df['plot_date'], results_df['short_cvar'], marker='o', label='short CVaR')

# Retrieve current axis object and get the y-limits
ax = plt.gca()
ymin, ymax = ax.get_ylim()
# Choose a y-position for event annotations (e.g. near the bottom of the current range)
annotation_y = ymin + 0.05 * (ymax - ymin)

# Add vertical markers and annotations for each major event
for event_date_str, event in major_events.items():
    event_date = pd.to_datetime(event_date_str)
    ax.axvline(x=event_date, color=event['color'], linestyle='--', linewidth=1)

# Update plot labels in Hungarian
plt.xlabel('Idő')
plt.ylabel('Kockázati mutató')
plt.title('VaR és CVaR idősor')
plt.legend()
plt.grid(True)

# Flip the y-axis so that more negative values are plotted upward
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(output_path + 'risk_metrics_over_time_modified.png')
plt.show()
