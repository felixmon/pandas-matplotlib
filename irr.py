import numpy as np
import pandas as pd

# 计算租赁公司还款方式
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

pd.set_option('display.unicode.east_asian_width', True)


# -----------------在此修改参数 parameters begin ---------------------------------
# 本金
principal = 2e8
# 名义年利率 nominal annual rate
rate_nominal = 0.067
# 保证金 以及 手续费等需要在第一期就支付的金额 deposit at the first installment
deposit = 1e7 + 6.6e6
# 月份数 period in months
period = 36
# 间隔，3 = 按季，2 = 半年， 1 = 年
interval = 3
# -----------------参数输入结束 parameters end -----------------------------------
n = int(period / interval)
n_index =[]
for item in range(1,n+1):
    n_index.append(item)

# Finer Control: Display Values https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html#Finer-Control:-Display-Values
pd.options.display.float_format = '{:,.2f}'.format

# Python string format setting
form = '{:,.2f}'

# 每期归还本金等于本金除以期数
premium_fixed = principal / n

# 期间基数，严格意义来讲应该等于实际天数
periodic = 30/360

# 构建 dataframe，4列
df = pd.DataFrame(n_index,columns=['number'])
df['Principal Fixed']= premium_fixed # or form.format(premium_fixed)
df['interest'] = 0
df['Cash Flow'] = 0

# 期数列以及每期本金列都是固定数值，已经计算好
# 现在通过循环以计算利息以及每期现金流
for idx,content in df.iterrows():
    # 每一期利率
    # idx 返回每一行的 index
    # content 返回每一行对应的所有列的内容
    # 这里只用 index 的作用，以便逐行计算利息以及现金流
    result = (principal - premium_fixed * idx) * (rate_nominal*(periodic*interval))
    df.loc[idx,'interest'] = result
    df.loc[idx,'Cash Flow'] = df.loc[idx,'Principal Fixed'] + df.loc[idx,'interest']

    # format output
    # keep format and float type
    df.apply(pd.to_numeric,errors='coerce')

print('\n', df)

# calculate IRR
cash_flow = df['Cash Flow'] # return dtype pandas.series

# 将 series 转换为 list 以便计算 irr
irr = list(cash_flow)
irr_ori = list(cash_flow)

# 将初始值插入到首位，并调整为负值
# insert at the beginning of the irr list
principal_modified = -1 * (principal - deposit)
irr.insert(0,principal_modified)
irr_ori.insert(0,-1 * principal)

# 设置为百分比显示（此时数值变为字符串格式化输出）
form ='{:,.2%}'

# 将单期 irr 变为年化 irr
irr_result = np.irr(irr) * interval
irr_result_ori = np.irr(irr_ori) * interval

# 输出
print('\n')
print('IRR:', form.format(irr_result))
print('IRR, with no deposit:', form.format(irr_result_ori))
print('\n')

# IRR 是每期报酬率，不是年度回报率。IRR 是用来同样期限的投资组合，谁更划算。
# IRR的参数并没有绝对日期，只有『一期』的观念。每一期可以是一年、一个月或一天，随著使用者自行定义。如果每一格是代表一个[月]的现金流量，那麽传回的报酬率就是[月报酬率]；如果每一格是代表一个『年』的现金流量，那麽传回的报酬率就是[年报酬率]。
# 上述例子中, irr_result = np.irr(irr) * interval 就是求 年报酬率
