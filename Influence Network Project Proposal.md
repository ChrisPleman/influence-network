**SIADS 699 \- Project Proposal Form**

**How to Use this Form:**

1. Create a copy of this document so you can edit it.   
2. Please fill out the following information below. We will review your responses and assign a mentor for you. You will also be given feedback on your responses to help guide your planning and approach.  
3. ***Give access to the teaching team*** and provide a link to the document in Canvas.

This proposal is graded on your participation by filling in the text box below. You must submit a proposal for credit. Proposals missing substantial information may be returned for improvement at the teaching team's discretion.

**Only one submission per team is required.**

\--

**Please create a short name for your project and team (such as "Team Avengers").**

Team Glass House

---

**What is the subject of your proposal and what questions do you hope to answer or explore? Please introduce your topic in a brief paragraph.**

Our project aims to uncover the scope of influence that dark money organizations have on politics. By analyzing IRS, FEC, Lobbying, and Congressional data, we will build a dashboard tool that displays the network of dark money laundering, and we will also develop predictive models to measure the effect that this network has on the outcomes of proposed policy.

Our project centers around the flow of dark money via tax-exempt organizations (e.g., 501(c)(4)), who controls these organizations, and how they influence politics via contributions to Super PACs and lobbying congress. Through this project we hope to unveil the scope of political influence, connect who the biggest entities are in this space, and how exactly policy is affected as a result.

---

**If applicable, please describe the dataset(s) you plan to use. You'll want to share the source, access method, and what features of the data you plan to explore.**

We plan to work with several datasets:

