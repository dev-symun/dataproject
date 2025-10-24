import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="🌍 국가별 MBTI 분석",
    layout="wide",
    page_icon="🌈"
)

# ---- 스타일 정의 ----
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Pretendard', sans-serif;
    }
    h1, h2, h3 {
        color: #334155;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stPlotlyChart {
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ---- 데이터 불러오기 ----
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

st.title("🌍 국가별 MBTI 데이터 분석 대시보드")
st.markdown("이 페이지는 **결측치, 이상치 처리** 후 **국가별 MBTI 분포 및 MBTI별 국가 순위**를 시각화합니다.")

# ---- 데이터 미리보기 ----
with st.expander("📄 데이터 미리보기"):
    st.dataframe(df.head())

# ---- 결측치 처리 ----
st.subheader("🧹 결측치 처리")
missing_before = df.isnull().sum().sum()
df = df.fillna(df.mean(numeric_only=True))
missing_after = df.isnull().sum().sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("처리 전 결측치 수", missing_before)
with col2:
    st.metric("처리 후 결측치 수", missing_after)

# ---- 이상치 처리 (IQR) ----
st.subheader("⚠️ 이상치 처리 (IQR 기반)")
numeric_cols = df.select_dtypes(include=[np.number]).columns

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df = df[(df[col] >= lower) & (df[col] <= upper)]

st.success("이상치 처리가 완료되었습니다.")

# ---- MBTI 열 목록 ----
mbti_cols = [c for c in df.columns if c.upper() in [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]]

# ---- 국가별 MBTI 분포 (파이 차트) ----
st.subheader("🌐 국가별 MBTI 분포 분석")

country_list = sorted(df["Country"].unique())
selected_country = st.selectbox("국가를 선택하세요:", country_list)

country_df = df[df["Country"] == selected_country]

if len(mbti_cols) > 0:
    melted_df = country_df.melt(
        id_vars=["Country"],
        value_vars=mbti_cols,
        var_name="MBTI",
        value_name="비율"
    )

    melted_df = melted_df.groupby("MBTI")["비율"].mean().reset_index()
    melted_df = melted_df.sort_values("비율", ascending=False)
    top_type = melted_df.iloc[0]["MBTI"]

    # 원 그래프
    fig = px.pie(
        melted_df,
        names="MBTI",
        values="비율",
        color="MBTI",
        color_discrete_sequence=px.colors.qualitative.Safe,
        title=f"🇨🇳 {selected_country}의 MBTI 비율 분포"
    )
    fig.update_traces(textinfo="percent+label", pull=[0.1 if i == 0 else 0 for i in range(len(mbti_cols))])
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"💡 이 국가에서 가장 많은 유형은 **{top_type}** 입니다.")
else:
    st.warning("MBTI 유형 열을 찾을 수 없습니다.")

# ---- MBTI 선택 시 국가 순위 그래프 ----
st.subheader("📈 MBTI별 국가 순위")

selected_mbti = st.selectbox("MBTI 유형을 선택하세요:", mbti_cols)

mbti_country_df = df[["Country", selected_mbti]].groupby("Country")[selected_mbti].mean().reset_index()
mbti_country_df = mbti_country_df.sort_values(selected_mbti, ascending=False)

fig3 = px.bar(
    mbti_country_df,
    x="Country",
    y=selected_mbti,
    text_auto=".2f",
    color=selected_mbti,
    color_continuous_scale="RdYlBu_r",
    title=f"{selected_mbti} 유형이 많은 국가 순위"
)
fig3.update_traces(marker_line_width=1.2, marker_line_color="#333", textposition="outside")
fig3.update_layout(
    title_x=0.5,
    xaxis_title="국가",
    yaxis_title="비율 (%)",
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(size=13)
)
st.plotly_chart(fig3, use_container_width=True)

# ---- 전체 국가 평균 비교 ----
st.subheader("📊 전 세계 MBTI 평균 비교")

avg_df = df.groupby("Country")[mbti_cols].mean().reset_index()
avg_df = avg_df.melt(id_vars=["Country"], var_name="MBTI", value_name="비율")

fig2 = px.bar(
    avg_df,
    x="MBTI",
    y="비율",
    color="Country",
    barmode="group",
    title="국가별 MBTI 평균 비율 비교"
)
fig2.update_layout(title_x=0.5, plot_bgcolor="#fff")
st.plotly_chart(fig2, use_container_width=True)

st.caption("© 2025 국가별 MBTI 데이터 분석 대시보드")
