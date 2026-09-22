# -*- coding: utf-8 -*-
"""
S&P 500 과거 데이터 분석
- 데이터 클렌징 (날짜/숫자 포맷 정리)
- 기본 통계, 연도별/월별 분석
- 이동평균, 일일 변동률, 연간 수익률 등 다각도 분석
- 종가 기준 라인 그래프 출력
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

CSV_PATH = "S&P 500 과거 데이터.csv"

# ---------------------------------------------------------------
# 0. 한글 폰트 설정 (그래프에 한글이 깨지지 않도록)
# ---------------------------------------------------------------
def set_korean_font():
    system = platform.system()
    if system == "Windows":
        plt.rcParams["font.family"] = "Malgun Gothic"
    elif system == "Darwin":
        plt.rcParams["font.family"] = "AppleGothic"
    else:
        plt.rcParams["font.family"] = "NanumGothic"
    plt.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------
# 1. 데이터 로드 & 클렌징
# ---------------------------------------------------------------
def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")

    # 날짜: "2019- 11- 14" 형태 -> 공백 제거 후 datetime 변환
    df["날짜"] = df["날짜"].str.replace(" ", "", regex=False)
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y-%m-%d")

    # 숫자형 컬럼: 천단위 콤마 제거 후 float 변환
    numeric_cols = ["종가", "시가", "고가", "저가"]
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 거래량: 값이 비어있는 행이 많음 -> 숫자 변환 (빈 값은 NaN)
    df["거래량"] = pd.to_numeric(
        df["거래량"].astype(str).str.replace(",", "", regex=False), errors="coerce"
    )

    # 변동 %: "0.08%" -> 0.08 (float)
    df["변동%"] = (
        df["변동 %"].astype(str).str.replace("%", "", regex=False).astype(float)
    )
    df = df.drop(columns=["변동 %"])

    # 날짜 오름차순 정렬 + 인덱스 설정
    df = df.sort_values("날짜").reset_index(drop=True)
    df = df.set_index("날짜")

    # 중복 날짜 제거 (있다면)
    df = df[~df.index.duplicated(keep="first")]

    return df


# ---------------------------------------------------------------
# 2. 다각도 분석
# ---------------------------------------------------------------
def analyze(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("1. 데이터 개요")
    print("=" * 60)
    print(f"기간: {df.index.min().date()} ~ {df.index.max().date()}")
    print(f"총 거래일 수: {len(df):,}일")
    print(df[["종가", "시가", "고가", "저가"]].describe().round(2))

    print("\n" + "=" * 60)
    print("2. 결측치 확인")
    print("=" * 60)
    print(df.isna().sum())

    print("\n" + "=" * 60)
    print("3. 연도별 종가 통계 (연초/연말/연간 변동률)")
    print("=" * 60)
    yearly = df["종가"].resample("YE").agg(["first", "last", "min", "max"])
    yearly["연간 수익률(%)"] = ((yearly["last"] / yearly["first"]) - 1) * 100
    yearly.index = yearly.index.year
    yearly.columns = ["연초종가", "연말종가", "최저종가", "최고종가", "연간수익률(%)"]
    print(yearly.round(2))

    print("\n" + "=" * 60)
    print("4. 일일 변동률(%) 통계")
    print("=" * 60)
    df["일일수익률(%)"] = df["종가"].pct_change() * 100
    print(df["일일수익률(%)"].describe().round(3))

    print("\n최대 상승일 TOP 5:")
    print(df["일일수익률(%)"].sort_values(ascending=False).head(5).round(2))
    print("\n최대 하락일 TOP 5:")
    print(df["일일수익률(%)"].sort_values().head(5).round(2))

    print("\n" + "=" * 60)
    print("5. 이동평균 (MA20, MA60, MA200) - 최근 5일")
    print("=" * 60)
    df["MA20"] = df["종가"].rolling(20).mean()
    df["MA60"] = df["종가"].rolling(60).mean()
    df["MA200"] = df["종가"].rolling(200).mean()
    print(df[["종가", "MA20", "MA60", "MA200"]].tail(5).round(2))

    print("\n" + "=" * 60)
    print("6. 월별 평균 종가 (최근 12개월)")
    print("=" * 60)
    monthly = df["종가"].resample("ME").mean()
    print(monthly.tail(12).round(2))

    print("\n" + "=" * 60)
    print("7. 최대 낙폭 (Max Drawdown)")
    print("=" * 60)
    cummax = df["종가"].cummax()
    drawdown = (df["종가"] / cummax - 1) * 100
    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()
    print(f"최대 낙폭: {max_dd:.2f}% (발생일: {max_dd_date.date()})")


# ---------------------------------------------------------------
# 3. 종가 라인 그래프
# ---------------------------------------------------------------
def plot_close_price(df: pd.DataFrame, save_path: str = "sp500_close_price.png") -> None:
    set_korean_font()

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df.index, df["종가"], color="#1f77b4", linewidth=1.2, label="종가")

    ax.set_title(
        f"S&P 500 종가 추이 ({df.index.min().date()} ~ {df.index.max().date()})",
        fontsize=15,
        fontweight="bold",
    )
    ax.set_xlabel("날짜")
    ax.set_ylabel("종가")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    fig.savefig(save_path, dpi=150)
    print(f"\n그래프 저장 완료: {save_path}")
    plt.show()


def main():
    df = load_and_clean(CSV_PATH)
    analyze(df)
    plot_close_price(df)


if __name__ == "__main__":
    main()
