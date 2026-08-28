# Clinical Evidence Assistant — Full-Stack AI Medical Evidence Research System

> **Project goal:** Build a production-style, mobile-first clinical evidence research assistant that searches biomedical literature, retrieves evidence, synthesizes findings with citations, verifies citations against source text/metadata, detects unsupported claims, and clearly communicates uncertainty.
>
> **Safety boundary:** This application is a **research and evidence-synthesis tool**, not a diagnostic system, prescribing system, emergency service, or substitute for a licensed clinician. It must not present an AI-generated recommendation as medical advice.

---

## 1. Executive Summary

### Product name

**Clinical Evidence Assistant (CEA)**

### Core user story

A user asks:

> "What does current research say about the effectiveness of metformin for type 2 diabetes in adults?"

The system should:

1. Understand the research question.
2. Rewrite the question into searchable biomedical queries.
3. Search multiple literature sources.
4. Deduplicate papers.
5. Rank evidence.
6. Retrieve abstracts/full text when legally and technically available.
7. Extract study characteristics.
8. Identify outcomes and limitations.
9. Detect conflicting evidence.
10. Generate an evidence synthesis.
11. Attach citations to individual claims.
12. Verify that each citation actually supports its claim.
13. Calculate a transparent confidence/evidence score.
14. Show the user the original papers and metadata.
15. Never fabricate a paper, DOI, PMID, result, author, or statistic.

---

# 2. Why This Is a Strong AI Engineering Portfolio Project

This project should demonstrate much more than "LLM + RAG".

It should demonstrate:

- LLM application engineering
- Retrieval-Augmented Generation
- biomedical information retrieval
- multi-source search
- semantic search
- hybrid search
- reranking
- citation grounding
- hallucination detection
- evidence grading
- agent orchestration
- structured extraction
- asynchronous processing
- API design
- database design
- caching
- observability
- evaluation
- security
- responsive UI
- production deployment

The project should be presented as:

> **An evidence-grounded AI research system for biomedical literature — not an AI doctor.**

---

# 3. High-Level Architecture

```text
                         USER
                           |
                           v
              +-------------------------+
              | Next.js Web Application  |
              | Mobile-first UI          |
              +------------+------------+
                           |
                           | HTTPS
                           v
              +-------------------------+
              | FastAPI API Layer       |
              | Authentication          |
              | Rate Limiting           |
              | Validation              |
              +------------+------------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
      Query Orchestrator          Research Database
             |                    PostgreSQL/pgvector
             |
       +-----+-----+--------+---------+
       |           |        |         |
       v           v        v         v
    PubMed      PMC      Semantic   OpenAlex/
                           Scholar  Crossref
       |           |        |         |
       +-----------+--------+---------+
                           |
                           v
                  Paper Normalization
                           |
                           v
                    Deduplication
                           |
                           v
                    Hybrid Retrieval
                  /        |         \
             BM25       Embeddings   Metadata
                  \        |         /
                           v
                       Reranker
                           |
                           v
                   Evidence Extractor
                           |
                           v
                    LLM Synthesizer
                           |
                           v
                   Claim Extraction
                           |
                           v
                  Citation Verification
                           |
                           v
                    Safety / QA Gate
                           |
                           v
                   Final Evidence Report
```

---

# 4. Recommended Technology Stack

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Server Components where appropriate
- TanStack Query for client-side API state
- Zod
- Recharts
- Lucide icons

## Backend

- Python
- FastAPI
- Pydantic
- httpx
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector

## AI

Primary development options:

- Gemini API
- OpenAI-compatible provider
- Groq
- OpenRouter
- Local Qwen/Llama/Gemma models

For low-cost development, implement an **LLM provider abstraction** so the application is not locked to one provider.

```text
LLMProvider
   |
   +-- GeminiProvider
   +-- OpenAIProvider
   +-- GroqProvider
   +-- LocalProvider
```

## Biomedical sources

### PubMed / NCBI

Use NCBI E-utilities for PubMed search and retrieval.

NCBI's E-utilities provide programmatic access to PubMed and other Entrez databases.

Official documentation:

https://www.ncbi.nlm.nih.gov/home/develop/api/

The E-utilities documentation also recommends identifying your application using `tool` and `email`, and has documented rate limits/API-key behavior.

### PubMed Central

Use PMC where appropriate for open-access full text.

### Semantic Scholar

Use Semantic Scholar for paper metadata, citation relationships, recommendations, abstracts where available, and academic graph information.

Official API:

https://www.semanticscholar.org/product/api

### OpenAlex

Use OpenAlex as an additional scholarly metadata source when useful.

### Crossref

Use Crossref for DOI metadata verification.

---

# 5. Important Medical-Safety Design

This is one of the most important parts of the project.

## The application MUST NOT:

- diagnose a patient
- prescribe medication
- recommend medication dosage
- tell a patient to stop medication
- claim a treatment is definitely safe
- invent clinical guidelines
- fabricate studies
- fabricate citations
- replace a clinician
- provide emergency instructions as a substitute for emergency services

## The application SHOULD:

- present evidence
- summarize research
- identify uncertainty
- identify conflicting studies
- distinguish study types
- distinguish association from causation
- show publication dates
- show limitations
- show evidence quality
- show citations beside claims
- encourage consultation with qualified healthcare professionals for personal medical decisions

---

# 6. Core Features

## MVP

### Search

User enters:

```text
What does current research say about GLP-1 receptor agonists and cardiovascular outcomes?
```

The system returns:

- relevant studies
- publication year
- authors
- journal
- DOI
- PMID
- study type
- abstract
- relevance score

---

## Evidence Synthesis

Generate:

### Executive Summary

Short explanation.

### Key Findings

Bullet points.

### Evidence Table

| Study | Year | Type | Population | Intervention | Outcome | Result | Limitations |
|---|---:|---|---|---|---|---|---|

### Conflicting Evidence

Identify disagreements between studies.

