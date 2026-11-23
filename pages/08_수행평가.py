
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import re

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="지역별 인구 & 여행 추천",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ 지역별 인구 분석 & 여행 추천")
st.write(
    "우리 지역의 연령대별 인구를 분석하고 "
    "나에게 어울리는 여행지도 찾아봐요! 😊"
)

st.divider()

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

FILE_PATH = os.path.join(
    BASE_DIR,
    "202610_202610_연령별인구현황_월간.csv"
)

@st.cache_data
def load_data(path):

    for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:

        try:
            return pd.read_csv(
                path,
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해주세요.")

if not os.path.exists(FILE_PATH):

    st.error("CSV 파일을 찾을 수 없습니다.")

    st.info(
        "CSV 파일이 pages 폴더의 상위 폴더에 있는지 확인해주세요."
    )

    st.stop()

try:

    df = load_data(FILE_PATH)

except Exception as e:

    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()

# ==========================================
# 3. 데이터 전처리
# ==========================================

# 지역명 정리
df["지역"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)", "", regex=True)
    .str.strip()
)

# 연령대 컬럼 자동 탐색
age_columns = {}

for column in df.columns:

    match = re.search(
        r"_계_(\d+~\d+세|100세 이상)$",
        column
    )

    if match:

        age = match.group(1)
        age_columns[age] = column

def age_sort_key(age):

    if age == "100세 이상":
        return 1000

    return int(age.split("~")[0])

age_groups = sorted(
    age_columns.keys(),
    key=age_sort_key
)

if len(age_groups) == 0:

    st.error("연령대 컬럼을 찾지 못했습니다.")
    st.stop()

# 인구 데이터 숫자 변환
for column in age_columns.values():

    df[column] = pd.to_numeric(
        df[column].astype(str).str.replace(
            ",", "", regex=False
        ),
        errors="coerce"
    )

# 전체 인구 컬럼
total_columns = [
    c for c in df.columns
    if re.search(r"_계_총인구수$", c)
]

if total_columns:

    total_column = total_columns[0]

    df[total_column] = pd.to_numeric(
        df[total_column].astype(str).str.replace(
            ",", "", regex=False
        ),
        errors="coerce"
    )

else:
    total_column = None

# ==========================================
# 4. 데이터 요약
# ==========================================

st.subheader("📊 데이터 기본 정보")

missing_count = df[
    list(age_columns.values())
].isnull().sum().sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("전체 행", f"{len(df)}개")

with c2:
    st.metric("분석 지역", f"{len(df) - 1}개")

with c3:
    st.metric("연령대", f"{len(age_groups)}개")

with c4:
    st.metric("연령 데이터 결측치", f"{missing_count}개")

with st.expander("🔍 데이터 자세히 살펴보기"):

    st.write("**데이터 크기**")
    st.write(f"{df.shape[0]}행 × {df.shape[1]}열")

    st.write("**결측치 확인**")
    st.write(df.isnull().sum())

    st.write("**데이터 유형**")
    st.write(df.dtypes.astype(str))

    st.write("**CSV 미리보기**")
    st.dataframe(df, use_container_width=True)

# ==========================================
# 5. 지역 및 연령대 선택
# ==========================================

st.divider()

st.header("🗺️ 지역별 인구 분석")

regions = sorted(
    df.loc[df["지역"] != "전국", "지역"].dropna().unique()
)

col1, col2 = st.columns(2)

with col1:

    selected_region = st.selectbox(
        "📍 여행할 지역을 선택하세요!",
        regions,
        index=regions.index("서울특별시")
        if "서울특별시" in regions else 0
    )

with col2:

    selected_age = st.selectbox(
        "👥 여행할 연령대를 선택하세요!",
        age_groups
    )

# 선택 지역 데이터
region_data = df[
    df["지역"] == selected_region
]

if region_data.empty:

    st.error("해당 지역의 데이터가 없습니다.")
    st.stop()

region_data = region_data.iloc[0]

# ==========================================
# 6. 연령대별 인구 계산
# ==========================================

chart_data = []

for age in age_groups:

    value = region_data[age_columns[age]]

    if pd.isna(value):
        value = 0

    chart_data.append({
        "연령대": age,
        "인구수": int(value)
    })

chart_df = pd.DataFrame(chart_data)

chart_df["순위"] = (
    chart_df["인구수"]
    .rank(method="min", ascending=False)
    .astype(int)
)

