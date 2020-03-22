# Transfer statements from PA to database

#coding=utf-8
from __future__ import unicode_literals
from pymongo import MongoClient
import pymongo
import openpyxl as xl
import argparse
import numpy as np
import pandas as pd
import re
import sys
import json


# 将企业财务报表转换为标准 Excel 并输入 mongoDB

# Global constants
company_name ='广州越秀产业投资基金管理股份有限公司'
province = '广东'
city = '广州'
industry = '私募'
collection_name = 'YuexiuFund'# collection name to insert to database
database_type = 'BalanceSheets'# database name to insert to database
dest_col_name_1 = '2015-12-31'# end year
dest_col_name_2 = '2014-12-31'# start year
input_file = pd.read_excel('input.xlsx')# 企业报表 input.xlsx，大致模式是分列、多 sheets 显示科目金额，方便阅读但不方便计算
income_statements = pd.read_excel('input.xlsx', sheet_name = 1)
cash_flows = pd.read_excel('input.xlsx', sheet_name= 2)
model_file = pd.read_excel('destination.xlsx')# 报表模板 destination.xlsx，一个已经制作好表位的 Excel 模板
standard_file = model_file.iloc[0:194]# 取上半截， 取第1 到第193 行，即资产+负债+损益科目
cashflows_file = model_file.iloc[194:317]# 取下半截 一共316行，从193开始取剩下

# Open database
New_Client=MongoClient('localhost',27017)
New_db = New_Client[database_type]
New_Collection = New_db[collection_name]
original_collection = New_Collection.find({},{'_id': False})# 取数据库数据，看看又没存量数据。有的话就保留。return pymongo.cursor.Cursor object, which cannot be dataframed
original_stats = list(original_collection)#change to list, which can be dataframed
original_df = pd.DataFrame(original_stats)#得到数据库里的原表

try:
    original_cashflows_df = original_df.loc[194:317,dest_col_name_2]# 取出数据库里本次输入的期初值（dest_col_name_2)对应的下半截（现金流），由于是截取的单独标签，故返回一个series。dtype = series. the pab cash flows only has the values for the end year, so we have to retain the original values of the start year's cash flow. iloc rows must match with cashflows_file in order to concat。取这半截数据的原因是保护起来，否则会被新输入的零值覆盖。
    df_c = pd.DataFrame(original_cashflows_df,columns=[dest_col_name_2])# 改为 dataframe
except:
    pass

try:
    original_df = original_df.drop(["科目名称","行次"],axis=1)
except:
    pass
for hed in original_df.columns:
    if hed == dest_col_name_1:#end year
        print('dropping end year:',hed)
        original_df = original_df.drop([hed],axis = 1)
    if hed == dest_col_name_2:#start year
        print('dropping start year:',hed)
        original_df = original_df.drop([hed],axis = 1)
#original_df = original_df.fillna(0,inplace = True)
#print(original_df)
New_Collection.drop()

# get the first name of the columns(headers)
#col_1 = input_file.columns[0]
col_2 = standard_file.columns[0]
#col_3 = income_statements.columns[0]
#col_4 = cash_flows.columns[0]

