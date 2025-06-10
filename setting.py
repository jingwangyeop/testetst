import openai
import langchain
import ast
import os
import requests
from langchain_openai import ChatOpenAI
import streamlit as st
import streamlit.components.v1 as components

os.environ["OPENAI_API_KEY"] = "1"
model = ChatOpenAI(model="gpt-4.1-mini")

from langchain_core.tools import tool

from langchain_core.messages import ToolMessage

from langchain_community.tools import DuckDuckGoSearchResults

from langgraph.prebuilt import create_react_agent

KAKAO_API_KEY = "83c0445f5fc4a2ee846f09e47fb00187"



def get_coordinates_by_keyword(query):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        documents = response.json()['documents']
        if documents:
            first = documents[0]
            return float(first['x']), float(first['y'])  # (longitude, latitude)
    return None

# 2. 좌표 기준으로 특정 업종 카테고리 장소들 검색
def find_places_by_categories(x, y, category_codes, radius=1000):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    all_results = []

    for code in category_codes:
        params = {
            "category_group_code": code,
            "x": x,
            "y": y,
            "radius": radius,
            "sort": "distance"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            all_results += response.json()['documents']

    return all_results

# 3. 전체 실행 함수: 장소이름 입력하면 [장소이름, 장소위치] 리스트 반환
def search_nearby_places_list(place_name, category_codes):
    coords = get_coordinates_by_keyword(place_name)
    if not coords:
        print("❌ 장소 좌표를 찾을 수 없습니다.")
        return []

    x, y = coords
    results = find_places_by_categories(x, y, category_codes)
    output_list = []

    for place in results:
        name = place['place_name']
        address = place.get('road_address_name') or place.get('address_name')
        output_list.append([name, address])  # 부가설명 제거

    return output_list


where = "사상구 학장동"
# ✅ 실행 예시
data = search_nearby_places_list(where, ["CT1", "AT4"])
for item in data:
    st.write(item)



st.title("📍 카카오맵 예제 (Streamlit 삽입)")

# 본인의 JavaScript 키로 바꿔주세요
KAKAO_JAVASCRIPT_KEY = "d920a6e3a78bfb47c41cbdfbe01e4030"

html_code = f"""
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8"/>
	<title>Kakao 지도 시작하기</title>
</head>
<body>
	<div id="map" style="width:500px;height:400px;"></div>
	<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=d920a6e3a78bfb47c41cbdfbe01e4030"></script>
	<script>
		var container = document.getElementById('map');
		var options = {
			center: new kakao.maps.LatLng(33.450701, 126.570667),
			level: 3
		};

		var map = new kakao.maps.Map(container, options);
	</script>
</body>
</html>
"""

# HTML 삽입
components.html(html_code, height=450)
