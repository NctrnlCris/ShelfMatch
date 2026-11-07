from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parent

# 1. Load our prepared model
matrix = load_npz(ROOT / "model" / "item_user.npz")

# 2. Load book metadata
books = pd.read_csv(ROOT / "data" / "raw" / "books.csv")
books = books.set_index("book_id")

# 3. Choose three favourite books by ID
favourites = [1, 2, 3]

print("Your favourite books:")
for book_id in favourites:
    print(f"- {books.loc[book_id, 'title']}")

# 4. Convert IDs to matrix row indices
indices = np.array(favourites) - 1

# 5. Calculate cosine similarities
similarities = matrix @ matrix[indices].T

# 6. Average similarity across favourites
scores = np.asarray(
    similarities.mean(axis=1)
).ravel()

# 7. Exclude the selected books
scores[indices] = -np.inf

# 8. Find the 10 best matches
top_indices = np.argsort(scores)[::-1][:10]

# 9. Display recommendations
print("\nRecommended books:")

for index in top_indices:
    book_id = int(index) + 1

    print(
        f"{books.loc[book_id, 'title']} "
        f"— Score: {scores[index]:.4f}"
    )
