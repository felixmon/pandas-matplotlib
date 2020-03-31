# merge all excel in current path and export to csv file using Pandas dataframe
import os
import pandas as pd


#print (df.loc[0])

path = os.getcwd()
files = os.listdir(path)
files_xls = [f for f in files if f[-3:] == 'xls']

df_sum = pd.DataFrame()

for i in range(len(files_xls)):
    df = pd.read_excel(files_xls[i],header=None)
    df = df[1:]
    new_header = df.iloc[0]
    df.columns = new_header
    df=df[1:]
    df.reset_index(drop=True,inplace=True)
    df_sum = pd.concat([df_sum,df], ignore_index = True,sort = False)

df_sum.to_csv('sum.csv',index=False)
