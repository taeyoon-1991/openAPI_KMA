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
from urllib import request
from urllib.request import urlopen
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np

def _check_valid_time(time):
    gap = datetime.now() - time
    assert gap.days == 0 or gap.total_seconds() >= 0, \
    f"Request time shoud be within 24 hours from now, your time is {time}"

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

        _check_valid_time(fcst_time)
        return {"Production-time": fcst_time,"baseTime":fcst_time}
    
    def get_UltraSrtFcst_baseTime(self, time):
        fcst_time = time.replace(minute=30,second=0,microsecond=0)
        if time.minute < 30: fcst_time = fcst_time + timedelta(hours=-1)

        #Published after 15 mins of Production
        gap = datetime.now().replace(minute=45,second=0,microsecond=0) - time
        gap = gap.total_seconds()
        if gap < 15*60 and gap >= 0 : fcst_time = fcst_time + timedelta(hours=-1)             

        _check_valid_time(fcst_time)
        return {"Production-time": fcst_time,"baseTime":fcst_time}

    def get_UltraSrtNcst_baseTime(self, time):
        ncst_time = time.replace(minute=30,second=0,microsecond=0)
        if time.minute < 30: ncst_time = ncst_time + timedelta(hours=-1)
        
        #Published after 10 mins of Production
        gap = datetime.now().replace(minute=40,second=0,microsecond=0) - time
        gap = gap.total_seconds()
        if gap < 10*60 and gap >= 0: ncst_time = ncst_time + timedelta(hours=-1)

        _check_valid_time(ncst_time)
        return {"Production-time": ncst_time,"baseTime":ncst_time.replace(minute=0)}

    def getFcstVersion(self, ftype, basedatetime, save_path=False):
        assert ftype in ['ODAM','VSRT','SHRT'], f"ftype shoud be one of 'ODAM'/'VSRT'/'SHRT', (UltraSrtNcst-ODAM, UltraSrtFcst-VSRT, VilageFcst-SHRT)"
        
        _check_valid_time(basedatetime)        
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

    def getWthrDataList(self, stnIds, startDtHh, endDtHh, save_path=False):
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

        start = pd.to_datetime(startDtHh.replace(minute=0,second=0,microsecond=0))
        end   = pd.to_datetime(  endDtHh.replace(minute=0,second=0,microsecond=0))
        df_time = pd.DataFrame(index=(pd.date_range(start, end, freq='H')))
        return pd.concat([ df_time, DF ],axis=1)