#-----data cleaning
# preparation
# 去除空格，谢谢 https://cloud.tencent.com/developer/ask/116074
input_file.replace(r'\s+','',inplace=True, regex=True)
income_statements.replace(r'\s+','',inplace=True, regex=True)
cash_flows.replace(r'\s+','',inplace=True, regex=True)
# get cols titles
col_assets = input_file.iloc[:,0]
col_liabilities_equity = input_file.iloc[:,4]
col_income = income_statements.iloc[:,0]
col_cash_flows = cash_flows.iloc[:,0]
# replace the non-number with NaN, then dropna() later 将非数转为空值
col_values_startyear_assets = pd.to_numeric(input_file.iloc[:,2], errors='coerce')
col_values__endyear_assests = pd.to_numeric(input_file.iloc[:,3], errors='coerce')
col_values_startyear_lia_equity = pd.to_numeric(input_file.iloc[:,6], errors='coerce')
col_values_endyear_lia_equity = pd.to_numeric(input_file.iloc[:,7], errors='coerce')
col_values_startyear_income = pd.to_numeric(income_statements.iloc[:,2], errors='coerce')#第三列年初值
col_values_endyear_income = pd.to_numeric(income_statements.iloc[:,3], errors='coerce')#第四列年末值
col_values_endyear_cashflows = pd.to_numeric(cash_flows.iloc[:,2], errors='coerce')#第三列年末值
#col_values_startyear_cashflows = pd.to_numeric(df_c[:,0], errors='coerce')
# begin concat and forge the balance sheet
# stage 1 搭积木，两列合并为一列
df_titles = pd.concat([col_assets,col_liabilities_equity], ignore_index = True)
df_startyear = pd.concat([col_values_startyear_assets,col_values_startyear_lia_equity], ignore_index = True)
df_endyear = pd.concat([col_values__endyear_assests,col_values_endyear_lia_equity], ignore_index = True)
# stage 2 排排坐，两列合并为一表
# 每个 df 只有2列，一列title，另外一列金额
df_clean_balance_startyear = pd.concat([df_titles,df_startyear], axis = 1, ignore_index = True)
df_clean_balance_endyear = pd.concat([df_titles,df_endyear], axis = 1, ignore_index = True)
df_clean_income_startyear = pd.concat([col_income,col_values_startyear_income], axis = 1, ignore_index = True)
df_clean_income_endyear = pd.concat([col_income,col_values_endyear_income], axis = 1, ignore_index = True)
df_clean_cashflows_endyear = pd.concat([col_cash_flows,col_values_endyear_cashflows], axis = 1, ignore_index = True)
#df_clean_cashflows_startyear = pd.concat([col_cash_flows,col_values_startyear_cashflows], axis = 1, ignore_index = True)
# stage 3 去除空值
df_clean_balance_startyear.dropna(inplace = True)
df_clean_balance_endyear.dropna(inplace = True)
df_clean_income_startyear.dropna(inplace = True)
df_clean_income_endyear.dropna(inplace = True)
df_clean_cashflows_endyear.dropna(inplace = True)
#df_clean_cashflows_startyear.dropna(inplace = True)
print('\nData cleaning completed. Start processing...')
#-----end cleaning

# 以 input.xlsx 的数据为主
# 先读取 input.xlsx 的数据，然后寻址输入 destination.xlsx 的相应位置
# 如果寻址失败，则显示无法寻址的科目及其金额

#print(input_file[col_2].where(input_file[col_1]=='    应收账款'))

'''
# use index to search the exact match
# https://stackoverflow.com/questions/21800169/python-pandas-get-index-of-rows-which-column-matches-certain-value
query = input_file.loc[4][0]
print('quering :',query)
idx = input_file.index[input_file[col_1]==query]
if idx.empty:
    print('Query empty, exit now')
    sys.exit()
else:
    print('Query success.')
search = input_file.loc[idx]#return a dataframe
# get row 1, col 4
value = search.iloc[0][3]
print('value is: ',value)

standard_file['2019-12-31'][4]=value
standard_file.to_excel('output.xlsx',sheet_name = 'Balance Sheet',index=False)
'''

