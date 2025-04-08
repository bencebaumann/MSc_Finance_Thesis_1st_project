
import configparser
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Patch

# === Load configuration from config.ini ===
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Load configuration
config = load_config('config.ini')

# Retrieve paths from the configuration file
local_dir_base = config['Paths']['local_dir_base']


# Define file paths for LNG data
lng_folder = local_dir_base + "Thesis_Risk/OEC_gas_exp_imp/LNG"
lng_files = [
    {'filename': 'Exporters-of-Natural-gas-liquefied-2021-Click-to-Select-a-Country.csv', 'direction': 'export', 'year': 2021},
    {'filename': 'Importers-of-Natural-gas-liquefied-2021-Click-to-Select-a-Country.csv', 'direction': 'import', 'year': 2021},
    {'filename': 'Exporters-of-Natural-gas-liquefied-2023-Click-to-Select-a-Country.csv', 'direction': 'export', 'year': 2023},
    {'filename': 'Importers-of-Natural-gas-liquefied-2023-Click-to-Select-a-Country.csv', 'direction': 'import', 'year': 2023}
]

# Define file paths for gaseous gas data
gas_folder = local_dir_base + "Thesis_Risk/OEC_gas_exp_imp/GAS"
gas_files = [
    {'filename': 'Exporters-of-Natural-gas-in-gaseous-state-2021-Click-to-Select-a-Country.csv', 'direction': 'export', 'year': 2021},
    {'filename': 'Importers-of-Natural-gas-in-gaseous-state-2021-Click-to-Select-a-Country.csv', 'direction': 'import', 'year': 2021},
    {'filename': 'Exporters-of-Natural-gas-in-gaseous-state-2023-Click-to-Select-a-Country.csv', 'direction': 'export', 'year': 2023},
    {'filename': 'Importers-of-Natural-gas-in-gaseous-state-2023-Click-to-Select-a-Country.csv', 'direction': 'import', 'year': 2023}
]

# Function to process files and add type column
def process_files(file_list, folder, data_type):
    merged_data = pd.DataFrame()

    for file_meta in file_list:
        file_path = os.path.join(folder, file_meta['filename'])

        try:
            # Read the file
            data = pd.read_csv(file_path)

            # Add columns for direction, year, and type
            data['direction'] = file_meta['direction']
            data['year'] = file_meta['year']
            data['type'] = data_type  # Add LNG or GAS as the type

            # Append to the merged DataFrame
            merged_data = pd.concat([merged_data, data], ignore_index=True)

        except FileNotFoundError:
            print(f"Warning: File not found - {file_path}")

    print(f"{data_type} data processed successfully.")
    return merged_data

# Process LNG and gaseous gas files
lng_data = process_files(lng_files, lng_folder, "LNG")
gas_data = process_files(gas_files, gas_folder, "GAS")

# Combine both datasets into one DataFrame
combined_data = pd.concat([lng_data, gas_data], ignore_index=True)

# Save the combined data to an Excel file with separate sheets
output_path = local_dir_base + 'Thesis_Risk/OEC_gas_exp_imp/merged_data.xlsx'
with pd.ExcelWriter(output_path, mode='w') as writer:
    if not lng_data.empty:
        lng_data.to_excel(writer, sheet_name='LNG', index=False)
    if not gas_data.empty:
        gas_data.to_excel(writer, sheet_name='Gaseous Gas', index=False)
    combined_data.to_excel(writer, sheet_name='Combined Data', index=False)

print(f"Data merged with type column and saved to {output_path}")


