import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="MBTI 국가 추천",
    page_icon="🌍",
    layout="wide"
)

# 제목
st.title("🌍 MBTI 세계 국가 추천 프로그램")
st.write("나의 MBTI와 비율이 높은 국가를 찾아보세요!")

# CSV 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("countriesMBTI_16types.csv")

df = load_data()

# MBTI 유형 목록
mbti_types = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]

# 사용자 MBTI 선택
st.subheader("🧑 나의 MBTI 선택")

selected_mbti = st.selectbox(
    "자신의 MBTI를 선택하세요.",
    mbti_types
)

# 추천 버튼
if st.button("국가 추천받기", type="primary"):

    # 선택한 MBTI 기준으로 정렬
    result = df[["Country", selected_mbti]].copy()

    result = result.sort_values(
        by=selected_mbti,
        ascending=False
    )

    # 상위 5개 국가
    top5 = result.head(5).copy()

    # 백분율 변환
    top5["비율(%)"] = top5[selected_mbti] * 100

    st.success(f"✨ {selected_mbti} 유형의 추천 국가 TOP 5")

    # 결과 출력
    for i, row in enumerate(top5.itertuples(), 1):
        st.write(
            f"**{i}위. {row.Country}**"
            f" - {getattr(row, selected_mbti) * 100:.2f}%"
        )

    # 그래프
    st.subheader("📊 국가별 MBTI 비율")

    fig = px.bar(
        top5,
        x="Country",
        y="비율(%)",
        color="Country",
        text="비율(%)",
        title=f"{selected_mbti} 국가별 비율 TOP 5"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="MBTI 비율 (%)",
        xaxis_title="국가",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# 전체 데이터 확인
st.divider()
st.subheader("📁 전체 국가 데이터")

if st.checkbox("전체 데이터 보기"):
    st.dataframe(df, use_container_width=True)

