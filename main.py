import streamlit as st

# 페이지 설정
st.set_page_config(page_title="MBTI 진로 추천", layout="centered")

# 제목
st.title("🌟 MBTI로 알아보는 나의 진로 찾기 🌈")
st.write("너의 성격 유형(MBTI)을 선택하면, 그에 어울리는 진로를 추천해줄게! 😉")

# MBTI 리스트
mbti_types = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

# MBTI 선택
selected_mbti = st.selectbox("👉 너의 MBTI를 골라봐!", mbti_types)

# MBTI별 추천 진로 데이터
career_data = {
    "ISTJ": {
        "careers": ["공무원 🏛️", "회계사 💼"],
        "details": [
            {"major": "행정학과, 회계학과", "fit": "책임감 있고 꼼꼼한 사람에게 잘 맞아!"},
            {"major": "경제학과, 세무학과", "fit": "규칙과 절차를 중시하는 스타일이라면 찰떡!"}
        ]
    },
    "ENFP": {
        "careers": ["마케팅 기획자 📣", "콘텐츠 크리에이터 🎬"],
        "details": [
            {"major": "광고홍보학과, 경영학과", "fit": "아이디어 넘치고 사람 만나는 걸 좋아한다면 완전 딱이야!"},
            {"major": "미디어커뮤니케이션학과, 디자인학과", "fit": "창의력 뿜뿜! 감성 있는 사람에게 어울려 💡"}
        ]
    },
    "INTP": {
        "careers": ["데이터 분석가 📊", "연구원 🔬"],
        "details": [
            {"major": "컴퓨터공학과, 통계학과", "fit": "논리적이고 분석적인 두뇌파라면 완벽한 선택!"},
            {"major": "자연과학계열, 인공지능학과", "fit": "깊게 탐구하고 실험하는 걸 좋아한다면 찐이야!"}
        ]
    },
    "ESFP": {
        "careers": ["배우 🎭", "이벤트 플래너 🎉"],
        "details": [
            {"major": "연극영화학과, 방송예술학과", "fit": "에너지 넘치고 무대 위에서 빛나는 스타일에게 어울려!"},
            {"major": "호텔경영학과, 문화기획학과", "fit": "사람들과 어울리며 즐겁게 일하는 걸 좋아한다면 딱!"}
        ]
    },
    "INFJ": {
        "careers": ["심리상담사 🧠", "교사 👩‍🏫"],
        "details": [
            {"major": "심리학과, 상담학과", "fit": "다른 사람의 마음을 이해하고 돕는 걸 좋아한다면 굿!"},
            {"major": "교육학과, 국어교육과", "fit": "학생의 성장을 함께 이끄는 걸 좋아하는 사람에게 잘 맞아!"}
        ]
    },
    "ENTJ": {
        "careers": ["기업가 🚀", "프로젝트 매니저 🧩"],
        "details": [
            {"major": "경영학과, 창업학과", "fit": "리더십 있고 결단력 있는 사람이라면 진짜 찰떡!"},
            {"major": "산업공학과, 컴퓨터공학과", "fit": "체계적이고 목표 지향적인 성격에게 어울려 🔥"}
        ]
    }
}

# 데이터가 없는 MBTI는 기본 안내 표시
if selected_mbti not in career_data:
    st.markdown("😅 아직 이 MBTI에 대한 진로 데이터가 준비 중이야. 곧 추가될 예정이야!")
else:
    data = career_data[selected_mbti]
    st.markdown("---")
    st.header(f"✨ {selected_mbti} 유형에게 어울리는 진로는 바로 이거야! ✨")

    for i, career in enumerate(data["careers"]):
        st.subheader(f"{i+1}. {career}")
        st.write(f"📘 관련 학과: **{data['details'][i]['major']}**")
        st.write(f"💡 이런 사람에게 잘 맞아: {data['details'][i]['fit']}")
        st.markdown("---")

# 마무리 멘트
st.markdown("🎯 **너의 MBTI는 단지 시작일 뿐!** 진짜 중요한 건 너의 ‘흥미’와 ‘가치관’이야. 너답게 진로를 찾아보자 💪💫")
