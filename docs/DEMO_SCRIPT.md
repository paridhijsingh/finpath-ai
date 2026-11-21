# FinPath AI — Demo Script (~3:00)

## Setup (before recording)
1. `orchestrate env activate finpath --api-key "YOUR_KEY"`
2. `streamlit run app/main.py`
3. Open the live app at https://finpath-ai-copilot.streamlit.app/
4. Open a terminal side-by-side — viewers will see the tool input/output logs live
5. Clear browser history / close other tabs so only the app is on screen
6. Set browser zoom to ~110% so text is readable in the recording

---

## 0:00 – 0:12 · Cover

> **Say:** "FinPath AI is a personal finance copilot built on IBM watsonx Orchestrate.
> Every number you see comes from a deterministic Python tool — the AI agent never makes
> up a figure. Let me show you a live session."

*[Camera on app landing page — no typing yet.]*

---

## 0:12 – 0:35 · The problem

> **Say:** "Most financial chatbots guess. They produce plausible-sounding numbers with
> nothing behind them. FinPath AI enforces a strict rule: the agent must call a tool for
> every figure. If a tool isn't called, the number doesn't appear. That's the core
> design."

*[No interaction — keep the landing page visible.]*

---

## 0:35 – 1:05 · Profile & live health card

1. Click **"Recent Graduate"** preset.
   - All fields populate instantly: $3,200 income / $2,400 expenses / $1,500 savings /
     $8,000 debt / 7% APR / $250 payment.
2. Point to the **health card** in the right panel:
   > **Say:** "57 out of 100 — Needs attention. This score is calculated locally in the
   > browser — no API call, no token, instant feedback."
3. Point to the sub-scores:
   > **Say:** "Four sub-scores: cash flow, emergency fund coverage, debt-to-income ratio,
   > and savings rate. Top priority: build a one-month starter emergency fund."
4. Click **"Next →"**.

---

## 1:05 – 1:40 · Debt payoff (live agent call)

1. Click the suggestion chip **"How long to pay off my debt?"**
2. Click **"Ask FinPath →"**.
3. While waiting, point to the terminal:
   > **Say:** "Watch the terminal — you can see the exact profile being sent to the agent.
   > Every field: income, expenses, debt balance, rate in both percentage and decimal."
4. Reply arrives — point to the tool chip **⚙ debt_payoff_months**:
   > **Say:** "The agent called `debt_payoff_months` — that's the only way a number appears
   > in the reply. 36 months, $880.88 in total interest."
5. Point to the ✓ verified badge:
   > **Say:** "The verified badge means every dollar figure in that reply was cross-checked
   > against the raw tool output — no hallucination."

---

## 1:40 – 2:05 · Follow-up what-if (multi-turn)

1. Click the follow-up chip **"What if I paid $100 more a month?"**
2. Reply arrives — point to the two numbers side by side:
   > **Say:** "Same thread, same context. 28 months instead of 36 — saving $312 in
   > interest. The agent explicitly shows you the old number next to the new one."
3. Point to the terminal thread ID:
   > **Say:** "Same thread ID as the previous turn — Orchestrate maintains the conversation
   > server-side. No state lives in our app."

---

## 2:05 – 2:30 · Knowledge question (RAG)

1. Type: **"Why should I prioritise an emergency fund before investing?"**
2. Click **"Ask FinPath →"**.
3. Reply arrives — point to the citation at the bottom:
   > **Say:** "For conceptual questions like this, a second agent — `finpath_kb_agent` —
   > retrieves from our four-document knowledge base and must cite the source. See here:
   > Source: emergency_fund_guide.txt. The claim is grounded in the document, not in the
   > model's training data."

---

## 2:30 – 2:48 · Architecture in 15 seconds

> **Say:** "Under the hood: a ReAct loop in IBM watsonx Orchestrate runs `finpath_agent`,
> which delegates every calculation to 12 deterministic tools written in pure Python. For
> conceptual questions it delegates to `finpath_kb_agent`, which retrieves and cites from
> the knowledge base. The agent never invents a number — `api_client.py` verifies every
> figure after every turn."

*[Terminal visible — one last look at a tool call and response.]*

---

## 2:48 – 3:00 · Close

> **Say:** "FinPath AI: deterministic financial tools, grounded knowledge retrieval, and
> full auditability — all on IBM watsonx Orchestrate. All projections are illustrative.
> This is not financial advice."

---

## Key talking points for judges

| Point | Detail |
|---|---|
| IBM watsonx Orchestrate | Agent defined in YAML (`agents/finpath_agent.yaml`), 12 tools imported with `orchestrate tools import`, thread continuity maintained server-side |
| Grounded outputs | ReAct loop forces a tool call before every number; `_verify_figures()` in `api_client.py` cross-checks ±$0.51 tolerance; ✓ badge confirms no hallucination |
| RAG knowledge base | `finpath_kb` (4 documents) + `finpath_kb_agent` collaborator; every answer cites the source document and section |
| Testable offline | 217 unit tests, zero ADK dependencies in `tools/core/finance.py`; all pass with no credentials |
| Multi-turn | Same `thread_id` across follow-ups; agent explicitly compares old vs new numbers in every follow-up reply |
| IBM Bob | Used throughout development for code review, bug fixes, architecture docs, README, and UI refinements — session logs in `bob_sessions/` |

---

## Screen recording tips

- Record at 1920×1080, 30 fps.
- Use QuickTime (macOS) or OBS — capture browser + terminal in split screen.
- Mute notifications before starting.
- Run `orchestrate env activate finpath --api-key "YOUR_KEY"` immediately before recording so the token is fresh.
- If the agent is slow (>8 s), the spinner is visible — keep talking through the wait.
