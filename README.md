# 소개
[공공데이터 포털](https://Data.go.kr)은 [기상자료개방포털](https://data.kma.go.kr)과 연계해서 기상예보 및 관측 등 다양한 서비스를 제공합니다.  
본 모듈은 **Python3** 와 더불어 데이터 사이언스 분야에 많이 활용되는 **Numpy** 와 **Pandas** 를 사용합니다.  
포함된 모든 기능은 익숙한 형태의 **Dataframe** 형식으로 변환하는데 초점을 맞췄습니다.  
서비스별 상세 가이드는 [DOCUMENT](DOCUMENT/) 디렉토리에 Word 파일로 포함되어 있습니다. 

(2020년 12월 18일 기준)
* [동네예보 조회서비스(VilageFcstInfoService)](DOCUMENT/기상청18_동네예보&#32;조회서비스_오픈API활용가이드.docx)
* [중기예보 조회서비스(MidFcstInfoService)](DOCUMENT/기상청20_중기예보&#32;조회서비스_오픈API활용가이드.docx)
* [지상(종관, ASOS) 시간자료 조회서비스(AsosHourlyInfoService)](DOCUMENT/기상청01_지상(종관,ASOS)시간자료_조회서비스_오픈API활용가이드.docx)
* [지상(종관, ASOS) 일자료 조회서비스(AsosHourlyInfoService)](DOCUMENT/기상청02_지상(종관,ASOS)일자료_조회서비스_오픈API활용가이드.docx)

  <details>
    <summary>(예정)</summary>

    * 동네예보 통보문 조회서비스(VilageFcstMsgService)  
    * 기상특보 조회서비스(WthrWrnInfoService)  
    * 생활기상지수 조회서비스(LivingWthrIdxService01)  
    * 태풍정보 조회서비스(TyphoonInfoService)  
    * 기상청_지진정보(EqkInfoService)  
    * 관광코스별 관광지 상세 날씨 조회서비스(TourStnInfoService)  
    * 위성영상 조회서비스(getInsightSatlit)  
    * 보건기상지수 조회서비스(HealthWthrIdxService)  
    * 레이더영상 조회서비스(RadarImgInfoService)  
    * 지상(방재, AWS)기상관측자료 조회서비스(Aws1miInfoService)  
    * CCTV 기반 도로날씨정보 조회서비스(RoadWthrInfoService)  
    * 낙뢰분포도 조회서비스(LgtDistrbInfoService)  
    * 작물별 농업주산지 상세날씨 조회서비스(FmlandWthrInfoService)  
    * 수치모델자료(경량화) 조회서비스(NwpModelInfoService)  
    * 위성자료(경량화) 조회서비스(WthrSatlitInfoService)  
    * 지상기상월보 조회서비스(SfcMtlyInfoService)  
    * 레이더관측자료 조회서비스(RadarObsInfoService)  
    * 일기도 조회서비스(WthrChartInfoService)  
    * 낙뢰관측자료 조회서비스(LgtInfoService)  
    * 항공기상전문(IWXXMVer.2.0) 조회서비스(AmmIwxxmService)  
    * 해양기상관측자료 조회서비스(OceanInfoService)  
    * 서리발생 가능성 예측정보 조회서비스(FrstFcstInfoService)  
    * 지상기상연보 조회서비스(SfcYearlyInfoService)  
    * 레이더자료(경량화) 조회서비스(WthrRadarInfoService)  
    * 방재기상월보 조회서비스(AwsMtlyInfoService)  
    * 해양기상월보 조회서비스(SeaMtlyInfoService)  
    * 항공기상전문 조회서비스(AmmService)_기상청에서 운영하는 관측지점, 기상예보구역, 기상특보구역 등에 대한 정보를 제공합니다. ※ 방재기상업무 수행을 위해 공공기관에 한해서 제공하는 자료입니다. 활용목적을 정확히 적어주시기 바랍니다.  
    * 지점정보(기상관측, 특보구역) 조회서비스(WethrBasicInfoService)  
    * 황사정보 조회서비스(YdstInfoService)_황사일기도, 황사관측값, 황사위성영상 정보를 조회하는 서비스 ※ 방재기상업무 수행을 위해 공공기관에 한해서 제공하는 자료입니다. 활용목적을 정확히 적어주시기 바랍니다.  
    * 고층기상월보 조회서비스(UppMtlyInfoService)  
    * 방재기상연보 조회서비스(AwsYearlyInfoService)  
    * 세계공항 항공기상전문 조회서비스(AftnAmmService)  
    * 고층기상관측자료 조회서비스(UppInfoService)  
  </details>

# 설치방법
**"openAPI_KMA.py"** 모듈을 사용하고자 하는 프로젝트 폴더에 저장 후 해당 프로젝트에 import 하십시오.  
필요한 서비스 종류에 따라 from 을 사용하실 것을 권장합니다.  
예시) **from** openAPI_KMA **import** VilageFcstInfoService

# 사용방법
## 사전준비
### API 인증키 발급
[공공데이터 포털](https://Data.go.kr)에 가입해서 원하는 서비스에 대하여 활용신청을 합니다.  
마이페이지에서 해당 서비스 정보를 확인하면 "일반 인증키" 항목이 표시됩니다.  
"일반 인증키"는 본 모듈의 ServiceKey 로 사용되며 외부로 노출되지 않게 주의하십시오.  

<details>
  <summary><strong>1. 예보정보 관련 서비스</strong></summary>
    
  ## 동네예보 조회서비스(VilageFcstInfoService)
  사용예시: [tutorial_VilageFcstInfoService.py](tutorial_VilageFcstInfoService.py)

  |서비스명|기능|인자|기타|
  |------|---|---|---|
  |예보버전조회|**getFcstVersion**|서비스구분, 발표시각|'ODAM':실황/'VSRT':초단기예보/'SHRT':동네예보|
  |동네예보조회|**getVilageFcst**|X좌표, Y좌표, 발표시각|get_VilageFcst_baseTime(조회시간)|
  |초단기예보조회|**getUltraSrtFcst**|X좌표, Y좌표, 발표시각|get_UltraSrtFcst_baseTime(조회시간)|
  |초단기실황조회|**getUltraSrtNcst**|X좌표, Y좌표, 발표시각|get_UltraSrtNcst_baseTime(조회시간)|

  * 서비스별 발표시각은 조회시간 직전으로 자동 설정되며, 24시간 이내에 자료만 조회가 가능합니다.  
  * [동네예보 지점 좌표(위도 경도)_(20200401 기준)](METADATA/동네예보&#32;지점&#32;좌표(위도&#32;경도)_(20200401&#32;기준).csv)  
  * [기상청18_동네예보 조회서비스_오픈API활용가이드](DOCUMENT/기상청18_동네예보&#32;조회서비스_오픈API활용가이드.docx)  

  ## 중기예보 조회서비스(MidFcstInfoService)
  사용예시: [tutorial_MidFcstInfoService.py](tutorial_MidFcstInfoService.py)
  |서비스명|기능|인자|기타|
  |------|---|---|---|
  |중기전망조회|**getMidFcst**|지점번호, 발표시각|지점코드 참고|
  |중기기온조회|**getMidTa**|예보구역코드, 발표시각|중기기온예보구역 코드 참고|
  |중기육상예보조회|**getMidLandFcst**|예보구역코드, 발표시각|중기육상예보구역 코드 참고|
  |중기해상예보조회|**getMidSeaFcst**|예보구역코드, 발표시각|중기해상예보구역 코드 참고|
  * 중기예보는 모두 일 2회 (6시, 18시) 생산되며 발표시각은 조회시간 직전으로 자동 설정됩니다.
  * 동네예보와 마찬가지로 24시간 이내에 자료만 조회가 가능합니다.  
  * 서비스별 지점 및 구역 코드는아래 상세 가이드 문서의 부록에 정리되어 있습니다. 참고하십시오.
  * [기상청20_중기예보 조회서비스_오픈API활용가이드](DOCUMENT/기상청20_중기예보&#32;조회서비스_오픈API활용가이드.docx)  

</details>

___

<details>
  <summary><strong>2. 관측정보 관련 서비스</strong></summary>

## 지상(종관, ASOS) 시간자료 조회서비스(AsosHourlyInfoService)
사용예시: [tutorial_AsosHourlyInfoService.py](tutorial_AsosHourlyInfoService.py)
|서비스명|기능|인자|기타|
|------|---|---|---|
|기상관측시간자료목록조회|**getWthrDataList**|지점번호, 시작시각, 종료시각|한 번에 최대 999개까지 조회 가능|

* 조회기간은 지점별 운영기간 모두 가능하며, 전날 자료까지만 조회가능합니다. 
* 단, 서버사정에 따라 갱신이 늦을 수 있습니다. (보통 오전 10시 이후 전부 조회 가능)
* 한 번에 최대 999개까지 조회되기 때문에 기간은 한 달이내로 설정해주시기 바랍니다.  
* (한 번 조회에 24시간을 권장합니다.)
* [META_관측지점정보_20201215203551](METADATA/META_관측지점정보_20201215203551.csv)  
* [기상청01_지상(종관,ASOS)시간자료_조회서비스_오픈API활용가이드](DOCUMENT/기상청01_지상(종관,ASOS)시간자료_조회서비스_오픈API활용가이드.docx)

## 지상(종관, ASOS) 일자료 조회서비스(AsosDalyInfoService)
사용예시: [tutorial_AsosHourlyInfoService.py](tutorial_AsosDalyInfoService.py)
|서비스명|기능|인자|기타|
|------|---|---|---|
|기상관측일자료목록조회|**getWthrDataList**|지점번호, 시작날짜, 종료날짜|한 번에 최대 999개까지 조회 가능|
* 조회기간은 지점별 운영기간 모두 가능하며, 전날 자료까지만 조회가능합니다. 
* 단, 서버사정에 따라 갱신이 늦을 수 있습니다. (보통 오전 10시 이후 전부 조회 가능)
* 한 번에 최대 999개까지 조회되기 때문에 기간은 2년 이내로 설정해주시기 바랍니다.  
* [META_관측지점정보_20201215203551](METADATA/META_관측지점정보_20201215203551.csv)  
* [기상청01_지상(종관,ASOS)일자료_조회서비스_오픈API활용가이드](DOCUMENT/기상청02_지상(종관,ASOS)일자료_조회서비스_오픈API활용가이드.docx)

</details>

---

<details>
  <summary><strong>3. 위성 및 레이더 관련 서비스</strong></summary>
  (예정)
</details>

---

<details>
  <summary><strong>4. 수치예보 관련 서비스</strong></summary>
  (예정)
</details>

---

<details>
  <summary><strong>5. 특보 및 지진/태풍 관련 서비스</strong></summary>
  (예정)
</details>

---

<details>
  <summary><strong>6. 생활 및 산업 관련 서비스</strong></summary>
  (예정)
</details>

---

<details>
  <summary><strong>7. 기타</strong></summary>
  (예정)
</details>

---

# 참고
+ [기상청(Korea Meteorological Administration)](http://www.kma.go.kr/)

