
from pathlib import Path

@st.cache_data
def load_data():

    # 현재 파이썬 파일의 위치 확인
    current_dir = Path(__file__).resolve().parent

    # 상위 폴더와 현재 폴더에서 CSV 파일 찾기
    possible_paths = [
        current_dir.parent / "temperature.csv",
        current_dir / "temperature.csv"
    ]

    file_path = next(
        (path for path in possible_paths if path.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "상위 폴더에 temperature.csv가 있는지 확인하세요."
        )

    # 한글 인코딩 자동 처리
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

    # 날짜 처리
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    def parse_date(value):
        try:
            month_text, year_text = str(value).strip().split("-")
            month = month_dict[month_text.title()]
            year_num = int(year_text)

            year = 2000 + year_num if year_num <= 68 else 1900 + year_num

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
        subset=["날짜", "연도", "월", "평균기온(℃)"]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df.sort_values("날짜")

