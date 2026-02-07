"""
claude_client.py — Claude API integration for StudyForge.
"""

import json
import re
from anthropic import Anthropic


class ClaudeStudyClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def _call(self, system: str, user_msg: str, max_tokens: int = 4096) -> str:
        response = self.client.messages.create(
            model=self.model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user_msg}])
        return response.content[0].text

    def _parse_json(self, text: str):
        text = text.strip()
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
        if m: text = m.group(1).strip()
        try: return json.loads(text)
        except json.JSONDecodeError: pass
        for s, e in [('[', ']'), ('{', '}')]:
            si, ei = text.find(s), text.rfind(e)
            if si != -1 and ei > si:
                try: return json.loads(text[si:ei+1])
                except: continue
        return None

    def generate_flashcards(self, note_content: str, count: int = 10, context: str = "") -> list:
        system = ("You create high-quality flashcards testing key concepts. "
                  "Each card tests ONE piece of knowledge. Respond with ONLY a JSON array.")
        prompt = f"""Create exactly {count} flashcards from these lecture notes.
Rules: Front=clear question, Back=concise answer. Mix difficulty levels.
{f"Subject: {context}" if context else ""}
Respond ONLY with JSON: [{{"front":"...","back":"..."}}, ...]

--- NOTES ---
{note_content[:8000]}"""
        parsed = self._parse_json(self._call(system, prompt))
        return [c for c in parsed if "front" in c and "back" in c] if isinstance(parsed, list) else []

    def generate_quiz(self, note_content: str, count: int = 5, difficulty: str = "mixed") -> list:
        system = ("You create rigorous MCQ questions testing deep understanding. "
                  "Respond with ONLY a JSON array.")
        prompt = f"""Create {count} MCQ questions. Difficulty: {difficulty}
4 options each. "correct"=0-indexed. Include explanation.
JSON: [{{"question":"...","options":["A...","B...","C...","D..."],"correct":0,"explanation":"..."}}, ...]

--- NOTES ---
{note_content[:8000]}"""
        parsed = self._parse_json(self._call(system, prompt))
        return [q for q in parsed if "question" in q and "options" in q] if isinstance(parsed, list) else []

    def explain_concept(self, concept: str, context: str = "") -> str:
        system = "You are a patient expert tutor. Explain clearly with analogies and examples."
        prompt = f"""Explain: **{concept}**
{f"Context: {context}" if context else ""}
One-line definition, then deeper explanation with analogy, key distinctions. Under 300 words."""
        return self._call(system, prompt, 1500)

    def summarize_notes(self, note_content: str) -> str:
        system = "You create concise structured summaries capturing all key concepts."
        prompt = f"""Summarize these notes. Include:
1. Key Concepts  2. Important Details  3. Connections  4. Potential Exam Topics

--- NOTES ---
{note_content[:10000]}"""
        return self._call(system, prompt, 2000)

    def answer_question(self, question: str, note_content: str = "") -> str:
        system = "You are a knowledgeable tutor. Answer accurately, grounded in notes if provided."
        prompt = question
        if note_content:
            prompt = f"Question: {question}\n\n--- REFERENCE NOTES ---\n{note_content[:6000]}"
        return self._call(system, prompt, 2000)

    @staticmethod
    def test_key(api_key: str, model: str = "claude-sonnet-4-5-20250929") -> tuple[bool, str]:
        """Test if an API key is valid. Returns (success, message)."""
        try:
            client = Anthropic(api_key=api_key)
            resp = client.messages.create(
                model=model, max_tokens=20,
                messages=[{"role": "user", "content": "Say 'connected' only."}])
            return True, "Connected successfully"
        except Exception as e:
            err = str(e)
            if "401" in err or "authentication" in err.lower():
                return False, "Invalid API key"
            elif "404" in err or "model" in err.lower():
                return False, f"Model not found — check model name"
            elif "connection" in err.lower() or "network" in err.lower():
                return False, "Network error — check internet connection"
            return False, f"Error: {err[:120]}"

    def _call_with_model(self, system: str, user_msg: str, max_tokens: int = 4096, model_override: str = None) -> str:
        """Call Claude with an optional model override."""
        response = self.client.messages.create(
            model=model_override or self.model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user_msg}])
        return response.content[0].text

    def generate_hypothetical(self, note_content: str, topic: str = "", model_override: str = None) -> dict:
        """Generate a legal hypothetical scenario from notes.
        Returns dict: {"title": "...", "scenario": "...", "model_answer": "..."}
        """
        system = ("You are a law school professor who creates challenging hypothetical scenarios. "
                  "Create fact patterns that test legal reasoning, issue spotting, and rule application. "
                  "Respond with ONLY a JSON object.")
        prompt = f"""Create a legal hypothetical scenario based on these notes.
{f"Topic focus: {topic}" if topic else ""}

Include:
- A detailed fact pattern with multiple parties and legal issues
- Enough complexity to require analysis of competing arguments
- Realistic but challenging circumstances

Respond ONLY with JSON: {{"title":"...","scenario":"...","model_answer":"A thorough analysis covering all issues, arguments, and likely outcomes"}}

--- NOTES ---
{note_content[:8000]}"""
        parsed = self._parse_json(self._call_with_model(system, prompt, model_override=model_override))
        if isinstance(parsed, dict) and "scenario" in parsed:
            return parsed
        return {}

    def grade_hypothetical(self, scenario: str, response: str, model_answer: str = "", model_override: str = None) -> dict:
        """Grade a student's response to a legal hypothetical.
        Returns dict: {"grade": "A/B/C/D/F", "score": 0-100, "feedback": "...", "strengths": [...], "weaknesses": [...]}
        """
        system = ("You are an experienced law professor grading a student's hypothetical analysis. "
                  "Evaluate issue spotting, rule application, analysis depth, and writing quality. "
                  "Respond with ONLY a JSON object.")
        prompt = f"""Grade this student's response to the legal hypothetical.

--- HYPOTHETICAL ---
{scenario[:4000]}

--- STUDENT RESPONSE ---
{response[:6000]}

{f"--- MODEL ANSWER ---{chr(10)}{model_answer[:4000]}" if model_answer else ""}

Evaluate on: Issue spotting, Rule statements, Application/Analysis, Counterarguments, Organization, Writing clarity.
Respond ONLY with JSON: {{"grade":"A/A-/B+/B/B-/C+/C/C-/D/F","score":85,"feedback":"Overall assessment...","strengths":["..."],"weaknesses":["..."]}}"""
        parsed = self._parse_json(self._call_with_model(system, prompt, model_override=model_override))
        if isinstance(parsed, dict) and "grade" in parsed:
            return parsed
        return {}

    def grade_essay(self, prompt_text: str, essay: str, rubric: str = "", model_override: str = None) -> dict:
        """Grade a legal essay, optionally against a rubric.
        Returns dict: {"grade": "...", "score": 0-100, "feedback": "...", "rubric_scores": {...}, "strengths": [...], "weaknesses": [...]}
        """
        system = ("You are an experienced law professor grading a legal essay. "
                  "Evaluate thesis, analysis, use of authority, counterarguments, organization, and writing. "
                  "Respond with ONLY a JSON object.")
        rubric_section = f"\n--- RUBRIC ---\n{rubric[:4000]}\nGrade according to these rubric criteria." if rubric else ""
        user_prompt = f"""Grade this legal essay.

--- ESSAY PROMPT ---
{prompt_text[:2000]}
{rubric_section}

--- STUDENT ESSAY ---
{essay[:8000]}

Respond ONLY with JSON: {{"grade":"A/A-/B+/B/B-/C+/C/C-/D/F","score":85,"feedback":"Overall assessment...","rubric_scores":{{"criterion":"score/description"}},"strengths":["..."],"weaknesses":["..."],"suggestions":["..."]}}"""
        parsed = self._parse_json(self._call_with_model(system, user_prompt, model_override=model_override))
        if isinstance(parsed, dict) and "grade" in parsed:
            return parsed
        return {}

    def generate_participation_questions(self, note_content: str, topic: str = "", model_override: str = None) -> dict:
        """Generate class participation questions from notes.
        Returns dict: {"interesting": [...], "unanswered": [...], "key_questions": [...]}
        """
        system = ("You are a legal education expert identifying questions for class participation. "
                  "Think like a well-prepared law student who has read the material carefully. "
                  "Respond with ONLY a JSON object.")
        prompt = f"""Analyze these legal notes and generate three categories of questions:

1. **Interesting Questions**: Thought-provoking questions that would demonstrate engagement and critical thinking in class
2. **Unanswered/Open Questions**: Questions the material raises but doesn't fully resolve — gaps, ambiguities, or evolving areas of law
3. **Key Questions**: Essential questions a legally-educated student would genuinely want answered to fully understand the material

{f"Topic: {topic}" if topic else ""}

For each question, include a brief note on why it matters.

Respond ONLY with JSON: {{"interesting":[{{"question":"...","why_it_matters":"..."}}],"unanswered":[{{"question":"...","why_it_matters":"..."}}],"key_questions":[{{"question":"...","why_it_matters":"..."}}]}}

--- NOTES ---
{note_content[:8000]}"""
        parsed = self._parse_json(self._call_with_model(system, prompt, model_override=model_override))
        if isinstance(parsed, dict):
            return parsed
        return {}
