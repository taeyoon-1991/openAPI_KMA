###########################################################
# File: tutorial_MidFcstInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 17, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from openAPI_KMA import MidFcstInfoService
from datetime import datetime, time, timedelta

ServiceKey = " 이곳에 Data.go.kr에서 발급받은 ServiceKey를 입력하세요. "
ServiceKey = "BdJLVP6Ht6Z41L%2B5lMY8Fzeyob4xWJwkdI2a%2BHZ6aN7yWYjS6n9DAUGSPGf%2FZXujsUFZ2r4XH4hs7UjQSILr%2Fw%3D%3D"

KMA = MidFcstInfoService(ServiceKey)

""" 모든 예보는 현재기준 24시간 안에서만 조회 가능합니다. """
# #현재 시점을 기준으로 최신 예보정보를 조회하겠습니다. 
time = datetime.now()
#time = datetime.strptime("2020-12-15 10:59:00","%Y-%m-%d %H:%M:%S")
print(f"[Time: {time:%Y-%m-%d %H:%M}] 중기예보 조회서비스")

# #중기예보 발표시각(tmFc) 계산
tmFc = KMA.get_tmFc(time)

# #=====================================================================================
# #중기전망 조회 ------------------------------------------------------------------------
stnId = 108
df_MidFcst = KMA.getMidFcst(stnId, time)
print(df_MidFcst, '\n')
# #예보정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
#df_MidFcst = KMA.getMidFcst(stnId, time, save_path="./file_name_data.xml")

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_MidFcst.to_csv('./test_MidFcstInfoService_MidFcst.csv',encoding='euc-kr')

# #중기기온 조회 ------------------------------------------------------------------------
regId = '11B10101'
df_MidTa = KMA.getMidTa(regId, time)
print(df_MidTa, '\n')
df_MidTa.to_csv('./test_MidFcstInfoService_MidTa.csv',encoding='euc-kr')

# #중기육상예보 조회 --------------------------------------------------------------------
regId = '11B00000'
df_MidLandFcst = KMA.getMidLandFcst(regId, time)
print(df_MidLandFcst, '\n')
df_MidLandFcst.to_csv('./test_MidFcstInfoService_MidLandFcst.csv',encoding='euc-kr')

# #중기해상예보 조회 --------------------------------------------------------------------
regId = '12A20000'
df_MidSeaFcst = KMA.getMidSeaFcst(regId, time)
print(df_MidSeaFcst, '\n')
df_MidSeaFcst.to_csv('./test_MidFcstInfoService_MidSeaFcst.csv',encoding='euc-kr')
# #=====================================================================================
