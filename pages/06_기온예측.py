
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score


# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="기온 분석 및 회귀 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write(
    "3가지 회귀 알고리즘을 직접 선택하고 "
    "알고리즘에 따라 예측 결과가 어떻게 달라지는지 확인해 보세요!"
)

st.divider()


# =====================================
# 2. CSV 파일 불러오기
# =====================================

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

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
            "temperature.csv 파일을 찾을 수 없습니다. "
            "pages 폴더의 상위 폴더를 확인해 주세요."
        )

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
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    required_columns = [
        "일시",
        "평균기온(℃)"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"'{column}' 열이 CSV에 없습니다."
            )

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    def parse_date(value):
        value = str(value).strip()

        # YYYY-MM 형식 처리
        try:
            return pd.to_datetime(
                value,
                format="%Y-%m"
            )
        except ValueError:
            pass

        # YYYY.MM 형식 처리
        try:
            return pd.to_datetime(
                value,
                format="%Y.%m"
            )
        except ValueError:
            pass

        # Oct-07 형식 처리
        try:
            month_text, year_text = value.split("-")

            month = month_dict[month_text.title()]
            year_num = int(year_text)

            if year_num <= 68:
                year = 2000 + year_num
            else:
                year = 1900 + year_num

            return pd.Timestamp(year, month, 1)

        except (ValueError, KeyError):
            return pd.NaT

    df["날짜"] = df["일시"].apply(parse_date)

    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

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

    return df.sort_values("날짜")


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# =====================================
# 3. 월과 예측 연도 선택
# =====================================

st.subheader("🔎 분석 조건 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "📅 분석할 월 선택",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    latest_year = int(df["연도"].max())

    predict_year = st.number_input(
        "🔮 예측할 연도 입력",
        min_value=1900,
        max_value=2100,
        value=min(latest_year + 1, 2100),
        step=1
    )

predict_year = int(predict_year)


# =====================================
# 4. 회귀 알고리즘 선택
# =====================================

st.divider()
st.subheader("🤖 회귀 알고리즘 선택")

algorithm_names = {
    "선형회귀": "Linear Regression",
    "다항회귀": "Polynomial Regression",
    "랜덤 포레스트 회귀": "Random Forest Regression"
}

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    list(algorithm_names.keys())
)

algorithm_descriptions = {
    "선형회귀": "직선을 이용해 전체적인 기온 변화 추세를 학습합니다.",
    "다항회귀": "2차 곡선을 이용해 기온의 비선형적인 변화 패턴을 학습합니다.",
    "랜덤 포레스트 회귀": "여러 의사결정나무의 결과를 결합해 예측합니다."
}

st.info(
    f"💡 {selected_algorithm}: "
    f"{algorithm_descriptions[selected_algorithm]}"
)


# =====================================
# 5. 선택한 월의 데이터 추출
# =====================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("학습할 데이터가 부족합니다.")
    st.stop()

# 같은 연도에 데이터가 여러 개 있으면 평균 계산
month_df = (
    month_df.groupby("연도", as_index=False)
    ["평균기온(℃)"].mean()
)

if len(month_df) < 2:
    st.error("학습할 연도가 2개 이상 필요합니다.")
    st.stop()

# 연도를 첫 번째 연도 기준으로 변환
# 큰 연도 숫자로 인한 다항회귀 계산 문제 방지
base_year = int(month_df["연도"].min())

X = (
    month_df[["연도"]].values - base_year
)

y = month_df["평균기온(℃)"].values


# =====================================
# 6. 세 가지 알고리즘 생성
# =====================================

models = {

    "선형회귀": LinearRegression(),

    "다항회귀": make_pipeline(
        PolynomialFeatures(
            degree=2,
            include_bias=False
        ),
        LinearRegression()
    ),

    "랜덤 포레스트 회귀": RandomForestRegressor(
        n_estimators=200,
        max_depth=4,
        min_samples_leaf=2,
        random_state=42
    )
}


# =====================================
# 7. 세 가지 알고리즘 학습 및 비교
# =====================================

comparison_results = []
trained_models = {}

