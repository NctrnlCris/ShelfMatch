
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz


ROOT = Path(__file__).resolve().parent

DEMO_MODE = False


@lru_cache(maxsize=1)
def load_books():
    books = pd.read_csv(
        ROOT / "data" / "raw" / "books.csv",
        usecols=["book_id", "title", "authors"]
    )

    books["title"] = books["title"].fillna("")
    books["authors"] = books["authors"].fillna("")

    return books


@lru_cache(maxsize=1)
def load_model():
    return load_npz(
        ROOT / "models" / "item_user.npz"
    ).tocsr()

@lru_cache(maxsize=1)
def load_inventory():
    return pd.read_csv(
        ROOT / "data" / "processed" / "inventory.csv"
    )

@lru_cache(maxsize=1)
def load_genres():
    return pd.read_csv(
        ROOT / "data" / "processed" / "book_genres.csv"
    )


@lru_cache(maxsize=1)
def book_genre_lookup():
    return (
        load_genres()
        .sort_values(
            ["book_id", "genre_weight"],
            ascending=[True, False]
        )
        .groupby("book_id")["genre"]
        .agg(list)
        .to_dict()
    )



def search_books(query: str) -> list[dict]:
    query = query.strip().casefold()

    if len(query) < 2:
        return []

    books = load_books()

    matches = books[
        books["title"].str.casefold().str.contains(
            query, regex=False
        )
        |
        books["authors"].str.casefold().str.contains(
            query, regex=False
        )
    ].head(20)

    return [
        {
            "id": str(row.book_id),
            "title": row.title,
            "author": row.authors,
            "genres": book_genre_lookup().get(int(row.book_id), []),
            "catalogue_url": None
        }
        for row in matches.itertuples(index=False)
    ]




def get_recommendations(
    favourites: list[dict],
    genres: list[str],
    branch: str,
    priority: str,
) -> list[dict]:

    # 1. Load recommendation model and book information.
    matrix = load_model()
    books = load_books().set_index("book_id")

    # Convert selected book IDs to matrix indices.
    indices = np.array(
        [int(book["id"]) - 1 for book in favourites]
    )

    # 2. Calculate collaborative filtering scores.
    similarities = matrix @ matrix[indices].T

    scores = np.asarray(
        similarities.mean(axis=1)
    ).ravel()

    # Exclude the books the user already selected.
    scores[indices] = -np.inf

    # 3. Apply a soft genre boost.
    if genres:
        matched = load_genres()

        matched = matched[
            matched["genre"].isin(genres)
        ]

        genre_bonus = np.zeros_like(
            scores, dtype=float
        )

        np.add.at(
            genre_bonus,
            matched["book_id"].to_numpy(dtype=int) - 1,
            matched["genre_weight"].to_numpy(dtype=float)
        )

        # Maximum 25% increase in similarity score.
        scores *= (
            1 + 0.25 * np.minimum(genre_bonus, 1.0)
        )

    # Use the strongest unseen match before any inventory/availability filtering.
    # Branch and availability choices must not change a book’s relative score.
    positive_scores = scores[np.isfinite(scores) & (scores > 0)]
    best_score = float(positive_scores.max()) if positive_scores.size else 0.0

    # 4. Load simulated inventory for the selected branch.
    holdings = load_inventory()

    branch_inventory = holdings[
        holdings["branch"] == branch
    ].set_index("book_id")

    # Determine which books are eligible for recommendation.
    if priority == "available":
        # Available at the selected branch.
        eligible_ids = branch_inventory.index[
            branch_inventory["available_copies"] > 0
        ].to_numpy()

    elif priority == "any_available":
        # Available somewhere in the VPL system.
        eligible_ids = branch_inventory.index[
            branch_inventory["vpl_available_copies"] > 0
        ].to_numpy()

    else:
        # Best Matches: VPL must own at least one copy,
        # even if all copies are currently checked out.
        eligible_ids = branch_inventory.index[
            branch_inventory["total_copies"] > 0
        ].to_numpy()

    eligible_mask = np.zeros(
        len(scores), dtype=bool
    )

    eligible_mask[eligible_ids - 1] = True

    scores[~eligible_mask] = -np.inf


    # 5. Rank books by their final recommendation scores.
    ranked_indices = np.argsort(scores)[::-1]

    recommendations = []
    seen_authors = set()

    # 6. Examine books in descending score order.
    for index in ranked_indices:

        # Stop when there is no positive similarity.
        if scores[index] <= 0:
            break

        book_id = int(index) + 1
        book = books.loc[book_id]

        title = str(book["title"])
        author = str(book["authors"])

        # Use the primary author for diversity filtering.
        author_key = author.split(",")[0].strip().casefold()

        if author_key in seen_authors:
            continue

        # 7. Retrieve inventory information for this book.
        if book_id in branch_inventory.index:

            # Available copies at the selected branch.
            available = int(
                branch_inventory.at[
                    book_id, "available_copies"
                ]
            )

            # Total copies owned across VPL.
            total = int(
                branch_inventory.at[
                    book_id, "total_copies"
                ]
            )

            # Available copies across all VPL branches.
            vpl_available = int(
                branch_inventory.at[
                    book_id, "vpl_available_copies"
                ]
            )

        else:
            # VPL doesn't own this title in our simulation.
            available = 0
            total = 0
            vpl_available = 0

        # 8. Construct the recommendation dictionary.
        recommendations.append({
            "id": str(book_id),
            "recommendation_score": float(scores[index]),
            "match_score": float(100.0 * scores[index] / best_score) if best_score else 0.0,
            "title": title,
            "author": author,
            "genres": book_genre_lookup().get(book_id, []),
            "reason": (
                "Readers who enjoyed your favourite books "
                "also enjoyed this title."
            ),
            "available_copies": available,
            "total_copies": total,
            "vpl_available_copies": vpl_available,
            "catalogue_url": None,
        })

        # Prevent recommending another book by this author.
        seen_authors.add(author_key)

        # Stop after selecting 10 distinct authors.
        if len(recommendations) == 10:
            break

    return recommendations
