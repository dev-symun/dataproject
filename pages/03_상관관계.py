import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="상관관계 분석 도구", layout="wide")

st.title("📈 속성 간 상관관계 분석 대시보드")
st.markdown("""
이 앱은 데이터를 기반으로 두 속성 간의 상관관계를 직관적으로 분석하고 해석을 제공합니다.  
아래에서 파일을 업로드하거나 기본 데이터를 사용하세요.
""")

# 파일 업로드
uploaded = st.file_uploader("엑셀 또는 CSV 파일 업로드", type=["xlsx", "csv"])
if uploaded is None:
    default_path = "fitness data.xlsx"
    st.info(f"기본 데이터 사용 중: `{default_path}`")
    df = pd.read_excel(default_path)
else:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

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
    fig = px.scatter(df, x=x_col, y=y_col,
                     trendline="ols",
                     opacity=0.7,
                     title=f"{x_col} ↔ {y_col} 산점도 (상관계수: {corr_value:.4f})",
                     labels={x_col: x_col, y_col: y_col})
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

    st.markdown("""
    **상관계수 해석 기준**
    | | 절댓값 | 설명 |
    |:-:|:-:|:-|
    | 매우 강함 | ≥ 0.8 | 거의 직선 형태의 관계 |
    | 강함 | 0.6 ~ 0.8 | 뚜렷한 경향 존재 |
    | 중간 | 0.4 ~ 0.6 | 일정 경향 있으나 예외 존재 |
    | 약함 | 0.2 ~ 0.4 | 경향이 약함 |
    | 거의 없음 | < 0.2 | 관계가 거의 없음 |
    """)

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

pair_options = [f"{a} ↔ {b} (r={v:.3f})" for a, b, v, _ in top_pairs]
selected_pair = st.selectbox("상관관계가 높은 속성쌍 선택", pair_options)

if selected_pair:
    idx = pair_options.index(selected_pair)
    a, b, v, _ = top_pairs[idx]
    st.subheader(f"📈 {a} ↔ {b} (r={v:.4f})")

    # 산점도 출력
    fig2 = px.scatter(df, x=a, y=b, trendline="ols",
                      title=f"{a}와 {b}의 상관관계 시각화",
                      opacity=0.7)
    st.plotly_chart(fig2, use_container_width=True)

    # 해석 및 이유 설명
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

    st.markdown("**가능한 이유(데이터적 관점)**")
    if v > 0.6:
        st.markdown(f"- `{a}`와 `{b}`는 동일한 요인(예: 체력, 신체 크기, 시간 등)에 의해 함께 영향을 받는 변수일 가능성이 높습니다.")
        st.markdown(f"- 예를 들어 `{a}`가 크면 `{b}`도 커지는 자연스러운 패턴일 수 있습니다.")
    elif v < -0.6:
        st.markdown(f"- `{a}`와 `{b}`는 서로 반비례 관계를 가질 가능성이 있습니다. 한 변수가 증가하면 다른 변수가 감소하는 패턴입니다.")
        st.markdown(f"- 예를 들어 `{a}`가 커질수록 `{b}`에 필요한 값이 줄어드는 구조일 수 있습니다.")
    else:
        st.markdown(f"- `{a}`와 `{b}`는 어느 정도의 관계를 가지지만, 다른 요인의 영향도 있을 수 있습니다.")
        st.markdown(f"- 상관은 인과를 의미하지 않으며, 제3의 변수나 데이터 특성의 영향일 가능성이 있습니다.")

st.markdown("---")
st.markdown("출처: Pandas(Pearson 상관계수), Plotly(시각화), Streamlit(인터페이스)")
