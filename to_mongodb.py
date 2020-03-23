# Transfer Wind financial statements to MongoDB using template

import pandas as pd
import pymongo
from pymongo import MongoClient
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib

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
    df.replace(r'.*净利润.*不含.*','净利润',inplace=True, regex=True)

    # change the name of NaN header
    df.columns = df.columns.fillna('type')
    df.rename(columns={'type':'科目名称'}, inplace=True)
    # fill nan with 0
    df.fillna(0,inplace=True)
    df.replace('',0,inplace=True, regex=True)
    return df

def main(argv=None):

    # STAGE 1: OPEN
    # state the 3 filenames of the the 3 financial statements
    company_name = '深圳市元征科技股份有限公司'
    province = '广东'
    city = '深圳'
    industry = ['制造业','汽车','汽车后市场','物联网']
    filename_b = 'ARD.资产负债表[2488.HK].xlsx'
    filename_i = 'ARD.利润表[2488.HK].xlsx'
    filename_c = 'ARD.现金流量表[2488.HK].xlsx'
    if len(filename_b) == 0 or len(filename_i) == 0 or len(filename_c) == 0:
        print('missing input financial statements, exit now.')    
        sys.exit()
    # state the template
    template = 'template.xlsx'
    if len(template) == 0:
        print('missing template, exit now.')
        sys.exit()
    # end of parameters settings
    # open excel
    df_b = pd.read_excel(filename_b,engine='xlrd')
    df_c = pd.read_excel(filename_c,engine='xlrd')
    df_i = pd.read_excel(filename_i,engine='xlrd')
    df_t = pd.read_excel(template,engine='xlrd')

    # STAGE 2: DATA CLEANING
    # 思路：按行取数，得到2个serie, 一个是金额，另外一个时间节点（以index形式存在）
    # 取完之后重新建立一个 dataframe，以上述2个series为2列，另外添加 headers，然后plot
    df_b = pd.DataFrame(df_b)
    df_i = pd.DataFrame(df_i)
    df_c = pd.DataFrame(df_c)
    df_t = pd.DataFrame(df_t)
    # 清洗数据（去掉无用行、空格，科目名称互换等）
    df_b = data_cleaning(df_b)
    df_i = data_cleaning(df_i)
    df_c = data_cleaning(df_c)
    # 去掉损益表、现金流量表的头部2行
    df_c = df_c[2:]
    df_i = df_i[2:]

    # 合并：搭积木。注意次序：资产负债表、损益表、现金流量表
    df = pd.concat([df_b,df_i,df_c], ignore_index = True,sort = False)
    df.fillna(0,inplace = True)
    output_name = company_name + '_statement.xlsx'
    df.to_excel(output_name,index=False)

    # merge with template
    # merge ref:https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html
    # merge ref:https://www.jianshu.com/p/bd188347f5b1
    result = pd.merge(df_t,df,on='科目名称')
    result.to_excel('merge.xlsx',index=False)

    # Open database
    New_Client=MongoClient('localhost',27017)
    New_db = New_Client['BalanceSheet']
    collection = New_db['cnLaunch2488']

    # iterrows() https://blog.csdn.net/Softdiamonds/article/details/80218777, 按行返回object，非常有用
    # i.e. content['科目名称'] 返回科目名称, idx 返回index 
    for idx,content in result.iterrows():
        #print(dict(content))
        data = dict(content)
        for item in data:
            #print(item,':', data[item])
            collection.update_one(
                {"科目名称":data["科目名称"]},
                {
                '$set':{
                    item : data[item]
                }
                },upsert=True
            )

if __name__ == "__main__":
    sys.exit(main())
