import streamlit as st
import csv
import os

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------

st.set_page_config(
    page_title="연령대별 인구 & 여행 추천",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ 연령대별 인구 분석 & 여행지 추천")
st.write("우리나라 인구 데이터를 살펴보고, 연령대별로 가기 좋은 여행지도 알아봐요! 😊")

st.divider()

# ---------------------------------
# 2. CSV 파일 불러오기
# ---------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "population.csv")

if not os.path.exists(FILE_PATH):
    st.error("population.csv 파일을 찾을 수 없어요!")
    st.info("population.csv 파일이 pages 폴더의 상위 폴더에 있는지 확인해주세요.")
    st.stop()

# 한글 인코딩 자동 처리
data = None

for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:
    try:
        with open(FILE_PATH, "r", encoding=encoding) as file:
            reader = csv.DictReader(file)
            data = list(reader)
        break
    except UnicodeDecodeError:
        continue

if not data:
    st.error("CSV 파일을 읽을 수 없어요. 인코딩을 확인해주세요.")
    st.stop()

# ---------------------------------
# 3. 연도 및 성별 선택
# ---------------------------------

st.subheader("🔍 분석 조건 선택")

col1, col2 = st.columns(2)

available_years = []

for row in data:
    for key in row.keys():
        if key and "년_" in key:
            year = key.split("년_")[0]
            if year.isdigit() and year not in available_years:
                available_years.append(year)

available_years.sort()

if not available_years:
    st.error("CSV 파일에서 연도 정보를 찾을 수 없습니다.")
    st.stop()

with col1:
    selected_year = st.selectbox(
        "📅 분석할 연도",
        available_years,
        index=len(available_years) - 1
    )

with col2:
    selected_gender = st.selectbox(
        "👥 성별 선택",
        ["전체", "남성", "여성"]
    )

# 성별에 따른 컬럼 접두사
gender_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}

prefix = gender_prefix[selected_gender]

# ---------------------------------
# 4. 연령대 설정
# ---------------------------------

age_groups = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90세 이상"
]

# 90세 이상은 두 컬럼 합산
age_columns = {
    age: [age] for age in age_groups[:-1]
}

age_columns["90세 이상"] = [
    "90~99세",
    "100세 이상"
]

# ---------------------------------
# 5. 숫자 변환 함수
# ---------------------------------

def to_number(value):
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (ValueError, TypeError):
        return 0

# ---------------------------------
# 6. 행정구별 인구 계산
# ---------------------------------

def get_population(age_group):

    columns = age_columns[age_group]

    result = []

    for row in data:

        district = row.get("행정구역", "").strip()

        if not district:
            continue

        total = 0

        for age in columns:

            column_name = (
                f"{selected_year}년_"
                f"{prefix}거주자_{age}"
            )

            total += to_number(row.get(column_name, 0))

        result.append({
            "행정구역": district,
            "인구수": total
        })

    return result

# ---------------------------------
# 7. 연령대별 그래프 10개
# ---------------------------------

st.divider()

st.header("📊 연령대별 인구 그래프")

st.write(
    f"선택한 조건: **{selected_year}년 / {selected_gender}**"
)

st.caption(
    "각 그래프는 해당 연령대의 행정구역별 인구수를 나타냅니다. "
    "90세 이상은 90~99세와 100세 이상을 합산합니다."
)

for i in range(0, len(age_groups), 2):

    col1, col2 = st.columns(2)

    for col, age_group in zip(
        [col1, col2],
        age_groups[i:i+2]
    ):

        with col:

            st.subheader(f"👥 {age_group}")

            chart_data = get_population(age_group)

            if chart_data and any(
                item["인구수"] > 0 for item in chart_data
            ):

                st.bar_chart(
                    chart_data,
                    x="행정구역",
                    y="인구수",
                    color="#FF69B4",
                    height=350
                )

            else:
                st.warning(
                    f"{age_group}의 데이터를 찾을 수 없습니다."
                )

st.divider()

# ---------------------------------
# 8. 연령대별 여행지 추천
# ---------------------------------

st.header("🌏 연령대별 국내 여행지 추천")

st.write(
    "각 연령대의 관심사와 여행 스타일을 고려한 "
    "국내 관광지 3곳을 추천해 드릴게요! 🧳"
)

