 page_icon="🗺️",
    layout="wide"
)

# 제목
st.title("🗺️ 서울 외국인 관광객 주요 명소 TOP 10")
st.write("서울의 주요 관광 명소를 지도에서 확인해 보세요!")

# 관광 명소 데이터
places = [
    {"순위": 1, "장소": "명동", "방문객": 100910, "위도": 37.5636, "경도": 126.9850},
    {"순위": 2, "장소": "N서울타워", "방문객": 57370, "위도": 37.5512, "경도": 126.9882},
    {"순위": 3, "장소": "삼성역·코엑스", "방문객": 46813, "위도": 37.5125, "경도": 127.0588},
    {"순위": 4, "장소": "강남역", "방문객": 41210, "위도": 37.4979, "경도": 127.0276},
    {"순위": 5, "장소": "홍대", "방문객": 40213, "위도": 37.5563, "경도": 126.9236},
    {"순위": 6, "장소": "남대문시장", "방문객": 30132, "위도": 37.5592, "경도": 126.9770},
    {"순위": 7, "장소": "DDP", "방문객": 20871, "위도": 37.5671, "경도": 127.0095},
    {"순위": 8, "장소": "북촌한옥마을", "방문객": 6191, "위도": 37.5826, "경도": 126.9830},
    {"순위": 9, "장소": "경복궁", "방문객": 4235, "위도": 37.5796, "경도": 126.9770},
    {"순위": 10, "장소": "서울숲·성수동", "방문객": 3701, "위도": 37.5445, "경도": 127.0374}
]

df = pd.DataFrame(places)

# 관광 명소 순위 표시
st.subheader("🏆 관광 명소 TOP 10")

st.dataframe(
    df[["순위", "장소", "방문객"]],
    use_container_width=True,
    hide_index=True
)

# 지도 표시
st.subheader("📍 서울 관광 명소 지도")

# 서울 중심으로 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광 명소별 마커 추가
for place in places:
    popup_text = f"""
    <b>{place['순위']}위. {place['장소']}</b><br>
    방문객 수: {place['방문객']:,}명
    """

    folium.Marker(
        location=[place["위도"], place["경도"]],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=place["장소"],
        icon=folium.Icon(
            color="red" if place["순위"] <= 3 else "blue",
            icon="info-sign"
        )
    ).add_to(m)

# Streamlit 화면에 Folium 지도 출력
st_folium(
    m,
    width=None,
    height=600,
    use_container_width=True
)

# 안내 문구
st.caption(
    "※ 방문객 수는 참고 자료이며, 실제 관광객 입장객 수와 차이가 있을 수 있습니다."
)
