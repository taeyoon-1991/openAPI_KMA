###########################################################
#                                  동네예보 통보문 조회서비스
#
# File: tutorial_VilageFcstMsgService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 19, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from openAPI_KMA import VilageFcstMsgService

ServiceKey = " 이곳에 Data.go.kr에서 발급받은 ServiceKey를 입력하세요. "

KMA = VilageFcstMsgService(ServiceKey)

""" 동네예보 통보문은 현재기준 최신 정보만 조회 가능합니다. """

# #=====================================================================================
# #기상개황 조회 ------------------------------------------------------------------------
stnId = '108' #발표관서
df_WthrSituation = KMA.getWthrSituation(stnId)
print("1. 기상개황\n", df_WthrSituation, '\n')
# #개황정보를 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
# #조회된 실제 URL주소를 보고싶으면 [ show_url = True ] 를 추가하세요.
#df_WthrSituation = KMA.getWthrSituation(stnId, save_path="./test_VilageFcstMsgService_WthrSituation.xml")
#df_WthrSituation = KMA.getWthrSituation(stnId, show_url=True)

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_WthrSituation.to_csv('./test_VilageFcstMsgService_WthrSituation.csv', encoding='euc-kr')

# #육상예보 조회 ------------------------------------------------------------------------
regId = '11A00101' #예보구역코드
df_LandFcst = KMA.getLandFcst(regId)
print("2. 육상예보\n", df_LandFcst, '\n')
df_LandFcst.to_csv('./test_VilageFcstMsgService_LandFcst.csv', encoding='euc-kr')

# #해상예보 조회 ------------------------------------------------------------------------
regId = '12A20100' #예보구역코드
df_SeaFcst = KMA.getSeaFcst(regId)
print("3. 해상예보\n", df_SeaFcst)
df_SeaFcst.to_csv('./test_VilageFcstMsgService_SeaFcst.csv', encoding='euc-kr')
# #=====================================================================================
