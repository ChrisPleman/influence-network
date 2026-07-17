"""Influence Network — Streamlit dashboard.

Interactive front end over the 2024 money-to-policy pipeline: enter an organization
and see its lobbying spend, matched PAC(s), where that PAC's money went, and which
bills it lobbied — all pulled live from Senate LDA + FEC + Congress.gov.

Run it:
    pip install -r requirements.txt
    streamlit run dashboard/app.py

The pipeline mirrors notebooks/influence_pipeline_2024.ipynb. Only DEMO_KEY is needed
to start; add a real FEC key in the sidebar to run batches without hitting rate limits.
"""
from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher

import pandas as pd
import requests
import streamlit as st

# --- Defaults (overridable in the sidebar) -----------------------------------
FILING_YEAR = 2024        # LDA filing year
CYCLE = 2024              # FEC two-year transaction period (covers 2023-2024)
CONGRESS = 118           # 118th Congress = 2023-2024

# Legal / structural tokens that add noise but no identity.
_NOISE = {
    "inc", "incorporated", "llc", "lp", "llp", "co", "corp", "corporation",
    "company", "the", "and", "of", "for", "fund", "foundation", "trust",
    "pac", "committee", "cmte", "political", "action", "associates", "assn",
    "association", "society", "institute", "group", "holdings",
}


def normalize_org_name(name: str) -> str:
    """Canonicalize an org name so equivalent names collide.
    'Pfizer, Inc.' / 'PFIZER INC. PAC' / 'Pfizer Co' -> 'pfizer'."""
    if not name:
        return ""
    name = re.sub(r"[^a-z0-9\s]", " ", name.lower())
    return " ".join(t for t in name.split() if t not in _NOISE).strip()


def name_sim(a: str, b: str) -> float:
    """0..1 similarity on normalized names."""
    return SequenceMatcher(None, normalize_org_name(a), normalize_org_name(b)).ratio()


# Bill-reference regex: longer types first so "hjres" wins over "h".
_BILL_RE = re.compile(
    r"\b(H\.?\s?J\.?\s?Res\.?|S\.?\s?J\.?\s?Res\.?|"
    r"H\.?\s?Con\.?\s?Res\.?|S\.?\s?Con\.?\s?Res\.?|"
    r"H\.?\s?Res\.?|S\.?\s?Res\.?|H\.?\s?R\.?|S)\.?\s?(\d{1,5})\b",
    re.IGNORECASE,
)


def extract_bill_keys(text):
    """Yield canonical bill keys like 'hr3684', 's1339' from free text."""
    for m in _BILL_RE.finditer(text or ""):
        yield re.sub(r"[.\s]", "", m.group(1)).lower() + m.group(2)