chart_df = chart_df.sort_values(
    "인구수",
    ascending=False
)

# ==========================================
# 7. 그래프 색상 설정
# ==========================================

blue_colors = [
    "#174EA6",
    "#2864B4",
    "#3D7BC4",
    "#5592D4",
    "#70A9E1",
    "#8ABCEB",
    "#A6CDF2",
    "#BCDDF7",
    "#D1E8FA",
    "#E3F1FC"
]

color_map = {}

for _, row in chart_df.iterrows():

    if row["순위"] == 1:

        color_map[row["연령대"]] = "#FF3030"

    else:

        index = min(
            row["순위"] - 2,
            len(blue_colors) - 1
        )

        color_map[row["연령대"]] = blue_colors[index]

# ==========================================
# 8. 주요 인구 통계
# ==========================================

total_population = int(chart_df["인구수"].sum())

top_age = chart_df.iloc[0]

selected_population = int(
    chart_df.loc[
        chart_df["연령대"] == selected_age,
        "인구수"
    ].iloc[0]
)

st.subheader(f"📌 {selected_region} 인구 현황")

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "전체 인구",
        f"{total_population:,}명"
    )

with c2:

    st.metric(
        "인구 1위 연령대",
        top_age["연령대"]
    )

with c3:

    st.metric(
        f"{selected_age} 인구",
        f"{selected_population:,}명"
    )

# ==========================================
# 9. Plotly 그래프
# ==========================================

st.subheader("📊 연령대별 인구 막대그래프")

