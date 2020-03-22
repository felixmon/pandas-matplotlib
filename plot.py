# Basic plots.
# Plot basic charts of financial statements

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import re
import pymongo
import argparse
import sys
from decimal import Decimal
from decimal import getcontext
from numpy.random import randint

def def_Open_MongoDB(Database_name,Collection_Name):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient[Database_name]
    collection = mydb[Collection_Name]
    return collection

def investment_gain(collection):
    # --- begin ---
    stats = collection.find({"行次":{"$in":[163]}},{'_id': False})
    stats = list(stats)
    stats_df = pd.DataFrame(stats)
    print(stats_df)
    print('\n')
    stats_df = stats_df.drop(["科目名称","行次"],axis=1)

    investment_gain = stats_df.T
    legend = 'investment gain'
    print(investment_gain)
    #----- PLOT -----
    #plt.figure(0)

    investment_gain.plot()
    plt.legend([legend])
    plt.text(0,5.2*1e8,'526mm')
    plt.text(1,5.7*1e8,'566mm')
    plt.text(2,5.-3.5*1e8,'-357mm')
    plt.text(3,5.-0.7*1e8,'-70mm')
    #plt.ylim(-1.5*1e7, 1.5*1e8)
    plt.show()

def FCF_Debt_ratio(collection):
    stats = collection.find({"行次":{"$in":[67,70,71,100,101,226]}},{'_id': False})
    stats = list(stats)
    stats_df = pd.DataFrame(stats)
    print(stats_df)
    print('\n')
    stats_df = stats_df.drop(["科目名称","行次"],axis=1)

    # 前5项（也就是付息债务）求和加总
    debts = stats_df.head(5).sum(axis=0)
    free_cashflow = stats_df.tail(1)
    ratio = free_cashflow/debts
    # print(type(ratio)) --> DataFrame
    ratio = ratio.T
    free_cashflow = free_cashflow.T
    plt.figure(figsize=(5, 5))
    #free_cashflow.plot()

    print('The ratio is: ', ratio)
    print('The FCF is: ', free_cashflow)


    # get values for y axis
    y1=[]
    y_FCF = []
    for indexs in ratio.columns:
        y1.append(list(ratio[indexs]))
    
    for indexs in free_cashflow.columns:
        y_FCF.append(list(free_cashflow[indexs]))

    y2=[]
    for item in y1[0]:
        y2.append(item)
    
    y3=[]
    for item in y_FCF[0]:
        y3.append(item)
    # get values for x axix
    # x 轴不是年份，而是0，1，2，3...
    x1 = list(ratio.index)
    x2 = list(range(0,len(x1)))
    #plt.text(0,0.67,'67%',bbox=dict(facecolor='red', alpha=0.5))
    #for a,b in zip(x,y):
    #   plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom',fontsize=7)

    # 格式化输出：https://blog.csdn.net/IAlexanderI/article/details/74177730 格式化输出 —— 小数转化为百分数
    # https://blog.csdn.net/lanchunhui/article/details/52850631 格式化输出 —— 小数转化为百分数
    # https://blog.csdn.net/qq_20113327/article/details/54461585 % 、 "%s 和 % d" 代表的意思
    # https://blog.csdn.net/Kerrwy/article/details/82416063 格式化输出保留两位小数

    for a,b in zip(x2,y3):
        #plt.text(a,b,'%.2f%%' %(b*100))
        plt.text(a,b,'%.2fmm' %(b/1e6))
    
    #plt.text(0,y2,'%.2f' %y2)
    #plt.figure()
    #ratio.plot()
    legend = 'Free Cash Flow'
    plt.plot(free_cashflow,label=legend)
    plt.legend()
    plt.show()

'''
    plt.text(0,0.67,'67%')
    plt.text(1,0.79,'79%')
    plt.text(2,0.09,'8.9%')
    plt.text(3,0.06,'6.05%')
'''
    #plt.ylim(-1.5*1e7, 1.5*1e8)

