# package imports - a csomagokat futtatáshoz telepíteni kell, ajánlott pip-el vagy Pycharm Python Packagesben
import os
import configparser
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import levene

# === Load configuration from config.ini ===
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Load configuration
config = load_config('config.ini')

# Retrieve paths from the config file
local_dir_base = config['Paths']['local_dir_base']
file_path = os.path.join(local_dir_base, config['Paths']['price_file'])

# gördülő szórás lookback count
lookback_roll:int = 30

save_dir = os.path.join(local_dir_base, "Vizualizációk/Variance_py")

# Create directory if not exists
os.makedirs(save_dir, exist_ok=True)

# Read and prepare data
data = pd.read_excel(file_path)
data['time'] = pd.to_datetime(data['time'])
data['year'] = data['time'].dt.year

# Filter data from 2019 onwards for Plot 1
data_2019_onwards = data[data['year'] >= 2019]

# Rest of the data processing remains the same
war_data = data[data['Dummy'] == 1]
non_war_data = data[data['Dummy'] == 0]

war_variance = war_data['close'].var()
non_war_variance = non_war_data['close'].var()
annual_variance = data[data['year'] >= 2014].groupby('year')['close'].var().reset_index()
annual_variance.columns = ['Year', 'Annual_Variance']
comparison_df = data.groupby(['year', 'Dummy'])['close'].var().unstack()
comparison_df.columns = ['Non_War_Variance', 'War_Variance']

levene_stat, levene_p = levene(war_data['close'], non_war_data['close'])

data.set_index('time', inplace=True)  # Set datetime index for rolling calculation
rolling_var = data['close'].rolling(str(lookback_roll)+'D').var().loc['2021':'2023']  # lookback_roll:int-day window

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

# Levene's Test függbény
def compare_volatility(year_lt, data):
    """Compare volatility of a specified year against pre-2021 period using Levene's test"""
    pre_data = data.loc[:'2020-12-31', 'close']
    post_data = data.loc[str(year_lt), 'close']

    stat, p_value = levene(pre_data, post_data)

    print(f"\n=== Levene's Test for {year_lt} Volatility ===")
    print(f"Compared period: pre-2021 vs. {year_lt}")
    print(f"Levene's Statistic: {stat:.4f}")
    print(f"p-value: {p_value:.4f}")

    if p_value < 0.05:
        print(f"Significant difference in volatility between pre-2021 and {year_lt} (p < 0.05)")
    else:
        print(f"No significant difference in volatility between pre-2021 and {year_lt} (p ≥ 0.05)")

    return stat, p_value

# függvény hívás, Levene variancia normalitásteszt
for year in [2023, 2024, 2025]:
    compare_volatility(year, data)

# Print results (unchanged)
print("=== Basic Variance Analysis ===")
print(f"War Period Variance: {war_variance:.4f}")
print(f"Non-War Variance: {non_war_variance:.4f}\n")
print("=== Annual Variance (2014+) ===")
print(annual_variance.to_string(index=False))
print("\n=== Variance Equality Test ===")
print(f"Levene's Test p-value: {levene_p:.4f}")
print("Significant difference in variances" if levene_p < 0.05 else "No significant difference")

