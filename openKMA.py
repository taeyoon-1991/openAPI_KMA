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

    def __get_baseTime_VilageFcst(self, time):
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
    
    def __get_baseTime_UltraSrtFcst(self, time):
        fcst_time = time.replace(minute=30,second=0,microsecond=0)
        if time.minute < 30: fcst_time = fcst_time + timedelta(hours=-1)

        #Published after 15 mins of Production
        gap = datetime.now().replace(minute=45,second=0,microsecond=0) - time
        gap = gap.total_seconds()
        if gap < 15*60 and gap >= 0 : fcst_time = fcst_time + timedelta(hours=-1)             

        _check_valid_time(fcst_time)
        return {"Production-time": fcst_time,"baseTime":fcst_time}

    def __get_baseTime_UltraSrtNcst(self, time):
        ncst_time = time.replace(minute=30,second=0,microsecond=0)
        if time.minute < 30: ncst_time = ncst_time + timedelta(hours=-1)
        
        #Published after 10 mins of Production
        gap = datetime.now().replace(minute=40,second=0,microsecond=0) - time
        gap = gap.total_seconds()
        if gap < 10*60 and gap >= 0: ncst_time = ncst_time + timedelta(hours=-1)

        _check_valid_time(ncst_time)
        return {"Production-time": ncst_time,"baseTime":ncst_time.replace(minute=0)}

    def getFcstVersion(self, ftype, time, save_path=False, show_url=False):
        assert ftype in ['ODAM','VSRT','SHRT'], \
            f"ftype shoud be one of 'ODAM'/'VSRT'/'SHRT', (UltraSrtNcst-ODAM, UltraSrtFcst-VSRT, VilageFcst-SHRT)"
        
        basedatetime = ''
        if   ftype == 'ODAM': basedatetime = self.__get_baseTime_UltraSrtNcst(time)['baseTime']
        elif ftype == 'VSRT': basedatetime = self.__get_baseTime_UltraSrtFcst(time)['baseTime']
        else:                 basedatetime = self.__get_baseTime_VilageFcst(time)['baseTime'] # <-SHRT
        _check_valid_time(basedatetime)

        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getFcstVersion"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=10&dataType=XML"
        url = f"{url}&ftype={ftype}&basedatetime={basedatetime:%Y%m%d%H%M}&"
        if show_url: print(url)

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
                            return {'base':basedatetime, 'ver':version}
            else: assert False, f"{ftype},{basedatetime}: {resultMsg}({resultCode})"

    def __get_Fcst(self, X, Y, save_path, show_url, ftype, version):
        baseDate = version['base'].strftime("%Y%m%d")
        baseTime = version['base'].strftime("%H%M")

        url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService/get{ftype}"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&base_date={baseDate}&base_time={baseTime}"
        url = f"{url}&nx={X}&ny={Y}"
        if show_url: print(url)

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
        DF['version'] = version['ver']
        DF.index.name = 'fcstDateTime'
        return DF

    def __get_Ncst(self, X, Y, save_path, show_url, version):
        baseDate = version['base'].strftime("%Y%m%d")
        baseTime = version['base'].strftime("%H%M")

        url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtNcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&base_date={baseDate}&base_time={baseTime}"
        url = f"{url}&nx={X}&ny={Y}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        DF['baseDateTime'] = DF['baseDate'] + DF['baseTime']
        nx = DF['nx'][0];ny = DF['ny'][0]
        DF.set_index(pd.to_datetime(DF['baseDateTime'],format="%Y%m%d%H%M"),inplace=True)
        DF = DF.groupby([DF.index, 'category'])['obsrValue'].aggregate('first').unstack()
        DF = DF.to_dict('index');DF = pd.DataFrame.from_dict(DF, orient='index')
        DF['nx']=nx;DF['ny']=ny;DF['type']='UltraSrtNcst'
        DF['version'] = version['ver']
        DF.index.name = 'baseDateTime'
        return DF


    def getVilageFcst(self, X, Y, time, save_path=False, show_url=False):
        version = self.getFcstVersion('SHRT', time)
        return self.__get_Fcst(X,Y,save_path,show_url,'VilageFcst',version)

    def getUltraSrtFcst(self, X, Y, time, save_path=False, show_url=False):
        version = self.getFcstVersion('VSRT', time)
        return self.__get_Fcst(X,Y,save_path,show_url,'UltraSrtFcst',version)

    def getUltraSrtNcst(self, X, Y, time, save_path=False, show_url=False):
        version = self.getFcstVersion('ODAM', time)
        return self.__get_Ncst(X,Y,save_path,show_url,version)

