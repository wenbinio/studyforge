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