travel_recommendations = {

    "0~9세": [
        ("서울어린이대공원", "동물원과 놀이시설이 있어 가족과 함께 즐기기 좋아요. 🐘"),
        ("에버랜드", "다양한 놀이기구와 동물 체험을 할 수 있어요. 🎢"),
        ("국립과천과학관", "신기한 과학 전시와 체험을 즐길 수 있어요. 🔬")
    ],

    "10~19세": [
        ("롯데월드", "친구들과 신나는 놀이기구를 즐기기 좋아요. 🎠"),
        ("경주 대릉원", "역사와 문화를 배우면서 예쁜 사진도 찍을 수 있어요. 📸"),
        ("전주 한옥마을", "전통문화와 다양한 먹거리를 경험할 수 있어요. 🍡")
    ],

    "20~29세": [
        ("부산 광안리", "바다와 야경을 즐기며 특별한 추억을 만들 수 있어요. 🌊"),
        ("서울 성수동", "감성 카페와 개성 있는 전시 공간이 많아요. ☕"),
        ("제주도", "아름다운 자연과 다양한 액티비티를 즐길 수 있어요. 🏝️")
    ],

    "30~39세": [
        ("남이섬", "자연 속에서 산책과 휴식을 즐기기 좋아요. 🌳"),
        ("제주 에코랜드", "기차를 타고 제주도의 자연을 구경할 수 있어요. 🚂"),
        ("경주 동궁과 월지", "아름다운 야경과 역사적인 분위기를 느낄 수 있어요. 🌙")
    ],

    "40~49세": [
        ("순천만국가정원", "아름다운 정원과 자연 풍경을 감상할 수 있어요. 🌷"),
        ("경주 불국사", "한국의 역사와 전통문화를 경험하기 좋아요. 🏯"),
        ("강릉 경포대", "바다를 바라보며 여유로운 시간을 보내기 좋아요. 🌅")
    ],

    "50~59세": [
        ("담양 죽녹원", "대나무 숲길을 걸으며 힐링할 수 있어요. 🎋"),
        ("통영 동피랑", "아기자기한 벽화와 바다 풍경을 즐길 수 있어요. 🎨"),
        ("부여 백제문화단지", "백제의 역사와 문화를 알아볼 수 있어요. 🏛️")
    ],

    "60~69세": [
        ("여수 오동도", "아름다운 바다와 산책로가 매력적인 곳이에요. 🌊"),
        ("안동 하회마을", "한국의 전통적인 마을 풍경을 감상할 수 있어요. 🏡"),
        ("군산 근대역사거리", "옛 건축물과 근대 역사를 둘러보기 좋아요. 📷")
    ],

    "70~79세": [
        ("수원화성", "역사적인 성곽과 주변 풍경을 감상할 수 있어요. 🏰"),
        ("공주 공산성", "백제의 역사를 느끼며 여유롭게 둘러볼 수 있어요. 🌳"),
        ("올림픽공원", "넓고 완만한 산책로에서 자연을 즐기기 좋아요. 🌲")
    ],

    "80~89세": [
        ("서울숲", "자연을 감상하며 가볍게 산책하기 좋아요. 🌼"),
        ("국립중앙박물관", "실내에서 편안하게 역사와 문화를 관람할 수 있어요. 🏛️"),
        ("올림픽공원", "넓은 공원에서 쉬어가며 자연을 즐길 수 있어요. 🍃")
    ],

    "90세 이상": [
        ("집 근처 큰 공원", "이동 부담을 줄이고 가까운 곳에서 자연을 즐길 수 있어요. 🌳"),
        ("국립중앙박물관", "실내에서 천천히 전시를 관람할 수 있어요. 🖼️"),
        ("국립현대미술관 서울관", "다양한 예술 작품을 실내에서 감상할 수 있어요. 🎨")
    ]

}

# ---------------------------------
# 9. 여행지 추천 출력
# ---------------------------------

for age_group in age_groups:

    with st.expander(
        f"🎒 {age_group} 추천 여행지 확인하기",
        expanded=False
    ):

        places = travel_recommendations[age_group]

        st.write(
            f"### ✨ {age_group}에게 추천하는 여행지 TOP 3"
        )

        for index, (place, description) in enumerate(
            places, start=1
        ):

            st.markdown(
                f"**{index}. 📍 {place}**"
            )

            st.write(description)

            st.write("")

st.divider()

# ---------------------------------
# 10. 마무리
# ---------------------------------

st.success(
    "🎉 연령대별 인구 분석과 여행지 추천이 모두 끝났어요!"
)

st.info(
    "💡 여행지를 선택할 때는 개인의 취향과 건강 상태, "
    "이동 편의성, 동행자 등을 함께 고려해 주세요."
)

st.caption(
    "데이터 출처: population.csv | "
    "여행지 추천: 연령대별 일반적인 여행 선호를 고려한 예시"
)

