import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

df = pl.read_parquet("results/random_vs_min_vs_minmax_vs_sluffing_100.parquet")

df = df.group_by('player').agg(pl.col('score').mean())

order = {
    'Random': 0,
    'MinCard': 1,
    'MinMaxCard': 2,
    'Sluffing': 3
}

df = df.with_columns(pl.col('player').replace(order).alias('index')).sort('index')

print(df)

plt.figure(figsize=(10, 6))

sns.barplot(df, x='player', y='score')

plt.title("100 Game Results")

plt.xlabel("Agent")
plt.ylabel("Average cards won")



plt.show()