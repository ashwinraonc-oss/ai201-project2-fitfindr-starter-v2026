# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the local listings data for items matching free-text keywords, optionally filtered down by size and a maximum price.
- **Inputs:** `description` (str) — keywords describing what the user wants, e.g. `"vintage graphic tee"`. `size` (str or None) — a size to filter by, or `None` to skip size filtering (see the size-match rule below). `max_price` (float or None) — an inclusive price ceiling, or `None` to skip price filtering.
- **Returns:** A list of listing dicts, best keyword match first, at most `config.SEARCH_RESULT_LIMIT` (10) of them. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list[str]), `size`, `condition`, `price` (float), `colors` (list[str]), `brand` (str or None), `platform`.
- **When it has nothing:** Returns `[]` — an empty list, never `None`, never an exception.

**Size-match rule** (decided now, not left to the implementation): normalize both the listing's `size` and the query's `size` by lowercasing and dropping any parenthetical note (`"XL (oversized)"` → `"xl"`). Split the normalized listing size on `"/"` into candidate tokens (`"S/M"` → `["s", "m"]`), and additionally extract the bare number from a unit-prefixed size as a second candidate (`"US 8"` → `["us 8", "8"]`, `"W30"` → `["w30", "30"]`). A match requires the normalized query to be **exactly equal** to one of those candidates — never a substring check, because `"s" in "us 9"` and `"l" in "xl"` are both true and both wrong. `"One Size"` variants only match a query that itself normalizes to some form of "one size."

### `suggest_outfit`

- **What it does:** Given one thrifted listing and the user's wardrobe, asks the model for one or two outfit combinations that use that item.
- **Inputs:** `new_item` (dict) — a listing dict, the item under consideration. `wardrobe` (dict) — `{"items": [...]}`; the items list may be empty.
- **Returns:** A non-empty string with the model's outfit suggestion(s). When the wardrobe is non-empty, the string names specific wardrobe items by their `name` field rather than describing them generically.
- **When it has nothing:** When `wardrobe["items"]` is empty, returns general styling advice for the item on its own — still a non-empty string, never `""` and never an exception.

### `create_fit_card`

- **What it does:** Writes a short caption, in the voice of someone posting the find, combining the listing's details with the suggested outfit.
- **Inputs:** `outfit` (str) — the string returned by `suggest_outfit()`. `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence caption string that mentions the item, its price, and its platform exactly once each.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns the literal string `"Can't write a caption without an outfit to describe — suggest_outfit needs to run first."` rather than raising or returning `""`.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names what the user could change (e.g. "No listings matched — try a higher max price or a different size"), and stop — return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise, take `search_results[0]` as `selected_item` and continue on to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex (`agent.py::_parse_query`). A price like `under $30` / `$30` / `under 30` becomes `max_price`; `size <token>` becomes `size`; whatever is left is the `description`. No model call.

**What moves through the session:** `parsed` → `search_results` → `selected_item` (first result) → `outfit_suggestion` → `fit_card`. Each stage reads its inputs back out of the session; `error` is set (and the loop returns) if the search is empty.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

<!-- Added once the planning loop is built (Milestone 3's loop step) — the
     three tools below are tested standalone first, per the brief. -->

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', ...}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', ...}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', ...}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', ...}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', ...}]
```

6 results, all under $30, highest keyword-overlap score first. `lst_011` (cargo pants) is the weakest match — it only shares the token "tee" with the query, from "...layering with a long tee" in its description — which is the plain-keyword-overlap limitation criterion 1 in `criteria.md` names.

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two specific outfit ideas using the vintage Levi's 501 jeans and pieces from your existing wardrobe:

Outfit 1: Effortless Streetwear Minimal
- Bottoms: Vintage Levi's 501 Jeans ($38.00)
- Top: White ribbed tank top
- Outerwear: Oversized grey crewneck sweatshirt
- Shoes: Chunky white sneakers
- Accessories: Black crossbody bag

Outfit 2: Vintage Grunge Edge
- Bottoms: Vintage Levi's 501 Jeans ($38.00)
- Top: Black cropped zip hoodie
- Outerwear: Vintage black denim jacket
- Shoes: Black combat boots
- Accessories: Brown leather belt
```

Also tested with `get_empty_wardrobe()` in place of `get_example_wardrobe()` to hit the empty-case branch:

```
Pair these vintage Levi's 501s with a tucked-in graphic tee and a leather jacket for an effortless, classic streetwear look. Alternatively, dress them up with an oversized button-down shirt and loafers or retro sneakers to balance the relaxed medium-wash denim.
```

Non-empty general advice, no wardrobe pieces named — no crash, no empty string.

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Still screaming that I actually scored these vintage Levi's 501 jeans on Depop for only $38.00! The medium wash has that perfectly broken-in, 90s indie sleaze fade that you just can't fake. Throwing them on with some fresh white sneakers and calling it my entire personality for the foreseeable future.
```

Ran it three times on the same item to check for the identical-output trap the brief warns about. With the cache left on (the default), runs 2 and 3 came back **word-for-word identical** to run 1 — expected, since `TEMPERATURE` is 0.9 (not the other suspect) and an identical prompt reused the cached answer. Calling `generate.clear_cache()` between each of the three calls instead gave three genuinely different captions, each still naming the item, `$38.00`, and Depop exactly once:

```
Still screaming that I actually scored these vintage Levi's 501 jeans on Depop for only $38.00! The wash is that *exact* lazy-Sunday-morning blue that literally goes with everything. Honestly can't wait to throw them on with my beat-up white sneakers for the ultimate effortless 90s off-duty look.

Still not over scoring these vintage Levi's 501 jeans for just $38 on Depop! The medium wash has that *exact* broken-in 90s slouch I've been hunting for forever. Honestly about to live in these with my beat-up white sneakers all season.

Found the holy grail of denim today on depop and my life is officially complete. These vintage Levi's 501 jeans in the absolute dreamiest medium wash were only $38.00, which feels like an absolute steal. I'm already planning to live in them with my go-to white sneakers all through autumn.
```

Also tested the empty-outfit guard:

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('   ', load_listings()[0]))"

Can't write a caption without an outfit to describe — suggest_outfit needs to run first.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
