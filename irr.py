import numpy as np
import pandas as pd

# IRR的前提是

# 计算租赁公司租金 irr，或者满足：等额本金、利息递减且有保证金（及手续费）的还款计划的 irr
# 等额本金，即每期还款本金固定，且等于本金 / 期数
# 在按季付款的时候，时间!=(不等于)期数
# 一般是 36 个月，按季还本付息，期数为 36/3 = 12期
# 名义利率是6.7%，可设置
# 每期还款现金流 = 当期还款本金 + 利息
# 利息 = （本金 - 当期还款本金 * 期数）* （名义年利率*实际天数），其中实际天数 类似等于 = （30天/360 天）* 3 （一季）
# -----
# 程序实现思路
# 通过 pandas.dataframe 列示相关数据，columns = ['期数','当期还款本金','利息','现金流']
# 通过 numpy.irr 函数计算irr
# irr * 频率（3，一季）= 实际 irr



# -----------------在此修改参数 parameters begin ---------------------------------
# 本金，本金-保障金-费用=期初实际流出现金流
principal = 2e8
# 名义年利率 nominal annual rate，用于确定每期利息
rate_nominal = 0.06175
# 保证金，期末需要返回给客户，递减期末流入现金流
deposit = 1e7
# 手续费率，期初一次性收取
fee_rate = 0.033
# 月份数 period in months
period = 36
# 复利次数 frequency of compouding per year，4 = 按季，2 = 半年， 1 = 年
# 当 frequency = 4,意味这 12/4 = 3个月还本付息一次
frequency = 4

# -----------------参数输入结束 parameters end -----------------------------------
# -----------------计算常量 begin -----------------------------------
# 常量：
# 每期固定归还的本金
# 期数
# 利息计算因子
#----
# 期数 = 频率 * 年
number_of_intervals_of_timeline = int(frequency * (period/12))
n = number_of_intervals_of_timeline
# 每期归还本金等于本金除以期数，注意这里是一个trick，等额本金的等额不是根据t0期初实际获取贷款来计算，而是根据名义本金计算，这样会提高每一期FV（月供）
premium_fixed = principal / n
# 费用=本金*费率，一次性收取
fee = int(principal * fee_rate)
# 期初现金流=本金-保证金-费用
initial_investment = principal - deposit - fee
# 期初现金流属于流出现金流，为负数
initial_investment = -1 * initial_investment
# 利息实际天数基数，每年为360天，每月为30天
# 12/frequency = 每一期多少个月，如果frequency 是4，那么每一期就是3个月
# 30/360得出。。。？
#base = int((12/frequency)*(30/360))
# i.e. 12/4 = 3, 说明3个月还本付息一次
interest_factor = int(12/frequency) *  (30/360)

# -----------------计算常量 end -----------------------------------

# 设置 dataframe 格式
# Finer Control: Display Values https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html#Finer-Control:-Display-Values
pd.options.display.float_format = '{:,.2f}'.format
# Python string format setting
form = '{:,.2f}'


# 构建 dataframe，4列
# 先构建单列：期数
n_index =[]
for item in range(0,n+1):
    n_index.append(item)
# 创建 dataframe
df = pd.DataFrame(n_index,columns=['number'])

df['Principal Fixed']= premium_fixed # or form.format(premium_fixed)
df['interest'] = 0
df['Cash Flow'] = 0

# t0 期初现金流
df.loc[0,'number']=0
df.loc[0,'Principal Fixed']=0
df.loc[0,'interest']=0
df.loc[0,'Cash Flow']=initial_investment

# 期数列以及每期本金列都是固定数值，已经计算好
# 现在通过循环以计算利息以及每期现金流
for idx in range(1,n+1):
    # 已还本金 = 固定还款额 * （期数-1）
    # 期间利率 = （名义本金 - 已还本金） * 名义利率 * 利息因子
    periodic_interst = ((principal -premium_fixed*(idx-1)) * rate_nominal * interest_factor)
    inflow = premium_fixed + periodic_interst
    df.loc[idx,'interest'] = periodic_interst
    df.loc[idx,'Cash Flow'] = inflow

# 期末归还本金
df.loc[(n),'Cash Flow'] = df.loc[(n-1),'Cash Flow'] - deposit

# calculate IRR
cash_flow = df['Cash Flow'] # return dtype pandas.series

# 将 series 转换为 list 以便计算 irr
irr = list(cash_flow)

# 设置为百分比显示（此时数值变为字符串格式化输出）
form ='{:,.2%}'

# 将单期 irr 变为年化 irr
irr_result = np.irr(irr) * frequency

# 输出
# padding:
# http://www.datasciencemadesimple.com/right-pad-in-pandas-dataframe-python-2/
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.pad.html
# https://www.tutorialspoint.com/python/string_rjust.htm
# https://stackoverflow.com/a/46098243/13130970
# note that the column name will be changed after padding, thus raises KeyError if you want to use df['column name'] again.
df.columns = df.columns.map(lambda x: str(x).rjust(20))
df=df.to_string(index=False)

print('\n', df)
print('\n')

item_name = ['principal','rate nominal','deposit','fee','initial investment','IRR']
item_values = ['{:,.2f}'.format(principal),'{:,.2%}'.format(rate_nominal),'{:,.2f}'.format(deposit),'{:,.2f}'.format(fee),'{:,.2f}'.format(initial_investment), form.format(irr_result)]

df_2 = pd.DataFrame(zip(item_name,item_values))
df_2 = df_2.to_string(index=False,header=False)

print(df_2)
