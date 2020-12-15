###########################################################
# File_name: tutorial_AsosHourlyInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 16, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from numpy.lib.npyio import save
from openAPI_KMA import AsosHourlyInfoService
from datetime import date, datetime, timedelta

ServiceKey = " 이곳에 Data.go.kr에서 발급받은 ServiceKey를 입력하세요. "

KMA = AsosHourlyInfoService(ServiceKey)

""" data.kma.go.kr -> 데이터 -> 메타데이터 -> 지점정보
    에 가시면 조회에 필요한 지점번호를 찾을 수 있습니다. """
stnIds = 108 #서울 108지점

""" 종관기상관측 정보는 지점별 운영기간에 대해서 모두 조회가능합니다.
    단, 전날 자료까지만 조회가 가능하며 서버 사정에 따라 갱신이 늦을 수 있습니다. """
# #현재 시점을 기준으로 전날 ----------------------------------------------------------------------
startDtHh = ( datetime.now() + timedelta(days=-1) ).replace(hour=0)
endDtHh   = startDtHh.replace(hour=23)

# #==============================================================================================
# #전날 관측자료 조회 -----------------------------------------------------------
df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh)
print(df_WthrDataList)
# #예보정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
#df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh,save_path="./file_name_Asos.xml")

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_WthrDataList.to_csv('./file_name_Asos_yesterday.csv', encoding='euc-kr')
#df_WthrDataList.to_csv('./file_name_Asos_yesterday.csv', encoding='utf-8')

# #2020년 12월 1일 0시부터 2020년 12월 15일 23시까지 관측자료 조회 ---------------------------------
""" 단, 한 번 최대 999개까지 조회되기 때문에 기간은 한 달이내로 설정하세요. 
    한 번 조회에 24시간을 권장을 합니다. """
startDtHh = datetime.strptime("2020-12-01 00:00:00", "%Y-%m-%d %H:%M:%S")
endDtHh   = datetime.strptime("2020-12-15 23:00:00", "%Y-%m-%d %H:%M:%S")

df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh)
print(df_WthrDataList)
df_WthrDataList.to_csv('./file_name_Asos_15days.csv', encoding='euc-kr')
# #==============================================================================================