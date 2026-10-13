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

You tell FitFindr what you're looking for, like "vintage graphic tee under $30, size M", and it searches a pile of secondhand listings for the best match. Then it suggests an outfit or two that uses the item with stuff already in your wardrobe (or just general styling ideas if you haven't added any). Last, it writes a short caption you could post about the find, with the item, price and platform in it. If nothing matches, it stops there and tells you what to change, like the price, size or keywords.



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

- **What it does:** Looks through the local listings for items that match some keywords, and can also filter by size and max price.
- **Inputs:** `description` (str) — what the user wants, e.g. `"vintage graphic tee"`. `size` (str or None) — a size to filter on, or `None` for any size (rule below). `max_price` (float or None) — the most they'll pay, inclusive, or `None` for no limit.
- **Returns:** A list of listing dicts, best keyword match first, capped at `config.SEARCH_RESULT_LIMIT` (10). Each dict has `id`, `title`, `description`, `category`, `style_tags` (list[str]), `size`, `condition`, `price` (float), `colors` (list[str]), `brand` (str or None), `platform`.
- **When it has nothing:** Returns `[]` — an empty list, never `None`, never an exception.

**Size-match rule:** Lowercase both sizes and drop any parenthetical (`"XL (oversized)"` → `"xl"`). Split the listing size on `"/"` so `"S/M"` gives `s` and `m`, and also pull out any number so `"US 8"` gives `us 8` and `8`, and `"W30"` gives `w30` and `30`. The query size has to exactly equal one of those. I don't use a substring check because `"s" in "us 9"` and `"l" in "xl"` are both true, and both would be wrong. "One Size" listings only match a query that also says one size.

### `suggest_outfit`

- **What it does:** Takes one listing and the user's wardrobe and asks the model for one or two outfits using that item.
- **Inputs:** `new_item` (dict) — a listing dict, the item they're thinking of buying. `wardrobe` (dict) — `{"items": [...]}`; the items list may be empty.
- **Returns:** A non-empty string with the model's outfit suggestions. If the wardrobe has items, it names them by their `name` field instead of describing them generically.
- **When it has nothing:** If `wardrobe["items"]` is empty, it returns general styling advice for the item instead. Still a non-empty string, never `""`, never an exception.

### `create_fit_card`

- **What it does:** Writes a short caption like someone posting their find, using the listing details and the suggested outfit.
- **Inputs:** `outfit` (str) — the string from `suggest_outfit()`. `new_item` (dict) — the listing dict for the item.
- **Returns:** A caption of two to four sentences that mentions the item, price and platform once each.
- **When it has nothing:** If `outfit` is empty or just whitespace, it returns the string `"Can't write a caption without an outfit to describe — suggest_outfit needs to run first."` instead of raising or returning `""`.

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

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that says what the user could change (max price, size or keywords, built by `_no_results_message`) and return the session right away. `suggest_outfit` and `create_fit_card` never get called, so `session["fit_card"]` stays `None`. Otherwise take `search_results[0]` as `selected_item`, then run `suggest_outfit`, then `create_fit_card`. — `agent.py::run_agent`

**Where it lives:** `agent.py::run_agent`, in the `if not session["search_results"]:` check right after the `search_listings` call.

**How the query is parsed:** Regex, in `agent.py::_parse_query`. Something like `under $30`, `$30` or `under 30` becomes `max_price`, `size M` becomes `size`, and whatever's left is the `description`. No model call.

**What moves through the session:** `parsed` → `search_results` → `selected_item` (first result) → `outfit_suggestion` → `fit_card`. Each step reads its inputs back out of the session instead of taking them from the last call. If the search comes back empty, `error` gets set and the loop returns.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'


  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two outfit suggestions pairing the Y2K Butterfly Baby Tee with pieces already in your wardrobe:

**Outfit 1: Casual Streetwear Contrast**
* **Top:** Y2K Butterfly Baby Tee
* **Bottoms:** Baggy straight-leg jeans (dark wash)
* **Outerwear:** Black cropped zip hoodie (worn open or draped over the shoulders)
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag
* *Why it works:* The fitted, ultra-feminine silhouette of the baby tee balances out the relaxed, low-slung vibe of the baggy dark wash jeans. Adding the cropped zip hoodie and chunky white sneakers leans hard into a balanced Y2K streetwear aesthetic.