for name, model in models.items():

    # 모델 학습
    model.fit(X, y)

    # 과거 데이터 예측
    train_pred = model.predict(X)

    # 결정계수 계산
    score = r2_score(y, train_pred)

    # 사용자가 입력한 연도 예측
    future_X = np.array([
        [predict_year - base_year]
    ])

    future_prediction = model.predict(
        future_X
    )[0]

    trained_models[name] = model

    comparison_results.append({
        "알고리즘": name,
        "예측 평균기온(℃)": round(
            float(future_prediction), 2
        ),
        "결정계수(R²)": round(
            float(score), 4
        )
    })


# 비교 데이터프레임
comparison_df = pd.DataFrame(
    comparison_results
)

# 선택한 알고리즘
model = trained_models[selected_algorithm]

prediction = float(
    comparison_df.loc[
        comparison_df["알고리즘"] == selected_algorithm,
        "예측 평균기온(℃)"
    ].iloc[0]
)

r2 = float(
    comparison_df.loc[
        comparison_df["알고리즘"] == selected_algorithm,
        "결정계수(R²)"
    ].iloc[0]
)


# =====================================
# 8. 예측 결과 출력
# =====================================

st.divider()

st.subheader(
    f"📊 {selected_month}월 기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택 알고리즘",
        selected_algorithm
    )

with col2:
    st.metric(
        "예측 연도",
        f"{predict_year}년"
    )

with col3:
    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )

st.metric(
    "결정계수 (R²)",
    f"{r2:.4f}"
)


# =====================================
# 9. 그래프 생성
# =====================================

start_year = min(
    base_year,
    predict_year
)

end_year = max(
    int(month_df["연도"].max()),
    predict_year
)

line_years = np.linspace(
    start_year,
    end_year,
    300
)

line_X = (
    line_years.reshape(-1, 1) - base_year
)

line_temps = model.predict(line_X)

fig = go.Figure()

# 실제 기온 데이터
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
            color="royalblue",
            size=8
        )
    )
)

# 선택한 알고리즘의 예측선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temps,
        mode="lines",
        name=f"{selected_algorithm} 예측선",
        line=dict(
            color="red",
            width=3,
            dash="dash"
        )
    )
)

# 미래 예측 지점
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
        text=[f"{prediction:.2f}℃"],
        textposition="top center"
    )
)

