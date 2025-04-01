# Import necessary packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define file paths
local_dir_base = 'amendme'
file_path = local_dir_base + 'Thesis_Risk/prices.xlsx'
cost_of_carry_file = 'cost_of_carry.csv'

# Create directory for saving results if not exists
save_dir = local_dir_base + 'Thesis_Risk/Descriptive_Statistics'
os.makedirs(save_dir, exist_ok=True)

# Read and prepare data
data = pd.read_excel(file_path)
data['time'] = pd.to_datetime(data['time'])
data['year'] = data['time'].dt.year

# Read cost of carry data
carry_data = pd.read_csv(cost_of_carry_file, sep=';')
carry_data['time'] = pd.to_datetime(carry_data['time'], format='%d/%m/%Y')

# Create a dictionary mapping dates to rates for efficient lookup
date_to_rate = {}
for _, row in carry_data.sort_values('time').iterrows():
    date_to_rate[row['time']] = row['close']

# Function to find the nearest previous rate for a given date
def get_closest_previous_rate(date):
    previous_dates = [d for d in date_to_rate.keys() if d <= date]
    if not previous_dates:
        return np.nan
    return date_to_rate[max(previous_dates)]

# Apply the function to get carry rates for each price date
data['carry_rate'] = data['time'].apply(get_closest_previous_rate)

# Define reference date (latest date in the dataset for forward valuation)
reference_date = data['time'].max()

# Calculate time difference in days between each observation and the reference date
data['days_to_ref'] = (reference_date - data['time']).dt.days

# Calculate time fraction using 1/360 bond convention
data['time_fraction'] = data['days_to_ref'] / 360

# Apply the continuous compounding formula (exponential) to express all prices at the reference date
# This brings historical prices forward to a common date, accounting for the time value of money
data['price_with_carry'] = data['close'] * np.exp((data['carry_rate']/100) * data['time_fraction'])

# Save the corrected price data
data.to_csv(os.path.join(save_dir, 'prices_with_carry.csv'), index=False)

# Split data into war and non-war periods
war_data = data[data['Dummy'] == 1]
non_war_data = data[data['Dummy'] == 0]

# Calculate descriptive statistics for war and non-war periods with carry adjustment
war_stats = war_data['price_with_carry'].describe()
non_war_stats = non_war_data['price_with_carry'].describe()

# Additional metrics: skewness for both periods
war_skewness = war_data['price_with_carry'].skew()
non_war_skewness = non_war_data['price_with_carry'].skew()

# Print descriptive statistics
print("=== Descriptive Statistics with Cost of Carry: War Period ===")
print(war_stats)
print(f"Skewness: {war_skewness:.4f}\n")

print("=== Descriptive Statistics with Cost of Carry: Non-War Period ===")
print(non_war_stats)
print(f"Skewness: {non_war_skewness:.4f}\n")

# Create a new distribution plot using prices with carry
plt.figure(figsize=(10, 6))

# Plot KDE distributions
sns.kdeplot(war_data['price_with_carry'], label='Háborús időszak', color='red', fill=True)
sns.kdeplot(non_war_data['price_with_carry'], label='Nem háborús időszak', color='blue', fill=True, alpha=0.5)

# Calculate averages with carry
war_avg = war_data['price_with_carry'].mean()
non_war_avg = non_war_data['price_with_carry'].mean()

# Add average markers
plt.axvline(war_avg, color='red', linestyle='--', linewidth=2, label=f'Átlag (háborús): {war_avg:.2f} €')
plt.axvline(non_war_avg, color='blue', linestyle='--', linewidth=2, label=f'Átlag (nem háborús): {non_war_avg:.2f} €')

# Add title, labels, and legend
plt.title('Áreloszlás összehasonlítása (Cost of Carry korrekciós tényezővel)')
plt.xlabel('Záróár (€)')
plt.ylabel('Density')
plt.legend()

# Save the plot
plt.savefig(os.path.join(save_dir, 'distributions_with_averages_corrected.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"Corrected price distribution plot and statistics saved to {save_dir}")
