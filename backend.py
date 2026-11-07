"""
ShelfMatch backend placeholders.

These functions return fixed demo results. Replace the TODO sections
with your book-search and recommendation implementations.

Expected book format:
{
    "id": "unique-book-id",
    "title": "Book title",
    "author": "Author name",
    "genres": ["Fantasy"],
    "catalogue_url": None,  # Optional direct catalogue record URL
}
"""

DEMO_MODE = True


DEMO_BOOKS = [
    {
        "id": "book-1",
        "title": "The Midnight Library",
        "author": "Matt Haig",
        "genres": ["Fantasy", "Literary fiction"],
        "catalogue_url": None,
    },
    {
        "id": "book-2",
        "title": "Project Hail Mary",
        "author": "Andy Weir",
        "genres": ["Science fiction", "Adventure"],
        "catalogue_url": None,
    },
    {
        "id": "book-3",
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genres": ["Fantasy", "Adventure"],
        "catalogue_url": None,
    },
    {
        "id": "book-4",
        "title": "Educated",
        "author": "Tara Westover",
        "genres": ["Memoir", "Nonfiction"],
        "catalogue_url": None,
    },
    {
        "id": "book-5",
        "title": "Dune",
        "author": "Frank Herbert",
        "genres": ["Science fiction", "Adventure"],
        "catalogue_url": None,
    },
    {
        "id": "book-6",
        "title": "The Song of Achilles",
        "author": "Madeline Miller",
        "genres": ["Fantasy", "Romance"],
        "catalogue_url": None,
    },
]


DEMO_RECOMMENDATIONS = [
    {
        "id": "result-1",
        "title": "The House in the Cerulean Sea",
        "author": "TJ Klune",
        "genres": ["Fantasy", "Romance"],
        "reason": "A fixed demo recommendation.",
        "availability": None,
        "catalogue_url": None,
    },
    {
        "id": "result-2",
        "title": "Station Eleven",
        "author": "Emily St. John Mandel",
        "genres": ["Science fiction", "Literary fiction"],
        "reason": "A fixed demo recommendation.",
        "availability": None,
        "catalogue_url": None,
    },
    {
        "id": "result-3",
        "title": "The Thursday Murder Club",
        "author": "Richard Osman",
        "genres": ["Mystery", "Thriller"],
        "reason": "A fixed demo recommendation.",
        "availability": None,
        "catalogue_url": None,
    },
]


def search_books(query: str) -> list[dict]:
    """
    Search for books by title or author.

    TODO: Replace the demo search with your backend search.

    Return a list of book dictionaries using the format above.
    Make sure each book has a stable, unique ID.
    """
    query = query.strip().casefold()

    if not query:
        return []

    return [
        book.copy()
        for book in DEMO_BOOKS
        if query in f"{book['title']} {book['author']}".casefold()
    ]


def get_recommendations(
    favourites: list[dict],
    genres: list[str],
    branch: str,
    priority: str,
) -> list[dict]:
    """
    Return recommendations for the selected preferences.

    favourites:
        Selected book dictionaries with an additional "rating" field.
        The rating is None or an integer from 1 to 5.

    genres:
        Zero to three selected genres.

    branch:
        The selected library branch.

    priority:
        "best_matches" or "available".

    TODO: Connect your recommendation function here.

    TODO: Connect real branch availability here when you implement it.
    This placeholder does not simulate availability.

    TODO: Return direct VPL catalogue record URLs when available.
    """
    return [book.copy() for book in DEMO_RECOMMENDATIONS]