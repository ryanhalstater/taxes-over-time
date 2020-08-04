import csv
import requests
import pandas as pd
import numpy
# import cpi
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
#Need third column to specify path to the area to monitor
from bs4 import BeautifulSoup

#fix married filed jointly, or simply remove it from the data pool if I want (the special years still messed up)
#reshape for tablea
#calculate effective tax rate if i wanna
#desired is year status income and marginal tax rate
def main():
    get_all_tax_data()
    prepare_inflation_csv()
    convert_to_present_value(2020) #value passed in is reference year
    possible_statuses = ['Single', 'Married Filing Seperately', 'Married Filing Jointly', 'Head of Household']
    possible_incomes = [x * 1000 for x in [20,30,40,50,70,100,150,200,250,300,500,800, 1000, 1500, 2000, 5000,10000, 20000, 50000, 100000,500000,1000000]]
    get_marginal_tax_rate_over_time(possible_statuses, possible_incomes, 'marginal_tax_rate_over_time_final.csv')

    #note if preferred can comment this line out and reshape according to needs using jupyter notebook
    reshape_for_tableau()
    # returns df where index == (Year, Status, Income Level) and column == Marginal Tax Rate


def reshape_for_tableau():
    df = pd.read_csv('marginal_tax_rate_over_time_final.csv')
    df = df.set_index(['Year', 'Status'])
    df = df.stack()
    df = df.rename_axis(['Year', 'Status', 'Income Level'])
    df = df.to_frame()
    df.columns = ["Marginal Tax Rate"]
    df.to_csv('tableau_friendly.csv')

def get_marginal_tax_rate_over_time(statuses,incomes,name):

    pv_df = pd.read_csv('results_in_pv.csv')
    to_ret = pd.DataFrame(columns=['Year','Status'])
    for income in incomes:
        t = create_marginal_tax_series(statuses,income,pv_df)
        print(income)
        print(t.shape)
        to_ret = to_ret.merge(t,on=['Year','Status'],how="outer")
        del(t)

    print(to_ret.loc[to_ret['Year'] == 1955])
    temp_content = []
    for year in range(1949,1955):
        temp_content.append([year,'Married Filing Jointly'] + [numpy.nan for x in incomes])
    tmp_df = pd.DataFrame(temp_content, columns=list(to_ret.columns))
    to_ret = to_ret.append(tmp_df)
    to_ret = to_ret.set_index(['Year', 'Status']).sort_index()
    to_ret.to_csv(name)

def create_marginal_tax_series(statuses,income,pv_df):
    df_to_ret = pd.DataFrame(columns=['Year','Status',str(income)])
    for status in statuses:
        #create pool of possible lower bounds
        pv_df['helper'] = pv_df[status].isnull()
        df_temp = pv_df.loc[(pv_df['Lower Bound'] <= income) & (pv_df['helper'] == False),['Year','Lower Bound',status]]
        df_temp = df_temp.reset_index()
        #grab maxes of possible lower bounds
        df_temp_2 = df_temp.groupby('Year')['Lower Bound'].max()
        df_temp_2 = df_temp_2.reset_index()
        #create dateframe with years, max lower bounds, and associated tax rate
        df_temp = df_temp_2.merge(df_temp,on=['Year','Lower Bound'],how="left")
        df_temp = df_temp.drop('index',axis=1)
        #reshape dataframe to be year, status, and tax rate
        df_temp['Status'] = status
        df_temp.rename(columns = {status:str(income)}, inplace=True)
        df_temp = df_temp.reindex(columns=['Year','Status',str(income)])

        df_to_ret = pd.concat([df_to_ret,df_temp])
    print(df_to_ret.head())
    return df_to_ret

def convert_to_present_value(ref_year):
    df = pd.read_csv('results_not_pv.csv')
    inflation_df = pd.read_csv('inflation_data_cleaned.csv')
    new_index = float(inflation_df.loc[inflation_df['Year'] == ref_year, 'CPIAUCNS'])

    t1 = list(inflation_df['CPIAUCNS'])
    t1.append(257.971)  # assumed 2021 has same index as 2020
    t2 = list(inflation_df['Year'])
    t2.append(2021)
    inflation_dict = dict(zip(t2, t1))

    def convert(row):
        x = row['Year']
        old_index = inflation_dict[x]
        return (row['Lower Bound']) * new_index / old_index

    dsa = df.apply(lambda x: convert(x), axis=1)
    df['Lower Bound'] = dsa
    df = df.set_index(['Year','Lower Bound'])
    print(df.head())
    df.to_csv('results_in_pv.csv')


def prepare_inflation_csv():
    df = pd.read_csv('CPIAUCNS.csv')
    df['helper'] = df['DATE'].apply(lambda x: helper(x))

    res = df.loc[df['helper'] == 1]
    res['Year'] = res.apply(lambda x: x['DATE'][-4:], axis=1)

    res = res.drop(['helper', 'DATE'], 1)
    res = res.set_index(['Year'])
    res.to_csv('inflation_data_cleaned.csv')
    print(res.head())

def helper(x):
    if str(x)[:2] == '1/':
        return 1
    return 0

def get_tables(year):
    url = 'https://www.tax-brackets.org/federaltaxtable/'+str(year)
    response = requests.get(url) #, headers=headers

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table',{'class':'table table-striped table-bordered'})

    return tables

def get_tax_rate(table):
    results = []
    all_rows = table.find_all('tr')
    for r in all_rows[1:]: #skipping first row cause we all know what that is
        cells = r.find_all('td')
        tax_rate = cells[1].text
        results.append(float(tax_rate[:-2])*.01)
    return results

def get_lower_bounds(table):
    results = []
    all_rows = table.find_all('tr')
    for r in all_rows[1:]:  # skipping first row cause that is the header
        cells = r.find_all('td')
        lower_bound = cells[0].text.replace(',','')
        results.append(float(lower_bound[2:-2]))
    return results

def get_all_tax_data():
    df = pd.DataFrame(columns=['Year','Lower Bound','Single','Married Filing Seperately','Married Filing Jointly','Head of Household'])
    for year in range(1913,2022):  # goes from 1913 to 2021, where true year is listed - 1
        ts = get_tables(year)
        combo = []
        for t in ts:
            combo.append([get_lower_bounds(t),get_tax_rate(t)])
        temp_2 = []
        for t in combo:
            temp_2.extend(t[0])
        tax_brackets = []
        [tax_brackets.append(float(x)) for x in temp_2 if x not in tax_brackets]
        tax_brackets.sort()
        print(year)
        print(len(ts))

        if len(ts) == 3:
            #only single, married sep, and HoH
            combo = [combo[0],combo[1],[combo[0][0],[numpy.nan for x in combo[0][0]]],combo[2]]
            print('Year that didnt have married jointly (recall -1 is actual) ',year)

        base_df = pd.DataFrame({'Year':[year for x in tax_brackets],'Lower Bound':tax_brackets})

        labels = ['Single', 'Married Filing Seperately', 'Married Filing Jointly', 'Head of Household']
        for i in range(len(combo)):
            temp_df = pd.DataFrame({labels[i]:combo[i][1],'Lower Bound':combo[i][0]})
            base_df = pd.merge(base_df,temp_df,how="outer")
        df = pd.concat([df,base_df],sort=False)

    df = df.set_index(['Year','Lower Bound'])
    df.to_csv('results_not_pv.csv')
    print('tax data grabbed and writted to csv')

main()
