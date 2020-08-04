# taxes-over-time
- Visualization of USA Federal Income Tax rates over time for different income groups (accounting for inflation)
  - Contains breakdown of marginal tax rates by filing status 
## Methodology
- Data sourced from https://www.tax-brackets.org/federaltaxtable
  - There was no Married Filing Jointly tax bracket information available from 1949 to 1954
- Inflation data sourced from https://fred.stlouisfed.org/series/CPIAUCNS
  - The yearly inflation index used was the index's value in January of that year
  - Assumed inflation index for 2021 was the same as 2020 (2021 inflation not available at time)
- Python used to scrape yearly data and convert all money to present value (accounting for inflation)
  - Python's Pandas used to clean yearly data and inflation data
  - Marginal Tax Rate determined for multiple income levels using tax cutoffs (in present value) 
- Data reshaping for visualization in Tableau accessible in Jupyter Notebook (also in main.py) 
- Visualization done in Tableau

## Limitations
- Not reflective of true tax paid by different income groups
  - Omits capital gains tax, sales tax, property tax, and tax loopholes (among other factors)
  - Does not compute effective tax rate


## Results
![image](https://user-images.githubusercontent.com/6019805/89320873-179b4180-d650-11ea-9d52-50f91ef00dae.png)
![image](https://user-images.githubusercontent.com/6019805/89321795-5e3d6b80-d651-11ea-9f4d-b252b93eb13d.png)
![image](https://user-images.githubusercontent.com/6019805/89321803-609fc580-d651-11ea-93c5-226d8f991631.png)
![image](https://user-images.githubusercontent.com/6019805/89321811-62698900-d651-11ea-8b03-f4818b975ae3.png)
![image](https://user-images.githubusercontent.com/6019805/89320927-2e419880-d650-11ea-9ea3-460b2f39eebf.png)
![image](https://user-images.githubusercontent.com/6019805/89321000-57fabf80-d650-11ea-9dde-0d63f2c690a5.png)
![image](https://user-images.githubusercontent.com/6019805/89322172-dc9a0d80-d651-11ea-91e2-1e9bd0b3a09f.png)
<br/>
Please note that the Married Filing Jointly tax filing status data was not available between 1949 and 1954.