### Evidence Gaps

Explain what research does not establish.

### Confidence

Example:

```text
Overall evidence confidence: MODERATE
```

---

# 7. Advanced Features

## 7.1 Query Expansion

Original query:

```text
metformin cardiovascular outcomes
```

Generate:

```text
metformin AND cardiovascular outcomes
metformin AND cardiovascular disease
metformin AND myocardial infarction
metformin AND stroke
metformin AND mortality
```

Do not blindly trust LLM-generated queries.

Validate them before sending to APIs.

---

# 8. Research Pipeline

## Stage 1 — Query Understanding

Input:

```json
{
  "question": "Does metformin reduce cardiovascular risk?"
}
```

Output:

```json
{
  "population": "Adults with type 2 diabetes",
  "intervention": "Metformin",
  "comparison": "No metformin / alternative treatment",
  "outcomes": [
    "cardiovascular events",
    "myocardial infarction",
    "stroke",
    "mortality"
  ],
  "study_types": [
    "systematic review",
    "meta-analysis",
    "randomized controlled trial",
    "cohort study"
  ]
}
```

Use a PICO-style representation:

```text
P = Population
I = Intervention
C = Comparison
O = Outcome
```

---

# 9. Literature Retrieval

Run sources concurrently.

```python
results = await asyncio.gather(
    pubmed.search(query),
    semantic_scholar.search(query),
    openalex.search(query)
)
```

Normalize everything into one schema.

```python
class Paper(BaseModel):
    title: str
    authors: list[str]
    abstract: str | None
    year: int | None
    journal: str | None
    doi: str | None
    pmid: str | None
    pmcid: str | None
    url: str | None
    source: str
    study_type: str | None
```

---

# 10. PubMed Integration

Recommended flow:

```text
ESearch
   ↓
PMIDs
   ↓
ESummary / EFetch
   ↓
Normalized Paper
```

Use the official NCBI E-utilities endpoints.

Do not scrape PubMed HTML when an official API is available.

Store:

```text
pmid
title
abstract
authors
journal
publication_date
publication_type
mesh_terms
doi
pmc_id
```

Respect NCBI's API usage requirements and rate limits.

---

# 11. Semantic Scholar Integration

Use Semantic Scholar for:

- paper search
- paper metadata
- citation graph
- references
- recommendations
- author information

Normalize results into the same internal `Paper` schema.

Do not expose API keys to the browser.

---

# 12. Deduplication

The same paper may appear from multiple providers.

Deduplication priority:

```text
DOI
 ↓
PMID
 ↓
PMCID
 ↓
Normalized title
 ↓
Fuzzy title similarity
```

Example:

```python
if doi_a and doi_a == doi_b:
    duplicate = True
elif pmid_a and pmid_a == pmid_b:
    duplicate = True
elif rapidfuzz_ratio(title_a, title_b) > 95:
    duplicate = True
```

Keep the richest metadata record.

---

# 13. Evidence Ranking

Do NOT rank papers only by semantic similarity.

Create a combined score:

```text
Final Score =
    0.35 * Semantic Similarity
  + 0.20 * Keyword Relevance
  + 0.15 * Study Design Score
  + 0.10 * Recency
  + 0.10 * Citation/Metadata Quality
  + 0.10 * Source Reliability
```

The exact weights should be configurable and experimentally evaluated.

---

# 14. Study-Type Classification

Classify papers into:

```text
Systematic Review
Meta-analysis
Randomized Controlled Trial
Clinical Trial
Cohort Study
Case-Control Study
Cross-sectional Study
Case Report
Animal Study
In-vitro Study
Protocol
Review
Other
```

Never infer study quality solely from the title.

Use metadata and paper text when available.

---

# 15. Evidence Extraction

For each paper extract:

```json
{
  "study_design": "...",
  "population": "...",
  "sample_size": 0,
  "intervention": "...",
  "comparison": "...",
  "primary_outcomes": [],
  "secondary_outcomes": [],
  "main_results": [],
  "limitations": [],
  "conflicts_of_interest": [],
  "funding": [],
  "certainty": "low|moderate|high|unknown"
}
```

Every extracted field should retain a source reference.

---

# 16. Evidence Graph

Create an internal evidence graph.

```text
Question
   |
   +---- Study A
   |       |
   |       +-- supports claim 1
   |
   +---- Study B
   |       |
   |       +-- contradicts claim 1
   |
   +---- Study C
           |
           +-- supports claim 2
```

This makes conflicting evidence easier to identify.

---

# 17. Citation-Aware Generation

Never generate:

```text
Metformin reduces cardiovascular mortality by 25%.
```

without knowing exactly where the number came from.

Instead create structured claims:

```json
{
  "claim_id": "claim_001",
  "text": "Study X reported lower cardiovascular events.",
  "source_ids": ["paper_123"],
  "support_type": "direct",
  "confidence": 0.91
}
```

Then render:

```text
Study X reported lower cardiovascular events. [1]
```

---

# 18. Citation Verification

This should be one of the project's flagship features.

For every generated claim:

```text
Claim
 ↓
Retrieve cited source
 ↓
Extract supporting passage
 ↓
LLM/NLI verifier
 ↓
Support classification
```

Output:

```text
SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
CONTRADICTED
UNVERIFIABLE
```

Example:

```text
Claim:
"Study A found a 30% reduction."

Citation:
Study A

Verification:
PARTIALLY_SUPPORTED

Reason:
The study reports a relative risk reduction but does not support
the exact 30% figure stated by the generated answer.
```

The system should then either:

1. revise the claim,
2. remove the claim,
3. lower confidence.

---

# 19. Hallucination Detection

Calculate:

```text
Hallucination Rate =
Unsupported Claims / Total Claims
```

Target:

```text
< 5%
```

But do not claim the target is achieved until you actually benchmark it.

---

# 20. Answer Generation Pipeline

Recommended architecture:

