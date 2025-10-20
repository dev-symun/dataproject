import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="상관관계 분석 (Scatter Matrix + Correlation)")

st.title("📊 모든 속성 간 상관관계 — 산점도 행렬 + 상관계수")
st.markdown("엑셀 파일에서 수치형 변수들을 자동으로 골라 산점도 행렬을 그리고, 상관계수를 표시합니다.")

# 파일 입력: 업로드 우선, 없으면 기본 파일 경로 사용
uploaded = st.file_uploader("엑셀 파일 업로드 (.xlsx 또는 .csv 가능)", type=["xlsx", "csv"])
if uploaded is None:
    default_path = "/mnt/data/fitness data.xlsx"
    st.markdown(f"- 기본 파일 사용: `{default_path}` (업로드하면 이 파일 대신 사용)")
    try:
        df = pd.read_excel(default_path)
    except Exception as e:
        st.error("기본 파일을 열 수 없습니다. 업로드 파일을 제공하세요.")
        st.stop()
else:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

st.subheader("데이터 미리보기")
st.dataframe(df.head())

# 수치형 컬럼 선택
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) < 2:
    st.error("수치형 변수가 2개 이상 필요합니다. 파일을 확인하세요.")
    st.stop()

st.sidebar.markdown("### 옵션")
show_heatmap = st.sidebar.checkbox("상관계수 히트맵 표시", value=True)
show_scatter = st.sidebar.checkbox("산점도 행렬 표시", value=True)
top_n = st.sidebar.number_input("상관계수 높은 순 위 개수", min_value=1, max_value=20, value=10)

# 상관계수 계산
corr = df[numeric_cols].corr(method='pearson')

# 산점도 행렬 (Plotly)
if show_scatter:
    st.subheader("산점도 행렬 (Scatter Matrix)")
    fig_sm = px.scatter_matrix(df[numeric_cols],
                                dimensions=numeric_cols,
                                title="Scatter matrix of numeric variables",
                                labels={c: c for c in numeric_cols},
                                height=900, width=900)
    # 점 크기, 마진 조정
    fig_sm.update_traces(marker=dict(size=3, opacity=0.7), diagonal_visible=False)
    fig_sm.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_sm, use_container_width=True)

# 상관계수 히트맵 (주석 포함)
if show_heatmap:
    st.subheader("상관계수 히트맵 (Pearson)")
    z = corr.values
    fig_h = go.Figure(data=go.Heatmap(
        z=z,
        x=numeric_cols,
        y=numeric_cols,
        hovertemplate="(%{y}, %{x})<br>corr=%{z:.4f}<extra></extra>"
    ))
    # annotations: 값 표시
    annotations = []
    for i, row in enumerate(numeric_cols):
        for j, col in enumerate(numeric_cols):
            annotations.append(dict(
                x=col, y=row,
                text=f"{z[i][j]:.2f}",
                showarrow=False,
                font=dict(color="white" if abs(z[i][j])>0.5 else "black", size=11)
            ))
    fig_h.update_layout(annotations=annotations, height=800, width=800, margin=dict(l=50, r=50, t=50, b=50))
    st.plotly_chart(fig_h, use_container_width=True)

# 상관계수 높은 순 정렬 (절대값 기준)
pairs = []
cols = numeric_cols
for i in range(len(cols)):
    for j in range(i+1, len(cols)):
        a, b = cols[i], cols[j]
        val = corr.loc[a, b]
        pairs.append((a, b, float(val), abs(float(val))))
pairs_sorted = sorted(pairs, key=lambda x: x[3], reverse=True)

st.subheader(f"상관계수 높은 순 (총 {len(pairs_sorted)} 쌍) — 상위 {top_n}개")
top_list = pairs_sorted[:top_n]
top_df = pd.DataFrame([{"변수1": a, "변수2": b, "상관계수": v, "절대값": abs_v} for a,b,v,abs_v in top_list])
st.dataframe(top_df.style.format({"상관계수":"{:.4f}", "절대값":"{:.4f}"}))

# 양/음의 상관관계 교육 설명
st.subheader("상관관계 해석 (학생용 핵심 정리)")
st.markdown("""
- **상관계수(Pearson r)**: 두 변수의 선형 관계 강도와 방향을 나타냅니다. 범위는 **-1 ~ +1**.
  - **r > 0**: 양의 상관관계 — 한 변수가 증가할 때 다른 변수도 증가.
  - **r < 0**: 음의 상관관계 — 한 변수가 증가할 때 다른 변수는 감소.
  - **r = 0**: 선형 상관관계가 없음(비선형 관계 가능).
- **세기 기준(일반적인 가이드)**:
  - |r| ≥ 0.8 : 매우 강한 상관
  - 0.6 ≤ |r| < 0.8 : 강한 상관
  - 0.4 ≤ |r| < 0.6 : 중간 정도 상관
  - 0.2 ≤ |r| < 0.4 : 약한 상관
  - |r| < 0.2 : 거의 상관 없음
- **주의**:
  - 상관은 인과관계를 의미하지 않습니다. (A→B 또는 B→A, 혹은 제3변수의 영향 가능)
  - 이상치(outlier)가 상관계수에 큰 영향을 줄 수 있습니다.
""")

# 상위 상관 쌍을 이용한 간단 해석 예시 출력
st.subheader("상위 상관 쌍 사례 해석 (자동 생성)")
for a,b,v,abs_v in top_list:
    sign = "양의" if v>0 else "음의"
    strength = ("매우 강함" if abs_v>=0.8 else
                "강함" if abs_v>=0.6 else
                "중간" if abs_v>=0.4 else
                "약함" if abs_v>=0.2 else "거의 없음")
    st.markdown(f"- **{a} ↔ {b}**: 상관계수 **{v:.4f}** ({sign}, {strength}) — 해석: `{a}`가 증가하면 `{b}`가 {'증가' if v>0 else '감소'}하는 경향이 있다. 단, 인과관계는 아님.")

st.markdown("**참고**: 산점도에서 패턴(직선성, 곡선성), 군집, 이상치 등을 함께 관찰하세요.")

# 다운로드: 상관계수 표 CSV
csv = corr.reset_index().to_csv(index=False).encode('utf-8-sig')
st.download_button("상관계수 표 다운로드 (CSV)", data=csv, file_name="correlation_matrix.csv", mime="text/csv")

st.markdown("---")
st.markdown("출처: Pandas 계산 (Pearson), 시각화: Plotly, 실행: Streamlit")
