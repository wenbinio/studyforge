# Claude.md — Instructions for AI Agents Working on This Repository

## What NOT to Do

These rules are distilled from mistakes made across four separate competitive analysis attempts (`copilot/research-competitive-apps`, `copilot/explore-new-use-cases`, `copilot/explore-new-use-cases-again`, `copilot/add-new-use-cases`). Each produced 1,000–1,800 lines of analysis. Together they totaled ~5,500 lines — of which roughly 55–60% was redundant. The mistakes below appeared in every single attempt.

---

### 1. Do Not Invent Statistics

Every branch cited user counts, market sizes, and growth projections without sources. "30M+ users," "60% prefer mobile," "40% retention increase," "3x engagement" — none had citations. If you don't have a source, say "unverified estimate" or don't include the number. A document full of invented statistics is worse than one with no statistics, because it creates false confidence.

**Bad:** "Quizlet has 60M+ users and a $20/mo pricing model."
**Good:** "Quizlet is one of the largest flashcard platforms. Pricing and user counts should be verified against current public data before making strategic decisions based on them."

### 2. Do Not Ignore the Actual Codebase

Three of the four branches recommended features (React Native mobile, cloud sync, real-time collaboration, PostgreSQL migration) without checking what StudyForge actually is: a ~6,300-line Python/CustomTkinter desktop app with SQLite, no backend server, no API layer, and no test suite. Recommending a mobile app "in 1–2 months" to a project with zero mobile code, zero server infrastructure, and tightly coupled UI-to-database calls is not analysis — it's fantasy.

Before recommending features, read the code. Know what tables exist in database.py, what methods exist in claude_client.py, what the UI can actually render. Reference specific files and line numbers when discussing implementation.

### 3. Do Not Produce Multiple Redundant Documents

Branch 1 produced 4 documents where the quick reference was entirely derivative of the main analysis (~60% redundancy). Branch 3 produced 5 documents where NEW_USE_CASES.md was almost identical to FEATURE_RECOMMENDATIONS.md (~50% redundancy). The total unique content across all four branches was ~2,000–2,500 lines out of ~5,500.

Write one document. If it's long, add a table of contents. Do not split into "Executive Summary" + "Full Analysis" + "Quick Reference" + "Navigation Guide" — this creates maintenance burden, inconsistencies, and the illusion of more work done.

### 4. Do Not Contradict Yourself

Branch 2 ranked image occlusion #2 in its Top 10 list but placed it in the "Low Priority" tier. It called mobile a "critical gap" but put it in Phase 4 (last). Branch 3 marked features as "🔜 Coming Soon" in its competitive matrix while simultaneously advising to prioritize ruthlessly. These contradictions undermine the entire analysis.

Before finishing a document, search for every feature mentioned more than once and verify the priority/ranking is consistent across all mentions.

### 5. Do Not Recommend Without Constraints

Branch 2 listed 100+ features across 17 categories. Branch 4 listed 40+ features across 10 categories. Neither discussed team size, budget, opportunity cost, or what happens if a feature fails. Listing 100 features is not strategy — it's a wishlist.

Every recommendation needs: (a) what it costs to build, (b) what you give up by building it instead of something else, (c) what happens if it fails. If you can't answer those three questions, the recommendation is not ready.

### 6. Do Not Include Irrelevant Competitors

Branch 2 included Grammarly and Khan Academy as competitors. Their feature sets are tangential to a flashcard/SRS study app. The analysis never convincingly connected them to actionable StudyForge improvements. Including them padded the competitor count but diluted the analysis.

Only include competitors that a prospective StudyForge user would realistically evaluate as an alternative. "It's also an education product" is not sufficient justification.

### 7. Do Not Skip Cost Analysis

All four branches recommended AI-powered features (tutor, card generation, quizzes, summaries) in a freemium model without once mentioning that Claude API calls cost money. A free tier with unlimited AI generation could cost more per user than the Pro subscription revenue. None of the branches estimated: API cost per user per month, infrastructure costs for cloud sync, App Store fees, or development labor costs.

