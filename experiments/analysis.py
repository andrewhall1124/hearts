import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("charts", exist_ok=True)

file_name = "four_agents_10"
df = pl.read_parquet(f"results/{file_name}.parquet")

print(df)

n_games = df.select("game_name").unique().count()["game_name"].last()

df = df.group_by("player").agg(
    pl.col("score").mean().alias("mean"), pl.col("score").std().alias("std")
)

order = {"Random": 0, "MinCard": 1, "MinMaxCard": 2, "Sluffing": 3, "MCTS": 4}

df = (
    df.with_columns(pl.col("player").str.split(" ").alias("parts"))
    .with_columns(
        pl.col("parts").list.get(0).alias("player_type"),
        pl.col("parts").list.get(1).alias("number"),
    )
    .drop("parts")
    .with_columns(pl.col("player_type").replace(order).alias("index"))
    .sort(["index", "number"])
)

print(df)

plt.figure(figsize=(10, 6))

sns.barplot(df, x="player", y="mean", color='red')

plt.title(f"{n_games} Trials Results: Mean")

plt.xlabel("Agent")
plt.ylabel("Average cards won")

plt.savefig(f"charts/{file_name}_mean.png", dpi=300)
plt.clf()

plt.figure(figsize=(10, 6))

sns.barplot(df, x="player", y="std", color='blue')

plt.title(f"{n_games} Trials Results: Standard Deviation")

plt.xlabel("Agent")
plt.ylabel("Standard deviation of cards won")

plt.savefig(f"charts/{file_name}_std.png", dpi=300)
