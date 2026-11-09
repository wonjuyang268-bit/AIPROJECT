
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import calendar

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요!")

# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------
file_path = Path(__file__).resolve().parent.parent / "temperature.csv"

try:
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

except FileNotFoundError:
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# --------------------------------
# 3. 날짜 데이터 처리
# --------------------------------
# 날짜 형식: Oct-07, Nov-07 등
# 2자리 연도의 세기를 시간 순서에 따라 복원

month_dict = {
    name: number
    for number, name in enumerate(calendar.month_abbr)
    if name
}

dates = []
previous_date = None
century = 1900

for value in df["일시"]:
    try:
        month_text, year_text = str(value).strip().split("-")

        month = month_dict[month_text.title()]
        year_suffix = int(year_text)

        year = century + year_suffix
        current_date = pd.Timestamp(year, month, 1)

        while previous_date is not None and current_date < previous_date:
            century += 100
            year = century + year_suffix
            current_date = pd.Timestamp(year, month, 1)

        dates.append(current_date)
        previous_date = current_date

    except (ValueError, KeyError, TypeError):
        dates.append(pd.NaT)

df["날짜"] = dates
df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

# --------------------------------
# 4. 기온 데이터 숫자 처리
# --------------------------------
temperature_columns = ["최고기온(℃)", "최저기온(℃)"]

for col in temperature_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --------------------------------
# 5. 월 선택 기능
# --------------------------------
st.subheader("📅 분석할 월 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# --------------------------------
# 6. 선택한 월의 데이터 추출
# --------------------------------
result = df[df["월"] == selected_month].copy()

result = result.dropna(
    subset=["연도", "최고기온(℃)", "최저기온(℃)"]
)

result = result.sort_values("연도")

if result.empty:
    st.warning("선택한 월에 분석할 데이터가 없습니다.")
    st.stop()

# --------------------------------
# 7. 최고기온 및 최저기온 그래프
# --------------------------------
fig = go.Figure()

# 최고기온 - 핫핑크
fig.add_trace(go.Scatter(
    x=result["연도"],
    y=result["최고기온(℃)"],
    mode="lines+markers",
    name="최고 기온",
    line=dict(
        color="#FF1493",
        width=3
    ),
    marker=dict(size=6)
))

# 최저기온 - 하늘색
fig.add_trace(go.Scatter(
    x=result["연도"],
    y=result["최저기온(℃)"],
    mode="lines+markers",
    name="최저 기온",
    line=dict(
        color="#87CEEB",
        width=3
    ),
    marker=dict(size=6)
))

# 그래프 제목 및 축 설정
fig.update_layout(
    title={
        "text": "월별 기온분석",
        "x": 0.5,
        "xanchor": "center"
    },
    xaxis_title="연도",
    yaxis_title="온도 (℃)",
    legend_title="범례",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    font=dict(
        family="Malgun Gothic, sans-serif",
        size=13
    )
)

fig.update_xaxes(
    showgrid=True,
    dtick=5
)

fig.update_yaxes(
    showgrid=True
)

# --------------------------------
# 8. 그래프 출력
# --------------------------------
st.subheader(f"📊 {month_names[selected_month]} 기온 분석")

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------
# 9. 선택한 월의 기온 통계
# --------------------------------
st.subheader("📌 기온 통계")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "가장 높은 최고기온",
        f"{result['최고기온(℃)'].max():.1f}℃"
    )

with col2:
    st.metric(
        "가장 낮은 최저기온",
        f"{result['최저기온(℃)'].min():.1f}℃"
    )

with col3:
    st.metric(
        "분석 데이터 개수",
        f"{len(result)}개"
    )

# --------------------------------
# 10. 데이터 표 출력
# --------------------------------
with st.expander("📋 연도별 상세 데이터 보기"):
    display_df = result[
        ["연도", "최고기온(℃)", "최저기온(℃)"]
    ].copy()

    display_df["연도"] = display_df["연도"].astype(int)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.success("월별 기온 분석이 완료되었습니다! 🌱")
