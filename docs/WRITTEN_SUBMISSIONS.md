# FinPath AI — Written Submissions

---

## Problem and Solution Statement

### The challenge

Millions of people make consequential financial decisions — paying down debt, building
savings, planning for a goal — with almost no personalised, trustworthy guidance. Generic
online calculators ignore the user's full picture. Consumer chatbots and large language
models produce financial figures that sound authoritative but are frequently wrong: they
estimate, round, interpolate, and confabulate without any mechanism for verification. A
user asking "how long will it take to pay off my debt?" deserves an exact, reproducible
answer tied to their actual numbers — not a confident guess.

The core problem is not a lack of financial information. It is a lack of **grounded,
verifiable, personalised financial reasoning** that a non-expert can trust and act on.

### The solution

FinPath AI is a personal finance copilot built on IBM watsonx Orchestrate. It enforces
one strict rule: **the agent must call a deterministic Python tool for every number it
reports.** If a tool is not called, the number does not appear. This is not a guideline
or a prompt suggestion — it is a structural constraint enforced by the agent YAML and
verified programmatically in `api_client.py` after every turn.

A user describes their financial situation through a three-step profile wizard: income
breakdown, monthly expenses, savings balance, debt details, and a primary goal. As they
type, a live financial health score (0–100) updates instantly using local math — four
sub-scores covering cash flow, emergency fund coverage, debt-to-income ratio, and savings
rate — with an ordered list of priorities. No API call, no token, no latency.

They then ask a question. FinPath AI sends the full profile and the question to a
watsonx Orchestrate agent running a ReAct loop. The agent reasons through the question,
selects the appropriate tool (e.g. `debt_payoff_months`, `stress_test`,
`multi_debt_plan`), calls it with the user's exact values, and quotes the result
verbatim. Every dollar amount and percentage in the reply is cross-checked against the
raw tool output by `api_client._verify_figures()`. A ✓ verified badge confirms no
hallucination; a ⚠ warning appears if any figure deviates by more than $0.51.

Multi-turn conversation is a first-class feature. Follow-up questions like "what if I
paid $100 more a month?" reuse the same Orchestrate thread — the agent always has the
previous answer and explicitly compares old versus new numbers.

For conceptual questions ("why should I build an emergency fund before investing?"), a
second agent — `finpath_kb_agent` — retrieves from a four-document knowledge base
covering emergency funds, compound interest, debt repayment strategies, and the
savings-rate framework. Every factual claim is backed by a document citation.

The underlying math lives in `tools/core/finance.py` — 12 pure Python functions, zero
external dependencies, fully testable offline. GitHub Actions runs 217 unit tests on
every push. The app is deployed on Streamlit Community Cloud and continues to function
in Demo mode (health card, projections) even when the Orchestrate agent is unreachable.

FinPath AI is designed for anyone facing a real financial decision who needs an answer
they can verify — not an estimate they have to trust.

---

## Technology Statement

### IBM Bob

IBM Bob was the primary development environment for FinPath AI. Every significant code
change in the project was made using Bob in Agent mode:

- **Repository cleanup** — Bob identified and removed untracked `__pycache__`, `.pyc`,
  and stray `.gitignore` files, and tightened `.gitignore` rules. All 193 tests at the
  time still passed.

- **Rate-validation bug fix** — Bob diagnosed a silent miscalculation: debt rates
  entered as `20` (percent) instead of `0.20` (decimal) would produce a 2000% APR with
  no error. Bob added `_validate_rates()` to `tools/core/finance.py` and wrote 24
  regression tests covering the boundary. Test count moved to 217 and has stayed there.

- **Architecture documentation** — Bob authored `docs/ARCHITECTURE.md`, including a
  Mermaid system-flow diagram, a full tool reference table, and the guardrails summary,
  all grounded in the actual agent YAML and source files rather than speculative prose.

- **README and documentation** — Bob drafted the Built with Bob, Data sources,
  Responsible AI, Deploy, and profile-generator sections of `README.md`.

- **UI refinements** — Bob applied targeted diffs to `app/main.py` for chip-wrapping
  layout, the demo architecture section, and hero-panel polish.

- **Profile generator docs** — Bob reviewed `tools/generate_profile.py` and
  `data/finpath_profile_young.json` (commit 9b3e100) and added the "Generating sample
  profiles" section to the README.

All sessions are logged in `bob_sessions/` with screenshots.

### IBM watsonx Orchestrate

watsonx Orchestrate is the agent runtime that makes FinPath AI's core guarantee possible.

**Agent definition** — `agents/finpath_agent.yaml` defines `finpath_agent` with
`style: react_core` (a ReAct loop). The instructions are explicit: use a tool for every
number, quote the tool's `summary` field verbatim, state all assumptions, compare old
and new numbers on follow-ups, and close every reply with the disclaimer.

**Tool registration** — the 12 `@tool`-decorated wrappers in `tools/` are imported
with `orchestrate tools import --kind python`. The ADK generates JSON schemas
automatically from Python type annotations. Tool wrappers contain no logic — they
delegate entirely to `tools/core/finance.py`.

**Knowledge base and RAG agent** — `finpath_kb` is defined in
`knowledge/finpath_kb.yaml` and indexes four plain-text documents. `finpath_kb_agent`
is a collaborator agent that `finpath_agent` delegates to for conceptual questions. It
retrieves from the vector index and must cite the source document and section in every
response. It never performs arithmetic.

**Thread continuity** — `RunClient.create_run()` accepts a `thread_id`. The first
message returns a new `thread_id`; every follow-up passes it back. Orchestrate maintains
conversation context server-side — no state is stored in the Streamlit app.

**Credential resolution** — the app resolves credentials in priority order:
`st.secrets` (Streamlit Cloud) → environment variables → ADK local config
(`~/.wxo/`). Demo mode activates automatically if the agent is unreachable, so the
health card and projections remain functional for judges without live credentials.