```text
User Question
      ↓
Question Parser
      ↓
Query Expansion
      ↓
Multi-Source Retrieval
      ↓
Deduplication
      ↓
Evidence Ranking
      ↓
Evidence Extraction
      ↓
Conflict Detection
      ↓
Evidence Synthesis
      ↓
Claim Extraction
      ↓
Citation Verification
      ↓
Safety Gate
      ↓
Final Answer
```

Do not have one LLM call perform all of these tasks.

---

# 21. Backend Architecture

```text
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── search.py
│   │   │   ├── research.py
│   │   │   ├── papers.py
│   │   │   ├── citations.py
│   │   │   └── evaluations.py
│   │   │
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   ├── paper.py
│   │   ├── research.py
│   │   ├── claim.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── search.py
│   │   ├── research.py
│   │   └── response.py
│   │
│   ├── services/
│   │   ├── search/
│   │   │   ├── pubmed.py
│   │   │   ├── semantic_scholar.py
│   │   │   ├── openalex.py
│   │   │   └── crossref.py
│   │   │
│   │   ├── retrieval/
│   │   │   ├── hybrid.py
│   │   │   ├── embeddings.py
│   │   │   └── reranker.py
│   │   │
│   │   ├── ai/
│   │   │   ├── provider.py
│   │   │   ├── query_planner.py
│   │   │   ├── synthesizer.py
│   │   │   ├── verifier.py
│   │   │   └── safety.py
│   │   │
│   │   └── research/
│   │       ├── pipeline.py
│   │       ├── extraction.py
│   │       └── conflict.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   ├── models.py
│   │   └── repositories.py
│   │
│   └── tests/
│
├── requirements.txt
├── pyproject.toml
└── alembic.ini
```

---

# 22. Frontend Architecture

```text
frontend/
├── app/
│   ├── page.tsx
│   ├── research/
│   │   └── [id]/
│   │       └── page.tsx
│   ├── papers/
│   │   └── [id]/
│   │       └── page.tsx
│   ├── history/
│   │   └── page.tsx
│   ├── settings/
│   │   └── page.tsx
│   └── layout.tsx
│
├── components/
│   ├── search/
│   ├── research/
│   ├── evidence/
│   ├── citations/
│   ├── papers/
│   ├── charts/
│   ├── navigation/
│   └── ui/
│
├── lib/
│   ├── api.ts
│   ├── types.ts
│   ├── utils.ts
│   └── validation.ts
│
├── hooks/
│   ├── useResearch.ts
│   ├── useSearch.ts
│   └── usePapers.ts
│
└── public/
```

---

# 23. Mobile-First UI

The UI should be designed for:

```text
320px
375px
390px
430px
768px
1024px
1440px+
```

Do not design desktop first and then squeeze it into mobile.

Design mobile first.

---

# 24. Mobile Navigation

Use:

```text
┌──────────────────────────┐
│ Clinical Evidence        │
│ Assistant          ☰     │
├──────────────────────────┤
│                          │
│ Ask a research question  │
│                          │
│ ┌──────────────────────┐ │
│ │ What does research  │ │
│ │ say about...        │ │
│ └──────────────────────┘ │
│                          │
│ [ Search Evidence ]      │
│                          │
├──────────────────────────┤
│ Recent Research          │
│                          │
│ • Diabetes treatment     │
│ • Cardiovascular risk   │
│ • GLP-1 outcomes         │
│                          │
└──────────────────────────┘
```

Bottom navigation:

```text
Home
Search
Saved
History
Settings
```

---

# 25. Desktop Layout

```text
+-------------------------------------------------------+
| Logo                    Search            Profile     |
+-------------+-----------------------------------------+
|             |                                         |
| Navigation  | Research Question                        |
|             |                                         |
| Home        | [ What does current research say...? ] |
| Research    |                                         |
| Saved       | [ Search ]                               |
| History     |                                         |
| Settings    |-----------------------------------------|
|             | Evidence Summary                        |
|             |                                         |
|             | Findings | Studies | Conflicts | Gaps |
|             |                                         |
+-------------+-----------------------------------------+
```

---

# 26. Research Result Page

Create these sections:

### 1. Research Question

Show exactly what the system analyzed.

### 2. Executive Summary

3–6 sentences.

### 3. Evidence Strength

```text
High
Moderate
Low
Very Low
Unknown
```

### 4. Key Findings

Each finding must contain citations.

### 5. Evidence Table

Scrollable horizontally on mobile.

### 6. Conflicting Evidence

Use cards:

```text
Supports
----------------
Study A
Study B

Conflicts
----------------
Study C
```

### 7. Limitations

### 8. Research Gaps

### 9. References

### 10. Verification Report

```text
12 claims analyzed

10 supported
1 partially supported
1 removed

Citation coverage: 91.7%
```

---

# 27. Mobile Evidence Cards

Instead of huge tables on mobile:

```text
┌─────────────────────────────┐
│ Study Title                 │
│ 2025 · RCT                  │
│                             │
│ Population                  │
│ 2,140 adults                │
│                             │
│ Main finding                │
│ ...                         │
│                             │
│ Evidence: MODERATE          │
│                             │
│ [View Study] [Citation]     │
└─────────────────────────────┘
```

---

# 28. Visual Design

Recommended style:

### Theme

Clean scientific / medical SaaS.

Avoid:

- excessive gradients
- childish illustrations
- huge glowing AI text
- fake "doctor AI" branding
- excessive animation

Use:

- white/neutral backgrounds
- subtle borders
- rounded cards
- strong typography
- clear evidence badges
- restrained accent colors
- excellent spacing

---

# 29. Accessibility

Implement:

- WCAG-conscious contrast
- keyboard navigation
- semantic HTML
- screen-reader labels
- focus states
- reduced-motion support
- accessible charts
- minimum touch target around 44px

---

# 30. API Design

## Health

