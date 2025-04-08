Upload contains the scripts and the folder structure I used for calculations
and plotting for my MSc Finance Thesis. 

Scripts rely in config.ini as a configuration file, whereas local_dir_base
should be amended to the folder's location. 

I purpousefully held back Dutch TTF rolling futures prices that are within prices.xlsx, and the 
EURINTR annualised DoD rates that are within cost_of_carry.csv, as those are being prop 
data, email me at baumannbence@icloud.com if you wish to acquire the basis data. 

Once local_dir_base is amended, and the source data has been moved in to the folder, 
scripts are expected to replicate the plots and calculations if the code dependencies 
are handled via pip, and the IDE has been configured with a proper Python interprerer.

I used PyCharm 2021.3 (Community Edition), and Python 3.9 trough a venv, hence I recommend
to use a similar setup to run the scripts. 

You may install all dependencies from Terminal via the following command once pip is downloaded:



**pip install pandas numpy matplotlib seaborn scipy openpyxl**

I would like to flag that these scripts are my initial steps in programming, hence I strongly 
advise agaisnt implementing any of the solutions in production level code.