fig.update_layout(
    title=(
        f"{selected_month}월 연도별 평균기온 및 "
        f"{selected_algorithm} 예측"
    ),
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

fig.update_xaxes(showgrid=True)
fig.update_yaxes(showgrid=True)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 10. 세 가지 알고리즘 비교
# =====================================

st.divider()

st.subheader("🏆 세 가지 알고리즘 예측 결과 비교")

st.write(
    f"{predict_year}년 {selected_month}월의 "
    "예측 결과를 비교해 보세요."
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

# 예측값 비교 그래프
compare_fig = go.Figure()

compare_fig.add_trace(
    go.Bar(
        x=comparison_df["알고리즘"],
        y=comparison_df["예측 평균기온(℃)"],
        text=[
            f"{v:.2f}℃"
            for v in comparison_df["예측 평균기온(℃)"]
        ],
        textposition="outside",
        marker_color=[
            "royalblue",
            "orange",
            "seagreen"
        ],
        name="예측 평균기온"
    )
)

compare_fig.update_layout(
    title="알고리즘별 미래 평균기온 비교",
    xaxis_title="회귀 알고리즘",
    yaxis_title="예측 평균기온 (℃)",
    template="plotly_white",
    height=420,
    showlegend=False
)

st.plotly_chart(
    compare_fig,
    use_container_width=True
)

# 알고리즘 간 차이
highest = comparison_df.loc[
    comparison_df["예측 평균기온(℃)"].idxmax()
]

lowest = comparison_df.loc[
    comparison_df["예측 평균기온(℃)"].idxmin()
]

difference = (
    highest["예측 평균기온(℃)"]
    - lowest["예측 평균기온(℃)"]
)

st.info(
    f"📌 세 알고리즘 중 가장 높은 예측값은 "
    f"{highest['알고리즘']}의 "
    f"{highest['예측 평균기온(℃)']:.2f}℃이고, "
    f"가장 낮은 예측값은 {lowest['알고리즘']}의 "
    f"{lowest['예측 평균기온(℃)']:.2f}℃입니다. "
    f"두 예측값의 차이는 {difference:.2f}℃입니다."
)


# =====================================
# 11. 선택한 알고리즘 설명
# =====================================

st.divider()

st.subheader("🧠 회귀 알고리즘 작동 원리")

if selected_algorithm == "선형회귀":

    st.markdown("""
    ### ① 선형회귀 (Linear Regression)

    과거 데이터의 전체적인 변화 추세를 직선으로 나타내는 알고리즘입니다.

    **기본 공식: Y = aX + b**

    - X: 연도
    - Y: 예측 평균기온
    - a: 직선의 기울기
    - b: Y절편

    **작동 방식**
    1. 과거 연도별 평균기온을 수집합니다.
    2. 실제 데이터와 직선 사이의 오차 제곱합이 최소가 되도록 학습합니다.
    3. 학습된 직선에 미래 연도를 대입해 기온을 예측합니다.

    **특징:** 전체적인 증가 또는 감소 추세를 파악하기 좋습니다.
    """)

elif selected_algorithm == "다항회귀":

    st.markdown("""
    ### ② 다항회귀 (Polynomial Regression)

    직선이 아닌 곡선으로 데이터의 관계를 표현하는 알고리즘입니다.

    **이번 프로그램의 공식: Y = aX² + bX + c**

    - X: 연도
    - Y: 예측 평균기온
    - a, b, c: 학습을 통해 구하는 계수

    **작동 방식**
    1. 연도 데이터를 제곱한 새로운 변수도 만듭니다.
    2. X와 X²를 활용해 곡선의 형태를 학습합니다.
    3. 학습된 곡선에 미래 연도를 대입합니다.

    **특징:** 직선으로 표현하기 어려운 곡선 형태의 변화를 학습할 수 있습니다.

    ※ 이번 프로그램은 2차 다항회귀를 사용합니다.
    """)

else:

    st.markdown("""
    ### ③ 랜덤 포레스트 회귀 (Random Forest Regression)

    여러 개의 의사결정나무를 만들고 각 나무의 예측 결과를 평균 내는 알고리즘입니다.

    **작동 방식**
    1. 과거 데이터를 활용해 여러 의사결정나무를 만듭니다.
    2. 각각의 나무가 기온을 예측합니다.
    3. 여러 나무의 예측 결과를 평균 내어 최종 기온을 계산합니다.

    **특징:** 데이터의 복잡한 패턴을 학습할 수 있으며 직선이나 곡선과 다른 결과를 만들 수 있습니다.

    ※ 의사결정나무 기반 알고리즘이므로 학습 데이터 범위를 벗어난 연도를 예측할 때는 마지막 학습 구간의 예측값과 비슷한 값이 나올 수 있습니다.
    """)


# =====================================
# 12. 세 알고리즘의 차이점
# =====================================

st.divider()

st.subheader("📚 알고리즘 특징 한눈에 비교")

algorithm_info = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트 회귀"
    ],
    "그래프 형태": [
        "직선",
        "곡선",
        "계단 형태 등"
    ],
    "학습 방식": [
        "직선의 기울기와 절편 학습",
        "2차 곡선의 계수 학습",
        "여러 의사결정나무의 결과 결합"
    ],
    "주요 특징": [
        "전체 추세 파악",
        "곡선 패턴 학습",
        "복잡한 패턴 학습"
    ]
})

st.dataframe(
    algorithm_info,
    use_container_width=True,
    hide_index=True
)


# =====================================
# 13. 주의사항
# =====================================

st.divider()

st.subheader("⚠️ 예측 결과를 볼 때 주의할 점")

st.markdown("""
- 알고리즘마다 학습 방식이 다르므로 예측값이 달라질 수 있습니다.
- 결정계수(R²)는 학습에 사용한 과거 데이터에 대한 설명력을 나타냅니다.
- 결정계수가 높다고 미래 예측이 반드시 정확한 것은 아닙니다.
- 랜덤 포레스트는 학습 데이터 범위 밖의 미래 추세를 잘 연장하지 못할 수 있습니다.
- 실제 기온은 기후 변화, 강수량, 바람, 해양 환경 등 다양한 요인의 영향을 받습니다.

따라서 세 알고리즘의 결과를 서로 비교하면서
각 알고리즘의 장단점을 이해하는 것이 중요합니다.
""")

st.caption(
    "📚 데이터 출처: temperature.csv"
)

st.caption(
    "🤖 알고리즘: Linear Regression / "
    "Polynomial Regression / Random Forest Regression"
)

st.caption(
    "📊 그래프: Plotly | 데이터 분석: Pandas"
)
