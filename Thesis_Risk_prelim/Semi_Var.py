import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import seaborn as sns

# Configure paths
local_dir_base = '/Users/bencebaumann/Desktop/'
price_path = local_dir_base + 'Thesis_Risk/prices.xlsx'
save_dir = local_dir_base + 'Thesis_Risk/Vizualizációk/Semi_Var'
lookback_roll:int = 30

# Create save directory
os.makedirs(save_dir, exist_ok=True)

# Load data
df = pd.read_excel(
    price_path,
    parse_dates=['time'],
    usecols=['time', 'close', 'Dummy']
).set_index('time')

# Modified semi-variance calculation for short exposure
def rolling_semivariance(series, window):
    """Gördülő (lookback = """ +str(lookback_roll) + """) SV számítás SHORT vanilla pozícióra"""
    squared_deviations = []
    for i in range(window, len(series)):
        window_slice = series.iloc[i-window:i]
        # Focus on negative returns (price increases = losses in short position)
        losses = window_slice[window_slice < 0]
        sv = (losses.pow(2).mean() if not losses.empty else 0)
        squared_deviations.append(sv)
    return pd.Series(squared_deviations, index=series.index[window:])

# SHORT returns calculation (inverse of normal returns)
returns = -df['close'].pct_change().dropna()  # Invert returns for short exposure
df['SemiVariance'] = rolling_semivariance(returns, lookback_roll)

# 1. Time series plot with events
plt.figure(figsize=(14, 5))
plt.plot(df.index, df['SemiVariance'], color='darkred', lw=1)

# Event markers
event_colors = ['navy', 'green', 'purple']
for i, event_date in enumerate(pd.to_datetime(['2022-02-24', '2022-03-15', '2022-09-26'])):
    plt.axvline(event_date, color=event_colors[i], linestyle='--', alpha=0.7, lw=1)

plt.title('Short Exposure Félvariancia Idősor - Árfolyamnövekedés = Veszteség')
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))
plt.tight_layout()
plt.savefig(f'{save_dir}/short_semi_variance_timeseries.png', dpi=300)
plt.close()

# 2. Density plot by conflict status
plt.figure(figsize=(10, 5))

# Filter data
conflict_periods = df[df['Dummy'] == 1]['SemiVariance'].dropna()
non_conflict = df[df['Dummy'] == 0]['SemiVariance'].dropna()

# Calculate statistics
non_conflict_mean = non_conflict.mean()
conflict_mean = conflict_periods.mean()

# Density plot
sns.kdeplot(non_conflict, color='limegreen',
           label='Konfliktusmentes időszakok', fill=True, alpha=0.3)
sns.kdeplot(conflict_periods, color='darkred',
           label='Konfliktus időszakok', fill=True, alpha=0.3)

# Add mean markers
plt.axvline(non_conflict_mean, color='limegreen', linestyle=':', lw=2)
plt.axvline(conflict_mean, color='darkred', linestyle=':', lw=2)

plt.title('Short Exposure Félvariancia Eloszlás - Árfolyamcsökkenés = Nyereség')
plt.xlabel('Félvariancia (Árfolyamnövekedésből származó kockázat)')
plt.ylabel('Sűrűség')

# Legend and stats box
plt.legend(loc='upper right')
ax = plt.gca()
ax.text(0.98, 0.5,
       f"Konfliktus átlag:\n{conflict_mean:.5f}\n\nNormál átlag:\n{non_conflict_mean:.5f}",
       transform=ax.transAxes,
       bbox=dict(facecolor='white', edgecolor='gray', alpha=0.7),
       fontsize=9,
       verticalalignment='center',
       horizontalalignment='right')

plt.tight_layout()
plt.savefig(f'{save_dir}/short_semi_variance_density.png', dpi=300)
plt.close()
