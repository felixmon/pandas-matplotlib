import numpy as np
import pandas as pd

# 计算租赁公司还款方式
# 等额本金，即每期还款本金固定，且等于本金 / 期数
# 在按季付款的时候，时间!=(不等于)期数
# 一般是 36 个月，按季还本付息，期数为 36/3 = 12期
# 名义利率是6.7%，可设置
# 每期还款现金流 = 当期还款本金 + 利息
# 利息 = （本金 - 当期还款本金 * 期数）* （名义年利率*实际天数），其中实际天数 类似等于 = （30天/360 天）* 3 （一季）

principal = 2e8
rate = 0.67

# IRR
# nominal annual rate
rate_nominal = 0.067
# deposit at the first installment
deposit = 1e7 + 6.6e6
# period in months
period = 36
# 
interval = 3
n = int(period / interval)
n_index =[]
for item in range(1,n+1):
    n_index.append(item)

pd.options.display.float_format = '{:,.2f}'.format
pd.set_option('display.width', 1000)
form = '{:,.2f}'
premium_fixed = principal / n
#premium_fixed = '{:,.2f}'.format(premium_fixed)
periodic = 30/360
df = pd.DataFrame(n_index,columns=['number'])
df['Principal Fixed']= premium_fixed # or form.format(premium_fixed)
df['interest'] = 0
df['Cash Flow'] = 0

for idx,content in df.iterrows():
    # 每一期利率
    result = (principal - premium_fixed * idx) * (rate_nominal*(periodic*interval))
    df.loc[idx,'interest'] = result
    df.loc[idx,'Cash Flow'] = df.loc[idx,'Principal Fixed'] + df.loc[idx,'interest']

    # format output
    # keep format and float type
    df.apply(pd.to_numeric,errors='coerce')

print('\n', df)

# calculate IRR
cash_flow = df['Cash Flow'] # return dtype pandas.series
irr = list(cash_flow)
irr_ori = list(cash_flow)
# insert at the beginning of the irr list
principal_modified = -1 * (principal - deposit)
irr.insert(0,principal_modified)
irr_ori.insert(0,-1 * principal)
form ='{:,.2%}'
irr_result = np.irr(irr) * interval
irr_result_ori = np.irr(irr_ori) * interval
print('\n')
print('IRR:', form.format(irr_result))
print('IRR, with no deposit:', form.format(irr_result_ori))
print('\n')