def aseet_liablities_ratio(collection):
    stats = collection.find({"行次":{"$in":[65,116]}},{'_id': False})
    stats = list(stats)
    stats_df = pd.DataFrame(stats)
    stats_df = stats_df.drop(["科目名称","行次"],axis=1)
    print('orginal stats:\n', stats_df)
    # 改动 y 值
    # 修改总资产，即修改第 1 行，第 4 列， iloc[0][3]

    #增加 1 行
    #stats_df.loc[2]=list(randint(10, size=4))
    # copy 一行
    #stats_df.iloc[2] = stats_df.loc[0] * 1
    #old_value = stats_df.iloc[2][3]
    #added_value = 3E9
    #stats_df.loc[2][3]  = old_value + added_value

    ''' 
    #stats_df.loc['after'] = ['999','666']
    # https://blog.csdn.net/hhgood/article/details/79342481 最简单增加一列的办法
    stats_df['After Capital Increse'] = stats_df['2019-12-31']
    added_value = 3E9 #增资30亿
    stats_df['After Capital Increse'][0] = stats_df['2019-12-31'][0] + added_value
    print('Added stats:\n', stats_df)
    '''
    assets = stats_df.iloc[0]
    liabilities = stats_df.iloc[1]
    stats_df = liabilities / assets # return dtype:series
    ratio = stats_df.T
    assets = assets.T
    liabilities = liabilities.T
    y1=[]
    y2=[]
    y3=[]
    for item in list(ratio):
        y1.append(item)

    for item in list(assets):
        y2.append(item)

    for item in list(liabilities):
        y3.append(item)


    x1 = list(range(0,len(list(ratio.index))))
    x2 = list(range(0,len(list(assets.index))))
    x3 = list(range(0,len(list(liabilities.index))))

    plt.figure(figsize=(8,8))
    #-----------------plot ratio--------------------------------------------
    title = 'Assets and Liabilites'
    plt.title(title)
    plt.subplot(311)
    #plt.ylabel(r'$\frac{Assets}{Liabilites}$',fontsize=13,fontweight='bold')
    for a,b in zip(x1,y1):
        plt.text(a,b,'%.2f%%' %(b*100))
    plt.ylim((0.5,1))
    plt.plot(ratio,label=r'$\frac{Assets}{Liabilites}$')
    plt.legend()
    #-----------------plot assets--------------------------------------------
    plt.subplot(312)
    plt.subplots_adjust(hspace =0.5)
    # 设置 y 轴单位（因为科学计数法的展示效果一般，其实挺好的）
    # Tick formatters 官方用法：https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-formatters.html
    # Tick formatters 网友用法：https://blog.csdn.net/zhangpeterx/article/details/96887459
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: "%.0dB" % (x/1e9)))

    # 设置y轴标题plt.ylabel("Assets",fontsize=13,fontweight='bold')
    for a,b in zip(x2,y2):
        plt.text(a,b,'%.2fB' %(b/1e9))
    plt.ylim((1e10,3e10))
    plt.plot(assets,label='Assets, billions',color='red')
    plt.legend()
    #-----------------plot liabilities---------------------------------------
    plt.subplot(313)
    plt.subplots_adjust(hspace =0.5)
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: "%.0dB" % (x/1e9)))
    #plt.ylabel("Liabilities",fontsize=13,fontweight='bold')
    for a,b in zip(x3,y3):
        plt.text(a,b,'%.2fB' %(b/1e9))
    plt.ylim((1e10,3e10))
    plt.plot(assets,label='Liabilities, billions',color='orange')
    plt.legend()
    #------------------------------------------------------------------------
    plt.suptitle(title)
    plt.savefig('asset-liabilities.png',dpi = 150)
    plt.show()

def y_fmt(x, y):
    return '{:2.2e}'.format(x).replace('e', 'x10^')

def ebida_interest_ratio(collection):
    # 利息保障倍数=(利润总额+利息费用+折旧+摊销)/利息费用
    #           =(利润总额+利息支出)/利息支出
    #           =EBIDA/利息费用
    
    stats = collection.find({"行次":{"$in":[152,180]}},{'_id': False})
    stats = list(stats)
    stats_df = pd.DataFrame(stats)

    print('original stats:\n',stats_df)

    stats_df = stats_df.drop(["科目名称","行次"],axis=1)

    '''
    # 在列['2019-12-31']后增加一列值
    # 增加的方法很简单，直接 dataframe.['new_col_name'] 即可
    # 模拟授信后的利息支出增加
    stats_df['Assumption'] = stats_df['2019-12-31']
    added_value = 3e9 * 0.05
    stats_df['Assumption'][0] = stats_df['2019-12-31'][0] + added_value
    '''

    # 两者比率
    series_1 = stats_df.iloc[0]#利息费用，行次152
    series_2 = stats_df.iloc[1]#利润总额，行次180

    #财务费用为负则取绝对值.ABS()

    series_3 = (series_1+series_2)/ series_1
    # 保留2位小数
    series_3 = series_3.map(lambda x: '%.2f' % x)
    stats_df = series_3

    stats_df = pd.to_numeric(series_3,errors='ignore')
    ratio = stats_df.T
    print ('ratio stats:\n',ratio)

    ebida = pd.to_numeric(series_1+series_2,errors='ignore')
    ebida = ebida.T

    print('ebida stats:\n',ebida)

    
    y1=[]
    for item in list(ratio):
        y1.append(item)
    print ('ratio is:' , y1)

    y2=[]
    for item in list(ebida):
        y2.append(item)
    print ('EBIDA is: ', y2)

    x1 = list(range(0,len(list(ratio.index))))
    x2 = list(range(0,len(list(ebida.index))))
    print(y2)

    # plot canvas first, before everything else
    # figsize=(width,height)
    plt.figure(figsize=(8,8))
    # plt.subplot(rows,cols,index,**kwargs)
    # 211 = 2 rows, 1 cols, index 1, index starts at 1 in the upper left corner and increases to the right
    plt.subplot(211)
    # x1, y1 for ratio
    # x2, y2 for ebida
    for a,b in zip(x1,y1):
        plt.text(a,b,b)
        #plt.text(a,b,'%.2fmm' %(b/1e6))
    
    #plt.plot(ebida,label='EBIDA')
    
    plt.plot(ratio,label='ratio')
    plt.legend()
    # -----------------------------------------------------------
    plt.subplot(212)
    #plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: "%.0dmm" % (x/1e6)))
    # thousand separator 千分位 https://stackoverflow.com/questions/51734218/formatting-y-axis-matplotlib-with-thousands-separator-and-font-size
    # https://www.cnblogs.com/crawer-1/p/8241882.html Python 数字系列-数字格式化输出
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x/1e6), ',')))
    #plt.ylim((0,1e9))
    for a,b in zip(x2,y2):
          # old way to format output: plt.text(a,b,'%.0dmm' %(b/1e6))
          # thousand separator
          plt.text(a,b,format(float(b/1e6), '0,.1f'))
          #plt.text(a,b,lambda x: '{:,}' % format(b))# lambda x: "{:,}".format(x[Loop_H]
    plt.plot(ebida,label='EBIDA, millions',color='red')
    plt.legend()
    title = 'EBIDA'
    plt.suptitle(title)
    plt.savefig('ebida.png',dpi = 150)
    plt.show() 

def main(argv=None):
    collection = def_Open_MongoDB("BalanceSheets","CMC")
    ebida_interest_ratio(collection)
    #aseet_liablities_ratio(collection)

if __name__ == "__main__":
    sys.exit(main())
