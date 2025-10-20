import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 기본 설정
st.set_page_config(page_title="상하이 여행 계획", layout="wide")

st.title("🧳 상하이 여행 계획 페이지")
st.markdown("중국 상하이를 여행하기 위한 일정, 예산, 방문지 정보를 한눈에 정리합니다.")

# --- 여행 기본 정보 입력 ---
st.header("✈️ 여행 기본 정보")
col1, col2, col3 = st.columns(3)

with col1:
    days = st.number_input("여행 일수", min_value=1, max_value=14, value=4)
with col2:
    budget = st.number_input("총 예산 (원화 기준)", min_value=0, value=1200000, step=100000)
with col3:
    season = st.selectbox("여행 시기", ["봄", "여름", "가을", "겨울"])

st.write(f"**여행 일수:** {days}일 / **예산:** {budget:,}원 / **시기:** {season}")

# --- 추천 방문지 데이터 ---
st.header("📍 추천 방문지 Top10")

places = [
    {"name": "와이탄(外滩, The Bund)", "lat": 31.2401, "lon": 121.4905, "desc": "상하이의 대표 야경 명소"},
    {"name": "동방명주탑 (东方明珠塔)", "lat": 31.2397, "lon": 121.4998, "desc": "상하이 랜드마크 전망대"},
    {"name": "예원 (豫园)", "lat": 31.2272, "lon": 121.4925, "desc": "전통 중국식 정원"},
    {"name": "난징루 보행가 (南京路步行街)", "lat": 31.2381, "lon": 121.4900, "desc": "쇼핑 거리와 야경 명소"},
    {"name": "상하이 박물관", "lat": 31.2304, "lon": 121.4737, "desc": "중국 예술과 문화의 중심"},
    {"name": "티안즈팡 (田子坊)", "lat": 31.2075, "lon": 121.4669, "desc": "예술 거리와 카페 골목"},
    {"name": "신톈디 (新天地)", "lat": 31.2205, "lon": 121.4750, "desc": "유럽풍 레스토랑 거리"},
    {"name": "상하이 디즈니랜드", "lat": 31.1440, "lon": 121.6570, "desc": "세계 최대 규모의 디즈니랜드 중 하나"},
    {"name": "푸동 리버사이드 공원", "lat": 31.2427, "lon": 121.5111, "desc": "도시 스카이라인 조망 명소"},
    {"name": "상하이 타워 (上海中心大厦)", "lat": 31.2336, "lon": 121.5055, "desc": "세계 2위 높이의 초고층 빌딩"},
]

# --- 지도 표시 ---
st.subheader("🗺️ 상하이 주요 명소 지도")

shanghai_center = [31.2304, 121.4737]
m = folium.Map(location=shanghai_center, zoom_start=12, tiles="CartoDB positron")

for p in places:
    folium.Marker(
        [p["lat"], p["lon"]],
        tooltip=p["name"],
        popup=f"<b>{p['name']}</b><br>{p['desc']}",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

st_folium(m, width=1000, height=600)

# --- 일정표 (DataFrame 입력) ---
st.header("🕓 여행 일정표 작성")
st.markdown("방문지와 시간 계획을 자유롭게 추가하세요.")

schedule = pd.DataFrame({
    "날짜": [f"Day {i+1}" for i in range(days)],
    "주요 방문지": ["" for _ in range(days)],
    "식사 장소": ["" for _ in range(days)],
    "예상 교통수단": ["" for _ in range(days)],
    "예상 비용 (원)": [0 for _ in range(days)]
})

edited_schedule = st.data_editor(schedule, num_rows="dynamic")

total_estimated = edited_schedule["예상 비용 (원)"].sum()
remain = budget - total_estimated

st.metric(label="예상 총 지출", value=f"{total_estimated:,} 원")
st.metric(label="남은 예산", value=f"{remain:,} 원")

# --- 팁 섹션 ---
st.header("💡 여행 팁")
st.markdown("""
- **교통:** 지하철 이용이 가장 편리하며 알리페이(支付宝)로 QR 결제 가능  
- **환전:** 위안화(CNY) 환전은 국내 은행 또는 공항에서 미리  
- **음식 추천:** 샤오롱바오(小笼包), 상하이식 볶음면, 마라탕  
- **언어:** 간단한 중국어 인사말 숙지 추천  
- **유심/데이터:** eSIM 또는 현지 SIM카드 구매 가능  
- **주의:** 일부 지역에서는 구글맵보다 바이두맵 또는 애플맵이 더 정확함  
""")

# --- 마무리 ---
st.success("✈️ 상하이 여행 준비 완료! 멋진 여행을 즐기세요.")
