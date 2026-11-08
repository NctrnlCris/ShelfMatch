from pathlib import Path
import sys
import pandas as pd

"""Build a clean book-to-genre table from Goodbooks-10k shelf tags.

Run from project root: python scripts/build_genres.py
Requires: data/raw/books.csv, data/raw/tags.csv, data/raw/book_tags.csv
Outputs: data/processed/book_genres.csv, genre_coverage.csv, genre_tag_audit.csv
"""

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genre_config import GENRE_TAGS  # noqa: E402

RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Guard against personally tagged shelves with tiny counts or weak genre support.
MIN_SHELF_COUNT = 5
MIN_RELATIVE_WEIGHT = 0.10
MAX_GENRES_PER_BOOK = 5

books = pd.read_csv(RAW / "books.csv", usecols=["book_id", "goodreads_book_id"])
tags = pd.read_csv(RAW / "tags.csv")
book_tags = pd.read_csv(
    RAW / "book_tags.csv",
    usecols=["goodreads_book_id", "tag_id", "count"],
)

# Expand each ShelfMatch label into its explicitly approved Goodreads tag aliases.
requested = pd.DataFrame(
    [(genre, alias.casefold().strip())
     for genre, aliases in GENRE_TAGS.items()
     for alias in aliases],
    columns=["genre", "tag_name"],
).drop_duplicates()

tags["tag_name"] = tags["tag_name"].astype(str).str.casefold().str.strip()
lookup = requested.merge(tags, on="tag_name", how="left", validate="many_to_many")

# Save an audit of which candidate aliases actually exist in this dataset.
lookup["tag_found"] = lookup["tag_id"].notna()
lookup.to_csv(OUT / "genre_tag_audit.csv", index=False)
missing = lookup.loc[~lookup["tag_found"], ["genre", "tag_name"]]
print(f"Genre aliases found: {lookup['tag_found'].sum()} / {len(lookup)}")
if not missing.empty:
    print("Unmatched candidate aliases (ignored):")
    print(missing.to_string(index=False))

valid_tags = lookup.loc[lookup["tag_found"], ["genre", "tag_id"]].copy()
valid_tags["tag_id"] = valid_tags["tag_id"].astype("int64")

# IMPORTANT: book_tags.csv uses goodreads_book_id, not the 1..10000 book_id.
matched = (book_tags
    .merge(valid_tags, on="tag_id", how="inner", validate="many_to_many")
    .merge(books, on="goodreads_book_id", how="inner", validate="many_to_one")
)

# If a book has 'sci-fi' and 'science-fiction', use the stronger tag count.
# This avoids unfairly doubling the evidence for genres with many aliases.
book_genres = (matched
    .groupby(["book_id", "genre"], as_index=False)["count"]
    .max()
    .rename(columns={"count": "tag_count"})
)

# This is *relative tag evidence* within a book, not an ML probability.
max_per_book = book_genres.groupby("book_id")["tag_count"].transform("max")
book_genres["genre_weight"] = book_genres["tag_count"] / max_per_book

book_genres = book_genres.loc[
    (book_genres["tag_count"] >= MIN_SHELF_COUNT)
    & (book_genres["genre_weight"] >= MIN_RELATIVE_WEIGHT)
]

# Limit noisy long lists; a book can still have several genres.
book_genres = (book_genres
    .sort_values(["book_id", "tag_count", "genre"],
                 ascending=[True, False, True])
    .groupby("book_id", as_index=False)
    .head(MAX_GENRES_PER_BOOK)
    .reset_index(drop=True)
)
book_genres.to_csv(OUT / "book_genres.csv", index=False)

coverage = (book_genres.groupby("genre")
    .agg(books=("book_id", "nunique"),
         max_tag_count=("tag_count", "max"))
    .reindex(GENRE_TAGS, fill_value=0)
    .reset_index()
)
coverage.to_csv(OUT / "genre_coverage.csv", index=False)

print(f"\nTagged books: {book_genres['book_id'].nunique():,} / {len(books):,}")
print(f"Book–genre labels: {len(book_genres):,}")
print("\nGenre coverage (books with each genre):")
print(coverage.to_string(index=False))

# Print some concrete examples to inspect classification quality.
examples = [1, 2, 6, 12, 18]
print("\nSample book classifications:")
print(book_genres.loc[book_genres["book_id"].isin(examples)].to_string(index=False))

assert book_genres["book_id"].isin(books["book_id"]).all()
assert book_genres["genre_weight"].between(0, 1).all()
assert not book_genres.duplicated(["book_id", "genre"]).any()