- IRS Form 990/990-N/etc.: This is the form that organizations must submit to the IRS to determine if they qualify for the standards required for a 501(c)(4) tax-exempt organization. These data will be sourced from several different places:  
  - [Form 990 Bulk Download](https://www.irs.gov/charities-non-profits/form-990-series-downloads): XML files that contain the information submitted by e-filers. This contains the organization’s EIN, list of employees and their salaries, and signals around their political or lobbying activity. These data go back to 2019 and are downloaded by year and month.  
  - [Form 990-N (e-postcard) download](https://apps.irs.gov/pub/epostcard/data-download-epostcard.zip): (Found [here](https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads)) This is a pipe-delimited text file that contains the data pertaining to the shortened version of the 990 form for tax-exempt organizations with gross receipts of less than $50K dollars a year.  
  - [Older 990 data](https://projects.propublica.org/nonprofits/api): Pro Publica supports a RESTful API to obtain form 990 data in a JSON format. It seems that downloading the pdfs of the forms is rate limited, but otherwise it doesn’t seem to be.  
  - [Current Tax-Exempt Status](https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf): This is a master file maintained by the IRS for currently active tax-exempt organizations. This can be used to more easily search for EINs or Org names, and can be downloaded in bulk or in bulk by state.  
- [Super PAC Data (FEC)](https://www.fec.gov/data/browse-data/?tab=bulk-data): The PAC Summary group contains summary data for receipts and disbursements made by PACs and party committees registered with the FEC dating back to 1996\. Similarly the ‘Contributions by Individuals’ contains data pertaining to contributions made by individuals. Any overlap between 501(c)(4) organizations and/or their members will be cross referenced with the entities in these datasets.  
- [Lobbying data](https://lda.gov/system/public/): Rate-limited (120/Min). This RESTful API provides access to data lobbying fillings, contribution reports, registrants, clients, and lobbyists. We will search for overlap between any 501(c)(4) organizations that partake in lobbying to determine the scope of their contributions/lobbying efforts, and tie into any effects on policy.  
- [Congressional data](https://api.congress.gov/): Use Congress’ api to get a list of bills seen, voted, amended, and nominated on/by the House and the Senate. These data will be used to determine if there is a relationship between the lobbying/support by these tax-exempt organizations and the formulation and evolution of congressional policy. 

---

**Does your dataset have any usage restrictions? Please check for a license associated with the dataset.**

For example, some datasets prohibit redistribution (sharing copies of the data in a public GitHub repository). Some APIs and websites have restrictions, too.

**Form 990:** All confidential information is already redacted. All other information is public.

**Super PAC Data:** All information is usable for non-commercial & academic purposes ([Link](https://www.fec.gov/updates/using-information-obtained-from-fec-reports/) *tip: Search for “May an individual use contributor information for an academic research project?” in the FAQ*).

**Lobbying Data:** There are no restrictions on usage, only that we cite the LDA gov api as a source ([Link](https://lda.gov/api/tos/)).

**Congressional Data:** There is no mention of restrictions for using this data ([Link](https://www.congress.gov/help/using-data-offsite)).

---

**What is the minimum viable product (MVP) that you will turn in? It could be a particular set of analyses presented and interpreted in a report, a tool (like a dashboard) with a particular set of features, a predictive model or something else.**

The MVP should be deliverable whether or not you "find" something interesting in your data. It does not depend on having exciting results. You will be expected to deliver your MVP at the end of class. Please be as clear as possible.

**MVP:** 

1\. A unified dataset: that connects four government data sources that are currently siloed. Today, IRS 990 nonprofit filings, FEC campaign-finance records, Senate lobbying disclosures, and [Congress.gov](http://Congress.gov) bill data each live in separate systems with no shared ID linking them. Our deliverable is a single dataset that links them around two anchors: the organization (e.g., "Pfizer" tied to its nonprofit filings, its PAC, and its lobbying filings) and the bill (which bills each organization lobbied on). Because the sources don't share keys, we build the links ourselves — matching organizations by name and pulling bill numbers out of lobbying text — and for every link we record where it came from and how confident we are in it, so anyone can trace a connection back to the original filing and reproduce the dataset from scratch.  

2\. A dashboard to explore it.:

Search any organization → see its money, lobbying, and the bills it touched, in one place. An interactive network graph of the connections.

3\. An analysis notebook: descriptive network analysis \+ a semantic-alignment score between lobbying-issue text and bill text, presented and interpreted even if the correlation is weak.

---

**What ethical challenges or concerns do you expect to encounter in this project? If there are potential concerns, how do you plan to mitigate them?**

We do not expect to encounter ethical challenges or concerns as all of our data is publicly available, and the output of our work specifically addresses ethical concerns with legal loopholes.

---

**What technical challenges do you anticipate in managing your data and analyses, if any? For example, needing to use large datasets (\>1 GB), difficult data cleaning tasks, a complicated machine learning pipeline, need for specialized tools/libraries/hardware.**

**How will you evaluate the outcomes / claim success for the project?**

**Scope and complexity of the form 990 data set:** The form 990 dataset is a vast set of xml files pertaining to a variety of different organization types **and** form types. We cannot know before parsing an xml file what organization it pertains to, the form type, or the number of additional forms included. Some organizations are required to fill out regular 990s, others 990-EZ or 990-PF, 990-Ts, and more. Each of these have different questions, different xml structure, and different xml element tags for similar information. As a result, the variation and scope of potential targets is quite large. This problem is difficult to mitigate, however, we are considering limiting the scope of form types and form schedules to a more manageable level.

**Connecting the datasets:** We will need to find suitable links between these disparate datasets. Tax-exempt organizations are not required to list their donors, which is the core of the issue. However, they do list the names, EINs, and addresses of orgs they contribute to. This will be the first method of linking information. We will additionally utilize the published list of board members and employees to see if there is overlap between organizations and Super PACs and lobbying activity.

**NLP:** We currently plan to analyze how policy language changes over time as a result of lobbying activity. We plan to use the cosine similarity between policy language to that of lobbying language and missions of the lobbying groups/tax-exempt orgs. This will likely be a time consuming task, and may or may not yield meaningful results. We’ve mitigated the scope of this component by utilizing pre-made sentence transformers, so we don’t need to manage the training.

**Dashboard:** We also want to present this information via a dashboard. This type of tooling can take time to implement, which itself could be a challenge. However, Keerthi already knows how to use Streamlit, so there’s a lower barrier to entry for this path.

---

**How will you evaluate the outcomes / claim success for the project?**

**Evaluating success:**

---

This will depend on the type of project you hope to pursue. If you are making a model, what benchmarks will you measure it against? If you are investigating a hypothesis, what analyses and visuals will you need to present to make your case? If you are making a tool, what features must be ready by the end of class?

A new unified dataset connecting IRS, FEC, Lobbying, and Congressional data.

1. This is the central, novel contribution (no one has joined all four before). Success means it's both connected and trustworthy:  
   1. Connectedness: what share of lobbying filings we tied to at least one bill, what share of organizations we matched to a campaign-finance committee, and what share of nonprofit grants we linked to a real recipient.  
   2. Correctness: because the sources share no common ID, we link them by organization name. We'll hand-check a random sample of matches and report how often they're right and how many we miss, tuning against records that share the same IRS EIN as a known-correct answer key.  
2. Reproducibility: every link traces back to its original filing, and the whole dataset regenerates from our code.

Another deliverable will be a dashboard/application to interact with the network graphs.

1. This will make the dataset and analysis usable to the general public  
   1. Dashboards are more intuitive, and you don’t need a programming background to navigate the large and complex information.  
   2. Dashboard contains information or links to key information pertaining to an organization:  
      1. Name, EIN (IRS org identifier), Address, etc.  
      2. Board members  
      3. Filings  
      4. Lobbying activity  
      5. Radar chart for transparency index  
2. Interactable network graph  
   1. Network graph constructed  
   2. Interactivity  
   3. Default filtering  
3. Expansion of previous research:  
   1. Can include transparency index developed by [Irvin, R.](https://doi.org/10.1515/npf-2022-0032)   
   2. Network graph and analysis expand the scope of work done by [Oklobdzija, S.](http://dx.doi.org/10.2139/ssrn.3189918)  
* Interactable network graph  
* Organization dashboard:  
  * Radar chart for dark money index  
  * Contributions and Activity over time  
  3. Links to actual filings

As a modeling component, we will predict whether a bill advances — that is, whether it moves past committee, passes a chamber, or becomes law, versus dies (as most bills do). The outcome label is read directly from each bill's action history in the [Congress.gov](http://Congress.gov) API.

The model uses features that are all available from data we have already collected:

* Tthe sponsor's party and seniority (number of terms served),  
* The number of cosponsors and how bipartisan they are,  
* Tthe bill's policy are and committee of referral, and  
* Ifwhether the bill was lobbied and how many lobbying filings name it (from our lobbying-text extraction).

We will start with logistic regression, which is interpretable and lets us report how each feature contributes, and compare it against a gradient-boosted tree model as a performance check. Because most bills die, simply guessing "dies" already yields high raw accuracy, so we evaluate with ROC-AUC rather than accuracy. Our central test is an ablation: we train the model with and without the lobbying feature and ask whether lobbying activity adds any predictive power beyond the political features alone — that comparison is the finding, in either direction. As an external reference point, prior work  reached roughly 85% AUC on the related task of predicting whether a bill was lobbied.

We are intentionally scoping the model to features we can build today. Linking individual donations to a bill's sponsors, attributing exact lobbying dollars to a single bill, and member-level vote prediction all require additional data linkages or sources and are treated as stretch goals rather than part of the core model.

---

**Briefly explain the planned contributions of each team member. It might help to have "roles", like Project Manager, Lead Developer, Lead Visualizer or, Lead Analyst.**

Chris:

* Development of the IRS data pipeline ETL/parsing pipeline  
* Documentation

Keerthi:

* Development of the ETL tasks for LDA dataset and Power BI Dashboards.

Matt:

* Tbd

---

**Will your project require any cloud computing tools (Google Colab, AWS, GCP)?**

**Is there anything the teaching team should know to support you in this project? Feel free to ask for resources or extra advising on a certain topic- it never hurts to ask\!**

We'd value advice on record linkage / entity resolution at scale (best practices for name normalization, blocking, and threshold selection without shared keys).

Guidance on honest causal framing for a money→policy association study.

A sanity check on scope: we plan to focus on 2–3 policy domains (e.g., pharma, energy, defense) and the 2024 cycle (118th Congress) to keep the joined dataset tractable — is that the right level of ambition for the timeline?

Note: API rate limits (FEC, LDA) constrain bulk pulls; we're caching aggressively.

Would the school have AWS, or AWS adjacent, offerings for free/low cost to save files in the cloud that we could access in our project and could be used for people in the future to access?