st.caption(
    "🔴 인구수 1위 / 🔵 나머지는 순위에 따른 파란색 그라데이션"
)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=age_groups,

        y=[
            int(
                chart_df.loc[
                    chart_df["연령대"] == age,
                    "인구수"
                ].iloc[0]
            )
            for age in age_groups
        ],

        marker_color=[
            color_map[age]
            for age in age_groups
        ],

        text=[
            f"{int(chart_df.loc[chart_df['연령대'] == age, '인구수'].iloc[0]):,}명"
            for age in age_groups
        ],

        textposition="outside",

        hovertemplate=(
            "<b>%{x}</b><br>"
            "인구수: %{y:,}명"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    title=f"{selected_region} 연령대별 인구 분석",
    xaxis_title="연령대",
    yaxis_title="인구수 (명)",
    template="plotly_white",
    height=550,
    showlegend=False,
    hovermode="x",
    yaxis=dict(
        tickformat=",",
        gridcolor="#EAEAEA"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 10. 여행 취향 카테고리
# ==========================================

age_preferences = {

    "0~9세": ["family", "experience", "nature"],
    "10~19세": ["activity", "photo", "culture"],
    "20~29세": ["activity", "photo", "cafe"],
    "30~39세": ["nature", "culture", "experience"],
    "40~49세": ["culture", "nature", "history"],
    "50~59세": ["culture", "nature", "healing"],
    "60~69세": ["healing", "culture", "easy"],
    "70~79세": ["easy", "healing", "culture"],
    "80~89세": ["easy", "healing", "indoor"],
    "90~99세": ["easy", "indoor", "healing"],
    "100세 이상": ["easy", "indoor", "healing"]

}

# ==========================================
# 11. 지역별 관광지 데이터
# ==========================================

# 각 지역의 대표 관광지
# 장소 이름, 관련 취향, 설명

local_places = {

    "서울특별시": [
        ("롯데월드", ["family", "activity"], "놀이기구와 다양한 체험을 즐길 수 있는 테마파크"),
        ("경복궁", ["culture", "history", "photo"], "한국의 역사와 전통 건축을 감상할 수 있는 곳"),
        ("서울숲", ["nature", "healing", "easy"], "자연 속에서 산책하고 휴식하기 좋은 공원"),
        ("성수동", ["cafe", "photo", "activity"], "개성 있는 카페와 전시 공간이 많은 거리")
    ],

    "경기도": [
        ("에버랜드", ["family", "activity", "experience"], "다양한 놀이시설과 동물 체험이 가능한 곳"),
        ("수원화성", ["history", "culture", "easy"], "유네스코 세계유산으로 유명한 역사 관광지"),
        ("한국민속촌", ["culture", "history", "experience"], "전통 생활문화와 공연을 체험할 수 있는 곳"),
        ("아침고요수목원", ["nature", "healing", "photo"], "아름다운 정원과 자연 풍경을 감상하는 곳")
    ],

    "부산광역시": [
        ("해운대 해수욕장", ["nature", "photo", "easy"], "부산을 대표하는 바다 관광지"),
        ("광안리 해수욕장", ["photo", "activity", "cafe"], "바다와 야경, 다양한 카페가 매력적인 곳"),
        ("감천문화마을", ["culture", "photo", "history"], "알록달록한 집과 예술 작품을 만날 수 있는 마을"),
        ("태종대", ["nature", "healing", "easy"], "바다 절경과 산책 코스를 즐길 수 있는 곳")
    ],

    "대구광역시": [
        ("이월드", ["family", "activity", "photo"], "놀이기구와 전망대가 있는 테마파크"),
        ("김광석 다시그리기길", ["culture", "photo", "cafe"], "음악과 벽화가 어우러진 거리"),
        ("앞산공원", ["nature", "healing", "activity"], "도심 풍경과 자연을 즐길 수 있는 공원"),
        ("대구 근대골목", ["history", "culture", "easy"], "대구의 근대 역사를 살펴볼 수 있는 곳")
    ],

    "인천광역시": [
        ("월미도", ["family", "activity", "photo"], "바다와 놀이시설을 함께 즐길 수 있는 곳"),
        ("차이나타운", ["culture", "photo", "experience"], "이국적인 거리와 다양한 먹거리가 있는 곳"),
        ("송도 센트럴파크", ["nature", "photo", "easy"], "도심 속에서 산책과 수변 풍경을 즐기는 곳"),
        ("강화도 전등사", ["history", "healing", "culture"], "역사와 자연을 함께 느낄 수 있는 사찰")
    ],

    "대전광역시": [
        ("엑스포과학공원", ["family", "experience", "culture"], "과학과 기술을 체험할 수 있는 공간"),
        ("한밭수목원", ["nature", "healing", "easy"], "다양한 식물과 정원을 감상하는 곳"),
        ("대청호", ["nature", "photo", "healing"], "호수 풍경을 보며 휴식하기 좋은 곳"),
        ("성심당 주변 원도심", ["cafe", "photo", "activity"], "먹거리와 옛 도심 분위기를 즐길 수 있는 곳")
    ],

    "울산광역시": [
        ("대왕암공원", ["nature", "healing", "easy"], "바다와 해안 산책로가 아름다운 곳"),
        ("태화강 국가정원", ["nature", "healing", "photo"], "꽃과 정원을 감상하며 쉬기 좋은 곳"),
        ("장생포 고래문화마을", ["family", "culture", "experience"], "고래와 관련된 역사와 문화를 체험하는 곳"),
        ("간절곶", ["photo", "nature", "easy"], "탁 트인 바다와 일출 풍경이 유명한 곳")
    ],

    "세종특별자치시": [
        ("국립세종수목원", ["nature", "healing", "indoor"], "다양한 식물을 관람할 수 있는 수목원"),
        ("세종호수공원", ["nature", "easy", "photo"], "호수 주변 산책과 휴식을 즐기기 좋은 곳"),
        ("국립세종도서관", ["indoor", "culture", "easy"], "건축과 독서 문화를 즐길 수 있는 공간"),
        ("금강보행교", ["photo", "activity", "easy"], "금강의 풍경을 감상하며 걷기 좋은 다리")
    ],

    "강원특별자치도": [
        ("속초 해수욕장", ["nature", "photo", "easy"], "바다 풍경과 해변 산책을 즐기는 곳"),
        ("남이섬", ["nature", "photo", "healing"], "아름다운 나무길과 자연이 매력적인 섬"),
        ("강릉 경포대", ["nature", "healing", "easy"], "바다와 호수의 풍경을 함께 즐기는 곳"),
        ("정선 레일바이크", ["activity", "experience", "nature"], "아름다운 자연을 보며 즐기는 체험 관광")
    ],

    "충청북도": [
        ("청남대", ["history", "nature", "easy"], "대통령 별장과 아름다운 정원을 둘러보는 곳"),
        ("단양 도담삼봉", ["nature", "photo", "easy"], "남한강의 아름다운 자연 경관을 감상하는 곳"),
        ("충주호", ["nature", "healing", "photo"], "호수와 산이 어우러진 관광지"),
        ("속리산 법주사", ["history", "culture", "healing"], "역사적인 사찰과 자연을 함께 느끼는 곳")
    ],

    "충청남도": [
        ("공주 공산성", ["history", "culture", "easy"], "백제의 역사를 느낄 수 있는 성곽"),
        ("부여 백제문화단지", ["history", "culture", "experience"], "백제의 역사와 문화를 체험하는 곳"),
        ("대천해수욕장", ["nature", "photo", "activity"], "넓은 해변과 해양 활동을 즐기는 곳"),
        ("아산 외암민속마을", ["history", "culture", "healing"], "전통 가옥과 옛 마을 풍경을 감상하는 곳")
    ],

    "전북특별자치도": [
        ("전주 한옥마을", ["culture", "photo", "experience"], "전통 한옥과 다양한 먹거리를 즐기는 곳"),
        ("군산 근대역사거리", ["history", "culture", "easy"], "근대 건축물과 역사 이야기가 있는 거리"),
        ("내장산 국립공원", ["nature", "healing", "photo"], "계절마다 아름다운 자연 경관을 즐기는 곳"),
        ("남원 광한루원", ["history", "culture", "easy"], "전통 정원과 춘향 이야기를 만나는 곳")
    ],

    "전남광주통합특별시": [
        ("순천만국가정원", ["nature", "healing", "easy"], "다양한 정원과 자연을 감상할 수 있는 곳"),
        ("여수 오동도", ["nature", "photo", "easy"], "바다와 동백나무 산책로가 매력적인 곳"),
        ("광주 국립아시아문화전당", ["culture", "indoor", "photo"], "다양한 예술 전시와 문화 활동을 즐기는 곳"),
        ("담양 죽녹원", ["nature", "healing", "easy"], "대나무 숲길을 걸으며 휴식할 수 있는 곳")
    ],

    "경상북도": [
        ("경주 불국사", ["history", "culture", "healing"], "신라의 역사와 전통 건축을 느낄 수 있는 곳"),
        ("안동 하회마을", ["history", "culture", "easy"], "한국의 전통 마을 풍경을 감상하는 곳"),
        ("포항 영일대해수욕장", ["nature", "photo", "cafe"], "바다와 야경을 즐기기 좋은 곳"),
        ("문경새재", ["nature", "healing", "activity"], "아름다운 산길과 역사적인 길을 걷는 곳")
    ],

    "경상남도": [
        ("통영 동피랑", ["photo", "culture", "easy"], "벽화와 바다 풍경을 즐길 수 있는 마을"),
        ("거제 바람의 언덕", ["nature", "photo", "healing"], "탁 트인 바다 풍경이 유명한 관광지"),
        ("진주성", ["history", "culture", "easy"], "역사적인 전투와 문화를 살펴볼 수 있는 성"),
        ("김해 가야테마파크", ["family", "experience", "activity"], "가야 역사와 다양한 체험을 즐기는 곳")
    ],

    "제주특별자치도": [
        ("성산일출봉", ["nature", "activity", "photo"], "제주의 아름다운 일출과 자연 경관"),
        ("섭지코지", ["nature", "photo", "easy"], "바다와 초원이 어우러진 산책 명소"),
        ("제주 아쿠아플라넷", ["family", "indoor", "experience"], "다양한 해양 생물을 관찰할 수 있는 곳"),
        ("한라수목원", ["nature", "healing", "easy"], "제주의 식물과 자연을 즐기는 공간")
    ]
}

# ==========================================
# 12. 전국 공통 추천 여행지
# ==========================================

national_places = {

    "0~9세": [
        ("에버랜드", "경기도", "다양한 놀이기구와 동물 체험을 즐길 수 있어요. 🎢"),
        ("국립과천과학관", "경기도", "재미있는 과학 전시와 체험이 가득해요. 🔬")
    ],

    "10~19세": [
        ("롯데월드", "서울", "친구들과 신나는 놀이기구와 사진을 즐겨봐요. 🎠"),
        ("전주 한옥마을", "전북", "전통문화와 맛있는 먹거리를 경험해 봐요. 🍡")
    ],

    "20~29세": [
        ("제주도", "제주", "아름다운 바다와 다양한 액티비티를 즐겨봐요. 🏝️"),
        ("부산 광안리", "부산", "야경과 바다, 감성 카페를 즐기기 좋아요. 🌊")
    ],

    "30~39세": [
        ("남이섬", "강원", "자연 속에서 여유로운 시간을 보내기 좋아요. 🌳"),
        ("경주 동궁과 월지", "경북", "역사와 아름다운 야경을 함께 즐겨봐요. 🌙")
    ],

    "40~49세": [
        ("순천만국가정원", "전남", "다양한 정원과 자연 풍경을 감상해요. 🌷"),
        ("경주 불국사", "경북", "우리나라의 역사와 전통문화를 경험해요. 🏯")
    ],

    "50~59세": [
        ("담양 죽녹원", "전남", "대나무 숲길에서 여유롭게 힐링해요. 🎋"),
        ("통영 동피랑", "경남", "아기자기한 벽화와 바다를 즐겨봐요. 🎨")
    ],

    "60~69세": [
        ("여수 오동도", "전남", "바다 풍경과 산책로를 즐겨봐요. 🌊"),
        ("안동 하회마을", "경북", "전통문화와 역사적인 마을을 둘러봐요. 🏡")
    ],

    "70~79세": [
        ("수원화성", "경기", "역사적인 성곽과 주변 풍경을 감상해요. 🏰"),
        ("국립중앙박물관", "서울", "실내에서 편안하게 역사와 문화를 관람해요. 🏛️")
    ],

    "80~89세": [
        ("국립중앙박물관", "서울", "실내에서 천천히 전시를 관람해요. 🖼️"),
        ("서울숲", "서울", "자연 속에서 가볍게 산책하고 쉬어가요. 🌼")
    ],

    "90~99세": [
        ("국립중앙박물관", "서울", "실내 전시를 편안하게 감상할 수 있어요. 🏛️"),
        ("국립현대미술관 서울관", "서울", "다양한 예술 작품을 감상해 봐요. 🎨")
    ],

    "100세 이상": [
        ("국립중앙박물관", "서울", "실내에서 여유롭게 문화생활을 즐겨요. 🏛️"),
        ("서울숲", "서울", "이동 동선을 짧게 잡고 자연을 즐겨봐요. 🌳")
    ]

}

# ==========================================
# 13. 지역 관광지 추천 계산
# ==========================================

def recommend_local(region, age):

    places = local_places.get(region, [])

    preferences = age_preferences.get(
        age,
        ["culture", "nature", "healing"]
    )

    scored_places = []

    for name, tags, description in places:

        score = sum(
            1 for tag in preferences
            if tag in tags
        )

        scored_places.append({
            "name": name,
            "description": description,
            "score": score
        })

    scored_places.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored_places[:3]

# ==========================================
# 14. 여행지 추천 화면
# ==========================================

st.divider()

st.header("🎒 나이대별 여행지 추천")

st.write(
    f"**{selected_region} / {selected_age}** 기준으로 "
    "추천 여행지를 찾아봤어요! ✨"
)

# 지역별 추천 3곳
st.subheader("📍 선택 지역 주변 추천 여행지 TOP 3")

local_recommendations = recommend_local(
    selected_region,
    selected_age
)

for i, place in enumerate(
    local_recommendations,
    start=1
):

    with st.container(border=True):

        st.markdown(
            f"### {i}. 🗺️ {place['name']}"
        )

        st.write(place["description"])

        st.caption(
            f"연령대 관심사 적합도: {place['score']}점"
        )

# ==========================================
# 15. 전국 공통 추천 2곳
# ==========================================

st.divider()

st.subheader("🌏 지역 상관없이 추천하는 전국 여행지 TOP 2")

st.write(
    f"{selected_age}에게 추천하는 "
    "전국의 대표 여행지예요! 🚀"
)

for i, place in enumerate(
    national_places.get(selected_age, []),
    start=1
):

    name, location, description = place

    with st.container(border=True):

        st.markdown(
            f"### {i}. ✨ {name}"
        )

        st.write(f"📍 위치: {location}")

        st.write(description)

# ==========================================
# 16. 마무리
# ==========================================

st.divider()

st.success(
    f"🎉 {selected_region}의 {selected_age} 인구 분석과 "
    "여행지 추천이 완료되었어요!"
)

st.info(
    "💡 여행지를 선택할 때는 개인의 취향, "
    "이동 거리, 건강 상태와 교통편도 함께 확인해 주세요."
)

st.caption(
    "인구 데이터: 2026년 10월 연령별 인구현황 CSV | "
    "관광지: 지역 대표 관광지 기반 자체 추천"
)
