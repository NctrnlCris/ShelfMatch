"""Generate reproducible, fictional VPL branch holdings for ShelfMatch.

Run from anywhere: python scripts/generate_inventory.py
This is a *simulation*, not Vancouver Public Library inventory data.
"""
from pathlib import Path

import numpy as np
import pandas as pd

"""Generate reproducible, fictional VPL branch holdings for ShelfMatch.

Run from anywhere: python scripts/generate_inventory.py
This is a *simulation*, not Vancouver Public Library inventory data.
"""

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "books.csv"
OUTPUT = ROOT / "data" / "processed" / "inventory.csv"

# Relative, fictional branch capacity factors (not measured VPL sizes).
# Keep these names consistent with BRANCHES in app.py.
BRANCH_CAPACITY = {
    "Central Library": 1.00,
    "Britannia": 0.48,
    "Carnegie": 0.32,
    "Champlain Heights": 0.40,
    "Collingwood": 0.55,
    "Dunbar": 0.55,
    "Firehall": 0.38,
    "Fraserview": 0.55,
    "Hastings": 0.48,
    "Joe Fortes": 0.60,
    "Kensington": 0.52,
    "Kerrisdale": 0.55,
    "Kitsilano": 0.65,
    "Marpole": 0.40,
    "Mount Pleasant": 0.72,
    "nə́c̓aʔmat ct Strathcona": 0.40,
    "Renfrew": 0.60,
    "South Hill": 0.50,
    "Terry Salman": 0.65,
    "West Point Grey": 0.46,
}

rng = np.random.default_rng(42)

books = pd.read_csv(
    SOURCE,
    usecols=["book_id", "ratings_count"],
)

counts = pd.to_numeric(books["ratings_count"], errors="coerce").fillna(0).clip(lower=0)

popularity = counts.rank(pct=True).to_numpy()

records = []
for branch, capacity in BRANCH_CAPACITY.items():
    # (1) Ownership: bigger branches own a wider selection. Popularity adds
    # a modest increase in the chance of owning a title.
    ownership_probability = np.clip(
        0.12 + 0.48 * capacity + 0.20 * (popularity - 0.5),
        0.05, 0.85,
    )
    owned = rng.random(len(books)) < ownership_probability
    ids = books.loc[owned, "book_id"].to_numpy(dtype=np.int32)
    demand = popularity[owned]

    # (2) Copies: popular titles and larger branches tend to own more copies.
    # At least one copy exists for every owned title; cap at eight for the demo.
    expected_extra_copies = 0.10 + 0.40 * demand + 2.0 * capacity * demand**2
    total = 1 + rng.poisson(expected_extra_copies)
    total = np.minimum(total, 8).astype(np.int16)

    # (3) Current availability: popular titles have a lower probability
    # of being on the shelf *per copy* because of fictional circulation demand.
    per_copy_available_probability = np.clip(0.78 - 0.62 * demand, 0.10, 0.90)
    available = rng.binomial(total, per_copy_available_probability).astype(np.int16)

    records.append(pd.DataFrame({
        "book_id": ids,
        "branch": branch,
        "total_copies": total,
        "available_copies": available,
    }))

inventory = pd.concat(records, ignore_index=True)
assert (inventory["available_copies"] >= 0).all()
assert (inventory["available_copies"] <= inventory["total_copies"]).all()
assert not inventory.duplicated(["book_id", "branch"]).any()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
inventory.to_csv(OUTPUT, index=False)

print(inventory.groupby("branch").agg(
    titles_owned=("book_id", "size"),
    copies_owned=("total_copies", "sum"),
    titles_available=("available_copies", lambda col: (col > 0).sum()),
    copies_available=("available_copies", "sum"),
))