```http
GET /api/health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Search

```http
POST /api/search
```

Request:

```json
{
  "query": "metformin cardiovascular outcomes",
  "limit": 20
}
```

---

## Start research

```http
POST /api/research
```

Request:

```json
{
  "question": "What does current research say about metformin and cardiovascular outcomes?"
}
```

Response:

```json
{
  "research_id": "res_123",
  "status": "processing"
}
```

---

## Get research

```http
GET /api/research/{research_id}
```

---

## Get papers

```http
GET /api/research/{research_id}/papers
```

---

## Get verification

```http
GET /api/research/{research_id}/verification
```

---

# 31. Database Schema

## users

```text
id
email
created_at
```

## research_queries

```text
id
user_id
question
status
created_at
completed_at
```

## papers

```text
id
title
abstract
authors
year
journal
doi
pmid
pmcid
url
source
study_type
created_at
```

## paper_embeddings

```text
paper_id
embedding
model
created_at
```

## research_papers

```text
research_id
paper_id
rank
relevance_score
```

## claims

```text
id
research_id
claim_text
support_status
confidence
created_at
```

## claim_sources

```text
claim_id
paper_id
evidence_text
support_score
```

---

# 32. Vector Search

Use PostgreSQL + pgvector for the first production version.

Embedding pipeline:

```text
Paper
 ↓
Title + Abstract
 ↓
Embedding Model
 ↓
pgvector
```

Query:

```text
User Question
 ↓
Embedding
 ↓
Vector Similarity
 ↓
Top K
```

Combine with keyword search.

---

# 33. Hybrid Retrieval

Use:

```text
Dense Retrieval
+
Keyword Retrieval
+
Metadata Filtering
```

Example:

```text
Final Retrieval Score =
0.50 * Vector Similarity
+
0.30 * BM25
+
0.20 * Metadata Relevance
```

Evaluate these weights instead of assuming they are optimal.

---

# 34. Reranking

Retrieve top 50.

Then rerank:

```text
50 candidates
      ↓
Reranker
      ↓
Top 15
      ↓
