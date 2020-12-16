###########################################################
# File: tutorial_VilageFcstInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 15, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from openAPI_KMA import VilageFcstInfoService
from datetime import datetime

ServiceKey = " 이곳에 Data.go.kr에서 발급받은 ServiceKey를 입력하세요. "

KMA = VilageFcstInfoService(ServiceKey)

""" data.kma.go.kr -> 소통과 참여 -> 자료실 -> 동네예보 지점 좌표(위도,경도) 정보
    에 가시면 조회에 필요한 X, Y 정보가 행정구역별 정의되어 있습니다. """
X, Y = 59, 125 #서울 동작구 신대방 X59, Y125 	

""" 모든 예보는 현재기준 24시간 안에서만 조회 가능합니다. """
# #현재 시점을 기준으로 최신 예보정보를 조회하겠습니다. 
time = datetime.now()
#time = datetime.strptime("2020-12-15 10:59:00","%Y-%m-%d %H:%M:%S")
print(f"[Time: {time:%Y-%m-%d %H:%M} 동네예보 조회서비스]")


# #==========================================================================================
# #동네예보 발표시각(baseTime) 계산
baseTime = KMA.get_VilageFcst_baseTime(time)['baseTime']

# #동네예보 버전 조회 ------------------------------------------------------------------------
version  = KMA.getFcstVersion("SHRT", baseTime) 
# #버전정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
#version  = KMA.getFcstVersion("SHRT", baseTime, save_path = "./test_VilageFcstInfoService_FcstVersion.xml") 
print(f"baseTime of VilageFcst: {baseTime:%Y-%m-%d %H:%M}(ver.{version:%Y.%m.%d.%H.%M})")

# #동네예보 조회 
df_VilageFcst = KMA.getVilageFcst(X, Y, time)
print(df_VilageFcst, "\n")
# #예보정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
#df_VilageFcst = KMA.getVilageFcst(X, Y, time, save_path="./test_VilageFcstInfoService_VilageFcst.xml")

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_VilageFcst.to_csv("./test_VilageFcstInfoService_VilageFcst.csv", encoding='utf-8')


# #초단기예보 버전 조회 -----------------------------------------------------------------------
baseTime = KMA.get_UltraSrtFcst_baseTime(time)['baseTime']
version  = KMA.getFcstVersion("VSRT", baseTime)
print(f"baseTime of UltraSrtFcst: {baseTime:%Y-%m-%d %H:%M}(ver.{version:%Y.%m.%d.%H.%M})")
# #초단기예보 조회
df_UltraSrtFcst = KMA.getUltraSrtFcst(X, Y, time) 
print(df_UltraSrtFcst, "\n")
df_UltraSrtFcst.to_csv("./test_VilageFcstInfoService_UltraSrtFcst.csv", encoding='utf-8')

# #초단기실황 버전 조회 -----------------------------------------------------------------------
baseTime = KMA.get_UltraSrtNcst_baseTime(time)['baseTime']
version  = KMA.getFcstVersion("ODAM", baseTime)
print(f"baseTime of UltraSrtNcst: {baseTime:%Y-%m-%d %H:%M}(ver.{version:%Y.%m.%d.%H.%M})")
# #초단기실황 조회
df_UltraSrtNcst = KMA.getUltraSrtNcst(X, Y, time) 
print(df_UltraSrtNcst, "\n")
df_UltraSrtNcst.to_csv("./test_VilageFcstInfoService_UltraSrtNcst.csv", encoding='utf-8')
# #==========================================================================================
