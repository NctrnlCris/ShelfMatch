
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz
from sklearn.preprocessing import normalize


ratings = pd.read_csv(
    "data/raw/ratings.csv",
    dtype={
        "user_id": "int32",
        "book_id": "int32",
        "rating": "int8"
    }
)

# For our first model, 4- and 5-star ratings
# indicate positive reader feedback.
positive = ratings.loc[
    ratings["rating"] >= 4,
    ["user_id", "book_id"]
].drop_duplicates()

# Matrix rows = books, columns = historical readers.
matrix = csr_matrix(
    (
        np.ones(len(positive), dtype=np.float32),
        (
            positive["book_id"].to_numpy() - 1,
            positive["user_id"].to_numpy() - 1
        )
    ),
    shape=(
        10000,
        len(ratings["user_id"].unique())
    )
)

# Normalize book vectors so their dot products
# become cosine similarity scores.
matrix = normalize(matrix, norm="l2", axis=1)


save_npz("models/item_user.npz", matrix)

print("Model created.")
print("Shape:", matrix.shape)
print("Nonzero interactions:", matrix.nnz)
