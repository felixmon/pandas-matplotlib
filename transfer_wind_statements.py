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

    # STAGE 1: OPEN
    input_filename = 'GSD.利润表[2488.HK].xlsx'
    df = pd.read_excel(input_filename,engine='xlrd')

    # STAGE 2: DATA CLEANING
    # 思路：按行取数，得到2个serie, 一个是金额，另外一个时间节点（以index形式存在）
    # 取完之后重新建立一个 dataframe，以上述2个series为2列，另外添加 headers，然后plot

    # 读取Excel
    df = pd.DataFrame(df)
    # 清洗数据（去掉无用行、空格，科目名称互换等）
    df = data_cleaning(df)
    # output clean dataset to excel for future usages
    df.to_excel('ref.xlsx',index=False)

    # STAGE 3: SELECT, (CALCULATE), AND PLOT
    # select single row, i.e. 净利润
    # 对照清洗后的数据取对应的行
    row1=21
    # print the 科目名称 which is going to be used
    row_name = df['科目名称'].iloc[row1]
    print(row_name)
    # drop column that will not be used
    df = df.drop(["科目名称"],axis=1)
    # sort columns, from old years to latest
    # 按照阅读习惯，从左至右，从久到新排列时间
    df = df.reindex(sorted(df.columns), axis=1)
    # select single row i.e. 净利润
    # iloc return a serie which contain only single row of values
    query_df=df.iloc[row1]
    # use serie.index as years
    year = list(query_df.index)
    # convert to list in order to create dataframe
    value = list(query_df)
    # create dataframe with 2 series/lists, using zip to combine the 2 lists.
    tdf = pd.DataFrame(list(zip(year,value)),columns=['year','value'])

    # select rows that are years with regex pattern
    # ref:https://stackoverflow.com/questions/15325182/how-to-filter-rows-in-pandas-by-regex
    tdf2 = tdf[tdf.year.str.contains(r'201.-12-31')]

    print(tdf2)

    # 线性图: tdf2.plot(x='year')
    # 直方图：https://blog.csdn.net/Darkman_EX/article/details/80738021
    # rotate x labels: https://stackoverflow.com/questions/32244019/how-to-rotate-x-axis-tick-labels-in-pandas-barplot
    tdf2.plot(x='year',kind='bar',alpha=0.75, rot=0)

    plt.show()
    

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
