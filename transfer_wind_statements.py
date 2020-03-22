# clean the financial statements downloaded fron Wind and plot.

#coding=utf-8
import pandas as pd
import pymongo
from pymongo import MongoClient
import numpy as np
import sys
import matplotlib.pyplot as plt

def data_cleaning(df):
    # stage 1: cleaning the excel

    # deal with the 'Unnamed: 1' headers

    # grab the first row for the header, header row is not the first row
    new_header = df.iloc[0]

    # take the data less the header row
    df = df[1:]

    # drop the last 16 rows
    df = df[:-16]

    # set the header row as the df header
    df.columns = new_header

    # fill na with 0
    df.fillna(0,inplace=True)

    # replace space
    df.replace(r'\s+','',inplace=True, regex=True)

    # replcae characters
    df.replace(r'合并报表',0,inplace=True, regex=True)
    df.replace(r'报告类型','报告期',inplace=True, regex=True)
    df.replace(r'年报',4,inplace=True, regex=True)
    df.replace(r'中报',2,inplace=True, regex=True)
    df.replace(r'一季报',1,inplace=True, regex=True)
    df.replace(r'二季报',2,inplace=True, regex=True)
    df.replace(r'三季报',3,inplace=True, regex=True)
    df.replace(r'营业总支出','营业总成本',inplace=True, regex=True)

    # change the name of NaN header
    df.columns = df.columns.fillna('type')
    df.rename(columns={'type':'科目名称'}, inplace=True)
    # fill nan with 0
    df.fillna(0,inplace=True)
    df.replace('',0,inplace=True, regex=True)
    return df

def main(argv=None):
    input_filename = 'GSD.利润表[2488.HK].xlsx'
    standard = 'STANDARD.xlsx'
    df = pd.read_excel(input_filename,engine='xlrd')
    df_s = pd.read_excel(standard,engine='xlrd')
    df_2ndH = df_s.iloc[193:317]
    df_bi = df_s.iloc[0:193]
    df = pd.DataFrame(df)
    df = data_cleaning(df)
    #df = df.reset_index()
    col = '科目名称'
    query_t = '主营业务收入'

    # use is in to find row vaules
    # if empty dataframe then len == 0.
    #result = df[df.科目名称.isin([query_t])]
    #result.reset_index(drop=True)
    #print(result)
    # result.iloc[0] with single label returns a series of values

    df.to_excel('ref.xlsx',index=False)

    df = df.drop(["科目名称"],axis=1)
    df.T
    # sort columns, from old years to latest
    df = df.reindex(sorted(df.columns), axis=1)
    query_df=df.iloc[23]
    plt.plot(query_df)
    print(query_df)
    plt.show()
    #print(df.iloc[3])

''' into standard

    not_found_list=[]
    for biaoti in df.columns[2:10]:
        for item in df.iloc[:,0]:
            value = df.loc[df.科目名称 == item, biaoti]
            df_bi.loc[df_bi.科目名称 == item, biaoti] = float(value)

    df_bi.to_excel('output.xlsx',sheet_name = 'Balance Sheet',index=False)
        
'''

'''
    if df.loc[n,query] == '主营业务收入':
        title = '2018-12-31'
        value = df.loc[n,title]
        print(value)
'''    

if __name__ == "__main__":
    sys.exit(main())
