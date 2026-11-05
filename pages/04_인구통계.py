
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

PINK = "#FF69B4"

AGE_GROUPS = [
    "0~9세", "10~19세", "20~29세",
    "30~39세", "40~49세", "50~59세",
    "60~69세", "70~79세", "80~89세",
    "90~99세", "100세 이상"
]

YEARS = [str(year) for year in range(2020, 2026)]

SEX_OPTIONS = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}

# ==========================================
# 2. 한글 글꼴 설정
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Noto Sans KR', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 제목
# ==========================================
st.title("📊 서울시 연령별 인구 분석")
st.caption(
    "행정구역, 성별, 연도를 선택하여 "
    "서울시의 연령대별 인구 분포를 확인할 수 있습니다."
)

# ==========================================
# 4. CSV 파일 경로
# pages 폴더의 상위 폴더에 있는 CSV 불러오기
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "population.csv"

# ==========================================
# 5. CSV 불러오기 및 한글 인코딩
# ==========================================
@st.cache_data
def load_data(file_path):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    data = None
    used_encoding = None
    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding,
                thousands=","
            )
            used_encoding = encoding
            break

        except UnicodeDecodeError as error:
            last_error = error

    if data is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인할 수 없습니다."
        ) from last_error

    if "행정구역" not in data.columns:
        raise ValueError(
            "'행정구역' 컬럼이 없습니다."
        )

    # 행정구역 코드 제거
    data["행정구역명"] = (
        data["행정구역"]
        .astype(str)
        .str.replace(
            r"\s*\(\d+\)\s*$",
            "",
            regex=True
        )
        .str.strip()
    )

    # 숫자 데이터 변환
    for column in data.columns:
        if column not in ["행정구역", "행정구역명"]:
            data[column] = pd.to_numeric(
                data[column]
                .astype(str)
                .str.replace(",", "", regex=False),
                errors="coerce"
            )

    return data, used_encoding


# ==========================================
# 6. 데이터 불러오기
# ==========================================
if not DATA_FILE.exists():

    st.error(
        "population.csv 파일을 찾을 수 없습니다. "
        "pages 폴더의 상위 폴더에 CSV 파일이 있는지 확인해주세요."
    )

    st.stop()

try:
    df, used_encoding = load_data(str(DATA_FILE))

except Exception as error:
    st.error(f"데이터 오류: {error}")
    st.stop()


# ==========================================
# 7. 선택 메뉴
# ==========================================
districts = sorted(
    df["행정구역명"].dropna().unique().tolist(),
    key=lambda name: (name != "서울특별시", name)
)

col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox(
        "🏙️ 행정구역 선택",
        districts,
        index=0
    )

with col2:
    selected_sex = st.selectbox(
        "👥 성별 선택",
        list(SEX_OPTIONS.keys()),
        index=0
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도 선택",
        YEARS,
        index=len(YEARS) - 1
    )


# ==========================================
# 8. 선택한 행정구역 데이터 추출
# ==========================================
selected_rows = df.loc[
    df["행정구역명"] == selected_district
]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_row = selected_rows.iloc[0]


# ==========================================
# 9. 연령별 컬럼명 생성
# ==========================================
sex_prefix = SEX_OPTIONS[selected_sex]

age_columns = [
    f"{selected_year}년_{sex_prefix}거주자_{age}"
    for age in AGE_GROUPS
]

missing_columns = [
    column for column in age_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "필요한 데이터 컬럼을 찾을 수 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ==========================================
# 10. 그래프 데이터 생성
# ==========================================
chart_data = pd.DataFrame({
    "연령대": AGE_GROUPS,
    "인구수": [
        selected_row[column]
        for column in age_columns
    ]
})

chart_data["인구수"] = pd.to_numeric(
    chart_data["인구수"],
    errors="coerce"
)

chart_data = chart_data.dropna(
    subset=["인구수"]
)

if chart_data.empty:
    st.warning("선택한 조건의 데이터가 없습니다.")
    st.stop()


# ==========================================
# 11. 주요 인구 정보
# ==========================================
total_population = int(
    chart_data["인구수"].sum()
)

largest_age_row = chart_data.loc[
    chart_data["인구수"].idxmax()
]

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "연령별 인구 합계",
    f"{total_population:,}명"
)

metric2.metric(
    "인구가 가장 많은 연령대",
    largest_age_row["연령대"]
)

metric3.metric(
    "해당 연령대 인구",
    f"{int(largest_age_row['인구수']):,}명"
)


# ==========================================
# 12. 핫핑크 꺾은선 그래프
# ==========================================
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_data["연령대"],
        y=chart_data["인구수"],
        mode="lines+markers",
        name="인구수",

        line=dict(
            color=PINK,
            width=4
        ),

        marker=dict(
            color=PINK,
            size=10,
            line=dict(
                color="white",
                width=1.5
            )
        ),

        hovertemplate=(
            "<b>%{x}</b><br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

fig.update_layout(

    title=dict(
        text=(
            f"{selected_district} "
            f"{selected_year}년 "
            f"{selected_sex} 연령별 인구"
        ),
        x=0.02,
        xanchor="left",
        font=dict(
            size=21,
            family="Noto Sans KR, NanumGothic, sans-serif"
        )
    ),

    font=dict(
        family="Noto Sans KR, NanumGothic, sans-serif",
        size=13,
        color="#333333"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    height=570,

    margin=dict(
        l=35,
        r=25,
        t=85,
        b=45
    ),

    # 가로축: 나이
    xaxis=dict(
        title="나이",
        type="category",
        categoryorder="array",
        categoryarray=AGE_GROUPS,
        tickmode="array",
        tickvals=AGE_GROUPS,
        ticktext=AGE_GROUPS,
        showgrid=True,
        gridcolor="#E5E5E5",
        gridwidth=1,
        showline=True,
        linecolor="#BBBBBB",
        tickangle=0
    ),

    # 세로축: 인구수
    yaxis=dict(
        title="인구수 (명)",
        rangemode="tozero",
        tickmode="linear",
        tick0=0,
        dtick=100000,
        tickformat=",",
        showgrid=True,
        gridcolor="#DCDCDC",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="#AAAAAA"
    ),

    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "displaylogo": False
    }
)


# ==========================================
# 13. 연령별 상세 데이터 표
# ==========================================
with st.expander("📋 연령대별 상세 인구 데이터 확인"):

    display_data = chart_data.copy()

    display_data["인구수"] = (
        display_data["인구수"]
        .apply(lambda value: f"{int(value):,}명")
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 14. 데이터 정보
# ==========================================
with st.expander("데이터 정보"):

    st.write(f"파일명: {DATA_FILE.name}")
    st.write(f"인코딩: {used_encoding}")
    st.write(f"행정구역: {selected_district}")
    st.write(f"성별: {selected_sex}")
    st.write(f"연도: {selected_year}")

    st.write(
        f"데이터 크기: {df.shape[0]}행 × {df.shape[1]}열"
    )

st.caption(
    "데이터 출처: population.csv | "
    "연령대는 10살 단위이며 100세 이상은 별도 구간입니다."
)
