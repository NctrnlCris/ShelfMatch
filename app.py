import base64
import logging
import math
from copy import deepcopy
from html import escape
from urllib.parse import urlencode

import streamlit as st
from backend import DEMO_MODE, get_recommendations, search_books
from genre_config import GENRES


st.set_page_config(
    page_title="ShelfMatch",
    page_icon="📚",
    layout="wide",
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Options
# ------------------------------------------------------------


MAX_FAVOURITES = 20

# TODO: Replace with branch names/IDs from your backend if needed.
BRANCHES = [
    "Central Library",
    "Britannia",
    "Carnegie",
    "Champlain Heights",
    "Collingwood",
    "Dunbar",
    "Firehall",
    "Fraserview",
    "Hastings",
    "Joe Fortes",
    "Kensington",
    "Kerrisdale",
    "Kitsilano",
    "Marpole",
    "Mount Pleasant",
    "nə́c̓aʔmat ct Strathcona",
    "Renfrew",
    "South Hill",
    "Terry Salman",
    "West Point Grey",
]


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------

DEFAULTS = {
    "view": "preferences",
    "favourites": {},
    "search_results": [],
    "search_complete": False,
    "saved_genres": [],
    "saved_branch": None,
    "saved_priority": "Best Matches",
    "recommendations": [],
}

for key, default in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = deepcopy(default)


def add_favourite(book):
    if len(st.session_state.favourites) < MAX_FAVOURITES:
        st.session_state.favourites[book["id"]] = deepcopy(book)


def remove_favourite(book_id):
    st.session_state.favourites.pop(book_id, None)


def save_preference(widget_key, saved_key):
    st.session_state[saved_key] = deepcopy(
        st.session_state[widget_key]
    )


def start_over():
    widget_keys = [
        "genre_widget",
        "branch_widget",
        "priority_widget",
        "book_search_query",
    ]

    for key in widget_keys:
        st.session_state.pop(key, None)

    for key, default in DEFAULTS.items():
        st.session_state[key] = deepcopy(default)


def catalogue_url(book):
    direct_url = book.get("catalogue_url") or ""

    if direct_url.startswith("https://vpl.bibliocommons.com/"):
        return direct_url

    parameters = urlencode({
        "query": f"{book['title']} {book['author']}",
        "searchType": "smart",
    })

    return f"https://vpl.bibliocommons.com/v2/search?{parameters}"


# ------------------------------------------------------------
# Styles
# ------------------------------------------------------------

st.markdown(
    """
<style>
.stApp {
    background: #F4F3EF;
    color: #152C40;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.sm-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 12px 0 24px;
    margin-bottom: 32px;
    border-bottom: 4px solid #152C40;
}

.sm-logo {
    color: #111111;
    font-size: 29px;
    font-weight: 850;
    letter-spacing: -1.5px;
}

.sm-logo span {
    color: #D8323B;
}

.sm-header a {
    color: #152C40;
    font-size: 13px;
    font-weight: 650;
    text-decoration: none;
    border-bottom: 2px solid #D8323B;
    padding-bottom: 4px;
}

.sm-hero {
    margin-bottom: 32px;
}

.sm-eyebrow {
    color: #D8323B;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 16px;
}

/* A custom title element avoids automatic heading-link icons. */
.sm-title {
    font-family: "Arial Black", "Segoe UI", Arial, sans-serif !important;
    font-size: clamp(38px, 5.5vw, 64px) !important;
    font-weight: 900 !important;
    line-height: 1.12 !important;
    letter-spacing: -0.045em !important;
    color: #152C40 !important;
    margin: 0 0 22px !important;
}

.sm-title .sm-accent {
    display: inline;
    font: inherit;
    color: inherit;
    padding: 0;
    background: none;
    text-decoration-line: underline;
    text-decoration-color: #FFD267;
    text-decoration-thickness: 0.12em;
    text-underline-offset: 0.04em;
    text-decoration-skip-ink: none;
}

.sm-description {
    color: #546471;
    font-size: 16px;
    line-height: 1.6;
}

/* Availability summary inside each recommendation card. */
.sm-availability {
    background: #F4F3EF;
    border: 1px solid #DADFE1;
    border-radius: 6px;
    padding: 14px;
    margin: 12px 0;
}

.sm-availability-title {
    color: #152C40;
    font-weight: 750;
    margin-bottom: 12px;
}

.sm-availability-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 6px;
    color: #152C40;
    font-size: 13px;
}

.sm-availability-row strong {
    font-weight: 750;
}

.sm-availability-divider {
    border-top: 1px solid #DADFE1;
    margin: 10px 0;
}

.st-key-books,
.st-key-genres,
.st-key-branch,
.st-key-priority {
    padding: 24px !important;
    border: 1px solid #DADFE1;
    border-radius: 5px;
    background: #FFFFFF;
    margin-bottom: 14px;
}

.st-key-books {
    border-top: 6px solid #D8323B;
}

.st-key-genres {
    background: #EAF3F9;
    border-top: 6px solid #147DAB;
}

.st-key-branch {
    background: #FFF4D6;
    border-top: 6px solid #E8B03C;
}

.st-key-priority {
    background: #E7F3EF;
    border-top: 6px solid #007F79;
}

.sm-section-heading {
    display: flex;
    align-items: center;
    gap: 11px;
    margin-bottom: 8px;
}

.sm-number {
    width: 29px;
    height: 29px;
    display: grid;
    place-items: center;
    background: #152C40;
    color: white;
    font-size: 12px;
    font-weight: 750;
    flex-shrink: 0;
}

.sm-section-title {
    color: #152C40;
    font-size: 21px;
    font-weight: 750;
    line-height: 1.25;
    letter-spacing: -0.025em;
}

.sm-section-description {
    color: #5F6D76;
    font-size: 13px;
    margin-bottom: 17px;
}

.sm-book-title {
    color: #152C40;
    font-size: 15px;
    font-weight: 750;
    line-height: 1.35;
}

.sm-book-author {
    color: #66727A;
    font-size: 12px;
    margin-top: 3px;
}

.stButton button,
.stFormSubmitButton button {
    border-radius: 5px;
    min-height: 42px;
    font-weight: 650;
}

button[kind="primary"] {
    background: #D8323B !important;
    border-color: #D8323B !important;
    color: white !important;
}

.sm-art {
    overflow: hidden;
    border-radius: 5px;
    border: 1px solid #C9D8DE;
}

.sm-art img {
    display: block;
    width: 100%;
}

.sm-bars {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    height: 15px;
    margin-top: 14px;
}

.sm-bars i:nth-child(1) { background: #D8323B; }
.sm-bars i:nth-child(2) { background: #147DAB; }
.sm-bars i:nth-child(3) { background: #FFD267; }
.sm-bars i:nth-child(4) { background: #007F79; }

.sm-footer {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    border-top: 3px solid #152C40;
    margin-top: 45px;
    padding-top: 19px;
    color: #62707A;
    font-size: 11px;
    line-height: 1.7;
}

.sm-footer strong {
    color: #111111;
    font-size: 16px;
}

.sm-footer strong span {
    color: #D8323B;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 18px;
        padding-right: 18px;
    }

    .sm-header {
        align-items: flex-start;
    }

    .sm-header a {
        font-size: 11px;
    }

    .st-key-books,
    .st-key-genres,
    .st-key-branch,
    .st-key-priority {
        padding: 18px !important;
    }

    .sm-art,
    .sm-bars {
        display: none;
    }
}
/* Optional polish: keyboard focus, compact status labels and mobile spacing. */
.sm-status {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin: 4px 0 10px;
}
.sm-status-local { background: #E7F3EF; color: #145C46; }
.sm-status-elsewhere { background: #EAF3F9; color: #195779; }
.sm-status-unavailable { background: #F3EDE2; color: #715020; }
.sm-book-title { overflow-wrap: anywhere; }
.sm-header a:focus-visible,
.stButton button:focus-visible,
[data-testid="stLinkButton"] a:focus-visible {
    outline: 3px solid #147DAB;
    outline-offset: 4px;
}
@media (max-width: 700px) {
    .sm-title { font-size: 38px !important; }
    .sm-header { gap: 12px; }
    .sm-footer { margin-top: 28px; }
    [class*="st-key-shelf_result_"] { padding: 16px !important; }
}

</style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------


def render_hero(results=False):

    if results:
        eyebrow = "YOUR READING SHORTLIST"
        first_line = "Your next"
        second_line = "chapter starts here."

        selected_genres = st.session_state.saved_genres

        if selected_genres:
            genre_text = ", ".join(selected_genres)

            description = (
                "Readers who enjoyed your favourite books also enjoyed "
                "these titles. We've given extra weight to books matching "
                f"your preferred genres: {genre_text}."
            )
        else:
            description = (
                "Readers who enjoyed your favourite books also enjoyed "
                "these titles."
            )
        

    else:
        eyebrow = "VANCOUVER / BOOK DISCOVERY"
        first_line = "Find your"
        second_line = "next great read."

        description = (
            "Your favourite books. Your local library. "
            "Recommendations made for you."
        )

    # Build the hero HTML.
    html = (
        '<div class="sm-hero">'
        f'<div class="sm-eyebrow">{eyebrow}</div>'
        '<div class="sm-title" role="heading" aria-level="1">'
        f'{first_line}<br>'
        f'<span class="sm-accent">{second_line}</span>'
        '</div>'
        f'<div class="sm-description">{escape(description)}</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)



def section_heading(number, title, description):
    html = (
        '<div class="sm-section-heading">'
        f'<span class="sm-number">{escape(number)}</span>'
        '<div class="sm-section-title" role="heading" aria-level="2">'
        f'{escape(title)}</div>'
        '</div>'
        '<div class="sm-section-description">'
        f'{escape(description)}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def show_book_name(book):
    st.markdown(
        '<div class="sm-book-title">'
        f'{escape(str(book["title"]))}</div>'
        '<div class="sm-book-author">'
        f'{escape(str(book["author"]))}</div>',
        unsafe_allow_html=True,
    )


def render_vancouver_art():
    svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 720">
  <rect width="400" height="720" fill="#D9ECF4"/>
  <circle cx="305" cy="110" r="59" fill="#FFD267"/>
  <path d="M0 294 89 173 132 220 231 92 334 224 400 166
           V420H0Z" fill="#74ABB8"/>
  <path d="m172 169 59-77 65 84-43-17-22-37-26 43-13-9Z"
        fill="#F7FAF5"/>
  <path d="M0 354 77 260 148 301 245 218 331 302 400 254
           V470H0Z" fill="#23847F"/>
  <path d="M0 389 64 338 138 374 216 322 300 370 400 316
           V500H0Z" fill="#17645F"/>
  <rect y="432" width="400" height="288" fill="#147DAB"/>
  <g fill="#152C40">
    <path d="M58 439V350H84V439M92 439V316H124V439
             M134 439V367H162V439M172 439V296H204V439
             M214 439V342H244V439M253 439V323H280V439
             M289 439V371H316V439"/>
    <rect x="186" y="274" width="4" height="23"/>
  </g>
  <g fill="#FFD267">
    <rect x="100" y="332" width="5" height="8"/>
    <rect x="112" y="332" width="5" height="8"/>
    <rect x="180" y="314" width="6" height="9"/>
    <rect x="192" y="314" width="6" height="9"/>
    <rect x="180" y="334" width="6" height="9"/>
    <rect x="262" y="341" width="8" height="10"/>
    <rect x="262" y="362" width="8" height="10"/>
  </g>
  <path d="m274 447 18-52 15 52Zm25 0 24-72 17 72Z
           m29 0 21-51 17 51Z" fill="#FFF7E5"/>
  <path d="M270 450H372L357 463H281Z" fill="#152C40"/>
  <g stroke="#75BDD2" stroke-width="3">
    <path d="M29 490H146M216 509H367M82 536H230
             M24 565H117M264 559H370"/>
  </g>
  <path d="M0 610Q100 574 199 614T400 606V720H0Z"
        fill="#152C40"/>
  <g transform="translate(48 592)">
    <rect width="43" height="100" rx="2" fill="#D8323B"/>
    <rect x="49" y="-17" width="49" height="117" rx="2"
          fill="#FFD267"/>
    <rect x="104" y="12" width="35" height="88" rx="2"
          fill="#62B6B0"/>
    <rect x="145" y="-4" width="52" height="104" rx="2"
          fill="#F4F3EF"/>
    <path d="m215 4 36-9 24 98-36 9Z" fill="#D8323B"/>
    <g stroke="#152C40" stroke-width="3" opacity=".5">
      <path d="M9 15H34M9 23H34M60 1H87M60 9H87
               M155 13H187M155 21H187"/>
    </g>
  </g>
</svg>
    """
    encoded = base64.b64encode(svg.encode()).decode()

    st.markdown(
        '<div class="sm-art">'
        f'<img src="data:image/svg+xml;base64,{encoded}" '
        'alt="Illustration of Vancouver mountains, waterfront, '
        'skyline, and colourful books."></div>'
        '<div class="sm-bars" aria-hidden="true">'
        '<i></i><i></i><i></i><i></i></div>',
        unsafe_allow_html=True,
    )


def render_match_score(book, colour):
    """Display the backend's relative score without implying a probability."""
    value = book.get("match_score")
    if value is None:
        return  # Older session results may not include scores yet.
    try:
        value = float(value)
    except (TypeError, ValueError):
        return
    if not math.isfinite(value):
        return
    value = max(0.0, min(100.0, value))
    label = f"{value:.1f}".removesuffix(".0")
    # SVG keeps the ring crisp at any screen size; the text also conveys the score.
    st.markdown(
        '<div style="display:flex;align-items:center;gap:14px;margin:12px 0 18px">'
        f'<svg width="76" height="76" viewBox="0 0 76 76" role="img" '
        f'aria-label="Relative match score: {label} out of 100" style="flex-shrink:0">'
        '<circle cx="38" cy="38" r="30" fill="none" stroke="#E9EEF0" stroke-width="8"/>'
        f'<circle cx="38" cy="38" r="30" fill="none" stroke="{colour}" '
        f'stroke-width="8" pathLength="100" stroke-dasharray="{value} 100" '
        'transform="rotate(-90 38 38)"/>'
        f'<text x="38" y="42" text-anchor="middle" fill="#152C40" '
        f'font-family="sans-serif" font-size="17" font-weight="700">{label}</text>'
        '</svg><div><div style="color:#152C40;font-weight:700">Match score</div>'
        '<div style="color:#5F6D76;font-size:13px">Relative score · out of 100</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def render_result(book, position):
    colours = [
        "#147DAB",
        "#D8323B",
        "#007F79",
        "#8D4B85",
        "#A86513",
        "#244D70",
    ]
    colour = colours[position % len(colours)]
    card_key = f"shelf_result_{position}"

    st.markdown(
        f"""
<style>
.st-key-{card_key} {{
    background: #FFFFFF;
    border: 1px solid #D8DFE2 !important;
    border-top: 6px solid {colour} !important;
    border-radius: 8px !important;
    padding: 22px !important;
}}
.st-key-{card_key} h3 {{
    color: #152C40;
    font-size: 24px;
    line-height: 1.2;
    letter-spacing: -0.03em;
    padding-top: 0;
}}
.st-key-{card_key} [data-testid="stLinkButton"] a {{
    background: {colour};
    color: white !important;
    border: 1px solid {colour};
    border-radius: 5px;
    font-weight: 650;
    text-decoration: none !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )

    # All information lives inside this single container.
    with st.container(border=True, key=card_key):
        st.caption(f"RECOMMENDATION {position + 1:02d}")
        st.subheader(book["title"], anchor=False)
        st.write(book["author"])

        genres = book.get("genres", [])
        if genres:
            st.caption(" · ".join(genres))

        render_match_score(book, colour)

        st.divider()
        # The shared explanation is already shown above the result grid.

        matching_genres = [
            genre
            for genre in book.get("genres", [])
            if genre in st.session_state.saved_genres
        ]

        if matching_genres:
            st.caption(
                "Matches your preferred genres: "
                + ", ".join(matching_genres)
            )

        available = int(book.get("available_copies") or 0)
        total = int(book.get("total_copies") or 0)
        vpl_available = int(book.get("vpl_available_copies") or 0)
        branch = st.session_state.saved_branch or "Selected branch"

        if available > 0:
            status, status_class = "Available at your branch", "local"
        elif vpl_available > 0:
            status, status_class = "Available at another branch", "elsewhere"
        elif total > 0:
            status, status_class = "Currently checked out", "unavailable"
        else:
            status, status_class = "Not in this collection", "unavailable"
        st.markdown(
            f'<span class="sm-status sm-status-{status_class}">'
            f'{escape(status)}</span>',
            unsafe_allow_html=True,
        )

        # Keep HTML flush-left: indented multi-line HTML gets rendered
        # as a Markdown code block in some Streamlit versions.
        availability_html = (
            '<div class="sm-availability">'
            '<div class="sm-availability-title">Availability</div>'
            '<div class="sm-availability-row">'
            f'<span>At {escape(str(branch))}</span>'
            f'<strong>{available} available</strong>'
            '</div>'
            '<div class="sm-availability-divider"></div>'
            '<div class="sm-availability-row">'
            '<span>Across all VPL branches</span>'
            f'<strong>{vpl_available} available / {total} total</strong>'
            '</div>'
            '</div>'
        )
        st.markdown(availability_html, unsafe_allow_html=True)

        if total == 0:
            st.caption("Not in this collection.")
        elif available == 0 and vpl_available > 0:
            st.caption(
                "No copies currently available at your branch. "
                "Check the catalogue for hold options."
            )
        elif vpl_available == 0:
            st.caption(
                "All copies are currently checked out. "
                "Check the catalogue for hold options."
            )

        st.link_button(
            "View in VPL catalogue ↗",
            url=catalogue_url(book),
            use_container_width=True,
        )


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    '<div class="sm-header">'
    '<div class="sm-logo">Shelf<span>Match</span></div>'
    '<a href="https://vpl.bibliocommons.com/" '
    'target="_blank" rel="noopener noreferrer">'
    'Explore the VPL catalogue ↗</a>'
    '</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Preferences
# ------------------------------------------------------------

if st.session_state.view == "preferences":
    render_hero()

    form_column, art_column = st.columns([2.05, 1], gap="large")

    with art_column:
        render_vancouver_art()

    with form_column:
        with st.container(key="books"):
            section_heading(
                "01",
                "What books have you enjoyed?",
                f"Select at least 3 books you loved, up to {MAX_FAVOURITES}."
            )

            with st.form("book_search", border=False):
                query = st.text_input(
                    "Search by title or author",
                    placeholder="Try Project Hail Mary or Matt Haig",
                    key="book_search_query",
                )
                search_clicked = st.form_submit_button("Search books")

            if search_clicked:
                st.session_state.search_results = []
                st.session_state.search_complete = False

                if len(query.strip()) < 3:
                    st.warning("Enter at least three characters.")
                else:
                    try:
                        with st.spinner("Searching books…"):
                            matches = search_books(query)

                        st.session_state.search_results = list({
                            book["id"]: book for book in matches
                        }.values())
                        st.session_state.search_complete = True
                    except Exception:
                        logger.exception("Book search failed")
                        st.error(
                            "Book search is unavailable. Please try again."
                        )

            if (
                st.session_state.search_complete
                and not st.session_state.search_results
            ):
                st.info("No books found. Try another title or author.")

            for book in st.session_state.search_results:
                title_column, button_column = st.columns([4, 1])

                with title_column:
                    show_book_name(book)

                with button_column:
                    added = (
                        book["id"] in st.session_state.favourites
                    )
                    st.button(
                        "Added" if added else "Add",
                        key=f"add_{book['id']}",
                        disabled=(
                            added
                            or len(st.session_state.favourites) >= MAX_FAVOURITES
                        ),
                        on_click=add_favourite,
                        args=(book,),
                        use_container_width=True,
                    )

            count = len(st.session_state.favourites)
            st.markdown(f"**Your favourites · {count}/{MAX_FAVOURITES}**")
            st.progress(count / MAX_FAVOURITES)
            if 0 < count < 3:
                remaining = 3 - count
                st.caption(f"Add {remaining} more to get recommendations.")
            elif count >= MAX_FAVOURITES:
                st.caption(
                    f"You’ve selected {MAX_FAVOURITES} books. Your reading list is ready. "
                    "Remove a book if you’d like to add another."
                )
            elif count >= 3:
                st.caption(
                    "Your reading list is ready. "
                    f"You can add more favourites, up to {MAX_FAVOURITES} in total."
                )

            if count == 0:
                st.caption("Search above to start your list.")

            for book_id, book in list(
                st.session_state.favourites.items()
            ):
                with st.container(border=True):
                    name_column, remove_column = st.columns([4, 1])

                    with name_column:
                        show_book_name(book)

                    with remove_column:
                        st.button(
                            "Remove",
                            key=f"remove_{book_id}",
                            on_click=remove_favourite,
                            args=(book_id,),
                            use_container_width=True,
                        )

        with st.container(key="genres"):
            section_heading(
                "02",
                "What are you in the mood for?",
                "Choose up to three genres, or skip.",
            )

            if "genre_widget" not in st.session_state:
                st.session_state.genre_widget = deepcopy(
                    st.session_state.saved_genres
                )

            st.multiselect(
                "Preferred genres",
                GENRES,
                max_selections=3,
                placeholder="Any genre",
                key="genre_widget",
                on_change=save_preference,
                args=("genre_widget", "saved_genres"),
                label_visibility="collapsed",
            )

        with st.container(key="branch"):
            section_heading(
                "03",
                "Where would you like to borrow from?",
                "Choose your Vancouver Public Library branch.",
            )

            if "branch_widget" not in st.session_state:
                st.session_state.branch_widget = (
                    st.session_state.saved_branch
                )

            st.selectbox(
                "Library branch",
                BRANCHES,
                index=None,
                placeholder="Select a branch",
                key="branch_widget",
                on_change=save_preference,
                args=("branch_widget", "saved_branch"),
                label_visibility="collapsed",
            )

        with st.container(key="priority"):
            section_heading(
                "04",
                "What matters most?",
                "Choose between local convenience, VPL-wide availability, or the strongest matches.",
            )

            if "priority_widget" not in st.session_state:
                st.session_state.priority_widget = (
                    st.session_state.saved_priority
                )

            st.radio(
                "Recommendation priority",
                [
                    "Available at My Branch",
                    "Available Anywhere in VPL",
                    "Best Matches",
                ],
                horizontal=False,
                key="priority_widget",
                on_change=save_preference,
                args=("priority_widget", "saved_priority"),
                label_visibility="collapsed",
            )

        missing_steps = []
        if len(st.session_state.favourites) < 3:
            missing_steps.append("select at least three favourite books")
        if not st.session_state.saved_branch:
            missing_steps.append("choose your branch")
        if missing_steps:
            st.caption("To continue, " + " and ".join(missing_steps) + ".")

        if st.button(
            "Find my next read →",
            type="primary",
            use_container_width=True,
        ):
            if len(st.session_state.favourites) < 3:
                st.error("Select at least three favourite books.")

            elif not st.session_state.saved_branch:
                st.error("Choose a library branch.")

            else:
                favourites = list(st.session_state.favourites.values())
 
                priority_map = {
                    "Available at My Branch": "available",
                    "Available Anywhere in VPL": "any_available",
                    "Best Matches": "best_matches",
                }

                priority = priority_map[
                    st.session_state.saved_priority
                ]


                try:
                    with st.spinner("Finding your next reads…"):
                        results = get_recommendations(
                            favourites=favourites,
                            genres=st.session_state.saved_genres,
                            branch=st.session_state.saved_branch,
                            priority=priority,
                        )
                except Exception:
                    logger.exception("Recommendation request failed")
                    st.error(
                        "Recommendations are unavailable. "
                        "Your selections have been kept. Please try again."
                    )
                else:
                    st.session_state.recommendations = results
                    st.session_state.view = "results"
                    st.rerun()

        if DEMO_MODE:
            st.caption(
                "Demo mode: sample book search and fixed example results."
            )


# ------------------------------------------------------------
# Results
# ------------------------------------------------------------

else:
    back_column, reset_column = st.columns([3, 1])

    with back_column:
        if st.button("← Edit my preferences"):
            st.session_state.view = "preferences"
            st.rerun()

    with reset_column:
        st.button(
            "Start over",
            on_click=start_over,
            use_container_width=True,
        )

    render_hero(results=True)
    st.info(
            "Library holdings and availability are simulated "
            "for this prototype, not live VPL data. "
            "Check the catalogue before visiting."
        )

    with st.expander("Your selected favourites", expanded=False):
        for favourite in st.session_state.favourites.values():
            show_book_name(favourite)

    branch_column, priority_column = st.columns(2)

    with branch_column:
        st.markdown("**Your branch**")
        st.write(st.session_state.saved_branch)

    with priority_column:
        st.markdown("**Your priority**")
        st.write(st.session_state.saved_priority)

    if st.session_state.saved_genres:
        st.caption(
            "Preferred genres: "
            + " · ".join(st.session_state.saved_genres)
        )

    if DEMO_MODE:
        st.info(
            "Demo preview: these are fixed example recommendations. "
            "Personalised matching and branch availability "
            "are not connected yet."
        )

    recommendations = st.session_state.recommendations

    if not recommendations:
        st.warning(
            "No recommendations were returned. "
            "Try Best Matches to include books that are currently checked out, "
            "or choose different favourite books."
        )

        if st.button("Change preferences"):
            st.session_state.view = "preferences"
            st.rerun()

    else:
        st.caption(f"{len(recommendations)} books to explore")
        st.caption(
            "Match scores compare these results with your strongest overall match (100), before availability filtering. "
            "They include your genre preferences and aren’t a percentage chance you’ll like a book."
        )

        for start in range(0, len(recommendations), 3):
            columns = st.columns(3, gap="medium")

            for offset, book in enumerate(
                recommendations[start:start + 3]
            ):
                with columns[offset]:
                    render_result(book, start + offset)


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.markdown(
    '<div class="sm-footer">'
    '<strong>Shelf<span>Match</span></strong>'
    '<span>An independent project for Vancouver readers.<br>'
    'Not affiliated with or endorsed by Vancouver Public Library.'
    '</span></div>',
    unsafe_allow_html=True,
)