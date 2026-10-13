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

You tell FitFindr what you want, like vintage graphic tee under $30, size M, and it searches the listings for the best match. Then it suggests an outfit using that item plus whatever's in your wardrobe (or just general advice if your wardrobe's empty). Last it writes a caption you could actually post, with the item, price, and platform in it. If nothing matches, it stops and tells you what to change — price, size, or keywords.

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

- **What it does:** Looks through the local listings for items matching some keywords, optionally filtered by size and max price.
- **Inputs:** `description` (str) — what the user wants, e.g. `"vintage graphic tee"`. `size` (str or None) — a size to filter on, `None` for any size (rule below). `max_price` (float or None) — the most they'll pay, inclusive, `None` for no limit.
- **Returns:** A list of listing dicts, best keyword match first, capped at `config.SEARCH_RESULT_LIMIT` (10). Each dict has `id`, `title`, `description`, `category`, `style_tags` (list[str]), `size`, `condition`, `price` (float), `colors` (list[str]), `brand` (str or None), `platform`.
- **When it has nothing:** Returns `[]`. Never `None`, never an exception.

**Size-match rule:** lowercase both sizes and drop any parenthetical (`"XL (oversized)"` → `"xl"`). Split the listing size on `"/"` so `"S/M"` gives `s` and `m`; also pull any number out, so `"US 8"` gives `us 8` and `8`, and `"W30"` gives `w30` and `30`. The query has to exactly equal one of those pieces — no substring check, because `"s" in "us 9"` and `"l" in "xl"` are both true and both wrong. `One Size` listings only match a query that also says one size.

### `suggest_outfit`

- **What it does:** Takes one listing and the user's wardrobe, asks the model for one or two outfits using that item.
- **Inputs:** `new_item` (dict) — the listing they're considering. `wardrobe` (dict) — `{"items": [...]}`, items list may be empty.
- **Returns:** A non-empty string with outfit ideas. If the wardrobe has items, it names them by their `name` field instead of describing them generically.
- **When it has nothing:** Empty `wardrobe["items"]` → general styling advice for the item instead. Still non-empty, never `""`, never an exception.

### `create_fit_card`

- **What it does:** Writes a short caption, like someone posting their find, from the listing details and the suggested outfit.
- **Inputs:** `outfit` (str) — the string `suggest_outfit()` returned. `new_item` (dict) — the listing dict.
- **Returns:** A 2–4 sentence caption that mentions the item, price, and platform once each.
- **When it has nothing:** Empty or whitespace-only `outfit` → returns `"Can't write a caption without an outfit to describe — suggest_outfit needs to run first."` instead of raising or returning `""`.

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

**Branch rule:** if `search_listings` comes back empty, put a message in `session["error"]` (built by `_no_results_message`, names what to change — max price, size, keywords) and return right away. `suggest_outfit`/`create_fit_card` never run, so `session["fit_card"]` stays `None`. Otherwise take `search_results[0]` as `selected_item` and go on to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`, the `if not session["search_results"]:` check right after the `search_listings` call.

**How the query is parsed:** regex, `agent.py::_parse_query`. `under $30` / `$30` / `under 30` → `max_price`; `size M` → `size`; whatever's left is the `description`. No model call.

**What moves through the session:** `parsed` → `search_results` → `selected_item` (first result) → `outfit_suggestion` → `fit_card`. Each step reads its inputs back out of the session instead of taking them straight from the last call. Empty search sets `error` and returns early.

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

Picked item is the first search result, outfit's about that same item. Last line says it came from cache — ran it earlier, so this was a repeat.

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', ...}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', ...}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', ...}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', ...}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', ...}]
```

6 results, all under $30. `lst_011` (cargo pants) is the weakest one — only shares the word tee with the query, from layering with a long tee buried in its description. Same keyword-overlap issue I flag in criterion 1.

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

Same call with `get_empty_wardrobe()` instead, to hit the empty case:

```
Pair these vintage Levi's 501s with a tucked-in graphic tee and a leather jacket for an effortless, classic streetwear look. Alternatively, dress them up with an oversized button-down shirt and loafers or retro sneakers to balance the relaxed medium-wash denim.
```

