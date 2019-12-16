import pandas as pd
import numpy as np
from io import StringIO
import os
os.makedirs('./result')
filename = './data/GPSdata.csv'
resultfile = './result/CarGPSStay.csv'
data = pd.read_csv(filename, header=0, index_col=None, delimiter = '/t', iterator = True)
from math import radians, cos, sin, asin, sqrt
def geodistance(lng1,lat1,lng2,lat2):
    lng1, lat1,lng2,lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
    distance=round(distance,3)
    return distance

StayList = [] #滞留队列汇总
colnames = ['longitude', 'latitude', 'time']

for i in range(0, len(data)):
    gpsdata = data.iloc[i]['doting_information_list']
    car_mark = data.iloc[i]['car_mark']
    user_id = data.iloc[i]['user_id']
    gpsdata = gpsdata.replace('#', '\n')
    TESTDATA = StringIO(gpsdata)
    tempdata = pd.read_csv(TESTDATA, sep=',', header=None, names=colnames, encoding='utf8', index_col=None)
    QueueList = []

    for index, row in tempdata.iterrows():
        if index % 5 == 0:
            # 一辆车的轨迹在这个循环中不断发送..
            if len(QueueList) == 0:
                QueueList.append(row)
            else:
                if geodistance(row['longitude'], row['latitude'], QueueList[0]['longitude'],
                               QueueList[0]['latitude']) < 250:
                    QueueList.append(row)  # 如果新数据与队尾元素距离接近，则push
                else:  # 与队尾数据距离远于250米
                    if len(QueueList) > 10:
                        stayBeginTime = QueueList[0]['time']  # 队尾点时间为滞留开始时间
                        staryEndTime = QueueList[-1]['time']  # 队首点时间为滞留结束时间
                        stayStruct = {
                            'car_mark': car_mark,
                            'user_id': user_id,
                            'stayBeginTime': stayBeginTime,
                            'stayEndTime': stayEndTime,
                            'stayNodes': QueueList
                        }
                        StayList.append(stayStruct)  # 将这些滞留点传给总部
                        QueueList = []  # 更新队列, 队列往前移动

                    else  # 1.队列没有那么长, 距离也比较远, 证明在正常行驶，没有逗留
                        # 更新队列， 队列往前移动
                        while len(QueueList) > 0 and geodistance(row['longitude'], row['latitude'],
                                                                 QueueList[0]['longitude'],
                                                                 QueueList[0]['latitude']) >= 250:
                            QueueList.pop(0)
                        QueueList.append(row)  # 队列步进



for i in range(0, len(StayList)):
    res = res.append({
        'user_id' : StayList[i]['user_id'],
        'car_mark' : StayList[i]['car_mark'],
        'stayBeginTime' : StayList[i]['stayBeginTime'],
        'stayEndTime' : StayList[i]['stayEndTime'],
        'stayNodesLongitude' : StayList[i]['stayNodes'][0]['longitude'],
        'stayNodesLatitude' : StayList[i]['stayNodes'][0]['latitude'],
        'stayDuration' : minNums(StayList[i]['stayBeginTime'], StayList[i]['stayEndTime'])
    }, ignore_index = True)

    res.to_csv(resultfile, sep=',', encoding='utf-8')


# 输入数据
#     car_mark ,  user_id,   doting_information_list
#     云12345      XIETAO111    102.43423,24.341423, 2019-11-01 00:00:20#102.43423,24.341423, 2019-11-01 00:00:20

# 输出数据
#     user_id     car_mark    stayBeginTime   staryEndTime    stayNodesLongitude      stayNodesLatitude   stayNodesLatitude