class AsosHourlyInfoService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey

    def getWthrDataList(self, stnIds, startDtHh, endDtHh, save_path=False, show_url=False):
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
        url = f"{url}&endDt={endDt}&endHh={endHh}&stnIds={stnIds}"
        #url = f"{url}&stnIds={stnIds}&schListCnt=999"
        if show_url: print(url)

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

    def __get_tmFc(self, time):
        time = time.replace(minute=0,second=0,microsecond=0)
        h = time.hour
        if   h >= 18: time = time.replace(hour=18)
        elif h >=  6: time = time.replace(hour= 6)
        else: time = ( time + timedelta(days=-1) ).replace(hour=18)

        _check_valid_time(time)
        return time

    def getMidFcst(self, stnId, tmFc, save_path=False, show_url=False):
        tmFc = self.__get_tmFc(tmFc)

        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidFcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&stnId={stnId}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree);DF['stnId'] = stnId;DF['tmFc']=tmFc
        DF.set_index('tmFc',inplace=True);DF.index = pd.to_datetime(DF.index)
        return DF
    
    def getMidTa(self, regId, tmFc, save_path=False, show_url=False):
        tmFc = self.__get_tmFc(tmFc)

        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&regId={regId}"
        if show_url: print(url)

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

    def getMidLandFcst(self, regId, tmFc, save_path=False, show_url=False):
        tmFc = self.__get_tmFc(tmFc)
        
        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&regId={regId}"
        if show_url: print(url)

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

    def getMidSeaFcst(self, regId, tmFc, save_path=False, show_url=False):
        tmFc = self.__get_tmFc(tmFc)
        
        url = f"http://apis.data.go.kr/1360000/MidFcstInfoService/getMidSeaFcst"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&tmFc={tmFc:%Y%m%d%H%M}&regId={regId}"
        if show_url: print(url)

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

class AsosDalyInfoService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey

    def getWthrDataList(self, stnIds, startDt, endDt, save_path=False, show_url=False):
        stnIds = stnIds
        startDt = startDt.date()
        endDt   = endDt.date()

        url = f"http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&dataCd=ASOS&dateCd=DAY"
        url = f"{url}&startDt={startDt:%Y%m%d}&endDt={endDt:%Y%m%d}&stnIds={stnIds}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        DF.set_index('tm',inplace=True);DF.index = pd.to_datetime(DF.index)
        DF.sort_index(inplace=True);DF.drop('item',axis=1,inplace=True)
        DF.index.name = 'tm'

        start = pd.to_datetime(startDt)
        end   = pd.to_datetime(  endDt)
        df_time = pd.DataFrame(index=(pd.date_range(start, end, freq='D')))
        return pd.concat([ df_time, DF ],axis=1)

class VilageFcstMsgService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey
            
    def getWthrSituation(self, stnId, save_path=False, show_url=False):
        url = f"http://apis.data.go.kr/1360000/VilageFcstMsgService/getWthrSituation"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&stnId={stnId}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree);DF['stnId'] = stnId
        DF.set_index('tmFc',inplace=True);DF.index = pd.to_datetime(DF.index)
        DF['requestTime']  = pd.to_datetime(datetime.now().replace(microsecond=0))
        return DF

    def __get_Fcst(self, regId, save_path, show_url, ftype):
        url = f"http://apis.data.go.kr/1360000/VilageFcstMsgService/get{ftype}"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&regId={regId}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = _xml_to_dataframe(tree)
        DF.set_index('numEf',inplace=True)
        if ftype == 'LandFcst':
            DF['announceTime'] = pd.to_datetime(DF['announceTime'],format="%Y%m%d%H%M")
        else :#ftype == 'SeaFcst':
            DF['tmFc'] = pd.to_datetime(DF['tmFc'],format="%Y%m%d%H%M")
        DF['requestTime']  = pd.to_datetime(datetime.now().replace(microsecond=0))
        return DF

    def getLandFcst(self, regId, save_path=False, show_url=False):
        return self.__get_Fcst(regId, save_path, show_url, 'LandFcst')

    def getSeaFcst(self, regId, save_path=False, show_url=False):
        return self.__get_Fcst(regId, save_path, show_url, 'SeaFcst')