# Visualization functions
def save_individual_plots():
    # Plot 1: Price Timeline (from 2018 onwards)
    plt.figure(figsize=(12, 6))
    plt.plot(data_2019_onwards['time'], data_2019_onwards['close'], label='Záróár', color='blue')
    plt.fill_between(data_2019_onwards['time'], data_2019_onwards['close'],
                     where=data_2019_onwards['Dummy'] == 1,
                     color='red', alpha=0.3, label='Háborús időszak')

    for date_str, event in major_events.items():
        event_date = pd.to_datetime(date_str)
        plt.axvline(event_date, color=event['color'], linestyle='--', alpha=0.7, label=event['label'])

    plt.title('TFN1! idősor')
    plt.xlabel('Idő')
    plt.ylabel('€/MWh/nap * 24')
    plt.legend()
    plt.savefig(os.path.join(save_dir, '1_timeline_2018_onwards_with_events_no_pointers.png'), dpi=300,
                bbox_inches='tight')
    plt.close()

    # Plot 2: Annual Price Variance (Log Scale)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Year', y='Annual_Variance', data=annual_variance, palette='viridis')
    plt.yscale('log')
    plt.title('Éves árvariancia (log skála)')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(save_dir, '2_annual_variance_log.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Plot 3: War vs Non-War Annual Variance
    plt.figure(figsize=(12, 6))
    sns.barplot(x=comparison_df.index, y='War_Variance', data=comparison_df, color='red')
    sns.barplot(x=comparison_df.index, y='Non_War_Variance', data=comparison_df, color='blue', alpha=0.5)
    plt.title('Háborús és nem háborús időszakok éves varianciája')
    plt.legend(['Háború', 'Nem háború'])
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(save_dir, '3_war_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Plot 4: Price Distribution Comparison with Average Markers
    plt.figure(figsize=(10, 6))
    sns.kdeplot(war_data['close'], label='Háborús időszak', color='red', fill=True)
    sns.kdeplot(non_war_data['close'], label='Nem háborús időszak', color='blue', fill=True, alpha=0.5)
    war_data_avg = war_data['close'].mean()
    non_war_data_avg = non_war_data['close'].mean()
    plt.axvline(war_data_avg, color='red', linestyle='--', linewidth=2, label=f'Átlag (háborús): {war_data_avg:.2f}')
    plt.axvline(non_war_data_avg, color='blue', linestyle='--', linewidth=2,
                label=f'Átlag (nem háborús): {non_war_data_avg:.2f}')
    plt.title('Áreloszlás összehasonlítása')
    plt.xlabel('Záróár')
    plt.legend()
    plt.savefig(os.path.join(save_dir, '4_distributions_with_averages.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Plot 5: Enhanced Rolling Variance with Legend
    plt.figure(figsize=(14, 7))
    ax = rolling_var.plot(title= str(lookback_roll) + ' napos gördülő variancia kulcsfontosságú eseményekkel (2021-2023)',
                          color='steelblue', linewidth=2)
    y_max = rolling_var.max() * 1.15
    for date_str, event in major_events.items():
        date = pd.to_datetime(date_str)
        ax.axvline(date, color=event['color'], linestyle='--', alpha=0.7, label=event['label'])
        ax.annotate(event['description'],
                    xy=(date, y_max),
                    xytext=(date + pd.Timedelta(days=30), y_max * 1.05),
                    arrowprops=dict(arrowstyle="->", color=event['color']),
                    fontsize=9,
                    color=event['color'],
                    rotation=30)
    plt.legend(loc='upper left', fontsize=10)
    plt.xlabel('Dátum')
    plt.ylabel('Variancia')
    plt.grid(True)
    plt.savefig(os.path.join(save_dir, '5_rolling_variance_events_with_legend.png'),
                dpi=300, bbox_inches='tight')
    plt.close()

# Generate and save individual plots
save_individual_plots()

# Create and save combined plot
plt.figure(figsize=(15, 10))
plt.subplot(2, 2, 1)
plt.plot(data_2019_onwards['time'], data_2019_onwards['close'])
plt.fill_between(data_2019_onwards['time'], data_2019_onwards['close'],
                 where=data_2019_onwards['Dummy'] == 1,
                 color='red', alpha=0.3, label='Háborús időszak')
plt.title('TFN1! idősor')
plt.xlabel('Dátum')
plt.ylabel('€/MWh/nap * 24')
plt.legend()

plt.subplot(2, 2, 2)
sns.barplot(x='Year', y='Annual_Variance', data=annual_variance, palette='viridis')
plt.yscale('log')
plt.title('Éves árvariancia (log skála)')
plt.xticks(rotation=45)

plt.subplot(2, 2, 3)
sns.barplot(x=comparison_df.index, y='War_Variance', data=comparison_df, color='red')
sns.barplot(x=comparison_df.index, y='Non_War_Variance', data=comparison_df, color='blue', alpha=0.5)
plt.title('Háborús és nem háborús időszakok éves varianciája')
plt.legend(['Háború', 'Nem háború'])
plt.xticks(rotation=45)

plt.subplot(2, 2, 4)
sns.kdeplot(war_data['close'], label='Háborús időszak', color='red', fill=True)
sns.kdeplot(non_war_data['close'], label='Nem háborús időszak', color='blue', fill=True, alpha=0.5)
war_data_avg = war_data['close'].mean()
non_war_data_avg = non_war_data['close'].mean()
plt.axvline(war_data_avg, color='red', linestyle='--', linewidth=2, label=f'Átlag (háborús): {war_data_avg:.2f}')
plt.axvline(non_war_data_avg, color='blue', linestyle='--', linewidth=2,
            label=f'Átlag (nem háborús): {non_war_data_avg:.2f}')
plt.title('Áreloszlás összehasonlítása')
plt.xlabel('Záróár')
plt.legend()

plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
plt.savefig(os.path.join(save_dir, 'combined_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()
