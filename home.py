import requests
import pandas as pd
import json
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("'.env' 파일에 'API_KEY'가 설정되지 않았습니다.")

# API URL 및 키 설정
api_url = "http://apis.data.go.kr/B552584/ArpltnStatsSvc/getCtprvnMesureSidoLIst"
api_key = "uawAvQmBrGkuqQoRTMridn2ERx35uh0dj7lh9z7XRGvP6FC2CpPbRcrpukJeXLKQXCLT2FIPjPBpS+8zJ9gXHg=="

# 광역시 리스트
sido_names = ["서울",'인천', '울산', '대전', "부산", "광주", "대구"]

# 전체 데이터를 저장할 리스트
all_data = []

# 각 광역시 데이터를 가져오기
for sido in sido_names:
    params = {
        "serviceKey": api_key,
        "returnType": "json",
        "numOfRows": 100,
        "pageNo": 1,
        "sidoName": sido,
        "searchCondition": "DAILY",
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        # items 데이터를 DataFrame으로 변환
        if "response" in data and "body" in data["response"]:
            items = data["response"]["body"]["items"]
            df = pd.DataFrame(items)

            # 지역 정보 추가
            df["sidoName"] = sido  # 현재 도시 이름 추가
            all_data.append(df)  # 결과 리스트에 추가
        else:
            print(f"{sido} 지역 데이터가 없습니다.")
    except requests.exceptions.RequestException as e:
        print(f"{sido} 데이터 요청 중 오류 발생: {e}")

# 모든 데이터를 하나의 DataFrame으로 합치기
final_df = pd.concat(all_data, ignore_index=True)

# 필요한 열만 선택
columns_of_interest = [
    "dataTime", "sidoName", "cityName", "so2Value", "coValue", "o3Value",
    "no2Value", "pm10Value", "pm25Value"
]
final_df = final_df[columns_of_interest]

# 수치 데이터를 숫자형으로 변환
numeric_columns = ["so2Value", "coValue", "o3Value", "no2Value", "pm10Value", "pm25Value"]
for col in numeric_columns:
    final_df[col] = pd.to_numeric(final_df[col], errors="coerce")


# 광역시별 평균 계산
mean_values = final_df.groupby(["sidoName","dataTime"])[numeric_columns].mean() 

# 대기질 평가 함수 정의 (점수 계산 포함)
def evaluate_air_quality_with_score(row):
    scores = []
    if row["so2Value"] <= 0.02:
        scores.append(1)
    elif row["so2Value"] <= 0.05:
        scores.append(2)
    elif row["so2Value"] <= 0.15:
        scores.append(3)
    else:
        scores.append(4)
    
    if row["coValue"] <= 2.0:
        scores.append(1)
    elif row["coValue"] <= 9.0:
        scores.append(2)
    elif row["coValue"] <= 15.0:
        scores.append(3)
    else:
        scores.append(4)
    
    if row["o3Value"] <= 0.03:
        scores.append(1)
    elif row["o3Value"] <= 0.09:
        scores.append(2)
    elif row["o3Value"] <= 0.15:
        scores.append(3)
    else:
        scores.append(4)
    
    if row["no2Value"] <= 0.03:
        scores.append(1)
    elif row["no2Value"] <= 0.06:
        scores.append(2)
    elif row["no2Value"] <= 0.20:
        scores.append(3)
    else:
        scores.append(4)
    
    if row["pm10Value"] <= 30:
        scores.append(1)
    elif row["pm10Value"] <= 80:
        scores.append(2)
    elif row["pm10Value"] <= 150:
        scores.append(3)
    else:
        scores.append(4)
    
    if row["pm25Value"] <= 15:
        scores.append(1)
    elif row["pm25Value"] <= 35:
        scores.append(2)
    elif row["pm25Value"] <= 75:
        scores.append(3)
    else:
        scores.append(4)
    
    # 통합 스코어 계산 (평균 점수)
    total_score = sum(scores) / len(scores)
    
    # 평가 등급 반환
    if total_score <= 1.5:
        return total_score, "매우 좋음"
    elif total_score <= 2.5:
        return total_score, "좋음"
    elif total_score <= 3.5:
        return total_score, "보통"
    elif total_score <= 4.0:
        return total_score, "나쁨"
    else:
        return total_score, "매우 나쁨"

# 평가 및 통합 스코어 계산
mean_values = mean_values.reset_index()  # 그룹화 결과를 평평하게 만듦
mean_values[["통합스코어", "대기질평가"]] = mean_values.apply(
    lambda row: pd.Series(evaluate_air_quality_with_score(row)), axis=1
)

final_data = mean_values[["sidoName", "dataTime", "통합스코어", "대기질평가", "pm10Value", "pm25Value"]]
print(final_data)

# 통합스코어 범위	대기질 평가	설명
# 1.0 ~ 1.5	 매우 좋음	 대기오염이 거의 없는 상태
# 1.6 ~ 2.5	 좋음	     대기오염이 적고 공기질이 양호한 상태
# 2.6 ~ 3.5	 보통	     대기오염이 약간 있는 상태
# 3.6 ~ 4.0	 나쁨	     대기오염이 심각해 건강에 영향을 미칠 수 있는 상태
# 4.0	     매우 나쁨	 대기오염이 매우 심각해 건강에 큰 영향을 미칠 수 있는 상태

# 각 광역시별 가장 최신 시간 데이터 선택
final_data_last_time = final_data.loc[final_data.groupby("sidoName")["dataTime"].idxmax()]

json_data = final_data_last_time.to_json(orient="records", force_ascii=False)

