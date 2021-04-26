###########################################################
#                                         동네예보 조회서비스
#
# File: tutorial_VilageFcstInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 15, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from openKMA import VilageFcstInfoService
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

# #==========================================================================================
# #예보 조회시간 및 버전 조회 -----------------------------------------------------------------
# #예보버전 조회는 예보 생산 시각으로 datetime 형식으로 base와 ver을 받습니다.
ftype    = "SHRT" #ODAM: 동네예보실황, -VSRT: 동네예보초단기, -SHRT: 동네예보단기
version  = KMA.getFcstVersion(ftype, time)
print(f"0. 예보버전 조회")
print(f"ftype         : {ftype}")
print(f"Request time  : {time}")
print(f"(basedatetime): {version['base']}")
print(f"(     version): {version['ver']}\n")
# #이후 예제에서 실질적으로 예보를 조회하는데 자동으로 요청하신 시간을 
# #가장 가까운 baseDateTime 으로 자동으로 계산하므로 크게 신경쓰지 않고 넘어가셔도 됩니다.
# #단, 문서를 통해 발표시간 및 버전에 대한 이해를 갖고 넘어가시길 추천드립니다.

# #동네예보 조회 -----------------------------------------------------------------------------
df_VilageFcst = KMA.getVilageFcst(X, Y, time)
print("1. 동네예보\n", df_VilageFcst, "\n")
# #예보정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
# #조회된 실제 URL주소를 보고싶으면 [ show_url = True ] 를 추가하세요.
#df_VilageFcst = KMA.getVilageFcst(X, Y, time, save_path="./test_VilageFcstInfoService_VilageFcst.xml")
#df_VilageFcst = KMA.getVilageFcst(X, Y, time, show_url=True)

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_VilageFcst.to_csv("./test_VilageFcstInfoService_VilageFcst.csv", encoding='utf-8')

# #초단기예보 조회 ---------------------------------------------------------------------------
df_UltraSrtFcst = KMA.getUltraSrtFcst(X, Y, time) 
print("2. 초단기예보\n", df_UltraSrtFcst, "\n")
df_UltraSrtFcst.to_csv("./test_VilageFcstInfoService_UltraSrtFcst.csv", encoding='utf-8')

# #초단기실황 조회 ---------------------------------------------------------------------------
df_UltraSrtNcst = KMA.getUltraSrtNcst(X, Y, time) 
print("3. 초단기실황\n", df_UltraSrtNcst)
df_UltraSrtNcst.to_csv("./test_VilageFcstInfoService_UltraSrtNcst.csv", encoding='utf-8')
# #==========================================================================================
