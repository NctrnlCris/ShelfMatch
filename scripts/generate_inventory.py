
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "raw" / "books.csv"
OUTPUT = ROOT / "data" / "processed" / "inventory.csv"

# Relative weights for where available copies are located.
# These are fictional, not actual VPL collection figures.
BRANCH_WEIGHTS = {
    "Central Library": 5.0,
    "Britannia": 1.5,
    "Carnegie": 0.8,
    "Champlain Heights": 1.0,
    "Collingwood": 1.4,
    "Dunbar": 1.5,
    "Firehall": 0.8,
    "Fraserview": 1.0,
    "Hastings": 1.2,
    "Joe Fortes": 1.7,
    "Kensington": 1.1,
    "Kerrisdale": 1.6,
    "Kitsilano": 1.8,
    "Marpole": 1.3,
    "Mount Pleasant": 1.9,
    "nə́c̓aʔmat ct Strathcona": 1.4,
    "Renfrew": 1.3,
    "South Hill": 1.1,
    "Terry Salman": 1.2,
    "West Point Grey": 1.4,
}

rng = np.random.default_rng(42)

books = pd.read_csv(
    SOURCE,
    usecols=["book_id", "ratings_count"]
)

# Relative Goodreads popularity, between 0 and 1.
popularity = (
    books["ratings_count"]
    .fillna(0)
    .clip(lower=0)
    .rank(pct=True)
    .to_numpy()
)

# STEP 1: Does VPL own this title at all?
ownership_probability = 0.48 + 0.35 * popularity

owned = rng.random(len(books)) < ownership_probability

book_ids = books.loc[owned, "book_id"].to_numpy()
demand = popularity[owned]

# STEP 2: How many copies does VPL own system-wide?
expected_extra_copies = 0.3 + 5.0 * demand**2

total_copies = (
    1 + rng.poisson(expected_extra_copies)
)

total_copies = np.minimum(total_copies, 12)

# STEP 3: Normalize branch weights.
branches = list(BRANCH_WEIGHTS)

weights = np.array(
    list(BRANCH_WEIGHTS.values()), dtype=float
)

weights = weights / weights.sum()

records = []

# STEP 4: Distribute each title's copies.
for book_id, total, popularity_score in zip(
    book_ids, total_copies, demand
):
    # Popular books are more likely to be checked out.
    p_available = np.clip(
        0.78 - 0.62 * popularity_score,
        0.10,
        0.90
    )

    # Available copies are distributed between branches.
    # The final category represents checked-out copies.
    probabilities = np.append(
        weights * p_available,
        1 - p_available
    )

    allocation = rng.multinomial(
        int(total), probabilities
    )

    branch_available = allocation[:-1]
    vpl_available = int(branch_available.sum())

    for branch, available in zip(
        branches, branch_available
    ):
        records.append({
            "book_id": int(book_id),
            "branch": branch,
            "total_copies": int(total),
            "available_copies": int(available),
            "vpl_available_copies": vpl_available,
        })

inventory = pd.DataFrame(records)

# Ensure system-wide availability is consistent.
summary = inventory.groupby("book_id").agg(
    total=("total_copies", "first"),
    available=("available_copies", "sum"),
    reported_available=("vpl_available_copies", "first"),
)

assert (summary["available"] <= summary["total"]).all()
assert (
    summary["available"] == summary["reported_available"]
).all()

assert not inventory.duplicated(
    ["book_id", "branch"]
).any()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
inventory.to_csv(OUTPUT, index=False)

print(f"Saved {len(inventory):,} inventory rows")
print(f"VPL titles: {len(summary):,}")
print(f"System-wide copies: {summary['total'].sum():,}")

print(
    inventory.groupby("branch")["available_copies"]
    .sum()
    .sort_values(ascending=False)
)

