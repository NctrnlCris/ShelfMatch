import pandas as pd

tags = pd.read_csv("data/raw/tags.csv")
book_tags = pd.read_csv("data/raw/book_tags.csv")

print(tags.head(20))
print(book_tags.head(20))
print(tags.shape)
print(book_tags.shape)

popular_tags = (
    book_tags.groupby("tag_id")["count"]
    .sum()
    .sort_values(ascending=False)
    .head(40)
)

print(
    tags.set_index("tag_id")
    .loc[popular_tags.index]
    .assign(total_count=popular_tags.values)
)