**Outfit 2: Soft Earth-Tone Contrast**
* **Top:** Y2K Butterfly Baby Tee
* **Bottoms:** Wide-leg khaki trousers
* **Accessories:** Brown leather belt
* **Shoes:** Chunky white sneakers (or black combat boots if you want an edgy twist)
* *Why it works:* The pink and purple tones in the butterfly print pop nicely against the neutral khaki trousers. Tucking the baby tee in with the brown leather belt pulls the look together, blending a cute Y2K top with minimal, earthy staples.

  Fit card: I am still not over scoring this dreamy butterfly print Y2K baby tee on Depop for just $18. It seriously gives off the exact right amount of early 2000s mall-goth nostalgia. Can't wait to style it with some baggy denim for the ultimate off-duty look!

0 model calls this session, 2 served from cache
```

The item it picked is the first search result, and the outfit text is about that same item. The last line says the answers came from cache, so I'd run it again with the cache off for a fresh one.

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', ...}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', ...}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', ...}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', ...}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', ...}]
```

6 results, all under $30. The cargo pants (`lst_011`) are the weakest match, since they only share the word "tee" with my query, from "layering with a long tee" in the description. That's the keyword-overlap problem I mention in criterion 1.

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

Same command with `get_empty_wardrobe()` to hit the empty case:

```
Pair these vintage Levi's 501s with a tucked-in graphic tee and a leather jacket for an effortless, classic streetwear look. Alternatively, dress them up with an oversized button-down shirt and loafers or retro sneakers to balance the relaxed medium-wash denim.
```

It gives general advice and doesn't name any wardrobe pieces. No crash and no empty string.

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Still screaming that I actually scored these vintage Levi's 501 jeans on Depop for only $38.00! The medium wash has that perfectly broken-in, 90s indie sleaze fade that you just can't fake. Throwing them on with some fresh white sneakers and calling it my entire personality for the foreseeable future.
```

I ran it three times on the same item to check for identical outputs. With the cache on (the default), runs 2 and 3 came back word-for-word identical to run 1. `TEMPERATURE` is already 0.9, so it was the cache returning the same answer for the same prompt. With the cache cleared between calls I got three different captions, and each one still has the item, `$38.00` and Depop once:

```
Still screaming that I actually scored these vintage Levi's 501 jeans on Depop for only $38.00! The wash is that *exact* lazy-Sunday-morning blue that literally goes with everything. Honestly can't wait to throw them on with my beat-up white sneakers for the ultimate effortless 90s off-duty look.

Still not over scoring these vintage Levi's 501 jeans for just $38 on Depop! The medium wash has that *exact* broken-in 90s slouch I've been hunting for forever. Honestly about to live in these with my beat-up white sneakers all season.

Found the holy grail of denim today on depop and my life is officially complete. These vintage Levi's 501 jeans in the absolute dreamiest medium wash were only $38.00, which feels like an absolute steal. I'm already planning to live in them with my go-to white sneakers all through autumn.
```

And the empty-outfit guard:

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('   ', load_listings()[0]))"

Can't write a caption without an outfit to describe — suggest_outfit needs to run first.
```

---

## How I Used AI

1. Building run_agent. I gave Claude the branch rule and asked for the loop. It wrote the session-driven loop, a regex parser, and the early return on an empty search.
2. Identical fit cards. I asked Claude to run create_fit_card three times, and all three captions came back identical. Claude checked config.py, saw TEMPERATURE was already 0.9, and reran with the cache off to get three different captions.
3. The MCP move. I asked Claude to move search_listings onto MCP and point the agent at it. It wrote the tool's description and typed inputs straight from the Tool Inventory, checked the registration with mcp_client.py before touching agent.py at all, then swapped the direct call for the MCP one.
4. The model-unavailable failure didn't actually fail safely. I asked Claude to trigger all three failure modes on purpose, including a broken API key. It found that a bad key crashed the whole process (exit code 1) instead of returning a usable session — app.py's catch-all kept it from printing a raw traceback, but the program still died. Claude added a try/except around the two model-calling steps in run_agent.
5. Criterion 1's "before" test wasn't testing what it claimed to. While scoring the Run Log, Claude pointed out that criterion 1's scenario sent the identical query five times, so it never exercised the phrasing-miss risk its own "why this target" argument in criteria.md was about, despite scoring 5/5. I had it extend run_eval.py so a scenario can cycle through five different phrasings instead, and used that as this unit's one improvement.