# --- Source fetchers (cached so re-runs don't re-hit the APIs) ----------------
@st.cache_data(show_spinner=False, ttl=3600)
def fetch_lda_filings(org: str, year: int, page_size: int = 25):
    r = requests.get(
        "https://lda.senate.gov/api/v1/filings/",
        params={"client_name": org, "filing_year": year, "page_size": page_size},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("results", [])


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_fec_committees(org: str, cycle: int, api_key: str, per_page: int = 20):
    r = requests.get(
        "https://api.open.fec.gov/v1/committees",
        params={"api_key": api_key, "q": org, "cycle": cycle, "per_page": per_page},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("results", [])


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_fec_disbursements(committee_id: str, cycle: int, api_key: str, per_page: int = 20):
    r = requests.get(
        "https://api.open.fec.gov/v1/schedules/schedule_b",
        params={"api_key": api_key, "committee_id": committee_id,
                "two_year_transaction_period": cycle, "per_page": per_page,
                "sort": "-disbursement_amount"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("results", [])


# --- The pipeline ------------------------------------------------------------
def trace_org(org: str, *, year: int, cycle: int, fec_key: str, threshold: float):
    """Stitch one organization across LDA + FEC + Congress for the given cycle."""
    filings = fetch_lda_filings(org, year)
    committees = fetch_fec_committees(org, cycle, fec_key)

    # 1) LOBBYING: coalesce income/expenses, aggregate per org_key.
    lda_rows = []
    for f in filings:
        name = (f.get("client") or {}).get("name")
        if not name:
            continue
        usd = f.get("income") or f.get("expenses") or 0
        lda_rows.append({"org_key": normalize_org_name(name),
                         "client": name, "lobbying_usd": float(usd or 0)})
    lda_df = pd.DataFrame(lda_rows)
    lda_agg = (lda_df.groupby("org_key", as_index=False)
                     .agg(client=("client", "first"),
                          n_filings=("client", "size"),
                          lobbying_usd=("lobbying_usd", "sum"))
               if not lda_df.empty else lda_df)

    # 2) MONEY: fuzzy-match FEC committees -> pull each PAC's disbursements.
    client_names = list(lda_agg["client"]) if not lda_agg.empty else [org]
    fec_df = pd.DataFrame([{"committee_id": c["committee_id"],
                            "committee": c["name"],
                            "type": c.get("committee_type"),
                            "designation": c.get("designation_full"),   # 'B' -> Lobbyist/Registrant PAC
                            "affiliated": c.get("affiliated_committee_name")}  # corporate parent
                           for c in committees])
    if not fec_df.empty:
        fec_df["match_score"] = fec_df["committee"].apply(
            lambda n: max(name_sim(n, cn) for cn in client_names))
        matched = (fec_df[fec_df["match_score"] >= threshold]
                   .drop_duplicates("committee_id")
                   .sort_values("match_score", ascending=False))
    else:
        matched = fec_df

    disb_rows = []
    for cid in matched.get("committee_id", []):
        for d in fetch_fec_disbursements(cid, cycle, fec_key):
            disb_rows.append({"committee_id": cid,
                              "recipient": d.get("recipient_name"),
                              "amount": float(d.get("disbursement_amount") or 0),
                              "date": d.get("disbursement_date"),
                              "purpose": d.get("disbursement_description")})
    disb_df = pd.DataFrame(disb_rows)

    # 3) POLICY: bills named in the lobbying-activity text.
    bill_counts = Counter()
    for f in filings:
        for act in (f.get("lobbying_activities") or []):
            for key in set(extract_bill_keys(act.get("description"))):
                bill_counts[key] += 1
    bills_df = pd.DataFrame(bill_counts.most_common(),
                            columns=["bill_key", "filings_mentioning"])

    summary = {
        "org": org,
        "n_filings": len(filings),
        "total_lobbying_usd": float(lda_agg["lobbying_usd"].sum()) if not lda_agg.empty else 0.0,
        "n_pacs": int(matched["committee_id"].nunique()) if not matched.empty else 0,
        "pac_total_disbursed": float(disb_df["amount"].sum()) if not disb_df.empty else 0.0,
        "n_bills_lobbied": len(bills_df),
    }
    return {"summary": summary, "lobbying": lda_agg, "pacs": matched,
            "disbursements": disb_df, "bills": bills_df}


# --- UI ----------------------------------------------------------------------
st.set_page_config(page_title="Influence Network", page_icon="🏛️", layout="wide")
st.title("🏛️ Influence Network — Money to Policy")
st.caption("Trace an organization across Senate lobbying (LDA), FEC PAC money, and Congress bills.")

with st.sidebar:
    st.header("Config")
    fec_key = st.text_input("FEC API key", value="DEMO_KEY", type="password",
                            help="DEMO_KEY works but is rate-limited. Get a real key at api.open.fec.gov.")
    year = st.number_input("LDA filing year", value=FILING_YEAR, step=1)
    cycle = st.number_input("FEC cycle", value=CYCLE, step=2)
    threshold = st.slider("Name-match threshold", 0.0, 1.0, 0.60, 0.05,
                          help="Minimum normalized-name similarity to accept an LDA↔FEC match.")

tab_single, tab_batch = st.tabs(["Single organization", "Batch watchlist"])

with tab_single:
    org = st.text_input("Organization / company / trade group", value="Pfizer")
    if st.button("Trace", type="primary") and org.strip():
        try:
            with st.spinner(f"Tracing {org}…"):
                result = trace_org(org.strip(), year=int(year), cycle=int(cycle),
                                   fec_key=fec_key, threshold=threshold)
        except requests.HTTPError as exc:
            st.error(f"API error (rate limit?): {exc}")
            st.stop()

        s = result["summary"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lobbying spend", f"${s['total_lobbying_usd']:,.0f}")
        c2.metric("PACs matched", s["n_pacs"])
        c3.metric("PAC disbursed", f"${s['pac_total_disbursed']:,.0f}")
        c4.metric("Bills lobbied", s["n_bills_lobbied"])

        st.subheader("Lobbying (LDA, aggregated per org)")
        st.dataframe(result["lobbying"], use_container_width=True)

        st.subheader("Matched PAC(s) (FEC)")
        st.dataframe(result["pacs"], use_container_width=True)

        st.subheader("Where the PAC money went (top disbursements)")
        st.dataframe(result["disbursements"].head(25), use_container_width=True)

        st.subheader("Bills lobbied (named in lobbying text → Congress)")
        bills = result["bills"]
        st.dataframe(bills.head(30), use_container_width=True)
        if not bills.empty:
            st.bar_chart(bills.head(15).set_index("bill_key"))
            st.download_button("Download bills (CSV)", bills.to_csv(index=False),
                               file_name=f"{org}_bills.csv", mime="text/csv")

with tab_batch:
    default = "Pfizer\nLockheed Martin\nExxon Mobil"
    raw = st.text_area("Watchlist (one org per line)", value=default, height=120)
    st.caption("DEMO_KEY is rate-limited (~hundreds/hr). Keep the list short or add a real FEC key.")
    if st.button("Run batch"):
        orgs = [o.strip() for o in raw.splitlines() if o.strip()]
        rows, prog = [], st.progress(0.0)
        for i, o in enumerate(orgs, 1):
            try:
                rows.append(trace_org(o, year=int(year), cycle=int(cycle),
                                      fec_key=fec_key, threshold=threshold)["summary"])
            except Exception as exc:  # keep going if one org errors / rate-limits
                st.warning(f"skip {o}: {exc}")
            prog.progress(i / len(orgs))
        if rows:
            summary_df = (pd.DataFrame(rows)
                          .sort_values("total_lobbying_usd", ascending=False)
                          .reset_index(drop=True))
            st.dataframe(summary_df, use_container_width=True)
            st.bar_chart(summary_df.set_index("org")["total_lobbying_usd"])
            st.download_button("Download summary (CSV)", summary_df.to_csv(index=False),
                               file_name="watchlist_summary.csv", mime="text/csv")
