import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==============================
# 페이지 설정
# ==============================
st.set_page_config(page_title="상관관계 분석 도구", layout="wide")
st.markdown(
    """
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #FFF9F0;  /* 연한 파스텔 베이지 */
        color: #000000;  /* 텍스트 검정 고정 */
    }
    /* 헤더/텍스트 색상 강제 */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("📈 속성 간 상관관계 분석 대시보드")
st.markdown("""
이 앱은 데이터를 기반으로 두 속성 간 상관관계를 직관적으로 분석하고 해석을 제공합니다.  
기본 데이터를 사용합니다.
""")

# ==============================
# 데이터 불러오기
# ==============================
default_path = "fitness data.xlsx"
st.info(f"기본 데이터 사용 중: `{default_path}`")
df = pd.read_excel(default_path)

# 수치형 변수 필터링
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) < 2:
    st.error("수치형 데이터가 2개 이상 필요합니다.")
    st.stop()

# ==============================
# 1️⃣ 개별 속성 간 상관관계 분석
# ==============================
st.header("1️⃣ 두 속성 간 상관관계 분석")
col1, col2 = st.columns(2)
x_col = col1.selectbox("X축 속성 선택", numeric_cols)
y_col = col2.selectbox("Y축 속성 선택", numeric_cols, index=min(1, len(numeric_cols)-1))

if x_col and y_col:
    corr_value = df[x_col].corr(df[y_col])

    st.subheader(f"📊 {x_col} vs {y_col}")

    fig = px.scatter(df, x=x_col, y=y_col, trendline="ols",
                     opacity=0.7,
                     title=f"{x_col} ↔ {y_col} 산점도 (상관계수: {corr_value:.4f})",
                     labels={x_col: x_col, y_col: y_col},
                     color_discrete_sequence=["#AEC6CF"])  # 파스텔 블루
    fig.update_traces(marker=dict(size=10, color="#AEC6CF"),
                      selector=dict(mode='markers'))
    fig.update_traces(line=dict(color="#FFB347"), selector=dict(mode='lines'))  # 파스텔 오렌지
    st.plotly_chart(fig, use_container_width=True)

    # 상관관계 해석
    def interpret_corr(r):
        direction = "양의 상관관계" if r > 0 else "음의 상관관계" if r < 0 else "상관 없음"
        strength = (
            "매우 강함" if abs(r) >= 0.8 else
            "강함" if abs(r) >= 0.6 else
            "중간 정도" if abs(r) >= 0.4 else
            "약함" if abs(r) >= 0.2 else
            "거의 없음"
        )
        return direction, strength

    direction, strength = interpret_corr(corr_value)
    relation_text = (
        f"**상관계수:** {corr_value:.4f}\n\n"
        f"- 두 변수는 **{direction}({strength})** 관계입니다.\n"
        f"- 즉, `{x_col}`이 증가하면 `{y_col}`은 "
        f"{'함께 증가' if corr_value>0 else '감소' if corr_value<0 else '별다른 변화 없음'}하는 경향이 있습니다."
    )
    st.markdown(relation_text)

# ==============================
# 2️⃣ 상관계수 Top10 속성쌍 분석
# ==============================
st.header("2️⃣ 상관계수 상위 10개 속성쌍 분석")

corr_matrix = df[numeric_cols].corr()
pairs = []
for i in range(len(numeric_cols)):
    for j in range(i + 1, len(numeric_cols)):
        a, b = numeric_cols[i], numeric_cols[j]
        val = corr_matrix.loc[a, b]
        pairs.append((a, b, val, abs(val)))

top_pairs = sorted(pairs, key=lambda x: x[3], reverse=True)[:10]
top_df = pd.DataFrame(top_pairs, columns=["속성1", "속성2", "상관계수", "절대값"])
st.dataframe(top_df.style.format({"상관계수": "{:.4f}", "절대값": "{:.4f}"}))

# 히트맵 추가
st.subheader("📊 상관계수 Top10 히트맵")
top_attrs = list(set([a for a, b, _, _ in top_pairs] + [b for a, b, _, _ in top_pairs]))
heatmap_matrix = corr_matrix.loc[top_attrs, top_attrs]
fig_heat = px.imshow(
    heatmap_matrix, 
    color_continuous_scale=px.colors.sequential.Peach
)
fig_heat.update_layout(coloraxis_colorbar=dict(title="상관계수"))
st.plotly_chart(fig_heat, use_container_width=True)

pair_options = [f"{a} ↔ {b} (r={v:.3f})" for a, b, v, _ in top_pairs]
selected_pair = st.selectbox("상관관계가 높은 속성쌍 선택", pair_options)

if selected_pair:
    idx = pair_options.index(selected_pair)
    a, b, v, _ = top_pairs[idx]
    st.subheader(f"📈 {a} ↔ {b} (r={v:.4f})")

    fig2 = px.scatter(df, x=a, y=b, trendline="ols",
                      opacity=0.7,
                      color_discrete_sequence=["#77DD77"])  # 파스텔 그린
    fig2.update_traces(marker=dict(size=10, color="#77DD77"),
                       selector=dict(mode='markers'))
    fig2.update_traces(line=dict(color="#FF6961"), selector=dict(mode='lines'))  # 파스텔 레드
    st.plotly_chart(fig2, use_container_width=True)

    sign_text = "양의 상관관계" if v > 0 else "음의 상관관계"
    degree_text = (
        "매우 강함" if abs(v) >= 0.8 else
        "강함" if abs(v) >= 0.6 else
        "중간" if abs(v) >= 0.4 else
        "약함" if abs(v) >= 0.2 else
        "거의 없음"
    )

    st.markdown(f"**상관관계 유형:** {sign_text} ({degree_text})")
    st.markdown(f"**해석:** `{a}`가 증가할수록 `{b}`는 {'함께 증가' if v > 0 else '감소'}하는 경향이 있습니다.")

st.markdown("---")
st.markdown("출처: Pandas(Pearson 상관계수), Plotly(시각화), Streamlit(인터페이스)")
