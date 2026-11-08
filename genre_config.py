"""Curated ShelfMatch genre labels and exact Goodreads shelf-tag aliases.

The names were selected after reviewing the public Goodbooks-10k tags.csv
vocabulary. The builder checks tag existence against the actual downloaded
CSV and ignores aliases that are not present. Add or remove aliases here.
"""

GENRE_TAGS = {
    # FICTION
    "Fantasy": [
        "fantasy", "epic-fantasy", "high-fantasy", "urban-fantasy",
        "dark-fantasy", "fantasy-epic", "fantasy-high", "fantasy-urban",
    ],
    "Science Fiction": [
        "science-fiction", "sci-fi", "scifi", "sciencefiction",
        "sci_fi", "space-opera", "cyberpunk", "sci-fi-space-opera",
        "sci-fi-cyberpunk",
    ],
    "Dystopian": [
        "dystopia", "dystopian", "dystopian-fiction", "dystopian-future",
        "dystopias", "post-apocalyptic",
    ],
    "Romance": [
        "romance", "romances", "romance-contemporary", "contemporary-romance",
        "historical-romance", "romance-historical", "romance-paranormal",
        "paranormal-romance",
    ],
    "Mystery": [
        "mystery", "mysteries", "mystery-cozy", "cozy-mystery",
        "mystery-detective", "detective-fiction", "mystery-historical",
    ],
    "Crime": [
        "crime-fiction", "crime-novel", "crime-novels",
        "detective-crime-fiction", "british-crime-fiction",
        "crime-and-mystery", "crime-mystery", "crime-thriller",
    ],
    "Thriller": [
        "thriller", "thrillers", "suspense", "suspense-thriller",
        "psychological-thriller", "thriller-political", "thriller-legal",
        "mystery-thriller",
    ],
    "Horror": [
        "horror", "horror-fiction", "horror-gothic", "gothic-horror",
        "horror-supernatural", "horror-macabre", "horror-stories",
    ],
    "Historical Fiction": [
        "historical-fiction", "historical-novel", "historical-novels",
        "historical_fiction", "historical-mystery", "historical-romance",
    ],
    "Literary Fiction": [
        "literary-fiction", "literary", "literary-novels",
    ],
    "Contemporary Fiction": [
        "contemporary-fiction", "contemporary-lit", "contemporary-literature",
        "contemporary-realistic-fiction", "realistic-fiction",
    ],
    "Adventure": [
        "adventure", "adventure-fiction", "adventure-action",
        "action-adventure", "adventure-and-survival",
    ],
    "Paranormal": [
        "paranormal", "paranormal-fiction", "paranormal-mystery",
        "paranormal-romance", "paranormal-supernatural", "supernatural",
    ],
    "Magical Realism": [
        "magical-realism", "magical-realisim", "magic-realism",
    ],
    "Humor & Comedy": [
        "humor", "humour", "comedy", "humor-and-comedy",
        "humor-comedy", "humorous-fiction", "satire",
    ],
    # NONFICTION
    "Nonfiction": [
        "nonfiction", "non-fiction", "non-fiction-general",
        "nonfiction-general",
    ],
    "Biography": [
        "biography", "biographies", "biography-memoir", "biography-history",
        "autobiography", "autobiographies",
    ],
    "Memoir": [
        "memoir", "memoirs", "autobiography", "autobiographies",
        "memoir-autobiography", "memoirs-and-autobiographies",
    ],
    "History": [
        "history", "history-general", "non-fiction-history",
        "nonfiction-history", "world-history",
    ],
    "True Crime": [
        "true-crime", "true_crime", "truecrime",
        "nonfiction-true-crime", "crime-non-fiction",
    ],
    "Science": [
        "science", "popular-science", "science-popular",
        "non-fiction-science", "nonfiction-science", "science-nonfiction",
    ],
    "Nature": [
        "nature", "nature-writing", "natural-history",
        "nature-environment", "nature-and-environment",
    ],
    "Psychology": [
        "psychology", "psychology-neuroscience", "psychology-self-help",
        "psychology-psychoanalysis", "psychology-neurology",
    ],
    "Philosophy": [
        "philosophy", "philosophy-general", "philosophy-ethics",
        "philosophy-metaphysics", "philosophy-existentialism",
    ],
    "Politics": [
        "politics", "political-science", "politics-and-current-events",
        "politics-and-government", "politics-current-events",
    ],
    "Business": [
        "business", "business-management", "business-entrepreneurship",
        "business-economics", "business-finance", "economics", "finance",
    ],
    "Self-Help": [
        "self-help", "selfhelp", "self-improvement",
        "personal-development", "personal-growth",
    ],
    "Travel": [
        "travel", "travel-writing", "travel-literature",
        "travelogue", "travel-guides", "travel-guide",
    ],
    "Religion & Spirituality": [
        "religion", "spirituality", "theology",
        "religion-spirituality", "religion-theology",
        "spirituality-and-religion",
    ],
    "Health & Wellness": [
        "health", "health-wellness", "health-fitness", "wellness",
        "nutrition", "fitness", "mental-health",
    ],
    # LITERARY FORMS
    "Poetry": [
        "poetry", "poetry-collection", "poetry-collections",
        "poetry-poems", "poems",
    ],
    "Short Stories": [
        "short-stories", "short-story", "short-stories-collections",
        "short-story-collection", "short-stories-anthologies",
        "short-story-collections",
    ],
    "Graphic Novels": [
        "graphic-novels", "graphic-novel", "comics", "comic-books",
        "comics-and-graphic-novels", "comics-graphic-novels",
    ],
    "Manga": [
        "manga", "manga-shonen", "manga-shoujo", "manga-seinen",
        "manga-japanese", "manga-shojo", "manga-shounen",
    ],
    # OTHER CLASSIFICATIONS (not strictly genres)
    "Classics": [
        "classics", "classic-literature", "literary-classics",
        "classics-literature", "classic",
    ],
    "Young Adult": [
        "young-adult", "ya", "ya-fiction", "young-adult-books",
        "young-adult-fiction", "ya-lit", "youngadult",
    ],
    "Middle Grade": [
        "middle-grade", "middle-grade-fiction", "middlegrade",
        "middle-grades", "middle-reader",
    ],
    "Children's": [
        "childrens", "children-s", "children-s-literature",
        "childrens-books", "children-s-fiction", "picture-books",
    ],
}

GENRES = list(GENRE_TAGS)
