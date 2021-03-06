###########################################################
#                        지상(종관, ASOS) 시간자료 조회서비스
#
# File: tutorial_AsosHourlyInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Apr. 26, 2021
# eom.taeyoon.kor@gmail.com
###########################################################

from openKMA import AsosHourlyInfoService
from datetime import datetime, timedelta

ServiceKey = "BdJLVP6Ht6Z41L%2B5lMY8Fzeyob4xWJwkdI2a%2BHZ6aN7yWYjS6n9DAUGSPGf%2FZXujsUFZ2r4XH4hs7UjQSILr%2Fw%3D%3D"

KMA = AsosHourlyInfoService(ServiceKey)

""" data.kma.go.kr -> 데이터 -> 메타데이터 -> 지점정보
    에 가시면 조회에 필요한 지점번호를 찾을 수 있습니다. """
stnIds = 108 #지점번호, 서울 108

""" 종관기상관측 정보는 지점별 운영기간에 대해서 모두 조회가능합니다.
    단, 전날 자료까지만 조회가 가능하며 서버 사정에 따라 갱신이 늦을 수 있습니다. """

# #==================================================================================================
# #현재 시점을 기준으로 전날 0 ~ 23시 -----------------------------------------------------------------
startDtHh = ( datetime.now() + timedelta(days=-1) ).replace(hour=0, minute=0, second=0, microsecond=0)
endDtHh   = startDtHh.replace(hour=23)
print(f"[Term: {startDtHh:%Y-%m-%d %H:%M} ~ {endDtHh:%Y-%m-%d %H:%M}] 지상(종관, ASOS) 시간자료 조회서비스")

# #전날 관측자료 조회 
df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh)
print(df_WthrDataList, '\n')

# #관측정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
#df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh,save_path="./test_AsosHourlyInfoService_WthrDataList.xml")

# #조회된 실제 URL주소를 보고싶으면 [ show_url = True ] 를 추가하세요.
#df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh,show_url=True)

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_WthrDataList.to_csv('./test_AsosHourlyInfoService_WthrDataList_yesterday.csv', encoding='euc-kr')
#df_WthrDataList.to_csv('./test_AsosHourlyInfoService_WthrDataList_yesterday.csv', encoding='utf-8')

# #2020년 12월 1일 0시부터 2020년 12월 15일 23시까지 관측자료 조회 -------------------------------------
""" 단, 한 번 최대 999개까지 조회되기 때문에 기간은 한 달이내로 설정하세요. 
    한 번 조회에 24시간을 권장을 합니다. """
startDtHh = datetime.strptime("2020-12-01 00:00:00", "%Y-%m-%d %H:%M:%S")
endDtHh   = datetime.strptime("2020-12-15 23:00:00", "%Y-%m-%d %H:%M:%S")
print(f"[Term: {startDtHh:%Y-%m-%d %H:%M} ~ {endDtHh:%Y-%m-%d %H:%M}]")

df_WthrDataList = KMA.getWthrDataList(stnIds,startDtHh,endDtHh)
print(df_WthrDataList)
df_WthrDataList.to_csv('./test_AsosHourlyInfoService_WthrDataList_15days.csv', encoding='euc-kr')

# #==================================================================================================
