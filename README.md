**MSc Finance Thesis Project**

This repository contains the scripts and folder structure utilized for calculations and plotting as part of my MSc Finance Thesis.
Below, you will find detailed instructions on how to configure and use the repository effectively.



**Project Overview**


The project analyzes financial data related to natural gas markets, employing Python scripts for data processing, visualization, and statistical calculations. The repository includes:
Scripts: Python files for performing calculations and generating plots.
Configuration File: A config.ini file to manage project settings.
Folder Structure: A predefined directory layout to organize input data and outputs.


**Setup Instructions**

**1. Configuration**
The scripts rely on a config.ini file for configuration. Update the local_dir_base variable in this file to match the location of the repository on your local machine.
**2. Data Requirements**
Certain proprietary datasets are excluded from this repository:
Dutch TTF Rolling Futures Prices: Contained in prices.xlsx.
EURINTR Annualized DoD Rates: Contained in cost_of_carry.csv.
To access these datasets, please email me at baumannbence@icloud.com.
Publicly available data, such as natural gas export/import volumes sourced from OEC World, is included in the repository.


**3. Dependencies**
Ensure that all required Python libraries are installed. You can install them using the following command:
bash

**pip install pandas numpy matplotlib seaborn scipy openpyxl**


**4. IDE and Python Environment**
I recommend using PyCharm 2021.3 (Community Edition) with Python 3.9 in a virtual environment (venv). Ensure your IDE is configured with the correct Python interpreter.
Running the Scripts
Clone this repository to your local machine.
Update local_dir_base in config.ini with the path to your local folder.
Place the source data files (prices.xlsx and cost_of_carry.csv) in their respective directories within the folder structure.
Run the scripts from your IDE or terminal to replicate the calculations and plots.
Folder Structure


These scripts represent my initial steps in programming, so they are not optimized for production-level use.
For any questions or issues, feel free to reach out via email.
Thank you for exploring my MSc Finance Thesis project!
