# Dark Money Influence Network (Money to Policy)

## Overview
501(c)(4) "social welfare" organizations generally do not need to publicly disclose their donor list, and are not limited in how much money they can spend on political activity as long as politics are not their "primary purpose." These legal loopholes make what is colloquially known as 'Dark Money'.

However, all of these organizations must obtain approval by submitting the IRS Form 990. The information contained in this filing is public, and it contains organizational revenues, expenses, grant recipients, board members, and officers. Alone this data doesn't provide much information on the 'Dark Money' network, but by systematically identifying the connections between organizations (shared personnel, grant flows, coordinated spending) we aim to shine a light on these veiled operations.

To study the impact that 'Dark Money' has on politics, we will analyze these data within the broader context of FEC donation records, Senate lobbying disclosures, congressional bill text, and roll call votes. These data will be joined to study who and how much do these parties influence public policy. This goal will require our team to employ graph analysis and NLP techniques at scale.

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
1. Data collection & cleaning
    - IRS Form 990:
        - Download IRS Form 990 XML bulk data from the IRS for data on/after 2019; Use ProPublica's API for older data.
        - Parse the XML into structured tables: organization EIN, name, revenue, expenses, political activity flag, grant recipients (with EINs), board member names, officer compensation, contractor names and amounts
    - Lobbying data:
        - API calls to the Lobbying data API
        - Format into a relational database (normalize as much as possible)
    - Congressional data:
        - API calls to the Congress API
        - Access the following endpoints (at a minimum):
            - Bill - All bills can be pulled here
            - Bill Details - Connects bills from Bill endpoint to all others
            - Actions - Actions taken on each bill (e.g., introduced to the House)
            - Amendments - Making changes to any given bill
            - Text - The version of the actual bill text over time
            - Notes - Any additional notes congress makes about the bill
            - Sponsors - Who sponsored the bill
            - Cosponsors - Who cosponsored the bill
            - Member - Senator/Representatives
        - Format into a relational database (normalize as much as possible)
    - FEC SuperPAC filings
        - Can bulk download or make requests to their API
        - Obtain the most pertinent form information
2. Build the organizational network: nodes are organizations (EIN); edges are:
        - Grant flows (org A → grant → org B, weighted by amount)
        - Shared board members / officers (two orgs with the same named individual)
        - Shared address (same registered address used by multiple orgs)
        - Shared contractors (both organizations pay the same consulting firm)
        - **Anything else?**
3. Identify politically active 501(c)(4)s: classify organizations as political based on Schedule C filings (political activity expenditure disclosure) and NLP on the mission/purpose statement
4. Link to FEC data: match political 501(c)(4)s to FEC SuperPAC disbursements and independent expenditures using name matching
    - Can we also match via members?
5. Link to Senate LDA: which lobbying filings come from organizations in the 501(c)(4) network?
6. Community detection: which clusters of organizations form coordinated spending networks? Which individuals are high-centrality nodes connecting multiple clusters?
7. Dashboard/Front End: search any organization or individual, see their 990 network, political spending, and lobbying connections
8. Collect FEC contribution data for all current members of Congress
9. Pull lobbying disclosure filings from the Senate LDA API - includes client, lobbyist, bills lobbied, and issue descriptions
10. Pull bill text from Congress.gov API
    - Study changes over time
11. Compute semantic similarity between lobbying issue descriptions and final bill language (sentence embeddings + cosine similarity)
    - **See previous: Does cosine similarity increase over time? As a function of money?**
12. Join to roll call votes via GovTrack/ProPublica Congress API
13. Build a bipartite graph: donors → representatives and lobbyists → bills
14. Analyze: does semantic alignment between lobbying language and bill text correlate with donation amount?


## Data Sources

| Source | What It Provides | Access | Rate Limit |
|---|---|---|---|
| FEC API (openFEC) | Campaign contributions, PAC filings, individual donors | Free REST API | 1,000*-7,200**/hr |
| OpenSecrets Bulk Data | Career finance totals, industry breakdowns (CSV) | Free for educational use | NA |
| Senate LDA API | Lobbying filings: client, lobbyist, bills lobbied, issue text | Free REST API | 120*/Min |
| Congress.gov API v3 | Full bill text (XML), amendments, committee reports | Free, requires key | 5,000*/hr |
| GovInfo Bulk Data | Bill text XML bulk download 113th Congress onward | Free | **What is this?** |
| ProPublica Congress API | Roll call votes, member profiles | Free | **Unsure** |
| GovTrack.us | Ideology scores, voting history | Free | **What is this?** |

\* Requires an API key

\** Email for greater rate limit 


## Technical Stack *We need to confirm this!!*

- **Collection:** Python (`requests`, `fecfile`, LDA SDK)
- **Data Wrangling/Storage**: Pandas, SQLite/PostgreSQL, Spark?
- **NLP pipeline:** `sentence-transformers` for semantic embeddings; TF-IDF + cosine similarity for bill-to-lobbying text alignment (replicates Jansa et al. 2017 methodology but applied to federal lobbying)  
- **Graph:** NetworkX
- **ML:** Regression models predicting vote outcome given donor profile + lobbying alignment score; Logistic regression on determining if a certain lobbied rep/senator votes for a bill?
- **Visualization:** Pyvis network graph, Streamlit or Dash dashboard, Flask?

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