def Special_Treatment(item, df, dest_col_name,value):
    if re.search(r'预付.项',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[9,dest_col_name] = value
    elif re.search(r'其他会计科目1',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[29,dest_col_name] = value
    elif re.search(r'其他会计科目2',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[60,dest_col_name] = value
    elif re.search(r'其他会计科目3',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[96,dest_col_name] = value
    elif re.search(r'其他会计科目4',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[114,dest_col_name] = value
    elif re.search(r'其他会计科目5',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[131,dest_col_name] = value
    elif re.search(r'预收.项',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[71,dest_col_name] = value
    elif re.search(r'实收资本.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[117,dest_col_name] = value
    elif re.search(r'盈余公积.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[125,dest_col_name] = value
    elif re.search(r'资本公积.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[121,dest_col_name] = value
    elif re.search(r'所有者权益.*合计',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[134,dest_col_name] = value
    elif re.search(r'负债和所有者权益.*计',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[137,dest_col_name] = value
    elif re.search(r'.*营业税金及附加.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[146,dest_col_name] = value
    elif re.search(r'.*公允价值变动收益.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[166,dest_col_name] = value
    elif re.search(r'^投资收益.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[162,dest_col_name] = value
    elif re.search(r'^汇兑收益.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[170,dest_col_name] = value
    elif re.search(r'.*营业利润.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[173,dest_col_name] = value
    elif re.search(r'.*利润总额.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[179,dest_col_name] = value
    elif re.search(r'.*所得税费用',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[180,dest_col_name] = value
    elif re.search(r'.*净利润.*',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[184,dest_col_name] = value
    elif re.search(r'少数股东损益',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[187,dest_col_name] = value
    elif re.search(r'^销售商品和提供劳务收到的现金',item):
        print('Processing ',item, '(special treatment):', value)
        #print(df)
        # 另外一个办法 ref:https://www.dataquest.io/blog/settingwithcopywarning/
        # pandas warning(SettingwithCopyWarning: How to Fix This Warning in Pandas) 也见上条链接
        df.loc[df.行次 == 195, dest_col_name] = value
    elif re.search(r'^收到的其他与经营活动有关的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[196,dest_col_name] = value
    elif re.search(r'^支付的其他与经营活动有关的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[214,dest_col_name] = value
    elif re.search(r'^经营活动产生的现金流量净额1',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[225,dest_col_name] = value
    elif re.search(r'^收回投资所收到的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[227,dest_col_name] = value
    elif re.search(r'^取得投资收益所收到的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[228,dest_col_name] = value
    elif re.search(r'^处置固定资产无形资产和其他长期资产所收回的现金净额',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[229,dest_col_name] = value
    elif re.search(r'^收到的其他与投资活动有关的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[231,dest_col_name] = value
    elif re.search(r'^购建固定资产无形资产和其他长期资产所支付的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[235,dest_col_name] = value
    elif re.search(r'^投资所支付的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[236,dest_col_name] = value
    elif re.search(r'^支付的其他与投资活动有关的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[238,dest_col_name] = value
    elif re.search(r'^吸收投资所收到的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[245,dest_col_name] = value
    elif re.search(r'^借款所收到的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[247,dest_col_name] = value
    elif re.search(r'^收到的其他与筹资活动有关的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[248,dest_col_name] = value
    elif re.search(r'^偿还债务所支付的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[253,dest_col_name] = value
    elif re.search(r'^分配股利、利润或偿付利息所支付的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[254,dest_col_name] = value
    elif re.search(r'^支付的其他与筹资活动有关的现金',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[256,dest_col_name] = value
    elif re.search(r'^筹集活动产生的现金流量净额',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[261,dest_col_name] = value
    elif re.search(r'^现金及现金等价物净增加额1',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[265,dest_col_name] = value
    elif re.search(r'^固定资产折旧',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[271,dest_col_name] = value
    elif re.search(r'^经营活动产生的现金流量净额2',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[290,dest_col_name] = value
    elif re.search(r'^现金等价物的期末余额',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[296,dest_col_name] = value
    elif re.search(r'现金等价物的期初余额',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[297,dest_col_name] = value
    elif re.search(r'现金及现金等价物净增加额2',item):
        print('Processing ',item, '(special treatment):', value)
        df.at[300,dest_col_name] = value
    else:
         Not_Found.append(item)

n = 0
value = 0
Not_Found = []
# 根据 input.xlsx 第一列遍历，取其对应行的第1列数值
# 无法合并两个寻址循环，因为科目会不一样（after dropna）
for item in df_clean_balance_endyear.iloc[:,0]:#item 是科目名称，比如 应收账款
    #query = item#要寻找的科目名称在第n行，第1列
    value = df_clean_balance_endyear.iloc[n,1]#要输入第值在第n行，第1列
    #print('Quering: ',item)
    # 根据 input 科目寻找 dest 对应的科目的index
    idx = standard_file.index[standard_file[col_2] == item]# 返回模板的位置
    if idx.empty:#模板里没有这个科目
        # 特殊科目处理
        Special_Treatment(item,standard_file,dest_col_name_1,value)
    else:#模板里有这个科目
        print('Processing ',item, ':', value)
        #search = standard_file.loc[idx]#return a dataframe with only single row
        # df.at[2,'B'] means index 2 at column 'B' , https://kanoki.org/2019/04/12/pandas-how-to-get-a-cell-value-and-update-it/
        standard_file.at[idx,dest_col_name_1] = value
    n += 1
n = 0
value = 0
for item in df_clean_balance_startyear.iloc[:,0]:
    value = df_clean_balance_startyear.iloc[n,1]
    idx = standard_file.index[standard_file[col_2] == item]
    if idx.empty:#模板里没有这个科目
        Special_Treatment(item,standard_file,dest_col_name_2,value)
    else:
        print('Processing ',item, ':', value)
        standard_file.at[idx,dest_col_name_2] = value
    n += 1
# Income statements
n = 0
value = 0
for item in df_clean_income_startyear.iloc[:,0]:
    value = df_clean_income_startyear.iloc[n,1]
    idx = standard_file.index[standard_file[col_2] == item]
    if idx.empty:#模板里没有这个科目
        Special_Treatment(item,standard_file,dest_col_name_2,value)
    else:
        print('Processing ',item, ':', value)
        standard_file.at[idx,dest_col_name_2] = value
    n += 1
n = 0
value = 0
for item in df_clean_income_endyear.iloc[:,0]:
    value = df_clean_income_endyear.iloc[n,1]
    idx = standard_file.index[standard_file[col_2] == item]
    if idx.empty:#模板里没有这个科目
        Special_Treatment(item,standard_file,dest_col_name_1,value)
    else:
        print('Processing ',item, ':', value)
        standard_file.at[idx,dest_col_name_1] = value
    n += 1
# Cash flows

n = 0
value = 0
for item in df_clean_cashflows_endyear.iloc[:,0]:
    value = df_clean_cashflows_endyear.iloc[n,1]
    idx = cashflows_file.index[cashflows_file[col_2] == item]
    if idx.empty:#模板里没有这个科目
        Special_Treatment(item,cashflows_file,dest_col_name_1,value)
    else:
        print('Processing ',item, ':', value)
        cashflows_file.at[idx,dest_col_name_1] = value
    n += 1


#cashflows_file[dest_col_name_2] = 99999999
try:
    if len(original_cashflows_df)!=0:
        cashflows_file[dest_col_name_2]=original_cashflows_df#series = series
except:
    pass
#print(cashflows_file[dest_col_name_2])
#print(type(standard_file[[dest_col_name_1,dest_col_name_2]]))#return a dataframe 

new_columns1 = ['科目名称','行次',dest_col_name_1,dest_col_name_2]
new_columns2 = ['科目名称','行次',dest_col_name_1]

standard_file = pd.concat([standard_file,cashflows_file], ignore_index = True,sort=False)
if len(original_df.columns)>0:
    for hed in original_df.columns:
        try:
            standard_file[hed] = original_df[hed]#series = series
        except:
            pass
#standard_file = pd.concat([standard_file,original_df], axis = 1, ignore_index = True,sort=False)
#test = standard_file[standard_file['行次']>193]# return dataframe
#test = standard_file.iloc[193:196]# return dataframe from row 193 to row 195(=196-1)
#print(test)
# -----------------------------------------------------------------------
if len(Not_Found) == 0:
    print ('\nAll items have been transfered.')
else:
    print('\nThe following items have not been transfered to the target:')
    for item in Not_Found:
        print(item)
standard_file.at[311,'科目名称'] = company_name
standard_file.at[312,'科目名称'] = province
standard_file.at[313,'科目名称'] = city
standard_file.at[314,'科目名称'] = industry
standard_file.fillna(0,inplace = True)
excel_export_name = company_name + '.xlsx'
standard_file.to_excel(excel_export_name,sheet_name = 'Balance Sheet',index=False)

# Insert dataframe to mongoDB
# ref: https://medium.com/analytics-vidhya/how-to-upload-a-pandas-dataframe-to-mongodb-ffa18c0953c1
#standard_file.reset_index(inplace=True) 不明白为什么要 reset_index, 暂时去掉
data_dict = standard_file.to_dict("records")
New_Collection.insert_many(data_dict)

New_Collection.create_index([("行次",pymongo.ASCENDING)])

'''
通过 iloc 查找
str.contains(string, na = False)
for item in standard_file.iloc[:,0]:
    result = input_file.loc[input_file[col_1].str.contains(item,na=False)]
    if result.empty:
        print (item, 'not found.')
    else:
        print(item, 'is', float(result.iloc[0][2]))

for item in standard_file.iloc[:,0]:
    result = input_file.loc[input_file[col_2].str.contains(item,na=False)]
    if result.empty:
        print (item, 'not found.')
    else:
        print(item, 'is', float(result.iloc[0][6]))
'''
