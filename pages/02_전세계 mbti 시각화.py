# streamlit_mbti_app.py
# Streamlit 앱: countriesMBTI_16types.csv 파일을 같은 디렉터리에 두고 실행하세요.
# 요구사항: Streamlit Cloud에서 동작하도록 작성.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide", page_title="MBTI by Country — Interactive 3D", initial_sidebar_state="expanded")

# ------------------------
# 유틸리티 함수
# ------------------------

@st.cache_data
def load_data(path='countriesMBTI_16types.csv'):
    df = pd.read_csv(path)
    return df


def gradient_colors_except_top(values, top_color='#ff0000', cmap=px.colors.sequential.Viridis):
    """값 리스트에서 최대값(=1등)은 top_color로, 나머지는 cmap 그라데이션으로 반환"""
    vals = np.array(values, dtype=float)
    idx_max = np.nanargmax(vals)
    # normalize excluding max for cmap mapping
    others = vals.copy()
    others[idx_max] = np.nan
    minv = np.nanmin(others)
    maxv = np.nanmax(others)
    colors = []
    for i, v in enumerate(vals):
        if i == idx_max:
            colors.append(top_color)
        else:
            # normalize to 0-1
            if np.isnan(v) or maxv==minv:
                t = 0.5
            else:
                t = (v - minv) / (maxv - minv)
            # map to colormap
            cmap_index = int(t * (len(cmap)-1))
            colors.append(cmap[cmap_index])
    return colors


# 3D 서피스 생성: x: MBTI, y: [0,1], z: [zeros ; values]
def country_surface_figure(mbti_labels, values):
    # build z as 2 x N so surface looks like vertical ridges
    z = np.vstack([np.zeros(len(values)), values])

    x = np.arange(len(values))
    y = np.array([0, 1])

    # colorscale: we will build per-vertex colors by mapping value to color
    # For a surface we can pass a colorscale and use `surfacecolor`.
    surfacecolor = np.vstack([np.zeros(len(values)), values])

    # Ensure the top is red: create a custom colorscale that ends with red at max
    # We'll use Viridis for gradient then override the top
    cs = px.colors.sequential.Viridis

    fig = go.Figure(data=[
        go.Surface(
            z=z,
            x=x,
            y=y,
            surfacecolor=surfacecolor,
            colorscale=cs,
            showscale=True,
            cmin=0,
            cmax=max(1.0, np.nanmax(values)),
            hovertemplate='MBTI: %{x}<br>높이: %{z}<extra></extra>'
        )
    ])

    # overlay annotations for MBTI names at y=1.05 plane
    annotations = []
    for i, label in enumerate(mbti_labels):
        annotations.append(dict(x=i, y=1.05, z=max(values)*0.02, text=label, showarrow=False))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='MBTI Index', tickmode='array', tickvals=list(range(len(mbti_labels))), ticktext=mbti_labels),
            yaxis=dict(visible=False),
            zaxis=dict(title='Value')
        ),
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig


# 3D PCA 산점도
def pca_3d_figure(df_mbti, country_names, n_components=3):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(df_mbti.fillna(0).values)
    pca = PCA(n_components=n_components, random_state=42)
    Xp = pca.fit_transform(Xs)
    pc_cols = [f'PC{i+1}' for i in range(Xp.shape[1])]
    plot_df = pd.DataFrame(Xp, columns=pc_cols)
    plot_df['Country'] = country_names

    fig = px.scatter_3d(plot_df, x='PC1', y='PC2', z='PC3', hover_name='Country', title='Countries in PCA 3D space (MBTI 기반)')
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    return fig


# 전세계 평균 3D 막대(대신 surface로 구현하여 입체감 제공)
def global_mean_surface(df_mbti):
    means = df_mbti.mean().values
    labels = df_mbti.columns.tolist()
    # create simple surface similar to country view
    return country_surface_figure(labels, means)


# ------------------------
# 앱 본문
# ------------------------

df = load_data()
mbti_cols = [c for c in df.columns if c != 'Country']

st.title('국가별 MBTI 분포 — 인터랙티브 3D 대시보드')
st.markdown('파일: `countriesMBTI_16types.csv` 에서 읽어옵니다.')

# 사이드바 컨트롤
with st.sidebar:
    st.header('컨트롤')
    country = st.selectbox('국가 선택', df['Country'].sort_values().tolist())
    show_pca = st.checkbox('PCA 3D 보기', value=True)
    show_global = st.checkbox('전세계 평균 보기', value=True)
    st.markdown('원하면 데이터 다운로드')
    st.download_button('데이터 CSV 다운로드', df.to_csv(index=False), file_name='countriesMBTI_16types.csv')

# 메인 레이아웃
col1, col2 = st.columns([1,1])

# 왼쪽: 선택 국가 MBTI (입체 surface)
with col1:
    st.subheader(f'{country} — MBTI 분포 (입체)')
    row = df[df['Country'] == country].iloc[0]
    labels = mbti_cols
    values = row[labels].astype(float).values

    # 색 구성: 1등 red, 나머지 그라데이션 (표시용 범례 따로)
    colors = gradient_colors_except_top(values, top_color='#ff0000')

    # Surface figure
    surf_fig = country_surface_figure(labels, values)

    # Add a 2D bar below for 정확한 값 표시 (Plotly bar) with color per bar
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition='auto'))
    bar_fig.update_layout(title=f'{country} MBTI 비율 (상세 막대)', xaxis_title='MBTI', yaxis_title='값', margin=dict(l=0,r=0,t=30,b=0))

    st.plotly_chart(surf_fig, use_container_width=True, theme='streamlit')
    st.plotly_chart(bar_fig, use_container_width=True, theme='streamlit')

# 오른쪽: 전세계 평균 + PCA
with col2:
    if show_global:
        st.subheader('전세계 MBTI 평균 (입체)')
        gm_fig = global_mean_surface(df[mbti_cols])
        st.plotly_chart(gm_fig, use_container_width=True, theme='streamlit')

    if show_pca:
        st.subheader('국가 군집 (PCA 3D)')
        pca_fig = pca_3d_figure(df[mbti_cols], df['Country'])
        st.plotly_chart(pca_fig, use_container_width=True, theme='streamlit')

# 하단: 요약 통계
st.markdown('---')
st.subheader('요약 통계')
global_stats = df[mbti_cols].agg(['mean','std','min','max']).T.reset_index().rename(columns={'index':'MBTI'})
st.dataframe(global_stats)

# 끝: 다운로드 버튼 및 requirements 안내
st.markdown('---')
st.markdown('**설치/배포**: Streamlit Cloud에 배포하려면 아래 `requirements.txt` 파일을 프로젝트 루트에 추가하세요.')
st.code('''
# requirements.txt
streamlit
pandas
numpy
plotly
scikit-learn
''', language='text')

st.markdown('앱 준비 완료. 동일 폴더에 `countriesMBTI_16types.csv`가 있어야 합니다.')
