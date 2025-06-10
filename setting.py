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


# 1. 장소 키워드로 좌표 얻기
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

# 2. 좌표 기준으로 업종별 장소 검색
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

# 3. 장소이름 → 결과 목록 + 좌표 반환
def search_nearby_places_list(place_name, category_codes):
    coords = get_coordinates_by_keyword(place_name)
    if not coords:
        print("❌ 장소 좌표를 찾을 수 없습니다.")
        return [], None

    x, y = coords
    results = find_places_by_categories(x, y, category_codes)
    output_list = []

    for place in results:
        name = place['place_name']
        address = place.get('road_address_name') or place.get('address_name')
        output_list.append([name, address])  # 장소명, 주소

    return output_list, (x, y)  # 장소 목록과 좌표 함께 반환


# 🧪 실행 예시
where = "사상구 학장동"
data, coords = search_nearby_places_list(where, ["CT1", "AT4"])

if coords:
    st.write(f"🔍 검색 장소: {where}")
    st.write(f"📍 좌표: 경도 {coords[0]}, 위도 {coords[1]}")
else:
    st.error("❌ 장소 좌표를 불러올 수 없습니다.")

if len(data) >= 3:
    st.write("▶️ 주변 장소:")
    for i in range(3):
        st.write(f"위치: {data[i][0]} , 주소: {data[i][1]}")
else:
    st.warning("🔎 결과가 충분하지 않습니다. 다른 장소를 시도해보세요.")
