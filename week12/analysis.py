import pandas as pd

def 정제(df):
    print("시작", len(df))

    df = df.dropna(subset=["점수"])
    print("빈 칸 제거", len(df))

    df = df.drop_duplicates()
    print("중복 제거", len(df))

    df["반"] = df["반"].str.strip()
    df["과목"] = df["과목"].str.strip()

    df = df[(df["점수"] >= 0) & (df["점수"] <= 100)]
    print("범위 밖 제거", len(df))

    return df

def 반별평균(df):
    return df.groupby("반")["점수"].mean()
if __name__ == "__main__":
    df = pd.read_csv("scores_2026.csv")
    df = 정제(df)

    print(sorted(df["반"].unique()))
    print(sorted(df["과목"].unique()))
        # 필터링
    수학 = df[df["과목"] == "수학"]
    print("수학 행 수:", len(수학))
        # 그룹화
    print("반별 평균")
    print(df.groupby("반")["점수"].mean())

    print("과목별·반별 평균")
    print(df.groupby(["과목", "반"])["점수"].mean())
        # 통계
    print("반별 통계")
    print(df.groupby("반")["점수"].agg(
        ["count", "mean", "median", "max"]
    ).round(2))
        # 합계 일치 검증
    print("그룹 합계:", df.groupby("반")["점수"].sum().sum())
    print("전체 합계:", df["점수"].sum())

    # 개수 일치 검증
    print("그룹 개수:", df.groupby("반")["점수"].count().sum())
    print("전체 개수:", len(df))

    # 스팟 체크
    print("1반 수학 점수")
    print(df[(df["반"] == "1반") & (df["과목"] == "수학")]["점수"])
        # mini.csv 손계산 검증
    미니 = 정제(pd.read_csv("mini.csv"))
    print("미니 정제 후 행 수:", len(미니))
    print(반별평균(미니))