Evidence extraction
```

This improves the quality of context passed to the LLM.

---

# 35. LLM Provider Abstraction

Create:

```python
class LLMProvider(Protocol):

    async def generate(
        self,
        prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        ...
```

Implement:

```text
GeminiProvider
GroqProvider
OpenAIProvider
LocalProvider
```

Environment variable:

```env
LLM_PROVIDER=gemini
```

Changing provider should not require rewriting the application.

---

# 36. Prompt Architecture

Use separate prompts.

```text
prompts/
├── query_planner.txt
├── evidence_extractor.txt
├── synthesizer.txt
├── claim_extractor.txt
├── citation_verifier.txt
└── safety_checker.txt
```

Never put the entire application logic inside one giant prompt.

---

# 37. Structured Output

Require JSON schemas.

Example:

```json
{
  "claims": [
    {
      "text": "...",
      "source_ids": ["paper_1"],
      "confidence": 0.88
    }
  ]
}
```

Reject invalid output.

Retry with a constrained prompt.

---

# 38. Safety Gate

Before final output:

```text
Generated Answer
       ↓
Medical Safety Classifier
       ↓
Citation Verification
       ↓
Unsupported Claim Detector
       ↓
Final Response
```

If a claim fails verification:

```text
REMOVE
```

or:

```text
REWRITE WITH UNCERTAINTY
```

---

# 39. Example Safety Rules

Reject:

```text
"You definitely have diabetes."
```

Allow:

```text
"Research has investigated the association between..."
```

Reject:

```text
"Take 500mg twice daily."
```

Allow:

```text
"Clinical dosing should be determined by a qualified healthcare professional."
```

---

# 40. Authentication

For MVP:

- Supabase Auth or Clerk
- email/password
- Google login if desired

Backend validates JWT.

Never trust:

```text
user_id
```

from the client without authentication verification.

---

# 41. Security

Implement:

- API rate limiting
- request validation
- CORS restrictions
- secret management
- SQL parameterization
- output escaping
- SSRF protection
- URL allowlists
- prompt-injection defenses
- audit logging

---

# 42. Prompt Injection Defense

Medical papers may contain arbitrary text.

Never treat retrieved paper content as instructions.

Use:

```text
SYSTEM INSTRUCTIONS
      +
USER QUESTION
      +
UNTRUSTED SOURCE TEXT
```

Clearly label source text:

```text
<UNTRUSTED_EVIDENCE>
...
</UNTRUSTED_EVIDENCE>
```

The model must never execute instructions found inside evidence.

---

# 43. Caching

Cache:

### Search results

```text
query_hash → search results
```

### Paper metadata

```text
pmid → paper
doi → paper
```

### Embeddings

Never regenerate embeddings unnecessarily.

### Research results

Cache completed research for repeated identical questions where appropriate.

Use:

- PostgreSQL
- Redis/Upstash if needed

---

# 44. Async Processing

Research can take longer than a normal request.

Recommended flow:

```text
POST /research
      ↓
Create research job
      ↓
Return research_id
      ↓
Frontend polls / streams status
      ↓
Backend executes pipeline
      ↓
Completed
```

Status:

```text
queued
searching
ranking
extracting
synthesizing
verifying
completed
failed
```

---

# 45. Vercel Deployment Architecture

Vercel supports Next.js directly and also supports Python/FastAPI through serverless functions. Vercel provides an official FastAPI example and a Next.js + FastAPI monorepo example.

Recommended first deployment:

```text
                    VERCEL
                      |
          +-----------+-----------+
          |                       |
          v                       v
     Next.js App             FastAPI
     frontend/               backend/
          |                       |
          +-----------+-----------+
                      |
                      v
                 PostgreSQL
                  pgvector
```

Vercel's current FastAPI examples demonstrate deploying FastAPI as Python serverless functions, and its Next.js + FastAPI starter demonstrates a monorepo deployment. 

---

# 46. Recommended Repository Structure for Vercel

```text
clinical-evidence-assistant/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── public/
│   ├── package.json
│   └── next.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── schemas/
│   ├── requirements.txt
│   └── pyproject.toml
│
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   └── safety.md
│
├── tests/
│
├── vercel.json
├── README.md
└── .gitignore
```

---

# 47. Vercel Configuration

Depending on the current Vercel project configuration, use a monorepo configuration similar to:

```json
{
  "services": {
    "frontend": {
      "root": "frontend/",
      "framework": "nextjs"
    },
    "backend": {
      "root": "backend/",
      "entrypoint": "app.main:app"
    }
  }
}
```

Verify the exact configuration against the current Vercel project/runtime behavior before production deployment.

---

# 48. Environment Variables

Frontend:

```env
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_APP_URL=
```

Backend:

```env
DATABASE_URL=
LLM_PROVIDER=
GEMINI_API_KEY=
OPENAI_API_KEY=
GROQ_API_KEY=
SEMANTIC_SCHOLAR_API_KEY=
NCBI_EMAIL=
NCBI_TOOL_NAME=
NCBI_API_KEY=
CROSSREF_MAILTO=
JWT_SECRET=
```

Never expose:

```text
GEMINI_API_KEY
OPENAI_API_KEY
GROQ_API_KEY
NCBI_API_KEY
DATABASE_URL
JWT_SECRET
```

to the browser.

Only variables prefixed with `NEXT_PUBLIC_` should be considered browser-exposed.

---

# 49. Vercel Deployment Steps

## Step 1 — Create GitHub repository

```bash
git init
git add .
git commit -m "Initial Clinical Evidence Assistant"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY>
git push -u origin main
```

---

## Step 2 — Create PostgreSQL database

Recommended options:

- Supabase
- Neon
- another PostgreSQL provider supporting pgvector

Enable pgvector.

---

## Step 3 — Configure database

Set:

```env
DATABASE_URL=...
```

Run migrations locally.

```bash
alembic upgrade head
```

---

## Step 4 — Configure Vercel

Connect the GitHub repository to Vercel.

Set:

```text
Root/monorepo configuration
Environment Variables
Production
Preview
Development
```

---

## Step 5 — Configure API keys

Add backend secrets in Vercel environment variables.

Do not commit `.env`.

---

## Step 6 — Deploy

Use:

```bash
npm i -g vercel
vercel
```

Then production:

```bash
vercel --prod
```

Vercel also supports Git-based deployments where pushes to the connected repository trigger deployments.

---

# 50. Important Vercel Architecture Limitation

Do not design the system around a permanently running Python worker inside a Vercel serverless function.

Avoid:

```text
Vercel Function
     ↓
20-minute research process
     ↓
Huge PDF processing
```

Instead:

```text
Vercel API
   ↓
Create Job
   ↓
External/managed job execution
   ↓
Database status
   ↓
Frontend polling/streaming
```

For the initial portfolio MVP, keep research batches small and bounded.

For heavier production workloads, move long-running jobs to a dedicated worker service or managed background-job platform while keeping the frontend on Vercel.

---

# 51. Recommended Free/Low-Cost Architecture

```text
Vercel
├── Next.js frontend
└── FastAPI API

Supabase/Neon
└── PostgreSQL + pgvector

NCBI
└── PubMed/PMC

Semantic Scholar
└── Scholarly metadata

OpenAlex
└── Scholarly metadata

LLM Provider
└── Gemini/Groq/OpenRouter/local model
```

This keeps the application inexpensive during development.

---

# 52. Frontend Implementation Phases

## Phase 1 — UI foundation

Build:

- layout
- navbar
- mobile navigation
- search page
- loading states
- error states
- paper cards
- evidence cards

Do not connect AI yet.

---

## Phase 2 — Search

Connect:

```text
Next.js
 ↓
FastAPI
 ↓
PubMed
```

Then add:

```text
Semantic Scholar
OpenAlex
```

---

## Phase 3 — Research pipeline

Implement:

```text
Question
 ↓
Query Planner
 ↓
Search
 ↓
Deduplication
 ↓
Ranking
```

---

## Phase 4 — RAG

Implement:

```text
Embedding
 ↓
Vector Database
 ↓
Hybrid Search
 ↓
Reranking
```

---

## Phase 5 — Evidence extraction

Implement structured extraction.

---

## Phase 6 — Synthesis

Generate evidence-grounded answers.

---

## Phase 7 — Citation verification

Implement claim-level verification.

---

## Phase 8 — Safety layer

Implement:

- unsupported claim removal
- medical safety rules
- uncertainty handling
- disclaimer

---

## Phase 9 — Evaluation

Create benchmark dataset.

---

## Phase 10 — Production deployment

Deploy frontend + backend.

---

# 53. Backend Implementation Order

### Milestone 1

```text
FastAPI
Health endpoint
Pydantic schemas
Logging
Configuration
```

### Milestone 2

```text
PubMed client
Semantic Scholar client
OpenAlex client
Crossref client
```

### Milestone 3

```text
Normalization
Deduplication
Ranking
```

### Milestone 4

```text
PostgreSQL
SQLAlchemy
Alembic
```

### Milestone 5

```text
Embeddings
pgvector
Hybrid retrieval
```

### Milestone 6

```text
LLM provider abstraction
Query planning
Evidence extraction
```

### Milestone 7

```text
Claim extraction
Citation verification
```

### Milestone 8

```text
Safety gate
```

### Milestone 9

```text
Evaluation
Observability
Performance optimization
```

---

# 54. Testing Strategy

Do not only test endpoints.

Use four levels.

## Unit tests

Test:

- query normalization
- deduplication
- scoring
- citation parsing
- safety rules

---

## Integration tests

Test:

```text
API
 ↓
PubMed
 ↓
Database
 ↓
LLM
```

---

## Retrieval tests

Create a golden dataset.

Example:

```json
{
  "query": "metformin cardiovascular outcomes",
  "expected_pmids": [
    "123456",
    "234567"
  ]
}
```

Measure:

```text
Recall@5
Recall@10
MRR
nDCG
```

---

## Generation tests

Measure:

```text
Answer correctness
Citation precision
Citation recall
Faithfulness
Unsupported claim rate
```

---

# 55. Evaluation Dashboard

Build an internal page:

```text
AI Evaluation

Retrieval Recall@5       91.4%
Citation Precision       95.7%
Citation Recall          92.1%
Faithfulness             93.8%
Unsupported Claims        3.1%
Avg Latency              4.2s
Avg Cost                  $0.00X
```

Do not hardcode these numbers.

They must come from actual benchmark runs.

---

# 56. Benchmark Dataset

Create at least:

```text
100 research questions
```

Better:

```text
300 research questions
```

Categories:

- diabetes
- cardiovascular disease
- cancer
- infectious disease
- mental health
- nutrition
- exercise
- pharmacology
- public health

Each query should have human-verified relevant sources.

---

# 57. Human Evaluation

Have reviewers evaluate:

```text
1. Correctness
2. Citation quality
3. Evidence coverage
4. Hallucination
5. Clarity
6. Uncertainty communication
```

Use a 1–5 scale.

Example:

```text
Criterion                Score

Correctness               4.6
Citation quality          4.8
Evidence coverage         4.4
Uncertainty               4.5
Clarity                   4.7
```

---

# 58. Observability

Log:

```text
request_id
user_id
query
retrieval_latency
retrieval_count
llm_latency
token_usage
citation_verification
final_status
```

Never log sensitive patient information unnecessarily.

---

# 59. Performance Optimization

Implement:

### Concurrent API calls

```python
asyncio.gather(...)
```

### Caching

Cache:

- papers
- searches
- embeddings

### Batch operations

Avoid:

```text
1 database request per paper
```

Prefer:

```text
bulk insert
bulk update
```

### Limit context

Don't send 100 full papers to the LLM.

Use:

```text
50 retrieved
↓
15 reranked
↓
8 evidence chunks
↓
LLM
```

---

# 60. UX Loading States

Research should show progress:

```text
✓ Understanding question

✓ Searching PubMed

✓ Searching Semantic Scholar

✓ Removing duplicates

✓ Ranking evidence

● Extracting study findings

○ Checking conflicting evidence

○ Verifying citations

○ Preparing final report
```

This is much better than a generic spinner.

---

# 61. Error Handling

Example:

```text
PubMed unavailable
```

Do not fail the entire research process.

Use:

```text
PubMed       ✓
Semantic     ✓
OpenAlex     ✗
Crossref     ✓
```

Then continue with available sources.

---

# 62. Citation UI

Each citation should be clickable.

Example:

```text
Metformin was associated with lower cardiovascular risk
in several observational studies. [1][2]
```

Click `[1]`:

```text
┌───────────────────────────────┐
│ Citation                      │
│                               │
│ Study title                   │
│ Authors                       │
│ Journal · 2024                │
│                               │
│ Why it supports this claim:   │
│ "..."                         │
│                               │
│ PMID: XXXXX                   │
│ DOI: XXXXX                    │
│                               │
│ [Open Source]                 │
└───────────────────────────────┘
```

---

# 63. Confidence Model

Do not use arbitrary "AI confidence" alone.

Use evidence-derived confidence:

```text
Confidence =
    Source Agreement
  + Study Quality
  + Evidence Directness
  + Citation Verification
  + Retrieval Reliability
```

Then explain the score.

Example:

```text
Moderate confidence

Why:
- 4 relevant studies
- 3 broadly agree
- 1 conflicting study
- 2 studies are observational
- no strong randomized evidence identified
```

---

# 64. Conflict Detection

Example:

```text
Study A:
Treatment associated with lower risk.

Study B:
No significant difference.

Study C:
Possible increased risk in subgroup.

System:

Evidence is mixed.

Possible explanation:
- population differences
- study design
- follow-up duration
- outcome definition
```

Do not force the literature into one conclusion.

---

# 65. Research Quality

Add a study-quality explanation:

```text
Study type:
Randomized controlled trial

Strengths:
- randomized design
- defined outcomes
- prospective follow-up

Limitations:
- small sample
- short follow-up
- limited population
```

Do not claim a formal risk-of-bias assessment unless the system actually performs a validated assessment.

---

# 66. PDF / Full-Text Handling

Only process full text when legally and technically available.

Pipeline:

```text
Paper
 ↓
Check Open Access
 ↓
Retrieve allowed full text
 ↓
Parse
 ↓
Chunk
 ↓
Metadata
 ↓
Embedding
```

Do not bypass publisher access controls.

---

# 67. Chunking Strategy

For biomedical papers:

```text
Title
Abstract
Introduction
Methods
Results
Discussion
Conclusion
```

Prefer section-aware chunks.

Example:

```text
chunk_id
paper_id
section
text
token_count
embedding
```

---

# 68. Medical Terminology

Add terminology normalization.

Example:

```text
heart attack
myocardial infarction
MI
```

Map to a common concept.

Potential future integrations:

- MeSH
- UMLS where licensing/access conditions permit
- SNOMED CT where properly licensed

For MVP, start with MeSH/PubMed metadata.

---

# 69. AI Agent Architecture

Don't build a completely autonomous agent first.

Use controlled orchestration:

```text
Research Orchestrator
       |
       +-- Query Planner
       |
       +-- Search Agent
       |
       +-- Evidence Agent
       |
       +-- Synthesis Agent
       |
       +-- Verification Agent
       |
       +-- Safety Agent
```

Each agent has:

- clear input
- clear output
- limited tools
- structured schema
- failure behavior

---

# 70. Example Agent State

```json
{
  "research_id": "res_001",
  "question": "...",
  "pico": {},
  "papers": [],
  "evidence": [],
  "claims": [],
  "verification": [],
  "safety": {},
  "status": "verifying"
}
```

---

# 71. Example End-to-End Output

```text
Research Question

What does current research say about metformin and
cardiovascular outcomes in adults with type 2 diabetes?

------------------------------------------------------

Executive Summary

Current evidence suggests an association between metformin
use and cardiovascular outcomes, but the strength of evidence
varies by study design and outcome.

------------------------------------------------------

Key Findings

1. Several observational studies report an association
   with lower cardiovascular risk. [1][2]

2. Randomized evidence is more limited for some outcomes. [3]

3. Differences in populations and treatment comparisons make
   direct comparison difficult. [1][3]

------------------------------------------------------

Evidence Strength

MODERATE

Why:
• Multiple relevant studies
• Some consistency across evidence
• Important observational-study limitations
• Remaining uncertainty

------------------------------------------------------

Conflicting Evidence

Some studies report no statistically significant difference.

------------------------------------------------------

Limitations

• Study populations differ
• Treatment exposure varies
• Observational studies may contain confounding
• Long-term evidence may be limited

------------------------------------------------------

Citation Verification

Claims analyzed: 8
Supported: 7
Partially supported: 1
Unsupported: 0

Citation coverage: 100%
```

---

# 72. Frontend Pages

Build these pages:

```text
/
├── Landing page

/search
├── Search interface

/research/[id]
├── Research report

/papers/[id]
├── Paper details

/history
├── Previous research

/saved
├── Saved papers/reports

/evaluation
├── Internal benchmark dashboard

/settings
├── Account/settings
```

---

# 73. Landing Page

Hero:

> **Understand Biomedical Evidence Faster**

Subtitle:

> Search scientific literature, compare evidence, verify citations, and explore uncertainty with an AI-assisted research workflow.

CTA:

```text
[Start Research]
```

Include:

```text
Multi-source search
Evidence synthesis
Citation verification
Conflict detection
```

Avoid marketing language such as:

> "Your AI Doctor"

---

# 74. Mobile UX Requirements

Must support:

- one-handed use
- sticky search input
- bottom navigation
- collapsible evidence sections
- swipe-friendly cards
- responsive tables
- readable citation chips
- no horizontal page overflow
- minimum 16px body text
- touch-friendly controls

---

# 75. PWA

Optional but highly recommended.

Add:

- manifest
- installable app
- offline shell
- app icon
- splash screen

Do not cache sensitive medical research content indiscriminately.

---

# 76. SEO

Add metadata:

```text
title
description
Open Graph
Twitter/X card
canonical
```

Important pages:

```text
/
```

and public research methodology pages.

Avoid indexing private research histories.

---

# 77. Analytics

Track only what is necessary.

Possible events:

```text
research_started
research_completed
paper_opened
citation_opened
verification_viewed
error_occurred
```

Do not collect unnecessary sensitive medical queries.

---

# 78. Privacy

The user may enter sensitive information.

Therefore:

- minimize stored query data
- allow deletion
- encrypt data in transit
- protect database access
- avoid unnecessary logging
- never expose one user's research to another
- define retention policies

For the portfolio demo, explicitly state:

> "Do not enter personally identifiable patient information."

---

# 79. Development Roadmap

## Week 1 — Foundation

```text
[ ] Create monorepo
[ ] Next.js setup
[ ] FastAPI setup
[ ] PostgreSQL setup
[ ] Environment configuration
[ ] Basic UI
[ ] Health endpoint
```

## Week 2 — Literature Search

```text
[ ] PubMed client
[ ] Semantic Scholar client
[ ] OpenAlex client
[ ] Crossref client
[ ] Normalized paper schema
[ ] Deduplication
```

## Week 3 — Retrieval

```text
[ ] Embedding model
[ ] pgvector
[ ] Hybrid retrieval
[ ] Reranking
[ ] Search evaluation
```

## Week 4 — AI Research Pipeline

```text
[ ] Query planner
[ ] PICO extraction
[ ] Evidence extraction
[ ] Study classification
[ ] Conflict detection
```

## Week 5 — Grounded Generation

```text
[ ] Evidence synthesis
[ ] Claim extraction
[ ] Citation attachment
[ ] Citation verification
[ ] Hallucination detection
```

## Week 6 — UI

```text
[ ] Research report
[ ] Citation drawer
[ ] Evidence cards
[ ] Mobile layout
[ ] Progress UI
[ ] History
```

## Week 7 — Safety + Evaluation

```text
[ ] Safety gate
[ ] Benchmark dataset
[ ] Human evaluation
[ ] Retrieval metrics
[ ] Citation metrics
[ ] Hallucination metrics
```

## Week 8 — Production

```text
[ ] Security audit
[ ] Rate limiting
[ ] Caching
[ ] Monitoring
[ ] Vercel deployment
[ ] Documentation
[ ] Demo video
```

---

# 80. Git Commit Strategy

Use meaningful commits:

```text
feat: initialize Next.js frontend
feat: initialize FastAPI backend
feat: add PubMed search service
feat: add Semantic Scholar integration
feat: implement paper normalization
feat: implement paper deduplication
feat: add PostgreSQL repository
feat: add pgvector retrieval
feat: add query planner
feat: add evidence extraction
feat: add citation verification
feat: add safety gate
feat: implement research report UI
feat: optimize mobile layout
test: add retrieval benchmark
test: add citation verification benchmark
perf: add literature caching
fix: handle PubMed rate limiting
docs: add architecture documentation
```

---

# 81. README Structure

Your GitHub README should contain:

```text
Clinical Evidence Assistant

1. Demo
2. Screenshots
3. Problem
4. Solution
5. Architecture
6. Features
7. Tech Stack
8. Research Pipeline
9. Citation Verification
10. Safety
11. Evaluation
12. Results
13. Installation
14. Environment Variables
15. Deployment
16. Limitations
17. Future Work
18. License
19. References
```

---

# 82. Recruiter Demo Script

Your demo should take approximately 2–3 minutes.

### Demo 1

Enter:

> What does current research say about treatment X?

### Demo 2

Show:

```text
Searching PubMed
Searching Semantic Scholar
Ranking evidence
```

### Demo 3

Show final report.

### Demo 4

Click a citation.

Show the exact supporting evidence.

### Demo 5

Open:

```text
Verification
```

Show:

```text
8 claims
7 supported
1 partially supported
0 unsupported
```

### Demo 6

Show evaluation dashboard.

This tells the recruiter:

> "I didn't just connect an LLM API. I built an evidence retrieval, verification, evaluation, and safety pipeline."

---

# 83. What NOT to Build

Avoid a project where:

```text
User
 ↓
LLM API
 ↓
Answer
```

That is too basic.

Also avoid:

```text
PDF
 ↓
Embedding
 ↓
Vector DB
 ↓
LLM
```

without evaluation.

Your differentiator should be:

```text
Retrieval
+
Evidence
+
Verification
+
Evaluation
+
Safety
```

---

# 84. Future Version

## V2

Add:

- conversational research
- saved evidence collections
- personalized research workspace
- citation graph visualization
- automatic systematic-review workflow
- evidence timelines
- study comparison
- subgroup analysis
- multilingual research
- voice input

## V3

Add:

- automated evidence table extraction
- meta-analysis assistance
- statistical extraction
- forest plots
- publication-bias analysis
- reproducible research packages

These should be implemented cautiously and clearly labeled as research tooling rather than clinical decision-making.

---

# 85. Portfolio Positioning

Use this project title:

> **Clinical Evidence Assistant — Evidence-Grounded Biomedical Research AI**

Portfolio description:

> A full-stack AI research platform that searches biomedical literature across multiple scholarly sources, performs hybrid retrieval and evidence extraction, synthesizes findings with claim-level citations, detects conflicting evidence, verifies citation support, and evaluates hallucination and retrieval performance.

Resume bullet:

> **Built an evidence-grounded biomedical research AI using FastAPI, Next.js, PostgreSQL/pgvector, multi-source literature retrieval, RAG, structured LLM extraction, and claim-level citation verification; designed evaluation benchmarks for retrieval quality, citation accuracy, and unsupported-claim detection.**

---

# 86. Recommended Final Architecture

```text
                           ┌─────────────────────┐
                           │       USER          │
                           │ Mobile / Desktop    │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │      NEXT.JS        │
                           │ Vercel              │
                           │                     │
                           │ Search UI           │
                           │ Research Report     │
                           │ Evidence Cards      │
                           │ Citation Viewer     │
                           │ Evaluation UI       │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │       FASTAPI       │
                           │ Vercel Python       │
                           │                     │
                           │ Auth                │
                           │ API                 │
                           │ Validation          │
                           │ Orchestration       │
                           └──────────┬──────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
                 ▼                    ▼                    ▼
        ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
        │ Literature     │   │ PostgreSQL     │   │ LLM Provider   │
        │ Sources        │   │ + pgvector     │   │                │
        │                │   │                │   │ Gemini/Groq/   │
        │ PubMed         │   │ Papers         │   │ OpenAI/Local   │
        │ PMC            │   │ Embeddings     │   │                │
        │ Semantic       │   │ Claims         │   └───────┬────────┘
        │ Scholar        │   │ Evidence       │           │
        │ OpenAlex       │   └───────┬────────┘           │
        │ Crossref       │           │                    │
        └───────┬────────┘           │                    │
                │                    │                    │
                └────────────┬───────┴────────────────────┘
                             ▼
                   ┌──────────────────────┐
                   │ Research Orchestrator│
                   └──────────┬───────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       Query Planner    Evidence Agent   Conflict Agent
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Evidence Synthesis  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Claim Extraction    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Citation Verifier   │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Safety / QA Gate    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Verified Report     │
                    └─────────────────────┘
```

---

# 87. Definition of Done

The project is **not finished** when the chatbot answers a question.

It is finished when:

```text
[ ] Multi-source biomedical retrieval works
[ ] Papers are deduplicated
[ ] Evidence is ranked
[ ] Research findings are structured
[ ] Claims have citations
[ ] Citations are verified
[ ] Unsupported claims are removed/revised
[ ] Conflicting evidence is displayed
[ ] Safety layer is implemented
[ ] Retrieval benchmark exists
[ ] Generation benchmark exists
[ ] Mobile UI works
[ ] Desktop UI works
[ ] Authentication works
[ ] Database security is configured
[ ] API secrets are protected
[ ] Vercel deployment works
[ ] README is complete
[ ] Architecture diagram is included
[ ] Demo video exists
```

---

# 88. Final Goal

The strongest version of this project is **not**:

> "I built a medical chatbot."

It is:

> **"I engineered an evidence-grounded biomedical research platform that retrieves scientific literature, evaluates evidence, synthesizes findings, verifies citations at the claim level, detects unsupported statements, communicates uncertainty, and measures its own retrieval and generation quality."**

That positioning makes the project substantially more relevant to **AI Engineer, AI Software Engineer, ML Engineer, RAG Engineer, LLM Engineer, and Research Engineer** roles.

---

## Official Technical References

- Vercel Next.js: https://vercel.com/frameworks/nextjs
- Vercel FastAPI: https://vercel.com/templates/python/fastapi-python-boilerplate
- Vercel Next.js + FastAPI: https://vercel.com/templates/fast-api/next-js-fastapi-starter
- NCBI APIs: https://www.ncbi.nlm.nih.gov/home/develop/api/
- NCBI E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25499/
- Semantic Scholar API: https://www.semanticscholar.org/product/api
- Semantic Scholar API Tutorial: https://webflow.semanticscholar.org/product/api/tutorial

---

## Important Disclaimer

This project is intended for **research, education, and evidence exploration**. It must not be presented as a medical diagnostic, prescribing, or emergency-response system. Users should consult qualified healthcare professionals for personal medical decisions.

