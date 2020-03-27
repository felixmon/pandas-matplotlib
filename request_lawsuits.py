import requests
import json
import re
import datetime
import pandas as pd

# API address:http://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=%E8%AF%89%E8%AE%BC&sdate=&edate=&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=1

# set page number start at 1, ends at 'Loop'
pageNum = 1
Loop = 50

# create empty dataframe, later would be used to format the data and export to excel
df = pd.DataFrame(columns=['Date','secCode','secName','Title','URL'])
# start the loop
df_row = 0

for n in range(pageNum,Loop):
    url = 'http://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=%E8%AF%89%E8%AE%BC&sdate=&edate=&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=' + str(n)
    r = requests.get(url=url)#return values in json format
    data = json.loads(r.text)
    length = len(data['announcements'])# all data are wrapped in 'announcements' level(node), so we need to loop them out

    # start the loop for getting the content of each line of the search result
    for i in range(0,length):
        
        # convert unix timestamp to human datetime
        timestamp = datetime.datetime.fromtimestamp( data['announcements'][i]['announcementTime']/1000)# sample is 1585324800000, You have to divide your timestamp by 1000 to convert from milliseconds to seconds.
        secCode =  data['announcements'][i]['secCode']
        secName = data['announcements'][i]['secName']
        title = data['announcements'][i]['announcementTitle'].replace('<em>','').replace('</em>','')
        date = timestamp.strftime('%Y-%m-%d')
        secURL = data['announcements'][i]['adjunctUrl']
        secURL = 'http://static.cninfo.com.cn/' + secURL#add prefix of the URL
        result = secCode + ':' + title + date
        # replace highlighted keyword with ''
        result = result.replace('<em>','').replace('</em>','')
        # dataframe
        df.loc[df_row,'Date'] = timestamp
        df.loc[df_row,'secCode'] = secCode
        df.loc[df_row,'secName'] = secName
        df.loc[df_row,'Title'] = title
        df.loc[df_row,'URL'] = secURL
        df_row += 1

df.to_excel('lawsuit.xlsx',index=False)
