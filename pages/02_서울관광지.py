import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 관광 명소 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 서울 관광지 데이터
places = [
    {
        "rank": 1, "name": "명동", "english": "Myeong-dong",
        "visitors": 100910, "lat": 37.5636, "lon": 126.9850,
        "address": "서울 중구 명동",
        "category": "쇼핑 · K-뷰티",
        "description": "화장품, 패션 매장, 길거리 음식으로 유명한 쇼핑 거리!"
    },
    {
        "rank": 2, "name": "N서울타워", "english": "N Seoul Tower",
        "visitors": 57370, "lat": 37.5512, "lon": 126.9882,
        "address": "서울 용산구 남산공원길 105",
        "category": "전망 · 랜드마크",
        "description": "남산 정상에서 아름다운 서울의 전경을 감상할 수 있어요."
    },
    {
        "rank": 3, "name": "삼성역·코엑스", "english": "COEX",
        "visitors": 46813, "lat": 37.5125, "lon": 127.0588,
        "address": "서울 강남구 영동대로 513",
        "category": "쇼핑 · 문화",
        "description": "쇼핑몰, 별마당도서관, 전시 공간을 즐길 수 있는 곳이에요."
    },
    {
        "rank": 4, "name": "강남역", "english": "Gangnam Station",
        "visitors": 41210, "lat": 37.4979, "lon": 127.0276,
        "address": "서울 강남구 강남역 일대",
        "category": "쇼핑 · 맛집",
        "description": "트렌디한 상점과 맛집, 카페가 모여 있는 번화가예요."
    },
    {
        "rank": 5, "name": "홍대", "english": "Hongdae",
        "visitors": 40213, "lat": 37.5563, "lon": 126.9236,
        "address": "서울 마포구 홍익로 일대",
        "category": "K-컬처 · 공연",
        "description": "거리 공연과 음악, 패션, 개성 있는 카페가 유명해요."
    },
    {
        "rank": 6, "name": "남대문시장", "english": "Namdaemun Market",
        "visitors": 30132, "lat": 37.5592, "lon": 126.9770,
        "address": "서울 중구 남대문시장",
        "category": "전통시장 · 먹거리",
        "description": "다양한 상품과 한국의 전통 먹거리를 만날 수 있어요."
    },
    {
        "rank": 7, "name": "동대문디자인플라자", "english": "DDP",
        "visitors": 20871, "lat": 37.5671, "lon": 127.0095,
        "address": "서울 중구 을지로 281",
        "category": "건축 · 디자인",
        "description": "독특한 건축물과 전시, 디자인 행사를 만날 수 있어요."
    },
    {
        "rank": 8, "name": "북촌한옥마을", "english": "Bukchon Hanok Village",
        "visitors": 6191, "lat": 37.5826, "lon": 126.9830,
        "address": "서울 종로구 북촌로 일대",
        "category": "전통문화 · 한옥",
        "description": "한국의 전통 한옥과 옛 주거문화를 느낄 수 있어요."
    },
    {
        "rank": 9, "name": "경복궁", "english": "Gyeongbokgung Palace",
        "visitors": 4235, "lat": 37.5796, "lon": 126.9770,
        "address": "서울 종로구 사직로 161",
        "category": "역사 · 궁궐",
        "description": "조선 왕조의 법궁으로 한국의 역사와 문화를 경험할 수 있어요."
    },
    {
        "rank": 10, "name": "서울숲·성수동", "english": "Seoul Forest & Seongsu",
        "visitors": 3701, "lat": 37.5445, "lon": 127.0374,
        "address": "서울 성동구 뚝섬로 273 일대",
        "category": "공원 · 카페",
        "description": "자연을 즐길 수 있는 공원과 감각적인 카페가 유명해요."
    }
]

# 제목
st.title("🗺️ 서울 관광 명소 TOP 10")
st.subheader("Seoul's Top 10 Tourist Attractions 🇰🇷")
st.write("외국인 관광객이 많이 찾는 서울의 인기 관광지를 지도에서 만나 보세요!")

st.info(
    "📊 2025년 서울 주요 명소 외국인 방문 유동인구 분석 자료를 참고한 순위입니다."
)

# 지도 표시
st.header("📍 서울 관광지 지도")

map_data = pd.DataFrame(places)

st.map(
    map_data,
    latitude="lat",
    longitude="lon",
    zoom=11,
    size=100
)

st.caption("※ 지도에 표시된 마커는 각 관광지의 대표 위치입니다.")

# 관광지 TOP 10 표
st.header("🏆 관광지 TOP 10")

table_data = []

for p in places:
    table_data.append({
        "순위": str(p["rank"]) + "위",
        "관광지": p["name"],
        "영어 이름": p["english"],
        "일평균 방문 유동인구": f'{p["visitors"]:,}명',
        "분야": p["category"]
    })

st.dataframe(
    pd.DataFrame(table_data),
    use_container_width=True,
    hide_index=True
)

# 상세 정보 선택
st.header("🔎 관광지 자세히 알아보기")

selected = st.selectbox(
    "방문하고 싶은 관광지를 선택해 주세요!",
    places,
    format_func=lambda p: f'{p["rank"]}위 | {p["name"]} ({p["english"]})'
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 " + selected["name"])
    st.write(selected["description"])
    st.write("🌎 영어 이름:", selected["english"])
    st.write("✨ 관광 분야:", selected["category"])
    st.write("📍 주소:", selected["address"])
    st.write("👣 일평균 방문 유동인구:", f'{selected["visitors"]:,}명')

with col2:
    st.metric("관광지 순위", str(selected["rank"]) + "위")
    st.metric("일평균 방문 유동인구", f'{selected["visitors"]:,}명')

    map_url = (
        "https://www.google.com/maps/search/?api=1&query="
        + str(selected["lat"]) + "," + str(selected["lon"])
    )

    st.link_button(
        "🌐 Google 지도에서 위치 확인",
        map_url,
        use_container_width=True
    )

# 선택한 관광지 지도
st.header("🎯 선택한 관광지 위치")

selected_map = pd.DataFrame([{
    "lat": selected["lat"],
    "lon": selected["lon"]
}])

st.map(
    selected_map,
    latitude="lat",
    longitude="lon",
    zoom=15
)

st.divider()

st.success(
    "🎉 서울에는 다양한 매력이 있어요! "
    "마음에 드는 장소를 골라 즐거운 여행을 계획해 보세요."
)

st.caption(
    "자료 출처: 서울시·서울AI재단, 2025년 서울 주요 명소 외국인 방문 유동인구 분석. "
    "방문 유동인구는 실제 입장객 수와 다를 수 있습니다."
)

st.markdown(
    "[서울시 공식 발표 자료](https://english.seoul.go.kr/from-k-culture-to-k-hiking-foreign-tourists-venture-beyond-seouls-top-attractions/)"
)