**Moment 1**

- *What I asked for:* I asked Claude to test `create_fit_card` three times on the same item and tell me if the outputs were identical.
- *What came back:* All three captions were word-for-word the same. Claude checked `config.py` and saw `TEMPERATURE` was already 0.9, so it wasn't that. It reran the three calls with `AI201_CACHE=0` and got three different captions, which pointed at the cache returning the same answer for the same prompt.
- *What I changed:* No code. I left the cache on while building and wrote up in the Sample Run that the cache was the cause, not the temperature. Evaluation runs turn it off.

**Moment 2**

- *What I asked for:* I gave Claude my branch rule from the Tool Inventory and asked it to fill in `run_agent()`, with every tool result going into the session and read back out for the next call.
- *What came back:* A loop that checks the session each pass to decide the next step, a regex `_parse_query` for price and size, and an early return with an error message when `search_listings` comes back empty. I ran the happy path and checked that `selected_item` was `lst_002`, the same item `suggest_outfit` wrote about. The "designer ballgown size XXS under $5" query left `fit_card` as `None` and returned a message about the price, size and keywords.
- *What I changed:* The code worked as written, but the first README text for the branch rule didn't match it exactly, so I updated it to name `_no_results_message` and the `if not session["search_results"]` check.

**Moment 3 (unit 4)**

- *What I asked for:* I asked Claude to trigger each of the three failure modes on purpose — empty search, empty wardrobe, and a broken API key — and write down what the agent actually said each time.
- *What came back:* The first two were already handled correctly. The third wasn't: breaking one character of `GEMINI_API_KEY` and running a query made the whole process exit with code 1. `app.py`'s top-level catch kept it from printing a raw Python traceback, but the run still died instead of producing a usable session.
- *What I changed:* Claude added a `try/except ModelUnavailable` around the `suggest_outfit` and `create_fit_card` calls in `run_agent`, writing a readable message into `session["error"]` and returning the session normally instead of letting the exception kill the process. Retested with the same broken key — clean exit, then restored the real key.

**Moment 4 (unit 4)**

- *What I asked for:* I asked Claude to score my five criteria against the Run Log output and fill in Verdicts and Diagnoses.
- *What came back:* Everything scored MET, but Claude flagged two things I hadn't caught myself. First, criterion 3's claim that it's "checked from the trace" doesn't actually hold — `trace.py`'s summary collapses a tool's inputs down to `"dict with keys: new_item, wardrobe_items"`, never showing the `id`, so it verified that criterion with a separate instrumented run instead of citing the trace as proof. Second, criterion 1's scenario repeated the exact same query five times, so despite scoring 5/5 it never actually tested the phrasing-miss risk criterion 1's own justification is about.
- *What I changed:* I had Claude fix the second issue as this unit's one allowed improvement: it added list-of-queries support to `run_eval.py`/`scenarios.py` and rewrote criterion 1's scenario to use five different, pre-verified phrasings, then reran the eval. The verdict didn't change (still 5/5), but the evidence behind it is now real.

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
| 1. Matching query completes all three tools, returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item`'s id matches the id every later tool actually received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. 5 fit cards on the same item differ from each other, every one keeps the price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. A broken API key returns a readable `session["error"]` instead of crashing | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Scenarios for 1, 2, 3, and 4 are defined in `scenarios.py` and run by
`run_eval.py::main` → `agent.py::run_agent`, five tries each, caching off.
Criterion 5 can't go through that same harness: `generate.py` caches its
model client in a module-level global after the first successful call, so
breaking `GEMINI_API_KEY` partway through the same process would either leak
into whichever scenario ran next, or get silently ignored if a working
client was already cached. It's measured on its own by
`scripts/criterion5_model_unavailable.py`, which runs each of its five tries
in a fresh subprocess with the key overridden only in that subprocess's
environment — the real key in `.env` is never read or touched.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

Criterion 1, try 1 — produced by `agent.py::run_agent`, logged by
`run_eval.py::run_once` into `results/run_2026-10-13_1518_before.md`:

```
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)