If a feature has ongoing operational costs, estimate them. Even a rough estimate ("~$0.02 per AI generation × 50 generations/month = ~$1/user/month") is infinitely better than ignoring costs entirely.

### 8. Do Not Propose Architecture Changes Without Acknowledging the Migration

Three branches recommended migrating from SQLite to PostgreSQL, adding a FastAPI backend, deploying to Firebase, and building a React Native mobile app — while treating these as incremental additions to a Python desktop app. They are not incremental. They are a fundamental rewrite of the application architecture.

If a recommendation requires an architecture migration, say so explicitly. Estimate the migration effort. Identify what breaks during the transition. Don't bury "add PostgreSQL, Redis, Firebase, WebRTC, Stripe" in a roadmap bullet point as if it's a sprint task.

### 9. Do Not Produce a Roadmap Without Resource Assumptions

All three roadmaps (Branches 1, 2, 3) specified timelines ("Phase 1: months 1–3") without stating how many developers are working, how many hours per week, or what their skill sets are. A 3-month Phase 1 for a solo developer is very different from a 3-month Phase 1 for a team of five.

State your resource assumptions at the top of any roadmap. If you don't know the team size, say so and provide estimates for different team sizes (e.g., "1 developer: 6 months, 3 developers: 2 months").

### 10. Do Not Rank Accessibility as Low Priority

Branch 1 noted that accessibility is a "legal requirement in many jurisdictions" and then ranked it in the lowest priority tier. This is contradictory and irresponsible. Accessibility should be integrated into every feature from the start, not treated as a Phase 4 afterthought.

### 11. Do Not Write Analysis Without Reading Previous Analysis

The entire reason four branches exist with 55–60% redundant content is that each started from scratch without reading what the others had already produced. Before writing a competitive analysis, feature recommendation, or strategic document, check whether one already exists in the repository. Read it. Build on it. Don't rewrite it.

### 12. Do Not Confuse "Coming Soon" With "Exists"

Branch 3 marked numerous features as "🔜" in its competitive matrix, implying they were planned or imminent. This blurs the line between what StudyForge can do today and what someone hopes it will do someday. A competitive analysis must be honest about current capabilities. Mark features as ✅ (exists), ❌ (doesn't exist), or 🟡 (partially exists). "Coming soon" is marketing language, not analysis.

### 13. Do Not Omit "What NOT to Build"

Only one branch out of four (Branch 3) included an explicit list of things StudyForge should not attempt. The other three implicitly suggested building everything. A focused product says no to more things than it says yes to. Every analysis should include a "What NOT to Build" section with reasoning.

### 14. Do Not Propose User Research After Building

Branch 1's executive summary recommended "build Phase 1 in months 1–3, then survey users in weeks 2–4." The survey should come before the build decision, not after. Validating assumptions before investing engineering effort is the entire point of user research.

---

## What TO Do Instead

1. **Start by reading the codebase.** Run `find . -name "*.py" | head -30`, open database.py, read the schema. Know what exists before proposing what should exist.
2. **Check for existing analysis.** Search the repo and all branches for related documents before creating new ones.
3. **One document, one purpose.** Write a single document with a clear table of contents. No derivative companion documents.
4. **Cite sources or flag estimates.** Every statistic should either have a citation or be explicitly marked as an estimate.
5. **Include constraints.** Team size, budget, technical debt, and migration costs are not optional context — they are core inputs to any recommendation.
6. **Be honest about current state.** Use ✅/❌/🟡 for what exists today. Don't blur the line with "coming soon."
7. **Say what NOT to build.** Exclusions are as important as inclusions.
8. **Estimate costs.** Especially for AI features, cloud infrastructure, and third-party APIs.
9. **Validate before building.** User research templates are useless if the plan is to build first and ask questions later.
10. **Self-check for contradictions.** Before submitting, search the document for every feature mentioned more than once and verify consistent prioritization.
