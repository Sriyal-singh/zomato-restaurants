# %%
# # Zomato India Restaurant Analysis
# Best cuisines, rating distribution, price analysis, cost vs rating, restaurant density.
# Dataset: Kaggle "Zomato Restaurants" (India subset) -> `data/zomato_india.csv` (synthetic sample used if missing).

# %%
import os
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid")
os.makedirs("images", exist_ok=True)
PATH = "data/zomato_india.csv"
if not os.path.exists(PATH):
    from generate_data import generate
    generate(PATH)
try:
    raw = pd.read_csv(PATH)
except UnicodeDecodeError:
    raw = pd.read_csv(PATH, encoding="latin-1")
raw.head()

# %%
# ## 1. Cleaning
# `Aggregate rating == 0` means "not rated", so it is excluded from rating statistics (not treated as a terrible score).
df = raw.drop_duplicates("Restaurant ID").copy()
df["Cuisines"] = df["Cuisines"].fillna("Unknown")
df["rated"] = df["Aggregate rating"] > 0
rated = df[df["rated"]].copy()
cost_cap = df["Average Cost for two"].quantile(.99)
df = df[df["Average Cost for two"] <= cost_cap]; rated = rated[rated["Average Cost for two"] <= cost_cap]
df.to_csv("cleaned_dataset.csv", index=False)
print(f"{len(df)} restaurants, {len(rated)} rated ({len(rated)/len(df):.0%})")

# %%
# ## 2. Best cuisines (popularity and quality)
cu = rated.assign(c=rated["Cuisines"].str.split(", ")).explode("c")
cs = cu.groupby("c").agg(restaurants=("Restaurant ID", "size"), avg_rating=("Aggregate rating", "mean"), votes=("Votes", "sum"))
cs = cs[cs["restaurants"] >= 30]
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
cs["restaurants"].sort_values().tail(10).plot.barh(ax=ax[0], color="#e23744").set_title("Most common cuisines")
cs["avg_rating"].sort_values().tail(10).plot.barh(ax=ax[1], color="#cb202d").set_xlim(cs["avg_rating"].min() - .1, None); ax[1].set_title("Highest-rated cuisines (min 30 restaurants)")
for a in ax: a.set_ylabel("")
plt.tight_layout(); plt.savefig("images/cuisines.png", dpi=150); plt.show()

# %%
# ## 3. Ratings distribution
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
sns.histplot(rated["Aggregate rating"], bins=30, kde=True, ax=ax[0], color="#e23744").set_title("Distribution of ratings (rated restaurants)")
rated["Rating text"].value_counts().plot.pie(ax=ax[1], autopct="%1.0f%%", ylabel="").set_title("Rating categories")
plt.tight_layout(); plt.savefig("images/ratings_distribution.png", dpi=150); plt.show()

# %%
# ## 4. Price analysis
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
city_cost = df.groupby("City")["Average Cost for two"].median().sort_values()
city_cost.plot.barh(ax=ax[0], color="#2a9d8f").set_title("Median cost for two by city (Rs)")
sns.countplot(data=df, x="Price range", ax=ax[1], hue="Price range", palette="Reds", legend=False).set_title("Restaurants by price range (1 = cheapest)")
plt.tight_layout(); plt.savefig("images/price_analysis.png", dpi=150); plt.show()

# %%
# ## 5. Cost vs rating
corr = rated[["Average Cost for two", "Aggregate rating", "Votes", "Price range"]].corr()
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
sns.scatterplot(data=rated.sample(min(2000, len(rated)), random_state=0), x="Average Cost for two", y="Aggregate rating", alpha=.4, ax=ax[0], color="#e23744")
ax[0].set_title(f"Cost vs rating (r = {corr.loc['Average Cost for two', 'Aggregate rating']:.2f})")
sns.boxplot(data=rated, x="Price range", y="Aggregate rating", ax=ax[1], color="#f4a261").set_title("Rating by price range")
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=ax[2]); ax[2].set_title("Correlations")
plt.tight_layout(); plt.savefig("images/cost_vs_rating.png", dpi=150); plt.show()

# %%
# ## 6. Restaurant density
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
df["City"].value_counts().sort_values().plot.barh(ax=ax[0], color="#264653").set_title("Restaurants per city")
dens = df.groupby("Locality").size().sort_values().tail(10); dens.plot.barh(ax=ax[1], color="#e76f51").set_title("Densest localities"); ax[1].set_ylabel("")
plt.tight_layout(); plt.savefig("images/density.png", dpi=150); plt.show()
plt.figure(figsize=(8, 6)); sc = plt.scatter(df["Longitude"], df["Latitude"], c=df["Price range"], cmap="Reds", s=5, alpha=.5)
plt.colorbar(sc, label="Price range"); plt.title("Restaurant map (colour = price range)"); plt.xlabel("Longitude"); plt.ylabel("Latitude")
plt.tight_layout(); plt.savefig("images/restaurant_map.png", dpi=150); plt.show()

# %%
# ## 7. Do online delivery / table booking help ratings?
feat = rated.groupby(["Has Online delivery", "Has Table booking"])["Aggregate rating"].agg(["mean", "size"]).round(2); feat

# %%
# ## 8. Insights
print("Insights:")
print(f"1. Most common cuisine: {cs['restaurants'].idxmax()}; highest rated: {cs['avg_rating'].idxmax()} ({cs['avg_rating'].max():.2f})")
print(f"2. {(1 - len(rated) / len(df)):.0%} of restaurants have no rating yet; the average rating of the rest is {rated['Aggregate rating'].mean():.2f}")
print(f"3. Most expensive city (median cost for two): {city_cost.index[-1]} (Rs {city_cost.iloc[-1]:.0f})")
print(f"4. Correlation between cost and rating is {corr.loc['Average Cost for two', 'Aggregate rating']:.2f}")
print(f"5. Densest city: {df['City'].value_counts().index[0]} with {df['City'].value_counts().iloc[0]} restaurants")