Fit card:
Still not over finding this butterfly print Y2K baby tee on Depop for just $18! It's giving major early-2000s mall rat energy, and I am so ready to live out my ultimate Y2K pop star fantasy.
```

Criterion 2, try 1 — produced by `agent.py::run_agent`'s branch (the `if not
session["search_results"]` check), same file:

```
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

stopped early: yes — No listings matched your search. You could raise your max price above $5, try a different size than XXS or drop the size, or use broader or different keywords than "designer ballgown".
```

Criterion 3 — the trace's own `_short()` summary collapses a tool's `inputs`
dict down to `"dict with keys: new_item, wardrobe_items"`, which doesn't
actually show the id, so I checked it directly instead of trusting the
trace text. This is real output from a one-off instrumented run (not saved
under `results/`, since `run_eval.py` doesn't capture it this way) that
monkeypatches `tools.suggest_outfit` and `tools.create_fit_card` to record
the `id` of the `new_item` they're actually called with, run through
`agent.py::run_agent` five times on the "90s track jacket" scenario:

```
try 1: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 2: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 3: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 4: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 5: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
```

Criterion 4, try 1 and try 5 — produced by `tools.py::create_fit_card`, same
item (`lst_002`, $18.0, depop) both times, logged in
`results/run_2026-10-13_1518_before.md`:

```
Try 1: Still screaming about finding this Y2K Baby Tee — Butterfly Print on depop for only $18.00! It's giving major model-off-duty energy, and I am so ready to style it with baggy denim and combat boots. My inner 2000s pop star could never.

Try 5: Found the holy grail on Depop today—this Y2K butterfly baby tee for only $18! I'm so obsessed with the cute little graphic and already planning a million baggy denim fits around it. Truly living out my early 2000s pop star dreams. 🦋✨
```

Different wording both times, and both name the price (`$18.00` / `$18`)
and the platform (`depop` / `Depop`).

Criterion 5, try 1 — produced by `scripts/criterion5_model_unavailable.py`,
calling `agent.py::run_agent` with `GEMINI_API_KEY` overridden to a broken
value in the subprocess environment only:

```
session['error']:            "Couldn't reach the model to suggest an outfit: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com."
session['outfit_suggestion']: None
session['fit_card']:          None
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
| 1 | Matching query completes all three tools, returns a fit card | 4 of 5 | MET | 5 of 5 tries completed — `stopped early: no` on every try, a fit card present every time. 5 clears the 4-of-5 target with room, so it holds. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET | 5 of 5 tries stopped early with the "no listings matched" message, 0 model calls each time (confirmed by the trace being 2 steps long, not 5). The target is 5 of 5 exactly, and 5 is what I got. |
| 3 | `selected_item`'s id matches the id every later tool actually received | 5 of 5 | MET | 5 of 5 — checked by instrumenting `tools.suggest_outfit` and `tools.create_fit_card` directly rather than trusting the trace's shortened summary (see Run Log above), since the trace alone doesn't show the id. All three ids agreed on every try. |
| 4 | 5 fit cards on the same item differ from each other, every one keeps the price and platform | 5 of 5 | MET | Read all 5 captions by eye: no two are word-for-word identical, and every one names `$18` or `$18.00` and `depop`/`Depop`. 5 of 5 against a 5-of-5 target. |
| 5 | A broken API key returns a readable `session["error"]` instead of crashing | 5 of 5 | MET | 5 of 5 from `scripts/criterion5_model_unavailable.py` — every try returned a non-empty `session["error"]` naming what broke, with `outfit_suggestion` and `fit_card` both still `None`, no crash. |

**Diagnoses**

I missed nothing — all five criteria held at their target, with four of the five landing at a clean 5/5. There's nothing to diagnose by tool, branch, session, or model output, because nothing failed.

