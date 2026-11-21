"""
generate_profile.py
-------------------
Generate FinPath AI–compatible profile JSON files.

Usage:
    python tools/generate_profile.py                  # interactive prompts
    python tools/generate_profile.py --preset young   # use a built-in preset
    python tools/generate_profile.py --list           # list all presets

Accepted presets: young, family, highdebt, investor, retiree

Output: a .json file you can upload directly via
        "⬆ Upload a saved FinPath AI profile (JSON)" in the app.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE FORMAT (must match _load_profile_from_dict in app/main.py)
# ─────────────────────────────────────────────────────────────────────────────
#
# Top-level keys (all numeric fields are integers or floats as noted):
#
#   income           int   – total monthly income  (auto = inc_salary+inc_side+inc_other)
#   expenses         int   – total monthly expenses (auto = sum of exp_* fields)
#   savings          int   – current total savings balance
#   savings_contrib  int   – monthly savings contribution
#   debt_bal         int   – total debt balance
#   debt_payment     int   – monthly debt payment
#   debt_rate        float – average debt APR in %
#   goal             str   – free-text primary goal description (can be "")
#
#   Income breakdown (must sum to income):
#     inc_salary     int
#     inc_side       int
#     inc_other      int
#
#   Expense breakdown (must sum to expenses):
#     exp_housing    int
#     exp_food       int
#     exp_transport  int
#     exp_subs       int
#     exp_other      int
#
#   Savings breakdown (must sum to savings):
#     sav_emergency  int
#     sav_invest     int
#     sav_other      int
#
#   goals  list[dict]  – up to 5 goals, each:
#     {
#       "name":          str   – goal label e.g. "Buy a car"
#       "target":        int   – target amount in $
#       "current_saved": int   – amount already saved toward this goal
#       "months":        int   – months to reach the target
#     }
#
#   multi_debts  list[dict]  – one row per debt:
#     {
#       "Name":            str   – debt label e.g. "Student Loan"
#       "Balance ($)":     int
#       "APR (%)":         float
#       "Min Payment ($)": int
#     }
#
#   use_multi_debt  bool  – True to use the multi-debt table, False for single values


# ─────────────────────────────────────────────────────────────────────────────
# BUILT-IN PRESETS
# ─────────────────────────────────────────────────────────────────────────────

PRESETS = {
    "young": {
        "description": "Young professional, entry-level salary, small emergency fund",
        "profile": {
            "inc_salary": 3800, "inc_side": 400, "inc_other": 0,
            "exp_housing": 1100, "exp_food": 400, "exp_transport": 250,
            "exp_subs": 100, "exp_other": 350,
            "sav_emergency": 2000, "sav_invest": 500, "sav_other": 200,
            "savings_contrib": 300,
            "debt_bal": 15000, "debt_payment": 250, "debt_rate": 5.5,
            "goal": "Build emergency fund and pay off student loans",
            "use_multi_debt": True,
            "multi_debts": [
                {"Name": "Student Loan", "Balance ($)": 15000, "APR (%)": 5.5, "Min Payment ($)": 250},
            ],
            "goals": [
                {"name": "Emergency fund (3 mo)", "target": 6600, "current_saved": 2000, "months": 18},
                {"name": "Pay off student loan",  "target": 15000, "current_saved": 0,    "months": 60},
            ],
        },
    },
    "family": {
        "description": "Dual-income family, mortgage, kids, college savings",
        "profile": {
            "inc_salary": 9000, "inc_side": 500, "inc_other": 200,
            "exp_housing": 2200, "exp_food": 1000, "exp_transport": 700,
            "exp_subs": 200, "exp_other": 900,
            "sav_emergency": 15000, "sav_invest": 20000, "sav_other": 5000,
            "savings_contrib": 800,
            "debt_bal": 220000, "debt_payment": 1500, "debt_rate": 3.8,
            "goal": "College fund for kids and early mortgage payoff",
            "use_multi_debt": True,
            "multi_debts": [
                {"Name": "Mortgage",   "Balance ($)": 210000, "APR (%)": 3.5, "Min Payment ($)": 1350},
                {"Name": "Car Loan",   "Balance ($)":  10000, "APR (%)": 5.9, "Min Payment ($)":  150},
            ],
            "goals": [
                {"name": "College fund",          "target": 50000, "current_saved": 5000, "months": 120},
                {"name": "Home renovation",        "target": 20000, "current_saved": 2000, "months": 36},
            ],
        },
    },
    "highdebt": {
        "description": "High debt load, credit cards, tight budget",
        "profile": {
            "inc_salary": 4500, "inc_side": 0, "inc_other": 0,
            "exp_housing": 1300, "exp_food": 500, "exp_transport": 350,
            "exp_subs": 150, "exp_other": 500,
            "sav_emergency": 500, "sav_invest": 0, "sav_other": 0,
            "savings_contrib": 100,
            "debt_bal": 28000, "debt_payment": 700, "debt_rate": 19.9,
            "goal": "Get out of credit card debt as fast as possible",
            "use_multi_debt": True,
            "multi_debts": [
                {"Name": "Credit Card A", "Balance ($)": 8000,  "APR (%)": 22.9, "Min Payment ($)": 200},
                {"Name": "Credit Card B", "Balance ($)": 5000,  "APR (%)": 19.9, "Min Payment ($)": 125},
                {"Name": "Personal Loan", "Balance ($)": 15000, "APR (%)": 14.5, "Min Payment ($)": 375},
            ],
            "goals": [
                {"name": "Starter emergency fund", "target": 1000, "current_saved": 500, "months": 6},
            ],
        },
    },
    "investor": {
        "description": "High earner, aggressive investing, minimal debt",
        "profile": {
            "inc_salary": 15000, "inc_side": 2000, "inc_other": 1000,
            "exp_housing": 3000, "exp_food": 1200, "exp_transport": 800,
            "exp_subs": 300, "exp_other": 1200,
            "sav_emergency": 50000, "sav_invest": 200000, "sav_other": 20000,
            "savings_contrib": 3000,
            "debt_bal": 5000, "debt_payment": 500, "debt_rate": 2.9,
            "goal": "Reach $1M investment portfolio in 5 years",
            "use_multi_debt": False,
            "multi_debts": [
                {"Name": "Car Loan", "Balance ($)": 5000, "APR (%)": 2.9, "Min Payment ($)": 500},
            ],
            "goals": [
                {"name": "$1M investment milestone", "target": 1000000, "current_saved": 200000, "months": 60},
                {"name": "Vacation property",         "target": 100000, "current_saved": 20000,  "months": 36},
            ],
        },
    },
    "retiree": {
        "description": "Near-retirement, fixed income, focus on wealth preservation",
        "profile": {
            "inc_salary": 0, "inc_side": 0, "inc_other": 5500,
            "exp_housing": 1500, "exp_food": 700, "exp_transport": 400,
            "exp_subs": 100, "exp_other": 500,
            "sav_emergency": 30000, "sav_invest": 400000, "sav_other": 70000,
            "savings_contrib": 500,
            "debt_bal": 0, "debt_payment": 0, "debt_rate": 0.0,
            "goal": "Make savings last 25+ years in retirement",
            "use_multi_debt": False,
            "multi_debts": [
                {"Name": "No Debt", "Balance ($)": 0, "APR (%)": 0.0, "Min Payment ($)": 0},
            ],
            "goals": [
                {"name": "Healthcare reserve",   "target": 50000,  "current_saved": 20000,  "months": 24},
                {"name": "Travel fund",          "target": 10000,  "current_saved": 5000,   "months": 12},
            ],
        },
    },
}


def _derive_totals(p: dict) -> dict:
    """Auto-compute income, expenses, savings totals from breakdowns."""
    p["income"]   = p["inc_salary"] + p["inc_side"] + p["inc_other"]
    p["expenses"] = p["exp_housing"] + p["exp_food"] + p["exp_transport"] + p["exp_subs"] + p["exp_other"]
    p["savings"]  = p["sav_emergency"] + p["sav_invest"] + p["sav_other"]
    return p


def build_profile(p: dict) -> dict:
    return _derive_totals(p)


def save_profile(p: dict, name: str = None) -> Path:
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    fname = f"finpath_profile_{name or date.today().isoformat()}.json"
    out_path = out_dir / fname
    out_path.write_text(json.dumps(p, indent=2))
    return out_path


def interactive_build() -> dict:
    print("\n── FinPath AI Profile Generator ──────────────────────")
    print("Press Enter to accept the default shown in [brackets].\n")

    def ask(label, default):
        raw = input(f"  {label} [{default}]: ").strip()
        return type(default)(raw) if raw else default

    p = {}
    p["inc_salary"]     = ask("Monthly salary/wages ($)",     5000)
    p["inc_side"]       = ask("Monthly side income ($)",         0)
    p["inc_other"]      = ask("Monthly other income ($)",         0)
    p["exp_housing"]    = ask("Monthly housing expense ($)",   1200)
    p["exp_food"]       = ask("Monthly food expense ($)",       600)
    p["exp_transport"]  = ask("Monthly transport expense ($)",  400)
    p["exp_subs"]       = ask("Monthly subscriptions ($)",      200)
    p["exp_other"]      = ask("Monthly other expenses ($)",     600)
    p["sav_emergency"]  = ask("Emergency fund balance ($)",    3000)
    p["sav_invest"]     = ask("Investment balance ($)",        2000)
    p["sav_other"]      = ask("Other savings balance ($)",     1000)
    p["savings_contrib"]= ask("Monthly savings contribution ($)", 200)
    p["debt_bal"]       = ask("Total debt balance ($)",       10000)
    p["debt_payment"]   = ask("Monthly debt payment ($)",       300)
    p["debt_rate"]      = ask("Average debt APR (%)",           6.0)
    p["goal"]           = ask("Primary goal (text)",              "")
    p["use_multi_debt"] = False
    p["multi_debts"]    = [{"Name": "Primary Debt",
                             "Balance ($)": p["debt_bal"],
                             "APR (%)":     p["debt_rate"],
                             "Min Payment ($)": p["debt_payment"]}]
    p["goals"]          = [{"name": p["goal"] or "My goal",
                             "target": 0, "current_saved": 0, "months": 12}]
    return build_profile(p)


def main():
    parser = argparse.ArgumentParser(description="Generate a FinPath AI profile JSON")
    parser.add_argument("--preset", choices=list(PRESETS), help="Use a built-in preset")
    parser.add_argument("--list",   action="store_true",   help="List available presets")
    parser.add_argument("--output", help="Output filename (without .json)")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable presets:")
        for k, v in PRESETS.items():
            print(f"  {k:<10}  {v['description']}")
        sys.exit(0)

    if args.preset:
        profile = build_profile(PRESETS[args.preset]["profile"])
        label   = args.preset
        print(f"\n✓ Using preset: {args.preset} — {PRESETS[args.preset]['description']}")
    else:
        profile = interactive_build()
        label   = args.output or None

    out = save_profile(profile, label)
    print(f"\n✅ Profile saved → {out}")
    print(   "   Upload it in FinPath AI via '⬆ Upload a saved FinPath AI profile (JSON)'\n")
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
