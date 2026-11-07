
import pandas as pd

books = pd.read_csv("data/raw/books.csv")

print("Number of books:", len(books))
print("Columns:", books.columns.tolist())

print(
    books[
        ["book_id", "title", "authors", "goodreads_book_id"]
    ].head(10)
)

print("Missing titles:", books["title"].isna().sum())
print("Missing Authors", books["authors"].isna().sum())
print("Duplicate book IDs:", books["book_id"].duplicated().sum())
