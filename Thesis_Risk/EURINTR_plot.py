# Import necessary packages
import os
import configparser
import pandas as pd
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
cost_of_carry_file = local_dir_base + 'Thesis_Risk/cost_of_carry.csv'

# Read cost of carry data
carry_data = pd.read_csv(cost_of_carry_file, sep=';')
carry_data['time'] = pd.to_datetime(carry_data['time'], format='%d/%m/%Y')

# Plot interest rate over time
plt.figure(figsize=(12, 6))
plt.plot(carry_data['time'], carry_data['close'], label='Rizikómentes kamatláb (ECONOMICS:EUINTR)', color='blue', linewidth=2)

# Add title and labels
plt.title('Rizikómentes kamatláb időbeli alakulása', fontsize=14)
plt.xlabel('Idő', fontsize=12)
plt.ylabel('Kamatláb (%)', fontsize=12)
plt.grid(True)
plt.legend()

# Save the plot
save_dir = local_dir_base + '/Thesis_Risk/Vizualizációk/'
os.makedirs(save_dir, exist_ok=True)
plt.savefig(os.path.join(save_dir, 'interest_rate_over_time.png'), dpi=300, bbox_inches='tight')

# Show the plot
plt.show()
