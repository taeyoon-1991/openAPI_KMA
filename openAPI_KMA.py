###########################################################
# File: openAPI_KMA.py
#
# Python == 3.8.5
# numpy  == 1.19.2
# pandas == 1.1.3
#
# Created by 엄태윤 on Dec. 15, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from datetime import datetime, timedelta
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from numpy.core.fromnumeric import product

import pandas as pd
import numpy as np

def _xml_to_dataframe(tree):
    root = tree.getroot();list_data = []
    for header in root.iter('header'):
        resultCode = header.find('resultCode').text
        resultMsg  = header.find('resultMsg').text
        if resultCode == "00":
            for body in root.iter('body'):
                for items in body.iter('items'):
                    for item in items.iter('item'):
                        dict_tmp = {}
                        for elem in item.iter():
                            dict_tmp[elem.tag] = elem.text
                        list_data.append(dict_tmp)
        else: assert False, f"NOT NORMAL RESPONSE OF API: {resultMsg}({resultCode})"
    return pd.DataFrame(list_data)

class VilageFcstInfoService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey

    def __check_valid_time(self, time):
        gap = datetime.now() - time
        assert gap.days == 0 or gap.total_seconds() >= 0, \
        f"baseTime shoud be within 24 hours from now, your baseTime is {time}"

    def get_VilageFcst_baseTime(self, time):
        h = time.hour
        if h < 2:
            time = time + timedelta(days=-1)
            h = 23
        else:
            if h%3==2: pass
            else: h = h - (h%3 + 1)
        fcst_time = time.replace(hour=h,minute=0,second=0,microsecond=0)
        
        #Published after 10 mins of Production
        gap = datetime.now().replace(minute=10,second=0,microsecond=0) - fcst_time
        gap = gap.total_seconds()
        if gap <  10*60 and gap >= 0: fcst_time = fcst_time + timedelta(hours=-3)

        self.__check_valid_time(fcst_time)
        return {"Production-time": fcst_time,"baseTime":fcst_time}
    
    def get_UltraSrtFcst_baseTime(self, time):
        fcst_time = time.replace(minute=30,second=0,microsecond=0)
        if time.minute < 30: fcst_time = fcst_time + timedelta(hours=-1)

        #Published after 15 mins of Production
        gap = datetime.now().replace(minute=45,second=0,microsecond=0) - time
        gap = gap.total_seconds()
        if gap < 15*60 and gap >= 0 : fcst_time = fcst_time + timedelta(hours=-1)             

        self.__check_valid_time(fcst_time)
        return {"Production-time": fcst_time,"baseTime":fcst_time}

    def get_UltraSrtNcst_baseTime(self, time):
        ncst_time = time.replace(minute=30,second=0,microsecond=0)
        if time.minute < 30: ncst_time = ncst_time + timedelta(hours=-1)
        
        #Published after 10 mins of Production
        gap = datetime.now().replace(minute=40,second=0,microsecond=0) - time
        gap = gap.total_seconds()
        if gap < 10*60 and gap >= 0: ncst_time = ncst_time + timedelta(hours=-1)

        self.__check_valid_time(ncst_time)
        return {"Production-time": ncst_time,"baseTime":ncst_time.replace(minute=0)}

    def getFcstVersion(self, ftype, basedatetime, save_path=False):
        assert ftype in ['ODAM','VSRT','SHRT'], f"ftype shoud be one of 'ODAM'/'VSRT'/'SHRT', (UltraSrtNcst-ODAM, UltraSrtFcst-VSRT, VilageFcst-SHRT)"
        
        self.__check_valid_time(basedatetime)        
        basedatetime = basedatetime.strftime('%Y%m%d%H%M')

        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getFcstVersion"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=10&dataType=XML"
        url = f"{url}&ftype={ftype}&basedatetime={basedatetime}&"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        root = tree.getroot();resultCode="";resultMsg=""
        for header in root.iter('header'):
            resultCode = header.find('resultCode').text
            resultMsg  = header.find('resultMsg').text
            if resultCode == "00":
                for body in root.iter('body'):
                    for items in body.iter('items'):
                        for item in items.iter('item'):
                            version = item.find('version').text
                            version = datetime.strptime(version, "%Y%m%d%H%M%S")
                            return version
            else: assert False, f"{ftype},{basedatetime}: {resultMsg}({resultCode})"

    def __get_Fcst(self, X, Y, baseDateTime, save_path, ftype, version):
        baseDate = baseDateTime.strftime("%Y%m%d")
        baseTime = baseDateTime.strftime("%H%M")

        url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService/get{ftype}"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&base_date={baseDate}&base_time={baseTime}"
        url = f"{url}&nx={X}&ny={Y}"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        DF['fcstDateTime'] = DF['fcstDate'] + DF['fcstTime']
        baseDateTime = DF['baseDate'][0] + DF['baseTime'][0]
        nx = DF['nx'][0];ny = DF['ny'][0]
        DF.set_index(pd.to_datetime(DF['fcstDateTime'],format="%Y%m%d%H%M"),inplace=True)
        DF = DF.groupby([DF.index, 'category'])['fcstValue'].aggregate('first').unstack()
        DF['nx']=nx;DF['ny']=ny;DF['baseDateTime']=baseDateTime;DF['type']=ftype
        DF['baseDateTime'] = pd.to_datetime(DF['baseDateTime'],format="%Y%m%d%H%M")
        DF['version'] = version
        DF.index.name = 'fcstDateTime'
        return DF

    def __get_Ncst(self, X, Y, baseDateTime, save_path, version):
        baseDate = baseDateTime.strftime("%Y%m%d")
        baseTime = baseDateTime.strftime("%H%M")

        url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtNcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&base_date={baseDate}&base_time={baseTime}"
        url = f"{url}&nx={X}&ny={Y}"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        DF['baseDateTime'] = DF['baseDate'] + DF['baseTime']
        baseDateTime = DF['baseDate'][0] + DF['baseTime'][0]
        nx = DF['nx'][0];ny = DF['ny'][0]
        DF.set_index(pd.to_datetime(DF['baseDateTime'],format="%Y%m%d%H%M"),inplace=True)
        DF = DF.groupby([DF.index, 'category'])['obsrValue'].aggregate('first').unstack()
        DF = DF.to_dict('index');DF = pd.DataFrame.from_dict(DF, orient='index')
        DF['nx']=nx;DF['ny']=ny;DF['type']='UltraSrtNcst'
        DF['version'] = version
        DF.index.name = 'baseDateTime'
        return DF


    def getVilageFcst(self, X, Y, datetime, save_path=False):
        baseDateTime = self.get_VilageFcst_baseTime(datetime)['baseTime']
        version = self.getFcstVersion('SHRT', baseDateTime)
        return self.__get_Fcst(X,Y,baseDateTime,save_path,'VilageFcst',version)

    def getUltraSrtFcst(self, X, Y, datetime, save_path=False):
        baseDateTime = self.get_UltraSrtFcst_baseTime(datetime)['baseTime']
        version = self.getFcstVersion('VSRT', baseDateTime)
        return self.__get_Fcst(X,Y,baseDateTime,save_path,'UltraSrtFcst',version)

    def getUltraSrtNcst(self, X, Y, datetime, save_path=False):
        baseDateTime = self.get_UltraSrtNcst_baseTime(datetime)['baseTime']
        version = self.getFcstVersion('ODAM', baseDateTime)
        return self.__get_Ncst(X,Y,baseDateTime,save_path,version)

class AsosHourlyInfoService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey

    def getWthrDataList(self,stnIds,startDtHh,endDtHh,save_path=False):
        stnIds = stnIds
        startDt = startDtHh.strftime("%Y%m%d")
        startHh = startDtHh.strftime("%H")
        endDt   = endDtHh.strftime("%Y%m%d")
        endHh   = endDtHh.strftime("%H")

        url = f"http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&dataCd=ASOS&dateCd=HR"
        url = f"{url}&startDt={startDt}&startHh={startHh}"
        url = f"{url}&endDt={endDt}&endHh={endHh}"
        url = f"{url}&stnIds={stnIds}&schListCnt=999"
        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        DF.set_index('tm',inplace=True);DF.index = pd.to_datetime(DF.index)
        DF.sort_index(inplace=True);DF.drop('item',axis=1,inplace=True)
        DF.index.name = 'tm'

        start = pd.to_datetime(startDtHh)
        end   = pd.to_datetime(endDtHh)
        df_time = pd.DataFrame(index=(pd.date_range(start, end, freq='H')))
        return pd.concat([ df_time, DF ],axis=1)