That's not the same as every target being well-set, though. Four of the five I'd defend as genuinely tested: criteria 2, 3, and 5 each check a plain code path (a branch, a variable assignment, an exception handler) that has no real reason to vary try to try, so 5/5 there is the right bar and meeting it is real evidence. Criterion 4 forces five actual, independent model calls on temperature 0.9 — a real chance to fail each time — and it held.

**Criterion 1 is the one I'd tighten, and the test is weaker than the number suggests.** The "why this target" I wrote in `criteria.md` was: *"my search is a plain keyword-overlap scorer, and a real phrasing can describe a listing that exists without sharing enough literal words with it — one miss in five realistic phrasings is a limitation of keyword matching, not a loop bug."* That's an argument about phrasing variance. But the scenario I actually wrote for it in `scenarios.py` sends the exact same query string, `"vintage graphic tee under $30"`, all five times. `search_listings` is deterministic — same query in, same ranked list out — so all five tries necessarily take the identical path through the branch; the only thing that could have varied between tries at all was `suggest_outfit` and `create_fit_card`'s wording, not whether search found anything. 5/5 here is real evidence that the model calls complete reliably, but it is **not** evidence for the thing the target's own justification is about — whether different realistic phrasings of the same request still find the item. I'd tighten this by replacing the single repeated query with five different phrasings of a request the data can satisfy (e.g. "band tee under $30", "graphic shirt, vintage, under $30", "cheap vintage graphic tee") and re-measure against those, which is the test the 4-of-5 target was actually written to describe.



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
$ python app.py ask 'vintage graphic tee under $30' --trace