General advice, no wardrobe pieces named, no crash, no empty string.

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Still screaming that I actually scored these vintage Levi's 501 jeans on Depop for only $38.00! The medium wash has that perfectly broken-in, 90s indie sleaze fade that you just can't fake. Throwing them on with some fresh white sneakers and calling it my entire personality for the foreseeable future.
```

Ran this three times on the same item to check for identical output. Cache on (default): runs 2 and 3 came back word-for-word the same as run 1. `TEMPERATURE` is already 0.9, so that wasn't it — the cache was just handing back the same answer for the same prompt. Cleared the cache between calls and got three different captions, each still naming the item, `$38.00`, and Depop once:

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

1. Building run_agent. Gave Claude the branch rule and asked for the loop. It wrote the session-driven loop, a regex parser, and the early return on empty search.
2. Identical fit cards. Asked Claude to run create_fit_card three times — all three came back identical. It checked config.py, saw TEMPERATURE was already 0.9, reran with the cache off, got three different captions.
3. The MCP move. Asked Claude to move search_listings onto MCP and point the agent at it. It wrote the tool's description and typed inputs from the Tool Inventory, checked the registration with mcp_client.py before touching agent.py, then swapped the direct call for the MCP one.
4. Model-unavailable wasn't actually handled. Asked Claude to trigger all three failure modes, including a bad API key. Turned out breaking the key crashed the whole process (exit code 1) instead of returning a usable session — app.py's catch-all kept it from printing a raw traceback, but the program still died either way. Claude added a try/except around the two model-calling steps in run_agent.
5. Criterion 1's test wasn't really testing anything. While scoring the Run Log, Claude noticed criterion 1's scenario used the same query five times, so it never actually tested the phrasing-miss problem its own why this target was about — even though it scored 5/5. Had it change run_eval.py so a scenario can cycle through five different phrasings instead, used that as this unit's improvement.

**Moment 1**

- *What I asked for:* test `create_fit_card` three times on the same item, tell me if the outputs matched.
- *What came back:* all three identical. Claude checked `config.py`, `TEMPERATURE` was already 0.9 so that wasn't it. Reran with `AI201_CACHE=0`, got three different captions — pointed at the cache, not the model.
- *What I changed:* no code. Left the cache on while building, wrote up in Sample Run that the cache was the cause. Eval runs turn it off anyway.

**Moment 2**

- *What I asked for:* gave Claude my branch rule from the Tool Inventory, asked it to fill in `run_agent()`, with every tool result going through the session.
- *What came back:* a loop that reads the session each pass to decide what's next, a regex `_parse_query`, an early return when `search_listings` comes back empty. Checked that `selected_item` was `lst_002`, same item `suggest_outfit` wrote about. The ballgown query left `fit_card` as `None` with a message about price/size/keywords.
- *What I changed:* the code was fine, but my README text for the branch rule didn't quite match it, so I fixed that to name `_no_results_message` and the actual `if` check.

**Moment 3 (unit 4)**

- *What I asked for:* trigger each of the three failure modes on purpose — empty search, empty wardrobe, broken key — and write down what the agent said each time.
- *What came back:* first two already worked. The key one didn't: breaking a character of `GEMINI_API_KEY` and running a query killed the whole process, exit code 1. No raw traceback (app.py catches that), but still a dead process instead of a usable session.
- *What I changed:* added `try/except ModelUnavailable` around the `suggest_outfit` and `create_fit_card` calls, writes a message into `session["error"]` and returns normally now. Retested with the same bad key — clean exit — then put the real key back.

**Moment 4 (unit 4)**

- *What I asked for:* score my five criteria against the Run Log and fill in Verdicts and Diagnoses.
- *What came back:* everything MET, but Claude caught two things I'd have missed. One, criterion 3's checked from the trace claim doesn't hold up — `trace.py` collapses a tool's inputs down to `dict with keys: new_item, wardrobe_items`, no id visible — so it verified that one with a separate instrumented run instead. Two, criterion 1's scenario repeated the same query five times, so the 5/5 wasn't really evidence of anything about phrasing.
- *What I changed:* fixed the second one as the improvement — added list-of-queries support to `run_eval.py`/`scenarios.py`, rewrote criterion 1's scenario to use five different phrasings, reran. Verdict's still 5/5, but now it means something.

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

Criteria 1–4 come from `scenarios.py`, run by `run_eval.py::main` → `agent.py::run_agent`, five tries each, caching off. Criterion 5 doesn't go through that harness — `generate.py` caches its model client in a module global after the first good call, so breaking `GEMINI_API_KEY` mid-run would mess with whatever scenario ran next, or just get ignored if a working client was already cached. It's measured separately by `scripts/criterion5_model_unavailable.py`, which runs each try in its own subprocess with the key overridden only in that subprocess's env — the real key in `.env` never gets touched.

**Real output from one try**, pasted as text, naming the file and function that produced it:

Criterion 1, try 1 — `agent.py::run_agent`, logged by `run_eval.py::run_once` into `results/run_2026-10-13_1518_before.md`:

```
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)

