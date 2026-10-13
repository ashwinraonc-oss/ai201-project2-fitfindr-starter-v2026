"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # Criterion 1's own "why this target" is about PHRASING variance —
        # a real request can describe a listing that exists without sharing
        # enough literal words with it for the keyword-overlap scorer to find
        # it. The "before" run tested this with the same query five times,
        # which search_listings answers identically every time since it's
        # deterministic — so it never actually exercised that risk. These
        # five are different real phrasings of the same findable item
        # (a vintage/band/retro graphic tee under $30); each one was checked
        # against search_listings directly before going in here, so a FAIL
        # means the phrasing genuinely didn't score, not that nothing in the
        # data could have matched it.
        "name": "matching query completes (5 different phrasings)",
        "query": [
            "vintage graphic tee under $30",
            "band tee under $30",
            "retro graphic shirt under $30",
            "80s or 90s style graphic t-shirt under $30",
            "faded vintage band t-shirt under $30",
        ],
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Criterion 3: the id in session["selected_item"] has to match the id
        # actually received by suggest_outfit and by create_fit_card. Any
        # matching query works here — what's being checked is what moves
        # through the session, not what the user typed.
        "name": "item id matches across every tool",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4: five real tries on the SAME item, cache off (run_eval.py
        # forces that), checking the five fit cards aren't word-for-word
        # identical and every one still names the price and platform.
        "name": "fit card varies without losing price or platform",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    # Criterion 5 ("A missing model stays recoverable") isn't in this file.
    # It needs GEMINI_API_KEY to be wrong for exactly its five tries, and
    # generate.py caches its model client in a module-level global once a
    # call succeeds — so breaking the key mid-run here would either leak into
    # whichever other scenario runs next in the same process, or get silently
    # ignored if a good client was already cached from an earlier scenario.
    # It's measured on its own with scripts/criterion5_model_unavailable.py
    # instead, which breaks the key, runs 5 tries in a fresh subprocess each
    # time, and restores the key — see the README for that run's real output.
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        query = scenario.get("query")
        # A scenario's query is usually one string, repeated every try. It can
        # also be a list of strings — one per try, see run_eval.py::run_once —
        # for a criterion that's actually about phrasing, not about the branch.
        if isinstance(query, list):
            if not query or any(not q.strip() for q in query):
                problems.append(f"scenario {i} has an empty query in its list")
        elif not (query or "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
