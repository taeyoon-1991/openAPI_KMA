###########################################################
#                                        기상특보 조회서비스
#
# File: tutorial_WthrWrnInfoService.py
#
# Python == 3.8.5
#
# Created by 엄태윤 on Dec. 19, 2020
# Email: eom.taeyoon.kor@gmail.com
###########################################################

from openAPI_KMA import WthrWrnInfoService
from datetime import datetime, timedelta

ServiceKey = " 이곳에 Data.go.kr에서 발급받은 ServiceKey를 입력하세요. "
ServiceKey = "BdJLVP6Ht6Z41L%2B5lMY8Fzeyob4xWJwkdI2a%2BHZ6aN7yWYjS6n9DAUGSPGf%2FZXujsUFZ2r4XH4hs7UjQSILr%2Fw%3D%3D"

KMA = WthrWrnInfoService(ServiceKey)

""" 기상특보는 현재기준 최대 6일 전까지만 조회 가능합니다. """

# #현재 시점을 기준으로 최근 5일 동안 기상특보를 조회하겠습니다. 
toTmFc   = datetime.now()
fromTmFc = toTmFc + timedelta(days=-5)

# #=====================================================================================
# #기상특보목록 조회 --------------------------------------------------------------------
stnId = 108
df_WthrWrnList = KMA.getWthrWrnList(stnId, fromTmFc, toTmFc)
print("1-1. 기상특보목록\n", df_WthrWrnList, '\n')
# #기상특보목록을 XML파일로 저장하고 싶으면 [ save_path = "./file_name.xml" ] 를 추가하세요.
# #조회된 실제 URL주소를 보고싶으면 [ show_url = True ] 를 추가하세요.
#df_WthrWrnList = KMA.getWthrWrnList(stnId, fromTmFc, toTmFc, save_path='./test_WthrWrnInfoService_WthrWrnList.xml')
#df_WthrWrnList = KMA.getWthrWrnList(stnId, fromTmFc, toTmFc, show_url=True)

# #데이터프레임을 CSV파일로 저장하고 싶으면 [ .to_csv("./file_name.csv") ] 를 붙이세요.
df_WthrWrnList.to_csv('./test_WthrWrnInfoService_WthrWrnList.csv', encoding='euc-kr')

# #기상특보통보문 조회 -------------------------------------------------------------------
df_WthrWrnMsg = KMA.getWthrWrnMsg(stnId, fromTmFc, toTmFc)
print("1-2. 기상특보통보문\n", df_WthrWrnMsg, '\n')
df_WthrWrnMsg.to_csv('./test_WthrWrnInfoService_WthrWrnMsg.csv', encoding='euc-kr')

# #기상정보목록 조회 --------------------------------------------------------------------
df_WthrInfoList = KMA.getWthrInfoList(stnId, fromTmFc, toTmFc)
print("2-1. 기상정보목록\n", df_WthrInfoList, '\n')
df_WthrInfoList.to_csv('./test_WthrWrnInfoService_WthrInfoList.csv', encoding='euc-kr')

# #기상정보문 조회 ----------------------------------------------------------------------
df_WthrInfo = KMA.getWthrInfo(stnId, fromTmFc, toTmFc)
print("2-2. 기상정보문\n", df_WthrInfo, '\n')
df_WthrInfo.to_csv('./test_WthrWrnInfoService_WthrInfo.csv', encoding='euc-kr')

# #기상속보목록 조회 --------------------------------------------------------------------
df_WthrBrkNewsList = KMA.getWthrBrkNewsList(stnId, fromTmFc, toTmFc)
print("3-1. 기상속보목록\n", df_WthrBrkNewsList, '\n')
df_WthrBrkNewsList.to_csv('./test_WthrWrnInfoService_WthrBrkNewsList.csv', encoding='euc-kr')

# #기상속보 조회 ------------------------------------------------------------------------
df_WthrBrkNews = KMA.getWthrBrkNews(stnId, fromTmFc, toTmFc)
print("3-2. 기상속보\n", df_WthrBrkNews, '\n')
df_WthrBrkNews.to_csv('./test_WthrWrnInfoService_WthrBrkNews.csv', encoding='euc-kr')

# #기상예비특보목록 조회 -----------------------------------------------------------------
df_WthrPwnList = KMA.getWthrPwnList(stnId, fromTmFc, toTmFc)
print("4-1. 기상예비특보목록\n", df_WthrPwnList, '\n')
df_WthrPwnList.to_csv('./test_WthrWrnInfoService_WthrPwnList.csv', encoding='euc-kr')

# #기상예비특보 조회 --------------------------------------------------------------------
df_WthrPwn = KMA.getWthrPwn(stnId, fromTmFc, toTmFc)
print("4-2. 기상예비특보\n", df_WthrPwn, '\n')
df_WthrPwn.to_csv('./test_WthrWrnInfoService_WthrPwn.csv', encoding='euc-kr')

# #특보코드 조회 ------------------------------------------------------------------------
areaCode    = 'L1070100' #특보구역코드
warningType = 4 #1-강풍, 2-호우, 3-한파, 4-건조,5-폭풍해일, 6-풍랑,7-태풍, 8-대설,9-황사, 12-폭염
df_PwnCd = KMA.getPwnCd(stnId, fromTmFc, toTmFc, areaCode, warningType)
print("5. 특보코드\n", df_PwnCd, '\n')
df_PwnCd.to_csv('./test_WthrWrnInfoService_PwnCd.csv', encoding='euc-kr')

# #특보현황 조회 ------------------------------------------------------------------------
df_PwnStatus = KMA.getPwnStatus()
print("6. 특보현황\n", df_PwnStatus, '\n')
df_PwnStatus.to_csv('./test_WthrWrnInfoService_PwnStatus.csv', encoding='euc-kr')
# #=====================================================================================