Fit card:
Still not over finding this butterfly print Y2K baby tee on Depop for just $18! It's giving major early-2000s mall rat energy, and I am so ready to live out my ultimate Y2K pop star fantasy.
```

Criterion 2, try 1 — `agent.py::run_agent`'s branch (`if not session["search_results"]`), same file:

```
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

stopped early: yes — No listings matched your search. You could raise your max price above $5, try a different size than XXS or drop the size, or use broader or different keywords than "designer ballgown".
```

Criterion 3 — the trace's `_short()` summary collapses a tool's inputs down to `dict with keys: new_item, wardrobe_items`, no id shown, so I didn't trust the trace for this one. Checked it with a one-off instrumented run instead (not saved under `results/` — `run_eval.py` doesn't log this way) that monkeypatches `tools.suggest_outfit` and `tools.create_fit_card` to record the `id` of the `new_item` they're actually called with, five runs of the 90s track jacket scenario:

```
try 1: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 2: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 3: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 4: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
try 5: selected_item.id='lst_004'  suggest_outfit got='lst_004'  create_fit_card got='lst_004'  -> PASS
```

Criterion 4, try 1 and try 5 — `tools.py::create_fit_card`, same item (`lst_002`, $18.0, depop) both times, from `results/run_2026-10-13_1518_before.md`:

```
Try 1: Still screaming about finding this Y2K Baby Tee — Butterfly Print on depop for only $18.00! It's giving major model-off-duty energy, and I am so ready to style it with baggy denim and combat boots. My inner 2000s pop star could never.

