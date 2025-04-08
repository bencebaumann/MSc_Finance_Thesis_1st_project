import os
import configparser
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load sensitive configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Read only sensitive values
local_dir_base = config.get('Paths', 'local_dir_base')
price_path = os.path.join(local_dir_base, config.get('Paths', 'price_file'))

# Hardcoded
output_path = os.path.join(local_dir_base, 'Thesis_Risk/TTF_gaz_ar_analizis.xlsx')
plot_save_path = os.path.join(local_dir_base, 'Thesis_Risk/Vizualizációk/SV.png')
lookback_window = 20
start_period = 2019
end_period = 2025

major_events = {
    '2022-02-24': {
        'label': 'Ukrajna invázió kezdete',
        'color': 'darkred',
        'description': 'Orosz invázió kezdete\n(azonnali ellátási félelmek)'
    },
    '2022-03-15': {
        'label': 'Szankciók bejelentése',
        'color': 'darkorange',
        'description': 'Nyugati szankciók bejelentése\n(gázellátási bizonytalanság)'
    },
    '2022-09-26': {
        'label': 'Nord Stream szabotázs',
        'color': 'purple',
        'description': 'Csővezeték robbanások\n(akut ellátási válság)'
    }
}

def semi_variance(df, window):
    df['semi_variance'] = df['filtered_ret'].rolling(window=window).var()
    return df

# Load and process data
try:
    df = pd.read_excel(
        price_path,
        parse_dates=['time'],
        usecols=['time', 'close', 'Dummy']
    )
except FileNotFoundError:
    print(f"File not found: {price_path}")
    exit()

# Extract date parts
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day

# Filter data
df = df[(df['year'] >= start_period) & (df['year'] <= end_period)]

# Calculate returns
df['returns'] = -df['close'].pct_change()
df['filtered_ret'] = df['returns'].apply(lambda x: x if x < 0.0 else 0.0)
df = semi_variance(df, lookback_window)

# Plot
plt.figure(figsize=(12, 8))
plt.plot(df['time'], df['semi_variance'], color='blue', label='Semi-Variance')
plt.xlabel('Év')
plt.ylabel('Semi-Variance')
plt.title(f"{lookback_window} napos rolling SV ({start_period} - {end_period}) - short TFN1!")
plt.grid()

# Event markers
for date, event in major_events.items():
    event_date = pd.to_datetime(date)
    plt.axvline(event_date, color=event['color'], linestyle='--', linewidth=1.5, label=event['label'])

# Format x-axis
date_format = mdates.DateFormatter("%Y")
plt.gca().xaxis.set_major_formatter(date_format)
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.xticks(rotation=45)
plt.legend(loc='upper left')

# Save + show plot
plt.tight_layout()
plt.savefig(plot_save_path)
plt.show()
print(f"Plot saved: {plot_save_path}")

# Export data
df.to_excel(output_path, sheet_name='Price Analysis')
print(f"File saved: {output_path}")
