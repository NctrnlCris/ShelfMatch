"""Generate a fictional, reproducible VPL inventory snapshot for ShelfMatch.

Save as scripts/generate_inventory.py and run from the project root:
    python scripts/generate_inventory.py

Requires numpy and pandas. Goodreads ratings_count is a popularity proxy;
all copy counts, checkout rates, and branch weights are modelling assumptions.
Copies belong to VPL. Branch allocations describe available copies' current
locations, not ownership. Checked-out copies have no current branch location.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "books.csv"
OUTPUT = ROOT / "data" / "processed" / "inventory.csv"
SEED = 42

# Keep the earlier collection coverage rule: top 20% guaranteed;
# other titles have an inclusion probability increasing from 80% to 95%.
GUARANTEED_TOP_FRACTION = 0.20
MIN_INCLUSION = 0.80
MAX_INCLUSION = 0.95

# Deterministic supply based on actual rating counts, not percentile rank.
# Power-law scaling keeps the long tail stocked without flattening the top.
MIN_COPIES = 1
MAX_COPIES = 30
COPY_POWER = 2/3
# Each copy independently has a 25%-90% chance of being checked out.
MIN_CHECKOUT = 0.25
MAX_CHECKOUT = 0.90

# Relative location weights, NOT measured branch sizes or ownership shares.
# Retained from the previous simulator; Central has the greatest weight.
# Oakridge is included with zero weight while closed (November 2026).
# Change its weight when modelling an open branch.
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
    "Oakridge": 0.0,
    "Renfrew": 1.3,
    "South Hill": 1.1,
    "Terry Salman": 1.2,
    "West Point Grey": 1.4,
}


def generate_inventory(books, seed=SEED):
    """Return one row per included title per branch, including zero availability."""
    books = books[["book_id", "ratings_count"]].copy()
    if books.empty or books["book_id"].isna().any():
        raise ValueError("books.csv must contain non-null book IDs and at least one row.")
    if books["book_id"].duplicated().any():
        raise ValueError("books.csv must contain unique book IDs.")
    books = books.sort_values("book_id").reset_index(drop=True)
    ratings = pd.to_numeric(books["ratings_count"], errors="coerce")
    if not np.isfinite(ratings).all() or (ratings < 0).any():
        raise ValueError("ratings_count must contain finite, non-negative numbers.")

    weights = np.array(list(BRANCH_WEIGHTS.values()), dtype=float)
    if not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("Branch weights must be non-negative with a positive sum.")
    branch_probabilities = weights / weights.sum()
    rng = np.random.default_rng(seed)

    # Percentile rank avoids a few huge rating counts dominating the model.
    # Equal rating counts receive equal popularity scores.
    popularity = ratings.rank(method="average", pct=True).to_numpy()

    cutoff = 1.0 - GUARANTEED_TOP_FRACTION
    inclusion_probability = MIN_INCLUSION + (MAX_INCLUSION - MIN_INCLUSION) * np.minimum(
        popularity / cutoff, 1.0
    )
    inclusion_probability[popularity > cutoff] = 1.0
    included = rng.random(len(books)) < inclusion_probability
    book_ids = books.loc[included, "book_id"].to_numpy()
    popularity = popularity[included]

    # Scale against the full catalogue maximum, before the inclusion filter.
    # A zero-rating catalogue receives MIN_COPIES for every included title.
    highest_count = float(ratings.max())
    relative_ratings = (
        ratings.to_numpy(dtype=float) / highest_count
        if highest_count > 0 else np.zeros(len(books))
    )
    total_copies = np.rint(
        MIN_COPIES + (MAX_COPIES - MIN_COPIES)
        * relative_ratings[included]**COPY_POWER
    ).astype(int)
    checkout_probability = MIN_CHECKOUT + (MAX_CHECKOUT - MIN_CHECKOUT) * popularity

    # Binomial = count how many copies are currently available.
    vpl_available = rng.binomial(total_copies, 1.0 - checkout_probability)

    # Multinomial = place those available copies across branches by size weight.
    # Each available copy appears at exactly one branch; no branch owns it.
    allocations = np.zeros((len(book_ids), len(weights)), dtype=int)
    for i, count in enumerate(vpl_available):
        allocations[i] = rng.multinomial(int(count), branch_probabilities)

    inventory = pd.DataFrame({
        "book_id": np.repeat(book_ids, len(weights)),
        "branch": np.tile(list(BRANCH_WEIGHTS), len(book_ids)),
        "total_copies": np.repeat(total_copies, len(weights)),
        "available_copies": allocations.ravel(),
        "vpl_available_copies": np.repeat(vpl_available, len(weights)),
    })

    # System totals repeat on every branch row: never sum these columns
    # across branches. Only available_copies is a branch-level quantity.
    if not np.array_equal(allocations.sum(axis=1), vpl_available):
        raise AssertionError("Branch counts do not match system availability.")
    if not np.all((vpl_available >= 0) & (vpl_available <= total_copies)):
        raise AssertionError("Invalid system availability.")
    return inventory


def main():
    books = pd.read_csv(SOURCE, usecols=["book_id", "ratings_count"])
    inventory = generate_inventory(books)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(OUTPUT, index=False)

    system = inventory.drop_duplicates("book_id")
    print(f"Saved synthetic inventory to: {OUTPUT}")
    print(f"Titles included: {len(system):,} / {len(books):,}")
    print(f"Total VPL copies: {system['total_copies'].sum():,}")
    print(f"Available VPL copies: {system['vpl_available_copies'].sum():,}")
    print("\nAvailable copies by current branch location:")
    print(inventory.groupby("branch")["available_copies"].sum()
          .sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()