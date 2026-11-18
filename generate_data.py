"""Synthetic data with the same columns as Kaggle 'Zomato Restaurants Data' (India subset)."""
import numpy as np, pandas as pd, os

CITIES = {"Mumbai": (19.07, 72.87, ["Bandra West", "Andheri West", "Colaba", "Powai", "Lower Parel", "Juhu"]),
          "New Delhi": (28.61, 77.20, ["Connaught Place", "Hauz Khas", "Saket", "Karol Bagh"]),
          "Bangalore": (12.97, 77.59, ["Indiranagar", "Koramangala", "HSR Layout", "Whitefield"]),
          "Hyderabad": (17.38, 78.48, ["Banjara Hills", "Jubilee Hills", "Gachibowli"]),
          "Pune": (18.52, 73.85, ["Koregaon Park", "Viman Nagar", "Kothrud"]), "Kolkata": (22.57, 88.36, ["Park Street", "Salt Lake", "Ballygunge"]),
          "Chennai": (13.08, 80.27, ["T. Nagar", "Adyar", "Anna Nagar"])}
CUISINES = ["North Indian", "Chinese", "South Indian", "Fast Food", "Italian", "Biryani", "Cafe", "Desserts", "Continental", "Mughlai", "Street Food", "Bakery", "Asian", "Seafood"]

def generate(path="data/zomato_india.csv", n=5000, seed=12):
    rng = np.random.default_rng(seed); rows = []
    cw = rng.dirichlet(np.ones(len(CUISINES)) * 1.5); city_names = list(CITIES); pw = np.array([.22, .2, .18, .1, .1, .1, .1])
    for i in range(n):
        city = rng.choice(city_names, p=pw); lat, lon, locs = CITIES[city]; loc = rng.choice(locs)
        cost = int(np.clip(rng.lognormal(6.1, .6), 100, 6000) // 50 * 50); pr = 1 if cost < 400 else 2 if cost < 900 else 3 if cost < 1800 else 4
        quality = rng.normal(3.5 + .12 * (pr - 2.2), .5)
        votes = int(rng.lognormal(4.5, 1.3)); rating = 0.0 if rng.random() < .12 else round(float(np.clip(quality, 1.8, 4.9)), 1)
        text = "Not rated" if rating == 0 else "Excellent" if rating >= 4.5 else "Very Good" if rating >= 4 else "Good" if rating >= 3.5 else "Average" if rating >= 2.5 else "Poor"
        rows.append((9000000 + i, f"Restaurant {i}", 1, city, f"{loc}, {city}", loc, f"{loc}, {city}", lon + rng.normal(0, .06), lat + rng.normal(0, .06),
                     ", ".join(rng.choice(CUISINES, int(rng.integers(1, 4)), replace=False, p=cw)), cost, "Indian Rupees(Rs.)",
                     rng.choice(["Yes", "No"], p=[.15 + .1 * (pr > 2), .85 - .1 * (pr > 2)]), rng.choice(["Yes", "No"], p=[.4, .6]), "No", "No", pr, rating, text, votes))
    df = pd.DataFrame(rows, columns=["Restaurant ID", "Restaurant Name", "Country Code", "City", "Address", "Locality", "Locality Verbose", "Longitude", "Latitude",
        "Cuisines", "Average Cost for two", "Currency", "Has Table booking", "Has Online delivery", "Is delivering now", "Switch to order menu", "Price range",
        "Aggregate rating", "Rating text", "Votes"])
    df.loc[rng.random(n) < .02, "Cuisines"] = np.nan
    os.makedirs(os.path.dirname(path), exist_ok=True); df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    generate(); print("Sample data written.")