[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: results found, continuing
[3] select_item
      in:  dict with keys: candidates
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    took the first result
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe_items
      out: Here are two outfit ideas that pair the new Y2K Butterfly Baby Tee with pieces from your existing wardrobe: …
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Obsessed with this Y2K butterfly baby tee I just scored on depop for only $18! The pastel pink and purple prin…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
  Outfit:   (two full outfit suggestions, pairing the tee with wardrobe pieces)
  Fit card: Obsessed with this Y2K butterfly baby tee I just scored on depop for only $18! ...

2 model calls this session, 750 prompt + 389 output tokens
```

**Empty search**

```
$ python app.py ask 'nonexistent designer ski suit size XXXL under $2' --trace

[1] parse_query
      in:  nonexistent designer ski suit size XXXL under $2
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

  No listings matched your search. You could raise your max price above $2, try a different size than XXXL or drop the size, or use broader or different keywords than "nonexistent designer ski suit".

0 model calls this session
```

Two steps instead of five, and it stops before `suggest_outfit` ever runs — 0 model calls confirms the branch actually short-circuits rather than just printing a different message at the end.

**On the MCP move:** `agent.py::run_agent` now calls `mcp_client.call_tool("search_listings", {...})` instead of importing and calling `tools.search_listings` directly (the direct import was removed from `agent.py`'s imports). The trace step is labeled `search_listings (via MCP)` so the MCP call is visible in the trace itself, not just inferred. Nothing behaved differently after the rewire: the same query returns the same item, same outfit, same fit card as the direct call did in unit 3 — confirmed by diffing the two runs' output before and after the swap.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

Not the agent — the *test* for criterion 1. `scenarios.py`'s "matching query completes" scenario sent the identical string, `"vintage graphic tee under $30"`, all five tries. `search_listings` is deterministic, so all five tries necessarily took the same path through the branch; nothing about whether different phrasings of the same request still find the item was ever actually exercised. I added support in `run_eval.py::run_once` / `_query_for_try` for a scenario's `"query"` to be a list of five strings instead of one repeated string — each try now gets a different one, cycling through the list — and changed criterion 1's scenario to five different real phrasings of the same findable item (`"band tee under $30"`, `"retro graphic shirt under $30"`, etc.), each checked against `search_listings` directly beforehand so a FAIL would mean the phrasing genuinely didn't score, not that nothing in the data could have matched it. `agent.py` and `tools.py` are untouched.

**Which failure it was meant to fix:**

Not a failure in the agent — nothing in the "before" run missed. It fixes a failure in the *measurement*: criterion 1's own "why this target" argument (in `criteria.md`) is specifically about keyword-overlap search missing on phrasing, and the "before" scenario didn't test that claim at all. This follows directly from the Diagnoses section above, where I named this as the one criterion I'd tighten.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes, 5 *different* phrasings | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged |
| 3. `selected_item`'s id matches every tool it reaches | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged |
| 4. 5 fit cards on the same item differ, keep price/platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged |
| 5. Broken key returns readable `session["error"]` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged, not rerun |

Full log: `results/run_2026-10-13_1528_after.md`, produced by `run_eval.py::main`. Criteria 2–4 used the same scenarios as "before" and came out identical, as expected — nothing about them changed. Criterion 5 isn't part of this harness (see the note under Run Log — Before) and nothing about it changed either, so I didn't re-run `scripts/criterion5_model_unavailable.py` — there was no new input to feed it.

Criterion 1, the actual new data — five different queries, five different results:

```
Try 1 — query: vintage graphic tee under $30             -> Y2K Baby Tee — Butterfly Print ($18.0, depop)
Try 2 — query: band tee under $30                        -> Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
Try 3 — query: retro graphic shirt under $30             -> Y2K Baby Tee — Butterfly Print ($18.0, depop)
Try 4 — query: 80s or 90s style graphic t-shirt under $30 -> Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
Try 5 — query: faded vintage band t-shirt under $30      -> Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
```

All five completed (`stopped early: no` on every try), picking two different real items depending on phrasing rather than the same one five times.

**Did it help, and how do I know:**

It didn't change the verdict — criterion 1 was MET before (5/5 on the weak test) and is still MET after (5/5 on the stronger one). If I only looked at the Verdict column, I'd say nothing happened.

But that's not really true, and the difference is visible in the row above it: before, the "5/5" was five identical runs of one query that could only have failed by chance (an API hiccup), because `search_listings` always returns the same ranked list for the same input. After, it's five runs of five different real phrasings, landing on two different items depending on which words were used — meaning the keyword-overlap scorer really was being tested against the thing criterion 1's own justification worried about, and it happened to clear all five anyway. So the improvement didn't fix a broken result; it replaced a number I couldn't actually trust with one I can. That's worth reporting plainly rather than as a bigger win than it was: the system's behavior didn't change at all, only my evidence for it did.



---

## What's Still Broken

No criterion is MISSED, before or after, so there's no per-criterion fix list to write here. That's not the same as nothing being left — these are the real gaps I know about that none of the five criteria happen to name:

- **The keyword-overlap scorer still surfaces weak matches, not just the right one.** Scoring against title + description + style_tags + brand + category equally means a single incidental word shared with an unrelated field counts the same as a real match — e.g. a cargo-pants listing scored against "graphic tee" purely because its description mentions "...layering with a long tee" once, in a sentence about something else entirely. The right item still ranks above it every time I've checked, so no criterion has caught this, but it's a precision gap, not a correctness one. I'd fix it by weighting matches in `title`/`style_tags` higher than matches in free-text `description`, or requiring at least one match outside `description` alone. I stopped at noticing it rather than fixing it because none of my five criteria name it, and this unit's rule is to follow a diagnosis, not chase every imperfection I happen to notice while reading output.

- **Criterion 5 lives outside `run_eval.py` entirely**, in `scripts/criterion5_model_unavailable.py`'s own subprocess harness. It works and I trust its output, but there's no single command that reproduces all five criteria in one run — someone checking my work has to run two different scripts. The real fix is giving `run_eval.py`'s scenarios an optional per-scenario environment override, so a "broken key" scenario could fold into the normal flow. I stopped short of building that because it's a harness change at least as large as this unit's one allowed improvement, and I'd already spent that on criterion 1's test.

- **Only `search_listings` is on MCP**, as the brief asked for — `suggest_outfit` and `create_fit_card` are still direct calls into `tools.py`. Not broken, and not a stretch feature I claimed, but it's the obvious next seam if this agent kept growing: right now a second agent could reach the catalog through MCP but still couldn't ask this one for outfit advice or a caption.



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
