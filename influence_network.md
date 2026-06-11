# Dark Money Influence Network (Money to Policy)

## One-Line Pitch
Connect publicly available IRS, campaign finance, lobbying disclosure, bill text, and congressional vote data into a unified graph that, then use NLP to measure how much this network influences legislation - and what it costs.

## The Problem
501(c)(4) "social welfare" organizations are not required to disclose their donors. They can spend unlimited money on political activity as long as politics is not their "primary purpose." This legal gray area has produced an enormous shadow political finance system that operates entirely outside FEC disclosure requirements. The IRS Form 990 data is public - it shows organizational revenues, expenses, grant recipients, board members, and officers - but the connections between organizations (shared personnel, grant flows, coordinated spending) have never been mapped systematically. Journalists trace these networks story by story; no systematic computational analysis exists.

The individual pieces of the money-in-politics picture are public: FEC donation records, Senate lobbying disclosures, congressional bill text, and roll call votes. They have never been joined into a single pipeline that answers: "For a given bill, which donors lobbied for it, how similar is the lobbying language to the final bill text, and how did each representative's donors vote?" That question requires combining graph analysis, NLP, and finance data at a scale that has only recently become tractable.

## Why It Fits 699
- Full pipeline:
    - Data collection: Full dataset is generated from several disparate data sources and source types (XML, JSON, CSV; bulk downloads, API)
    - Data Engineering: Development of an ETL pipeline for collecting, cleaning, and joining the data
    - Graph Analysis: Creating several networks based on EINs, board members, and more
    - NLP: Analysis of bill evolution over time, comparisons between organization, PAC, and lobbyist missions and bill text
    - ML: Quantifying the impact that this network has on policy
    - Visualization: Graphs, Feature importance, others?
- Civically important: Everyone in the US is affected by congressional policy, and therefore we should know if/who is financing/influencing that policy. Should we be able to join these data, we would be generating a dataset that future data journalists could use and build upon.
- Covers SIADS 524 (data collection), 632 (graph/network), 642/643 (ML), 682 (NLP)

## Core Concept
1. Download IRS Form 990 XML bulk data from the IRS for daat on/after 2019; Use ProPublica's API for older data.
2. Parse the XML into structured tables: organization EIN, name, revenue, expenses, political activity flag, grant recipients (with EINs), board member names, officer compensation, contractor names and amounts
3. Build the organizational network: nodes are organizations (EIN); edges are:
   - Grant flows (org A → grant → org B, weighted by amount)
   - Shared board members / officers (two orgs with the same named individual)
   - Shared address (same registered address used by multiple orgs)
   - Shared contractors (both organizations pay the same consulting firm)
4. Identify politically active 501(c)(4)s: classify organizations as political based on Schedule C filings (political activity expenditure disclosure) and NLP on the mission/purpose statement
5. Link to FEC data: match political 501(c)(4)s to FEC SuperPAC disbursements and independent expenditures using name matching
6. Link to Senate LDA: which lobbying filings come from organizations in the 501(c)(4) network?
7. Community detection: which clusters of organizations form coordinated spending networks? Which individuals are high-centrality nodes connecting multiple clusters?
8. Dashboard: search any organization or individual, see their 990 network, political spending, and lobbying connections

1. Collect FEC contribution data for all current members of Congress
2. Pull lobbying disclosure filings from the Senate LDA API - includes client, lobbyist, bills lobbied, and issue descriptions
3. Pull bill text from Congress.gov API (full XML)
4. Compute semantic similarity between lobbying issue descriptions and final bill language (sentence embeddings + cosine similarity)
5. Join to roll call votes via GovTrack/ProPublica Congress API
6. Build a bipartite graph: donors → representatives and lobbyists → bills
7. Analyze: does semantic alignment between lobbying language and bill text correlate with donation amount?

## Data Sources

| Source | What It Provides | Access |
|---|---|---|
| FEC API (openFEC) | Campaign contributions, PAC filings, individual donors | Free REST API |
| OpenSecrets Bulk Data | Career finance totals, industry breakdowns (CSV) | Free for educational use |
| Senate LDA API | Lobbying filings: client, lobbyist, bills lobbied, issue text | Free REST API |
| Congress.gov API v3 | Full bill text (XML), amendments, committee reports | Free, requires key |
| GovInfo Bulk Data | Bill text XML bulk download 113th Congress onward | Free |
| ProPublica Congress API | Roll call votes, member profiles | Free |
| GovTrack.us | Ideology scores, voting history | Free |

## Technical Stack

**Collection:** Python (`requests`, `fecfile`, LDA SDK), scheduled pulls to SQLite/PostgreSQL  
**NLP pipeline:** `sentence-transformers` for semantic embeddings; TF-IDF + cosine similarity for bill-to-lobbying text alignment (replicates Jansa et al. 2017 methodology but applied to federal lobbying)  
**Graph:** NetworkX bipartite graph + community detection (Louvain); optionally Neo4j for production  
**ML:** Regression models predicting vote outcome given donor profile + lobbying alignment score  
**Visualization:** Pyvis network graph, Streamlit or Dash dashboard

## Prior Academic Work (Your Differentiator)

- **Jansa, Hansen & Gray (2017)**: Established cosine similarity methodology for detecting model legislation. Applied to ALEC state bills. Your project extends this to federal lobbying vs. bill text.
- **arXiv 2005.06386**: ML models (logistic regression, LSTM) predict whether a bill has been lobbied using bill text features. Achieved 85%+ AUC. Your project adds the financial graph layer.
- **KDD 2016 (Burgess et al.)**: Legislative text reuse via local alignment. Shows the NLP approach is validated.
- **CongressWatch (GitHub)**: Open-source project that already does TF-IDF bill similarity. Your work adds the lobbying-to-bill alignment and the financial network.
- **Gap**: No existing project connects all four layers (finance, lobbying text, bill text, votes) into a unified quantitative pipeline.

## What's Novel
The semantic alignment score between lobbying language and bill text is the key innovation. You can rank bills by "lobbying fingerprint density" - how much of the final text traces back to lobby filings. Correlating this with donation amounts answers a question political scientists have studied qualitatively for decades with actual numbers.

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Senate LDA filings are vague (high-level issue descriptions) | High | Use sentence-level embedding similarity + entity overlap as dual signal; set realistic expectations |
| FEC data is messy (name variations, PAC structures) | Medium | Use OpenSecrets pre-cleaned career totals as primary; FEC for transaction-level |
| Graph is too large to analyze fully in 12 weeks | Medium | Scope to 2-3 specific policy domains (e.g., pharma, energy, defense) |
| Causal claims require more than correlation | Medium | Frame as "association analysis" not causal - honest and still publishable |

## Suggested Scope for 12 Weeks
- Scope to 2 policy domains (e.g., pharmaceutical pricing + energy)
- Collect all lobbying filings mentioning relevant bills, 2015-2024
- Build the donor-lobbyist-bill-vote graph for those domains
- Compute lobbying text vs. bill text alignment scores for 50-100 bills
- Statistical analysis: do higher-alignment bills pass? Do sponsors have more aligned donors?
- Dashboard: enter a bill number, see its influence graph

## Portfolio Impact
Very high. This project directly addresses a question that voters, journalists, and reformers care about. It is the kind of work that gets press coverage and is portfolio-distinguishing at a data science job, government role, or research position.