Try 5: Found the holy grail on Depop today—this Y2K butterfly baby tee for only $18! I'm so obsessed with the cute little graphic and already planning a million baggy denim fits around it. Truly living out my early 2000s pop star dreams. 🦋✨
```

Different wording both times, both name the price (`$18.00` / `$18`) and the platform (`depop` / `Depop`).

Criterion 5, try 1 — `scripts/criterion5_model_unavailable.py`, calling `agent.py::run_agent` with `GEMINI_API_KEY` overridden to garbage in the subprocess env only:

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
| 1 | Matching query completes all three tools, returns a fit card | 4 of 5 | MET | 5 of 5 — `stopped early: no` every try, fit card present every time. Clears 4-of-5 with room. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET | 5 of 5 — stopped early with the no-listings-matched message, 0 model calls each time (trace is 2 steps, not 5). Target was exactly 5, got 5. |
| 3 | `selected_item`'s id matches the id every later tool actually received | 5 of 5 | MET | 5 of 5, checked by instrumenting `suggest_outfit`/`create_fit_card` directly instead of trusting the trace's shortened summary (doesn't show the id). All three ids matched every time. |
| 4 | 5 fit cards on the same item differ, every one keeps the price and platform | 5 of 5 | MET | Read all 5 by eye — no two word-for-word identical, every one names `$18`/`$18.00` and `depop`/`Depop`. |
| 5 | A broken API key returns a readable `session["error"]` instead of crashing | 5 of 5 | MET | 5 of 5 from `scripts/criterion5_model_unavailable.py` — non-empty `session["error"]` every time, `outfit_suggestion`/`fit_card` still `None`, no crash. |

**Diagnoses**

Nothing missed, four of the five at a clean 5/5. No tool/branch/session/model-output failure to diagnose, because nothing failed.

Doesn't mean every target was a good test, though. Criteria 2, 3, and 5 each check a plain code path — a branch, a variable assignment, an exception handler — that has no real reason to differ try to try, so 5/5 there is the right bar and actually means something. Criterion 4 forces five real, independent model calls at temperature 0.9, a real chance to fail each time, and it held.

**Criterion 1 is the one I'd tighten.** My why-this-target note in `criteria.md` was about phrasing: a real request can describe something in the data without sharing enough words with it for the keyword scorer to find it. But the scenario I wrote for it sends the exact same string, `"vintage graphic tee under $30"`, all five times. `search_listings` is deterministic, so all five tries take the identical path — nothing about phrasing ever actually got tested. 5/5 proves the model calls complete reliably. It doesn't prove the thing the target was written to prove. Fix: swap in five different phrasings of a request the data can satisfy and measure against those instead — which is what I did for this unit's improvement, below.

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

Two steps instead of five, stops before `suggest_outfit` runs at all — 0 model calls, so it's really short-circuiting, not just printing a different message at the end.

**On the MCP move:** `agent.py::run_agent` calls `mcp_client.call_tool("search_listings", {...})` now instead of importing and calling `tools.search_listings` directly (removed that import). Trace step is labeled `search_listings (via MCP)`, so the MCP call shows up in the trace itself. Nothing behaved differently after the swap — same query, same item, same outfit, same fit card as the direct call in unit 3. Checked by diffing output from before and after.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

Not the agent, the test for criterion 1. `scenarios.py`'s scenario sent the identical string, `"vintage graphic tee under $30"`, all five tries, and `search_listings` is deterministic, so nothing about phrasing was ever actually exercised. Added support in `run_eval.py::run_once` / `_query_for_try` for a scenario's `"query"` to be a list of five strings instead of one repeated string, cycling through them per try. Changed criterion 1's scenario to five different real phrasings of the same findable item (`"band tee under $30"`, `"retro graphic shirt under $30"`, etc.), each checked against `search_listings` directly first so a FAIL would mean the phrasing genuinely missed, not that nothing in the data matched it. `agent.py` and `tools.py` untouched.

**Which failure it was meant to fix:**

Not a failure in the agent — nothing missed in the before run. Fixes the measurement: criterion 1's own justification is about keyword search missing on phrasing, and the old scenario never tested that. Comes straight from the Diagnoses section above.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes, 5 *different* phrasings | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged |
| 3. `selected_item`'s id matches every tool it reaches | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged |
| 4. 5 fit cards on the same item differ, keep price/platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged |
| 5. Broken key returns readable `session["error"]` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) — unchanged, not rerun |

Full log: `results/run_2026-10-13_1528_after.md`, from `run_eval.py::main`. Criteria 2–4 used the same scenarios as before and came out the same — nothing about them changed. Criterion 5 isn't in this harness (see Run Log — Before) and nothing about it changed either, so I didn't rerun `scripts/criterion5_model_unavailable.py`.

Criterion 1, the part that's actually new — five different queries, five results:

```
Try 1 — query: vintage graphic tee under $30             -> Y2K Baby Tee — Butterfly Print ($18.0, depop)
Try 2 — query: band tee under $30                        -> Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
Try 3 — query: retro graphic shirt under $30             -> Y2K Baby Tee — Butterfly Print ($18.0, depop)
Try 4 — query: 80s or 90s style graphic t-shirt under $30 -> Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
Try 5 — query: faded vintage band t-shirt under $30      -> Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
```

All five completed, landing on two different real items depending on phrasing instead of the same one five times.

**Did it help, and how do I know:**

Verdict didn't move — criterion 1 was MET before (5/5, weak test) and MET after (5/5, real test). Looking at just the Verdict column, you'd think nothing happened.

It did, though, just not in the verdict. Before, the 5/5 was five identical runs of one query — the only thing that could've failed was an API hiccup, since search_listings gives the same ranked list every time for the same input. After, it's five different phrasings landing on two different items depending on wording, which is actually the thing criterion 1 claims to be testing. It happened to clear all five anyway. So this didn't fix a broken result — it swapped a number I couldn't trust for one I can. The system's behavior didn't change. My evidence for it did.

---

## What's Still Broken

Nothing's MISSED, before or after, so there's no per-criterion fix list. Doesn't mean nothing's left — here's what I know is still off, none of which any of the five criteria happen to catch:

- **The keyword scorer still lets weak matches through.** It scores title + description + style_tags + brand + category all the same, so one stray word shared with an unrelated field counts just as much as a real match — e.g. a cargo-pants listing scored against graphic tee because its description mentions a long tee once, about something else entirely. The right item still outranks it every time I've checked, so this isn't a criterion miss, just sloppy precision. Fix would be weighting title/style_tags matches over description matches, or requiring a match outside description alone. Left it alone since none of my criteria name it, and chasing stuff I happen to notice isn't what this unit asked for.

- **Criterion 5 isn't inside `run_eval.py`.** It lives in its own subprocess script. Works fine, I trust it, but there's no single command that runs all five criteria — someone checking my work needs two scripts, not one. Real fix is an optional env override per scenario in `run_eval.py` itself. Didn't build that because it's its own harness change, at least as big as the one improvement I already used on criterion 1.

- **Only `search_listings` is on MCP**, which is what the assignment asked for — `suggest_outfit` and `create_fit_card` are still direct calls. Not broken, not a stretch feature I'm claiming, just the obvious next move if this grew: right now another agent could search the catalog through MCP but couldn't ask this one for outfit advice or a caption.

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

       [x] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [x] Run Log — Before, five criteria, five tries each
       [x] Real output pasted underneath, naming file and function
       [x] A verdict on every criterion
       [x] A diagnosis for every miss, naming a place AND a mechanism
       [x] Loop Trace, with the MCP call visible in it
       [x] All three failure modes triggered and handled
       [x] One improvement, with Run Log — After in the same format
       [x] What's Still Broken
       [x] At least four new commits
       [x] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
