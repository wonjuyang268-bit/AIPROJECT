
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write(
    "과거의 기온 데이터를 분석하고 "
    "선형회귀 알고리즘으로 미래의 기온을 예측해 보세요!"
)

st.divider()


# =====================================
# 2. CSV 데이터 불러오기
# =====================================

@st.cache_data
def load_data():

    # 현재 파일이 있는 폴더
    current_dir = Path(__file__).resolve().parent

    # 상위 폴더에서 CSV 찾기
    possible_paths = [
        current_dir.parent / "temperature.csv",
        current_dir / "temperature.csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다.\n"
            "pages 폴더의 상위 폴더에 "
            "temperature.csv가 있는지 확인해 주세요."
        )

    # 한글 인코딩 자동 처리
    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 읽을 수 없습니다."
        )

    # 필요한 열 확인
    required_columns = [
        "일시",
        "평균기온(℃)"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다."
            )

    # 날짜 변환
    month_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    def parse_date(value):
        try:
            month_text, year_text = (
                str(value).strip().split("-")
            )

            month = month_dict[month_text.title()]
            year_num = int(year_text)

            if year_num <= 68:
                year = 2000 + year_num
            else:
                year = 1900 + year_num

            return pd.Timestamp(
                year=year,
                month=month,
                day=1
            )

        except (ValueError, KeyError):
            return pd.NaT

    df["날짜"] = df["일시"].apply(parse_date)

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 평균기온 숫자로 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    # 결측치 제거
    df = df.dropna(
        subset=[
            "날짜",
            "연도",
            "월",
            "평균기온(℃)"
        ]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    # 날짜순 정렬
    df = df.sort_values("날짜")

    return df


# 데이터 불러오기
try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# =====================================
# 3. 월 선택 및 예측 연도 입력
# =====================================

st.subheader("🔎 분석 조건 선택")

month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "📅 분석할 월을 선택하세요",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    latest_year = int(df["연도"].max())

    predict_year = st.number_input(
        "🔮 예측할 연도를 입력하세요",
        min_value=1900,
        max_value=2100,
        value=min(latest_year + 1, 2100),
        step=1
    )

predict_year = int(predict_year)

st.divider()


# =====================================
# 4. 선택한 월의 데이터 추출
# =====================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error(
        "선택한 월의 데이터가 2개 미만입니다. "
        "다른 월을 선택해 주세요."
    )
    st.stop()


# =====================================
# 5. 선형회귀 알고리즘 학습
# =====================================

# X = 연도
# Y = 평균기온

X = month_df[["연도"]].values
y = month_df["평균기온(℃)"].values

# 선형회귀 모델 생성
model = LinearRegression()

# 과거 데이터 학습
model.fit(X, y)

# 입력한 연도의 기온 예측
prediction = model.predict(
    np.array([[predict_year]])
)[0]

# 학습된 데이터의 예측값
train_prediction = model.predict(X)

# 결정계수 계산
r2 = r2_score(
    y,
    train_prediction
)

# 회귀식의 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_


# =====================================
# 6. 회귀 직선 데이터 생성
# =====================================

start_year = min(
    int(month_df["연도"].min()),
    predict_year
)

end_year = max(
    int(month_df["연도"].max()),
    predict_year
)

line_years = np.linspace(
    start_year,
    end_year,
    200
).reshape(-1, 1)

line_temps = model.predict(line_years)


# =====================================
# 7. 예측 결과 출력
# =====================================

st.subheader(
    f"📊 {selected_month}월 평균기온 분석 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🔮 예측 연도",
        f"{predict_year}년"
    )

with col2:
    st.metric(
        "🌡️ 예측 평균기온",
        f"{prediction:.2f} ℃"
    )

with col3:
    st.metric(
        "📈 결정계수 (R²)",
        f"{r2:.3f}"
    )


# =====================================
# 8. 그래프 생성
# =====================================

fig = go.Figure()

# 실제 평균기온
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(
            color="royalblue",
            width=2
        ),
        marker=dict(
            size=8,
            color="royalblue"
        )
    )
)

# 선형회귀 예측선
fig.add_trace(
    go.Scatter(
        x=line_years.flatten(),
        y=line_temps,
        mode="lines",
        name="선형회귀 예측선",
        line=dict(
            color="red",
            width=3,
            dash="dash"
        )
    )
)