def create_net_trade_df(merged_file_path):
    # Load merged data
    merged_data = pd.read_excel(merged_file_path, sheet_name='Combined Data')

    # Create empty DataFrame with required structure
    net_trade = pd.DataFrame(columns=['year', 'country', 'type', 'exp', 'imp', 'net_trade'])

    # Get unique countries
    countries = merged_data['Country'].unique()

    # Generate all combinations
    combinations = [(year, gas_type)
                    for year in [2021, 2023]
                    for gas_type in ['GAS', 'LNG']]

    # Populate DataFrame using vectorized operations
    data = []
    for country in countries:
        for year, gas_type in combinations:
            # Get exports
            exp = merged_data[
                (merged_data['Country'] == country) &
                (merged_data['year'] == year) &
                (merged_data['type'] == gas_type) &
                (merged_data['direction'] == 'export')
                ]['Trade Value'].sum()

            # Get imports
            imp = merged_data[
                (merged_data['Country'] == country) &
                (merged_data['year'] == year) &
                (merged_data['type'] == gas_type) &
                (merged_data['direction'] == 'import')
                ]['Trade Value'].sum()

            data.append({
                'year': year,
                'country': country,
                'type': gas_type,
                'exp': exp if not pd.isna(exp) else 0,
                'imp': imp if not pd.isna(imp) else 0,
                'net_trade': (exp if not pd.isna(exp) else 0) - (imp if not pd.isna(imp) else 0)
            })

    return pd.DataFrame(data)


# Create and save net trade data
net_trade_2021_2023 = create_net_trade_df(output_path)

# Add to Excel file
with pd.ExcelWriter(output_path, mode='a', engine='openpyxl') as writer:
    net_trade_2021_2023.to_excel(writer, sheet_name='Net Trade', index=False)

print(f"Net trade analysis added to {output_path}")




# Load the net trade data
def load_data(file_path):
    try:
        return pd.read_excel(file_path, sheet_name='Net Trade')
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


# Function to create the visualizations
def create_visualizations(data, save_path):
    # Process for each year
    for year in [2021, 2023]:
        # Filter data for the current year
        year_data = data[data['year'] == year]

        # Combine LNG and GAS for each country
        net_trade_by_country = year_data.groupby('country')['net_trade'].sum().reset_index()

        # Add absolute net trade for sorting
        net_trade_by_country['abs_net_trade'] = net_trade_by_country['net_trade'].abs()

        # Get top 7 exporters (largest positive values)
        exporters = net_trade_by_country[net_trade_by_country['net_trade'] > 0].sort_values('net_trade',
                                                                                            ascending=False)

        # Get top 7 importers (largest negative values by absolute magnitude)
        # Using ascending=True for negative values will sort from most negative to least negative
        importers = net_trade_by_country[net_trade_by_country['net_trade'] < 0].sort_values('net_trade', ascending=True)

        top_exporters = exporters.head(7)
        top_importers = importers.head(7)

        # Combine for visualization
        viz_countries = pd.concat([top_exporters, top_importers])

        # Calculate weights (percentages)
        total_abs_trade = viz_countries['abs_net_trade'].sum()
        viz_countries['weight'] = (viz_countries['net_trade'] / total_abs_trade) * 100

        # Create colors based on net trade sign
        colors = ['green' if n > 0 else 'orange' for n in viz_countries['weight']]

        # Create the chart
        plt.figure(figsize=(15, 8))
        bars = plt.bar(viz_countries['country'], viz_countries['weight'], color=colors)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            va_pos = 'bottom' if height > 0 else 'top'
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.1f}%', ha='center', va=va_pos)

        # Add grid, labels, title and legend
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xlabel('Ország')
        plt.ylabel('Világkereskedelmi hányad (Földgáz) (%)')
        plt.title(f'LNG és vezetékes nettó földgázmérleg globális arányai ( +/- top7) - {year}')

        # Rotate x-axis labels to prevent overlap
        plt.xticks(rotation=45, ha='right')

        legend_elements = [
            Patch(facecolor='green', label='Positive Weights'),
            Patch(facecolor='orange', label='Negative Weights')
        ]
        plt.legend(handles=legend_elements)

        plt.tight_layout()
        plt.savefig(os.path.join(save_path, f'weights_{year}.png'))
        print(f"Visualization for {year} created successfully.")


# Main execution
file_path = local_dir_base + 'Thesis_Risk/OEC_gas_exp_imp/merged_data.xlsx'
save_path = local_dir_base + 'Thesis_Risk/OEC_gas_exp_imp/'

data = load_data(file_path)
if data is not None:
    create_visualizations(data, save_path)
else:
    print("Failed to load data. Please check the file path.")