class MidFcstInfoService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey

    def get_tmFc(self, time):
        time = time.replace(minute=0,second=0,microsecond=0)
        h = time.hour
        if   h >= 18: time = time.replace(hour=18)
        elif h >=  6: time = time.replace(hour= 6)
        else: time = ( time + timedelta(days=-1) ).replace(hour=18)

        _check_valid_time(time)
        return time

    def getMidFcst(self, stnId, tmFc, save_path=False):
        tmFc = self.get_tmFc(tmFc)

        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidFcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&stnId={stnId}"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree);DF['stnId'] = stnId;DF['tmFc']=tmFc
        DF.set_index('tmFc',inplace=True);DF.index = pd.to_datetime(DF.index)
        return DF
    
    def getMidTa(self, regId, tmFc, save_path=False):
        tmFc = self.get_tmFc(tmFc)

        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&regId={regId}"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        dic = DF.to_dict()
        DF = pd.DataFrame()
        for n in range(3-1,10+2):
            if not ( f'taMin{n}Low' in dic or f'taMin{n}' in dic or \
                     f'taMax{n}Low' in dic or f'taMax{n}' in dic): continue
            tmp = {'n_days_later': n , 
                   'Date'  : (tmFc + timedelta(days=+n)).date() }
            if f'taMin{n}Low'  in dic: tmp['taMinLow']  = dic[f'taMin{n}Low']
            if f'taMin{n}High' in dic: tmp['taMinHigh'] = dic[f'taMin{n}High']
            if f'taMin{n}'     in dic: tmp['taMin']     = dic[f'taMin{n}']
            if f'taMax{n}Low'  in dic: tmp['taMaxLow']  = dic[f'taMax{n}Low']
            if f'taMax{n}High' in dic: tmp['taMaxHigh'] = dic[f'taMax{n}High']
            if f'taMax{n}'     in dic: tmp['taMax']     = dic[f'taMax{n}']
            DF = DF.append(pd.DataFrame(tmp), ignore_index=True)
        DF['regId'] = regId;DF['tmFc'] = tmFc
        DF.set_index('Date',inplace=True);DF.index = pd.to_datetime(DF.index)
        return DF

    def getMidLandFcst(self, regId, tmFc, save_path=False):
        tmFc = self.get_tmFc(tmFc)
        
        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&regId={regId}"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        dic = DF.to_dict()
        DF = pd.DataFrame()
        for n in range(3-1,10+2):
            if not ( f'rnSt{n}Am' in dic or f'rnSt{n}' in dic or \
                     f'wf{n}Am'   in dic or f'wf{n}'  in dic ): continue
            tmp = {'n_days_later': n , 
                   'Date'  : (tmFc + timedelta(days=+n)).date() }
            if f'rnSt{n}Am' in dic: tmp['rnStAm'] = dic[f'rnSt{n}Am']
            if f'rnSt{n}Pm' in dic: tmp['rnStPm'] = dic[f'rnSt{n}Pm']
            if f'rnSt{n}'   in dic: tmp['rnSt']   = dic[f'rnSt{n}']
            if f'wf{n}Am'   in dic: tmp['wfAm']   = dic[f'wf{n}Am']
            if f'wf{n}Pm'   in dic: tmp['wfPm']   = dic[f'wf{n}Pm']
            if f'wf{n}'     in dic: tmp['wf']     = dic[f'wf{n}']
            DF = DF.append(pd.DataFrame(tmp), ignore_index=True)
        DF['regId'] = regId;DF['tmFc'] = tmFc
        DF.set_index('Date',inplace=True);DF.index = pd.to_datetime(DF.index)
        return DF

    def getMidSeaFcst(self, regId, tmFc, save_path=False):
        tmFc = self.get_tmFc(tmFc)
        
        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidSeaFcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&regId={regId}"

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        dic = DF.to_dict()
        DF = pd.DataFrame()
        for n in range(3-1,10+2):
            if not ( f'wh{n}AAm' in dic or f'wh{n}BAM' in dic or \
                     f'wh{n}A'   in dic or f'wf{n}Am'  in dic or \
                     f'wf{n}'    in dic ): continue
            tmp = {'n_days_later': n , 
                   'Date'  : (tmFc + timedelta(days=+n)).date() }
            if f'wh{n}AAm' in dic: tmp['whAAm'] = dic[f'wh{n}AAm']
            if f'wh{n}APm' in dic: tmp['whAPm'] = dic[f'wh{n}APm']
            if f'wh{n}BAm' in dic: tmp['whBAm'] = dic[f'wh{n}BAm']
            if f'wh{n}BPm' in dic: tmp['whBPm'] = dic[f'wh{n}BPm']
            if f'wh{n}A'   in dic: tmp['whA']   = dic[f'wh{n}A']
            if f'wh{n}B'   in dic: tmp['whB']   = dic[f'wh{n}B']
            if f'wf{n}Am'   in dic: tmp['wfAm'] = dic[f'wf{n}Am']
            if f'wf{n}Pm'   in dic: tmp['wfPm'] = dic[f'wf{n}Pm']
            if f'wf{n}'     in dic: tmp['wf']   = dic[f'wf{n}']
            DF = DF.append(pd.DataFrame(tmp), ignore_index=True)
        DF['regId'] = regId;DF['tmFc'] = tmFc
        DF.set_index('Date',inplace=True);DF.index = pd.to_datetime(DF.index)
        return DF
