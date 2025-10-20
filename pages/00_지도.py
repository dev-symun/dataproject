import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="서울 관광명소 Top10", layout="wide")

st.title("🌏 외국인들이 좋아하는 서울의 주요 관광지 Top10")

# 서울 주요 관광지 Top10 (한국관광공사 및 서울관광재단 자료 기반)
places = [
    {"name": "경복궁", "lat": 37.579617, "lon": 126.977041, "desc": "조선의 대표 궁궐, 전통과 역사의 상징"},
    {"name": "명동", "lat": 37.563757, "lon": 126.982669, "desc": "쇼핑과 길거리 음식의 천국"},
    {"name": "남산타워 (N서울타워)", "lat": 37.551169, "lon": 126.988227, "desc": "서울의 랜드마크, 야경 명소"},
    {"name": "북촌 한옥마을", "lat": 37.582604, "lon": 126.983998, "desc": "전통 한옥이 잘 보존된 마을"},
    {"name": "홍대 거리", "lat": 37.556332, "lon": 126.923611, "desc": "젊음과 예술의 거리"},
    {"name": "인사동", "lat": 37.574008, "lon": 126.984733, "desc": "한국 전통 공예와 문화의 거리"},
    {"name": "청계천", "lat": 37.569155, "lon": 126.978300, "desc": "도심 속 힐링 산책로"},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566477, "lon": 127.009128, "desc": "미래적 디자인의 대표 공간"},
    {"name": "롯데월드타워", "lat": 37.513068, "lon": 127.102531, "desc": "초고층 전망대와 쇼핑 복합공간"},
    {"name": "잠실 롯데월드", "lat": 37.511000, "lon": 127.098000, "desc": "서울의 대표 놀이공원"},
]

# 지도 중심 좌표
seoul_center = [37.5665, 126.9780]

# 지도 생성
m = folium.Map(location=seoul_center, zoom_start=12, tiles="CartoDB positron")

# 마커 추가
for place in places:
    popup_html = f"<b>{place['name']}</b><br>{place['desc']}"
    folium.Marker(
        [place["lat"], place["lon"]],
        tooltip=place["name"],
        popup=popup_html,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Streamlit에 folium 지도 표시
st_folium(m, width=1000, height=700)
