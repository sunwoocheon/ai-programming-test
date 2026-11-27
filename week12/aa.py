import pandas as pd

df = pd.read_csv("scores_2026.csv")

print(df.shape)
print(df["점수"].isna().sum())
print(df.duplicated().sum())
print(df["반"].unique())    
print(df["과목"].unique())
print(df["점수"].describe())
df = pd.read_csv("scores_2026_cp949.csv", encoding="cp949")
print(df.shape)