class WthrWrnInfoService:
    def __init__(self, ServiceKey=''):
        self.ServiceKey	= ServiceKey

    def __xml_to_dataframe(self, tree):
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
            elif resultCode == "03": return pd.DataFrame()
            else: assert False, f"NOT NORMAL RESPONSE OF API: {resultMsg}({resultCode})"
        return pd.DataFrame(list_data)

    def __get_Wthr(self, stnId, fromTmFc, toTmFc, save_path, show_url, ftype):
        url = f"http://apis.data.go.kr/1360000/WthrWrnInfoService/getWthr{ftype}"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&stnId={stnId}"
        url = f"{url}&fromTmFc={fromTmFc:%Y%m%d}&toTmFc={toTmFc:%Y%m%d}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = self.__xml_to_dataframe(tree)
        if DF.empty: return DF
        DF['tmFc'] = pd.to_datetime(DF['tmFc'],format="%Y%m%d%H%M")
        DF.set_index('tmFc',inplace=True)
        if ftype == 'WrnMsg': DF['t5'] = pd.to_datetime(DF['t5'],format="%Y%m%d%H%M")
        return DF

    def getWthrWrnList(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"WrnList")
    
    def getWthrWrnMsg(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"WrnMsg")

    def getWthrInfoList(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"InfoList")
    
    def getWthrInfo(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"Info")
        
    def getWthrBrkNewsList(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"BrkNewsList")
    
    def getWthrBrkNews(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"BrkNews")
    
    def getWthrPwnList(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"PwnList")
    
    def getWthrPwn(self, stnId, fromTmFc, toTmFc, save_path=False, show_url=False):
        return self.__get_Wthr(stnId,fromTmFc,toTmFc,save_path,show_url,"Pwn")
    
    def getPwnCd(self, stnId, fromTmFc, toTmFc, areaCode, warningType, save_path=False, show_url=False):
        url = f"http://apis.data.go.kr/1360000/WthrWrnInfoService/getPwnCd"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        url = f"{url}&stnId={stnId}"
        url = f"{url}&fromTmFc={fromTmFc:%Y%m%d}&toTmFc={toTmFc:%Y%m%d}"
        url = f"{url}&areaCode={areaCode}&warningType={warningType}"
        if show_url: print(url)

        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = self.__xml_to_dataframe(tree)
        if DF.empty: return DF
        DF['tmFc']      = pd.to_datetime(DF['tmFc'],format="%Y%m%d%H%M")
        DF['startTime'] = pd.to_datetime(DF['startTime'],format="%Y%m%d%H%M")
        DF.set_index('tmFc',inplace=True)
        return DF

    def getPwnStatus(self, save_path=False, show_url=False):
        url = f"http://apis.data.go.kr/1360000/WthrWrnInfoService/getPwnStatus"
        url = f"{url}?serviceKey={self.ServiceKey}"
        url = f"{url}&pageNo=1&numOfRows=999&dataType=XML"
        if show_url: print(url)
        
        tree = ET.parse(urlopen(url), parser=ET.XMLParser(encoding='utf-8'))
        if save_path: tree.write(save_path, encoding='utf-8')

        DF = self.__xml_to_dataframe(tree)
        if DF.empty: return DF
        DF['tmEf'] = pd.to_datetime(DF['tmEf'],format="%Y%m%d%H%M")
        DF['tmFc'] = pd.to_datetime(DF['tmFc'],format="%Y%m%d%H%M")
        DF.set_index('tmFc',inplace=True)
        return DF
