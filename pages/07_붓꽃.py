
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "인공지능이 붓꽃의 품종을 예측해 줍니다!"
)

st.divider()


# ----------------------------------
# 2. 데이터 불러오기
# ----------------------------------

@st.cache_data
def load_data():

    # 현재 파일이 pages 폴더에 있으므로
    # 상위 폴더에서 CSV 파일을 찾음
    file_path = Path(__file__).resolve().parent.parent / "Iris.csv"

    # 인코딩 자동 대응
    encodings = ["cp949", "utf-8-sig", "euc-kr"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일 인코딩을 확인해주세요.")

    # 컬럼명 공백 제거
    data.columns = data.columns.str.strip()

    # 컬럼명 오타 수정
    data = data.rename(columns={
        "꽃받임 너비": "꽃받침 너비"
    })

    required_columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{col}' 컬럼이 없습니다."
            )

    # 필요한 데이터만 사용
    data = data[required_columns].copy()

    # 숫자형 변환
    data["꽃잎 길이"] = pd.to_numeric(
        data["꽃잎 길이"], errors="coerce"
    )

    data["꽃잎 너비"] = pd.to_numeric(
        data["꽃잎 너비"], errors="coerce"
    )

    data = data.dropna()

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# ----------------------------------
# 3. 머신러닝 모델 학습
# ----------------------------------

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# 랜덤 포레스트 알고리즘
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)

st.success(
    f"AI 학습 완료! 총 {len(df)}개의 데이터를 학습했습니다."
)

st.divider()


# ----------------------------------
# 4. 사용자 입력
# ----------------------------------

st.subheader("✏️ 꽃잎 크기 입력하기")

st.info(
    """
    📌 입력 가능한 범위

    - 꽃잎 길이: 1.0 ~ 6.9 cm
    - 꽃잎 너비: 0.1 ~ 2.5 cm

    위 범위는 학습 데이터에 실제로 존재하는
    최솟값과 최댓값입니다.
    """
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=1.0,
        max_value=6.9,
        value=3.0,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.0,
        step=0.1
    )


# ----------------------------------
# 5. 품종 예측
# ----------------------------------

if st.button("🔍 붓꽃 품종 예측하기", type="primary"):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    st.divider()

    st.subheader("🎉 AI 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    st.write(
        f"입력한 꽃잎 길이: **{petal_length} cm**"
    )

    st.write(
        f"입력한 꽃잎 너비: **{petal_width} cm**"
    )

    # 품종별 예측 확률
    st.subheader("📊 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 확률": probabilities
    })

    probability_df = probability_df.sort_values(
        "예측 확률",
        ascending=False
    )

    st.bar_chart(
        probability_df.set_index("품종"),
        y="예측 확률",
        color="#FF69B4"
    )

    for species, probability in zip(
        model.classes_, probabilities
    ):
        st.write(
            f"**{species}** : {probability * 100:.1f}%"
        )

    # ----------------------------------
    # 6. 분류 영역 시각화
    # ----------------------------------

    st.divider()

    st.subheader("📍 붓꽃 품종 분류 시각화")

    st.write(
        "배경 색상은 AI가 각 위치를 어떤 품종으로 "
        "분류하는지 나타냅니다."
    )

    # 그래프 범위
    x_min = 0.8
    x_max = 7.1
    y_min = 0.0
    y_max = 2.7

    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 180),
        np.linspace(y_min, y_max, 120)
    )

    grid_data = pd.DataFrame({
        "꽃잎 길이": xx.ravel(),
        "꽃잎 너비": yy.ravel()
    })

    # 각 위치의 예측 품종
    Z = model.predict(grid_data)

    # 품종을 숫자로 변환
    species_to_number = {
        species: i
        for i, species in enumerate(model.classes_)
    }

    Z_number = np.array([
        species_to_number[value] for value in Z
    ]).reshape(xx.shape)

    # 품종별 색상
    colors = [
        "#F6A6A6",
        "#A5C8F0",
        "#C6A5E8"
    ]

    fig = go.Figure()

    # 배경 분류 영역
    fig.add_trace(
        go.Contour(
            x=xx[0],
            y=yy[:, 0],
            z=Z_number,
            colorscale=[
                [0.0, colors[0]],
                [0.3333, colors[0]],
                [0.3334, colors[1]],
                [0.6666, colors[1]],
                [0.6667, colors[2]],
                [1.0, colors[2]]
            ],
            opacity=0.35,
            showscale=False,
            hoverinfo="skip",
            contours=dict(
                coloring="fill",
                showlines=False
            )
        )
    )

    # 실제 학습 데이터 표시
    for i, species in enumerate(model.classes_):

        species_data = df[df["품종"] == species]

        fig.add_trace(
            go.Scatter(
                x=species_data["꽃잎 길이"],
                y=species_data["꽃잎 너비"],
                mode="markers",
                name=species,
                marker=dict(
                    size=8,
                    color=colors[i],
                    line=dict(
                        color="black",
                        width=0.5
                    )
                ),
                hovertemplate=(
                    "꽃잎 길이: %{x} cm<br>"
                    "꽃잎 너비: %{y} cm<br>"
                    f"품종: {species}"
                    "<extra></extra>"
                )
            )
        )

    # 사용자가 입력한 값: 초록색 별
    fig.add_trace(
        go.Scatter(
            x=[petal_length],
            y=[petal_width],
            mode="markers",
            name="내가 입력한 값",
            marker=dict(
                symbol="star",
                size=24,
                color="#00CC44",
                line=dict(
                    color="black",
                    width=1.5
                )
            ),
            hovertemplate=(
                "내가 입력한 값<br>"
                "꽃잎 길이: %{x} cm<br>"
                "꽃잎 너비: %{y} cm"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="붓꽃 품종별 분류 영역",
        xaxis_title="꽃잎 길이 (cm)",
        yaxis_title="꽃잎 너비 (cm)",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[y_min, y_max]),
        height=600,
        legend_title="범례",
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ----------------------------------
    # 7. 예측 이유 설명
    # ----------------------------------

    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    best_probability = max(probabilities) * 100

    st.write(
        f"""
        AI가 입력한 꽃잎의 크기를 분석한 결과,
        **{prediction}** 품종으로 분류했어.

        해당 품종으로 예측한 확률은
        **{best_probability:.1f}%**야.
        """
    )

    st.write(
        """
        📌 그래프 읽는 방법

        - 분홍색 영역: 첫 번째 품종의 분류 영역
        - 파란색 영역: 두 번째 품종의 분류 영역
        - 보라색 영역: 세 번째 품종의 분류 영역
        - 초록색 별: 사용자가 입력한 꽃잎 크기
        - 각 영역 안의 점: 실제 학습 데이터

        초록색 별이 어느 색상의 분류 영역에
        위치하는지 확인하면 AI가 왜 해당 품종으로
        예측했는지 시각적으로 이해할 수 있어.
        """
    )

else:
    st.info(
        "꽃잎 길이와 너비를 입력하고 "
        "'붓꽃 품종 예측하기' 버튼을 눌러주세요!"
    )


# ----------------------------------
# 8. 데이터 정보
# ----------------------------------

with st.expander("📚 학습에 사용한 데이터 확인하기"):

    st.write("전체 데이터")
    st.dataframe(df, use_container_width=True)

    st.write("품종별 데이터 개수")
    st.write(df["품종"].value_counts())

