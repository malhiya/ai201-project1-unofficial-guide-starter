# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
 
This project focuses on student-generated knowledge about UMass Amherst. This program will help student answer important question that might is not usually found in official school resources or documentations, succh as professor quality, dorm experiences, ccourse difficulty, dining hall opinions, and general student advice.

This knowledge is valuable since these are important questions that help a student get a potentially better college experience since they have answers from real student experiences rather than marketing materials or official policies. Students usually search  this information on Reddit threads, Rate My Professor reviews, and other unofficial online platforms.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit|General advice for a CS major at UMass | https://www.reddit.com/r/umass comments/1qh90xg/accepted_to_umass_cs_need_some_advice/ |
| 2 |Reddit |CS professor opinions |https://www.reddit.com/r/umass/comments/g223hu/for_those_who_are_cs_majors_what_teachers_to_take/ |
| 3 | Reddit| Dining Hall recommendations|https://www.reddit.com/r/umass/comments/1nwe70y/best_dining_hall_opinion/ |
| 4 | Reddit| Dorm Reccomendations| https://www.reddit.com/r/umass/comments/1c2du2h/where_should_i_dorm_oncampus/|
| 5 | Reddit | Fun Filler classes| https://www.reddit.com/r/umass/comments/1jserh4/cool_classes_to_take/ |
| 6 | Reddit | Clubs Recommendations|https://www.reddit.com/r/umass/comments/1f48q6v/best_clubs/ |
| 7 | Reddit | Professors Reccomendations | https://www.reddit.com/r/umass/comments/mu2up/name_the_best_professor_youve_ever_had_at_umass/|
| 8 | Rate MY Professor | CS Professor Ratings|https://www.ratemyprofessors.com/search/professors/1513?q=*&did=11|
| 9 |UMass College of Information & Computer Sciences Student Organizations Page |CS clubs at Umass | https://www.cics.umass.edu/community/student-organizations|
| 10 |Umaas CICS | CS Events Page  | https://www.cics.umass.edu/category/student-organization?page=0|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:*500 characters*

**Overlap:*100 characters*

**Reasoning:*Most of the sources are from reddit and the comment sizes vary, but it is safer to be 500 characters becuase it was noticed that a greater chunk size results in groupings of unrelated chunks which impacts the quality of the embeddings. It is worth preventing bad quality embedding. And 100 characters overlap should give enough context for continuity.*

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:*all-MiniLM-L6-v2 via sentence-transformers*

**Top-k:*5*

**Production tradeoff reflection:*Some queries can be very specific and other can be broad and having a fixed k can be simplification*

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which CS professor do students recommend, and why? | Professor Matthew Rattigan is repeatedly recommended — students call him "very understanding and generous" and "a great guy and lecturer" (with one caveat that he isn't very active on Piazza). *Source: cs-teachers-reddit.txt; also rate-my-professor.txt.* |
| 2 | Which dining hall is best for healthy eating? | Hampshire ("Hamp") is considered to have the healthiest options — it reportedly doesn't serve soda and has smoothies made with real fruit, and students praise its variety and short lines. *Source: dining-halls-reddit.txt.* |
| 3 | I don't like big crowds or noise — which residential area should I avoid? | Southwest. It's the largest concentration of students on campus (~5,500), "gets very loud at night," and is farthest from most classes. Students suggest ranking it low if you prefer fewer people; Central is recommended instead for being close to classes. *Source: dorm-recs.txt.* |
| 4 | As a CS major, will I have enough time for clubs and extracurriculars? | Yes — students consistently report a good work-life balance and "always had time for clubs." The workload is manageable outside the core classes (CS 311 and maybe CS 220 are the hard ones). *Source: general-cs-advice.txt.* |
| 5 | How much does a UMass student meal plan cost per semester? | "I don't know" / not enough information. None of the collected documents cover meal-plan pricing, the dining sources only discuss student opinions on which dining hall is best, not costs.* |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The sources are not embedded properly, creating bad quality or useless chunks which can give a bad answer 

2. There can be missing sourcce attributions whicch is an important aspect to credit the answer.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│                  THE UNOFFICIAL GUIDE — RAG PIPELINE                  │
└─────────────────────────────────────────────────────────────────────┘

  [1] DOCUMENT INGESTION
      Reddit threads, Rate My Professor, CICS pages  →  documents/
      Tools: Python file I/O, python-dotenv (config)
                              │
                              ▼
  [2] CHUNKING
      Split text into ~1,200-char chunks, 200-char overlap (~17%)
      Tool: custom chunk_text() in Python
                              │
                              ▼
  [3] EMBEDDING + VECTOR STORE
      Encode each chunk into a vector, store with metadata
      Tools: sentence-transformers (all-MiniLM-L6-v2) → ChromaDB
                              │
                              ▼
  [4] RETRIEVAL                         ◄──────  User query
      Embed query, similarity search             (embedded with
      Return top-k = 5 chunks                     same model)
      Tool: ChromaDB
                              │
                              ▼
  [5] GENERATION
      Build prompt from retrieved chunks, generate grounded answer
      Tool: Groq LLM (llama-3.x)
                              │
                              ▼
  [6] INTERFACE  (Milestone 5)
      User asks questions, sees answer + sources
      Tool: Gradio / Streamlit
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

     Claude Code will be used for the chunking strategy to create the necessary functions like chunk_text. The answer should addresses the query and try to be precise. The domain and resources will be given as an input. The answer should have a source attribution and give more context from the different chunks that were created.  

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
