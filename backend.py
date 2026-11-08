
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
            "genres": [],
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

    matrix = load_model()
    books = load_books().set_index("book_id")

    # Convert selected book IDs to matrix indices.
    indices = np.array(
        [int(book["id"]) - 1 for book in favourites]
    )

    # Compare all books against selected favourites.
    similarities = matrix @ matrix[indices].T

    # Average similarity across the favourites.
    scores = np.asarray(
        similarities.mean(axis=1)
    ).ravel()

    # Exclude the selected books.
    scores[indices] = -np.inf
    
    # Retrieve inventory for the selected branch.
    holdings = load_inventory()

    branch_inventory = holdings[
        holdings["branch"] == branch
    ].set_index("book_id")

    # Filter out unavailable books when requested.
    if priority == "available":
        available_ids = branch_inventory.index[
            branch_inventory["available_copies"] > 0
        ].to_numpy()

        available_mask = np.zeros(
            len(scores), dtype=bool
        )

        available_mask[available_ids - 1] = True

        scores[~available_mask] = -np.inf


    # Sort ALL candidates by similarity.
    ranked_indices = np.argsort(scores)[::-1]

    recommendations = []
    seen_authors = set()

    for index in ranked_indices:

        # Scores are in descending order.
        # Stop when there is no positive similarity.
        if scores[index] <= 0:
            break

        book_id = int(index) + 1
        book = books.loc[book_id]

        title = str(book["title"])
        author = str(book["authors"])

        # Normalize the main author's name.
        author_key = author.split(",")[0].strip().casefold()

        # Skip duplicate authors.
        if author_key in seen_authors:
            continue
        
        if book_id in branch_inventory.index:
            available = int(
                branch_inventory.at[
                    book_id, "available_copies"
                ]
            )

            total = int(
                branch_inventory.at[
                    book_id, "total_copies"
                ]
            )

            # availability_text = (
            #     f"{available} of {total} copies available "
            #     f"at {branch} (simulated)"
            # )

        else:
            # availability_text = (
            #     f"Not owned at {branch} (simulated)"
            # )
            total = 0
            available = 0


        recommendations.append({
            "id": str(book_id),
            "title": title,
            "author": author,
            "genres": [],
            "reason": (
                "Readers who enjoyed your favourite books "
                "also enjoyed this title."
            ),
            "available_copies": available,
            "total_copies" : total,
            "catalogue_url": None
        })

        seen_authors.add(author_key)

        if len(recommendations) == 10:
            break

    return recommendations
