###########################################################
# File: tutorial_AsosDalyInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 18, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from openAPI_KMA import AsosDalyInfoService
from datetime import datetime, timedelta

ServiceKey = " 이곳에 Data.go.kr에서 발급받은 ServiceKey를 입력하세요. "

KMA = AsosDalyInfoService(ServiceKey)

""" data.kma.go.kr -> 데이터 -> 메타데이터 -> 지점정보
    에 가시면 조회에 필요한 지점번호를 찾을 수 있습니다. """
stnIds = 108 #서울 108지점

""" 종관기상관측 정보는 지점별 운영기간에 대해서 모두 조회가능합니다.
    단, 전날 자료까지만 조회가 가능하며 서버 사정에 따라 갱신이 늦을 수 있습니다. """
# #현재 시점을 기준으로 15일 전부터 전날까지 자료 조회 -----------------------------------------------------
startDt = ( datetime.now() + timedelta(days=-15) )
endDt   = ( datetime.now() + timedelta(days= -1) )
print(f"[Term: {startDt:%Y-%m-%d} ~ {endDt:%Y-%m-%d}] 지상(종관, ASOS) 일자료 조회서비스")

# #==============================================================================================
# #최근 15일 동안 관측자료 조회 ------------------------------------------------------------------
df_WthrDataList = KMA.getWthrDataList(stnIds,startDt,endDt)
print(df_WthrDataList, '\n')
# #관측정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
# #조회된 실제 URL주소를 보고싶으면 [ show_url = True ] 를 추가하세요.
#df_WthrDataList = KMA.getWthrDataList(stnIds,startDt,endDt,save_path="./test_AsosDalyInfoService_WthrDataList.xml")
#df_WthrDataList = KMA.getWthrDataList(stnIds,startDt,endDt,show_url=True)

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_WthrDataList.to_csv('./test_AsosDalyInfoService_WthrDataList_15days.csv', encoding='euc-kr')
#df_WthrDataList.to_csv('./test_AsosHourlyInfoService_WthrDataList_yesterday.csv', encoding='utf-8')
# #==============================================================================================
