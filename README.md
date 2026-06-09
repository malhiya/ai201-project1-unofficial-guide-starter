# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | General advice for a CS major at UMass | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/1qh90xg/accepted_to_umass_cs_need_some_advice/ |
| 2 | CS professor opinions — who to take/avoid | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/g223hu/for_those_who_are_cs_majors_what_teachers_to_take/ |
| 3 | Dining hall recommendations | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/1nwe70y/best_dining_hall_opinion/ |
| 4 | Dorm / residential area recommendations | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/1c2du2h/where_should_i_dorm_oncampus/ |
| 5 | Fun filler classes to take | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/1jserh4/cool_classes_to_take/ |
| 6 | Club recommendations | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/1f48q6v/best_clubs/ |
| 7 | Best professors at UMass | Reddit (r/umass) | https://www.reddit.com/r/umass/comments/mu2up/name_the_best_professor_youve_ever_had_at_umass/ |
| 8 | CS professor ratings | Rate My Professor | https://www.ratemyprofessors.com/search/professors/1513?q=*&did=11 |
| 9 | CS clubs / student organizations at UMass | UMass CICS page | https://www.cics.umass.edu/community/student-organizations |
| 10 | CS student-organization events | UMass CICS page | https://www.cics.umass.edu/category/student-organization?page=0 |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** Most of these sources are Reddit threads where each comment is one short student opinion, so 500 characters is large enough to keep a single opinion together but small enough to avoid mixing unrelated comments. When chunks got bigger, unrelated comments got grouped together and the embeddings became less accurate. The 100 character overlap carries a little context across each boundary so an opinion that splits between two chunks can still be found.

**Final chunk count:** 130

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2

**Production tradeoff reflection:** If  cost was not a concern, a larger API hosted model that understands meaning more accurately would result in more accurate answers. The weakest results came from questions that were worded differently than the source text. A bigger model with a longer context length would also embed larger chunks without losing detail, which could help on broad questions. 

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt tells the model that it is The Unofficial Guide and must answer using only the retrieved student sources, with no outside knowledge. It is told that if the context does not contain enough information, it must plainly say "I don't know, the sources I have don't cover that" instead of guessing. The retrieved chunks are passed into the prompt as clearly labeled source blocks, and we use a low temperature so the model stays close to the actual text.

**How source attribution is surfaced in the response:** Every chunk is stored with its source document name in its metadata, so we always know where a retrieved passage came from. After generating an answer we collect those sources, remove duplicates, and return them alongside the answer. In the Gradio interface they appear in a separate "Retrieved from" box that lists each source by topic and file name.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which CS professor do students recommend, and why? | Professor Matthew Rattigan is repeatedly recommended — students call him "very understanding and generous" and "a great guy and lecturer" (with one caveat that he isn't very active on Piazza). *Source: cs-teachers-reddit.txt; also rate-my-professor.txt. | Similar to expected with more information like course number | Relevant | Accurate |
| 2 | Which dining hall is best for healthy eating? |Hampshire ("Hamp") is considered to have the healthiest options — it reportedly doesn't serve soda and has smoothies made with real fruit, and students praise its variety and short lines. *Source: dining-halls-reddit.txt.* | Similar to expected plus other dining halls mentioned as well| Relevant | Accurate |
| 3 |I don't like big crowds or noise — which residential area should I avoid? |  Southwest. It's the largest concentration of students on campus (~5,500), "gets very loud at night," and is farthest from most classes. Students suggest ranking it low if you prefer fewer people; Central is recommended instead for being close to classes. *Source: dorm-recs.txt.*| Answers the question, but doesn;t recommend alternatives| Relevant|Partially accurate |
| 4 | As a CS major, will I have enough time for clubs and extracurriculars?  | Yes, students consistently report a good work-life balance and "always had time for clubs." The workload is manageable outside the core classes (CS 311 and maybe CS 220 are the hard ones). *Source: general-cs-advice.txt.*| Somewhat similar to the expected but didn't mention core classes | Somewhat relevant | Partially accurate|
| 5 | How much does a UMass student meal plan cost per semester?| "I don't know" / not enough information. None of the collected documents cover meal-plan pricing, the dining sources only discuss student opinions on which dining hall is best, not costs.*| Similar, just says "I don't know" part from the expected answer|  Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** How is Marc Liberatore as a professor??

**What the system returned:** I don't know — the sources I have don't cover that.

This is wrong since the rate-my-professors.txt file has a content with the named Professor so the summmary of the review should have been generated *

**Root cause (tied to a specific pipeline stage):** This is a retrieval and chunking problem. In rate-my-professor.txt each professor is only a short stats block, so 500 character chunking packs several professors into one chunk, and that mixed chunk does not match a query about one specific name well enough to land in the top 5, so the model correctly says it does not know.

**What you would change to fix it:** I would chunk this file one professor per chunk so each professor's information embeds as its own unit, and I could also raise the top-k a little so a weaker match still gets retrieved.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Planning.md helped shaped my implementation because I was able to go off of the plan that was created from filling it out. I was able to refer to the diagram as I moved through each step of the implementation and refer it to Claude when creating the app. And having sample questions and the expected answers helped to keep in mind how to instruct the LLM to respond.

**One way your implementation diverged from the spec, and why:** The architecture diagram first planned 1,200 character chunks with 200 character overlap, but I ended up using 500 character chunks with 100 overlap. The switch was done  because the larger chunks grouped unrelated Reddit comments together and made the embeddings less accurate, so smaller chunks gave cleaner, more relevant retrieval.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My Retrieval Approach section and the architecture diagram from planning.md, and asked it to build the embedding and retrieval step.
- *What it produced:* retriever.py, which embeds the chunks with all-MiniLM-L6-v2, stores them in ChromaDB with source metadata, and returns the top 5 chunks for a query.
- *What I changed or overrode:* I had it also store each chunk's position in its document so the sources could be attributed more precisely.

**Instance 2**

- *What I gave the AI:* My grounding requirement (answer only from retrieved context with source attribution) and asked it to connect retrieval to the Groq llama-3.3-70b-versatile model.
- *What it produced:* generator.py with a system prompt that forbids outside knowledge and tells the model to say "I don't know" when the context does not cover the question.
- *What I changed or overrode:* I tested it on my evaluation questions and confirmed the "I don't know" behavior on the meal plan question, which is what surfaced the professor retrieval problem in the failure analysis.
