# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** My search is a plain keyword-overlap scorer against
`title`, `description`, and `style_tags` — it's not semantic search. A real
phrasing can describe a listing that genuinely exists in the data without
sharing enough literal words with it to score above zero (e.g. calling
something a "band tee" when the listing only says "graphic tee"). One miss in
five realistic phrasings is a limitation of keyword matching, not a loop bug,
so 4 of 5 is the honest target rather than 5 of 5.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** This path has no fuzzy matching to forgive. The branch
is: score every listing against the query, and if every score is zero, stop
and return the canned message — there's no model call and no ambiguous
judgment involved, just a plain `if not search_results`. If this branch ever
fails even once, that's a real defect in the loop (e.g. calling
`suggest_outfit` anyway, or crashing on an empty list), not natural variance
to tolerate, so the target is 5 of 5.

---

## 3. The same item moves through every tool

Across 5 full runs on a matching query, the `id` of `session["selected_item"]`
immediately after `search_listings` is identical to the `id` field of the
`new_item` dict actually received by `suggest_outfit`, and identical again to
the `id` field of the `new_item` dict actually received by `create_fit_card`
— 5 of 5 tries. This is checked from the trace: `trace.step()` logs each
tool's inputs, so the three `id`s can be read back and compared directly
instead of trusted from memory.

**Why this target:** Carrying a dict (or its `id`) from one variable into the
next function call is plain code, not a model call — there is nothing
probabilistic about it. If the `id` ever changed between steps, that would
mean something re-selected an item, indexed the wrong element, or mutated the
session — a real bug every time it happens, not an acceptable rate of drift.
So the target is 5 of 5, not 4.

---

## 4. Fit cards vary, but not the facts

Across 5 fit cards generated from 5 separate calls on the **same** listing,
the 5 caption strings are not word-for-word identical to each other, and
every one of the 5 still names that listing's `price` and `platform` at least
once — 5 of 5 tries.

**Why this target:** The fit card calling a model means the wording is
expected to differ run to run — that's `TEMPERATURE` doing its job, not a
defect. What's *not* acceptable is losing the two facts the caption exists to
convey (what it costs, where to get it), since those come from the listing
dict, not from the model's imagination, and dropping them would be a prompt
bug, not natural variation. Likewise, 5 identical captions would mean caching
is firing when it shouldn't be, during an evaluation run that's supposed to
turn it off. Neither failure is something temperature should cause, so I hold
both halves of this criterion to 5 of 5 rather than discounting for the
model's involvement.

---

## 5. A missing model stays recoverable

With `GEMINI_API_KEY` deliberately broken, so every model call raises
`ModelUnavailable`, the agent returns a session with `session["error"]` set
to a readable message (not `None`, not a stack trace, not a half-finished
session with some later fields filled in and others not) — 5 of 5 tries.

**Why this target:** A dead API key is nobody's bug — it's a thing that will
really happen (expired key, hit a quota, service outage) — but how the agent
reacts to it is entirely within my code's control: `agent.py` already imports
`ModelUnavailable` for exactly this reason. Catching it and writing a clear
`session["error"]` instead of letting the exception propagate is a decision
I either made correctly or didn't; there's no partial credit for "usually
catches it," so the target is 5 of 5.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