# 미래 예측기온
fig.add_trace(
    go.Scatter(
        x=[predict_year],
        y=[prediction],
        mode="markers+text",
        name="미래 예측기온",
        marker=dict(
            color="deeppink",
            size=18,
            symbol="star"
        ),
        text=[
            f"{prediction:.2f}℃"
        ],
        textposition="top center"
    )
)

# 그래프 디자인
fig.update_layout(
    title=f"{selected_month}월 연도별 평균기온 및 미래 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified",
    height=550,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

fig.update_xaxes(
    showgrid=True,
    dtick=1
)

fig.update_yaxes(
    showgrid=True
)

# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 9. 예측 결과 설명
# =====================================

st.success(
    f"🌡️ {predict_year}년 "
    f"{selected_month}월의 예측 평균기온은 "
    f"{prediction:.2f}℃입니다."
)

if predict_year > latest_year:
    st.info(
        f"현재 데이터의 마지막 연도는 {latest_year}년입니다. "
        "그 이후의 연도는 선형회귀 직선을 연장하여 예측합니다."
    )

elif predict_year == latest_year:
    st.info(
        "입력한 연도는 데이터의 마지막 연도와 같습니다. "
        "실제 관측값과 회귀 모델의 예측값은 다를 수 있습니다."
    )


# =====================================
# 10. 선형회귀 분석 정보
# =====================================

st.divider()

st.subheader("📐 선형회귀 분석 결과")

st.write(
    f"**회귀식:** "
    f"평균기온 = ({slope:.4f} × 연도) + ({intercept:.4f})"
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "회귀 직선의 기울기",
        f"{slope:.4f}"
    )

with col2:
    st.metric(
        "결정계수 (R²)",
        f"{r2:.4f}"
    )

st.caption(
    "기울기는 연도가 1년 증가할 때 "
    "회귀 모델이 예측하는 평균기온의 변화량을 의미합니다."
)


# =====================================
# 11. 선형회귀 알고리즘 설명
# =====================================

st.divider()

st.subheader("🧠 선형회귀 알고리즘이란?")

st.markdown("""
선형회귀(Linear Regression)는 과거의 데이터를 바탕으로
두 변수 사이의 관계를 직선으로 나타내고,
그 직선을 이용해 새로운 값을 예측하는 머신러닝 알고리즘입니다.

### ① 데이터 수집

- 선택한 월의 과거 연도별 평균기온을 수집합니다.
- 연도는 X값, 평균기온은 Y값으로 사용합니다.

### ② 데이터 학습

- 과거 데이터의 전체적인 흐름을 분석합니다.
- 실제 데이터와 회귀 직선 사이의 오차 제곱합이
  가장 작아지도록 직선을 학습합니다.

### ③ 미래 기온 예측

- 학습한 직선에 사용자가 입력한 연도를 대입합니다.
- 계산된 결과가 미래의 예측 평균기온입니다.

### 📌 선형회귀의 기본 공식

**Y = aX + b**

- X : 연도
- Y : 예측 평균기온
- a : 기울기
- b : Y절편

### 📊 그래프 색깔 설명

- 🔵 파란색 선과 점: 실제 관측된 과거 평균기온
- 🔴 빨간색 점선: 선형회귀 알고리즘이 학습한 예측 직선
- 💗 핫핑크 별: 입력한 연도의 예측 평균기온

### ④ 결정계수(R²)란?

결정계수는 회귀 모델이 실제 데이터의 변화를
얼마나 잘 설명하는지 나타내는 지표입니다.

- 1에 가까울수록 학습 데이터에 잘 맞습니다.
- 0에 가까울수록 학습 데이터의 변화를 잘 설명하지 못합니다.

단, 결정계수가 높더라도 미래 예측이 반드시 정확한 것은 아닙니다.

### ⚠️ 예측할 때 주의할 점

기온은 기후 변화, 강수량, 바람, 해양 환경 등
다양한 요인의 영향을 받습니다.

이번 프로그램은 연도와 평균기온 사이의 선형적인 관계만
학습하기 때문에 실제 미래 기온과 차이가 발생할 수 있습니다.
""")

# =====================================
# 12. 데이터 출처
# =====================================

st.divider()

st.caption(
    "📚 데이터 출처: temperature.csv"
)

st.caption(
    "🤖 예측 알고리즘: Scikit-learn Linear Regression"
)

st.caption(
    "📊 그래프 라이브러리: Plotly"
)
