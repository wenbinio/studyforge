"""
claude_client.py — Claude API integration for StudyForge.

Generates flashcards, quiz questions, explanations, and summaries
from lecture notes using the Anthropic Claude API.
"""

import json
import re
from urllib import request
from anthropic import Anthropic


PROVIDER_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5-20250929",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-1.5-flash",
    "perplexity": "sonar",
}


def detect_provider_from_key(api_key: str) -> str | None:
    """Infer provider from common API key markers."""
    key = (api_key or "").strip()
    if key.startswith("sk-ant-"):
        return "anthropic"
    if key.startswith("sk-proj-") or key.startswith("sk-"):
        return "openai"
    if key.startswith("AIza"):
        return "gemini"
    if key.startswith("pplx-"):
        return "perplexity"
    return None


def get_provider_options(api_key: str = "") -> list[str]:
    """Return provider choices, narrowed by detectable API key marker."""
    detected = detect_provider_from_key(api_key)
    return [detected] if detected else ["anthropic", "openai", "gemini", "perplexity"]


def _post_json(url: str, headers: dict[str, str], payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method="POST")
    with request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


class ClaudeStudyClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929", provider: str | None = None):
        self.api_key = api_key
        self.provider = provider or detect_provider_from_key(api_key) or "anthropic"
        self.model = model or PROVIDER_DEFAULT_MODELS.get(self.provider, PROVIDER_DEFAULT_MODELS["anthropic"])
        if self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None

    def _call(self, system: str, user_msg: str, max_tokens: int = 4096) -> str:
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_msg}]
            )
            return response.content[0].text

        if self.provider in ("openai", "perplexity"):
            url = "https://api.openai.com/v1/chat/completions"
            if self.provider == "perplexity":
                url = "https://api.perplexity.ai/chat/completions"
            data = _post_json(
                url,
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_msg},
                    ],
                    "max_tokens": min(max_tokens, 2048),
                },
            )
            return data["choices"][0]["message"]["content"]

        if self.provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            data = _post_json(
                url,
                {"Content-Type": "application/json"},
                {
                    "contents": [{"parts": [{"text": f"{system}\n\n{user_msg}"}]}],
                    "generationConfig": {"maxOutputTokens": min(max_tokens, 2048)},
                },
            )
            return data["candidates"][0]["content"]["parts"][0]["text"]

        raise ValueError(f"Unsupported provider: {self.provider}")

    def _parse_json_response(self, text: str) -> list | dict | None:
        """Extract JSON from a response that may contain markdown fences."""
        text = text.strip()
        # Try to find JSON in code fences
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find array or object
            for start_char, end_char in [('[', ']'), ('{', '}')]:
                start = text.find(start_char)
                end = text.rfind(end_char)
                if start != -1 and end != -1 and end > start:
                    try:
                        return json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        continue
            return None

    def generate_flashcards(self, note_content: str, count: int = 10, context: str = "") -> list[dict]:
        """
        Generate flashcards from note content.
        Returns list of dicts: [{"front": "...", "back": "..."}, ...]
        """
        system = (
            "You are an expert study assistant that creates high-quality flashcards. "
            "You focus on key concepts, definitions, relationships, and application-level understanding. "
            "Each card should test ONE specific piece of knowledge. "
            "You MUST respond with ONLY a valid JSON array — no commentary, no markdown."
        )
        prompt = f"""Create exactly {count} flashcards from the following lecture notes.

Rules:
- Front: A clear, specific question or prompt (not vague)
- Back: A concise, complete answer
- Mix difficulty levels: definitions, comparisons, applications, edge cases
- Focus on what a student would need for exams
{f"- Context/subject: {context}" if context else ""}

Respond ONLY with a JSON array: [{{"front": "...", "back": "..."}}, ...]

--- NOTES ---
{note_content[:8000]}
"""
        result = self._call(system, prompt)
        parsed = self._parse_json_response(result)
        if isinstance(parsed, list):
            return [c for c in parsed if "front" in c and "back" in c]
        return []

    def generate_quiz(self, note_content: str, count: int = 5, difficulty: str = "mixed") -> list[dict]:
        """
        Generate multiple-choice quiz questions.
        Returns list: [{"question": "...", "options": ["A","B","C","D"], "correct": 0, "explanation": "..."}, ...]
        """
        system = (
            "You are an expert exam question writer. You create rigorous multiple-choice questions "
            "that test deep understanding, not just surface recall. "
            "You MUST respond with ONLY a valid JSON array — no commentary, no markdown."
        )
        prompt = f"""Create exactly {count} multiple-choice questions from these notes.
Difficulty: {difficulty}

Rules:
- 4 options each (A, B, C, D)
- "correct" is the 0-indexed position of the right answer
- Include a brief explanation for the correct answer
- Make distractors plausible — test real understanding
- Vary question types: factual, conceptual, application, analysis

Respond ONLY with a JSON array:
[{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "correct": 0, "explanation": "..."}}, ...]

--- NOTES ---
{note_content[:8000]}
"""
        result = self._call(system, prompt)
        parsed = self._parse_json_response(result)
        if isinstance(parsed, list):
            return [q for q in parsed if "question" in q and "options" in q and "correct" in q]
        return []

    def generate_interleaved_quiz(self, notes: list[dict], count: int = 10, difficulty: str = "mixed") -> list[dict]:
        """
        Generate interleaved quiz questions from MULTIPLE notes.
        notes: list of dicts with "title" and "content" keys.
        Returns list: [{"question": "...", "options": [...], "correct": 0, "explanation": "...", "topic": "..."}, ...]
        """
        system = (
            "You are an expert exam writer specializing in interleaved practice — "
            "a proven learning technique where questions from different topics are deliberately mixed together "
            "to strengthen retrieval and discrimination skills. "
            "You MUST respond with ONLY a valid JSON array — no commentary, no markdown."
        )

        # Build combined notes with topic labels, budget per note
        per_note_chars = max(1000, 7000 // len(notes))
        notes_block = ""
        topic_names = []
        for i, note in enumerate(notes):
            title = note["title"]
            topic_names.append(title)
            notes_block += f"\n--- TOPIC {i+1}: {title} ---\n{note['content'][:per_note_chars]}\n"

        prompt = f"""Create exactly {count} interleaved multiple-choice questions drawn from these {len(notes)} topics.
Difficulty: {difficulty}

INTERLEAVING RULES:
- Distribute questions across ALL topics as evenly as possible
- Randomize the topic order — do NOT group questions by topic
- Include cross-topic comparison questions where topics overlap
- Each question must have a "topic" field with the source topic name

Rules:
- 4 options each (A, B, C, D)
- "correct" is the 0-indexed position of the right answer
- Include a brief explanation for the correct answer
- Make distractors plausible — test real understanding
- The "topic" field must match one of: {topic_names}

Respond ONLY with a JSON array:
[{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "correct": 0, "explanation": "...", "topic": "..."}}, ...]
{notes_block}
"""
        result = self._call(system, prompt, max_tokens=4096)
        parsed = self._parse_json_response(result)
        if isinstance(parsed, list):
            return [q for q in parsed if "question" in q and "options" in q and "correct" in q]
        return []

    def explain_concept(self, concept: str, context: str = "") -> str:
        """Get a clear explanation of a concept, optionally within a subject context."""
        system = (
            "You are a patient, expert tutor. Explain concepts clearly using analogies, "
            "examples, and structured reasoning. Adapt to an undergraduate level."
        )
        prompt = f"""Explain this concept clearly and thoroughly:

**{concept}**

{f"Subject context: {context}" if context else ""}

Use:
- A clear one-line definition first
- Then a deeper explanation with an analogy or example
- Key distinctions or common misconceptions
- Keep it under 300 words
"""
        return self._call(system, prompt, max_tokens=1500)

    def summarize_notes(self, note_content: str) -> str:
        """Create a structured summary of lecture notes."""
        system = (
            "You are an expert academic summarizer. Create concise, structured summaries "
            "that capture all key concepts, relationships, and important details."
        )
        prompt = f"""Summarize these lecture notes. Include:

1. **Key Concepts** — the main ideas (bullet points)
2. **Important Details** — definitions, formulas, dates, names
3. **Connections** — how concepts relate to each other
4. **Potential Exam Topics** — what's most likely to be tested

--- NOTES ---
{note_content[:10000]}
"""
        return self._call(system, prompt, max_tokens=2000)

    def answer_question(self, question: str, note_content: str = "") -> str:
        """Answer a study question, optionally grounded in specific notes."""
        system = (
            "You are a knowledgeable tutor. Answer questions accurately and clearly. "
            "If notes are provided, ground your answer in them but supplement with your knowledge."
        )
        prompt = question
        if note_content:
            prompt = f"""Answer this question using the provided notes as primary reference:

Question: {question}

--- REFERENCE NOTES ---
{note_content[:6000]}
"""
        return self._call(system, prompt, max_tokens=2000)

    def test_connection(self) -> tuple[bool, str]:
        """Test if the API key is valid."""
        try:
            response = self._call("You are a helpful assistant.", "Say 'connected' and nothing else.", max_tokens=20)
            return True, response.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def test_key(api_key: str, model: str = "claude-sonnet-4-5-20250929", provider: str | None = None) -> tuple[bool, str]:
        """Test if an API key is valid. Returns (success, message)."""
        try:
            resolved_provider = provider or detect_provider_from_key(api_key) or "anthropic"
            resolved_model = model or PROVIDER_DEFAULT_MODELS.get(resolved_provider, PROVIDER_DEFAULT_MODELS["anthropic"])
            client = ClaudeStudyClient(api_key, resolved_model, resolved_provider)
            client._call("You are a helpful assistant.", "Say 'connected' only.", max_tokens=20)
            return True, "Connected successfully"
        except Exception as e:
            err = str(e)
            if "401" in err or "authentication" in err.lower():
                return False, "Invalid API key"
            elif "404" in err or "model" in err.lower():
                return False, "Model not found — check model name"
            elif "connection" in err.lower() or "network" in err.lower():
                return False, "Network error — check internet connection"
            return False, f"Error: {err[:120]}"

    def _call_with_model(self, system: str, user_msg: str, max_tokens: int = 4096, model_override: str = None) -> str:
        """Call Claude with an optional model override."""
        if not model_override:
            return self._call(system, user_msg, max_tokens=max_tokens)
        original_model = self.model
        try:
            self.model = model_override
            return self._call(system, user_msg, max_tokens=max_tokens)
        finally:
            self.model = original_model

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
        parsed = self._parse_json_response(self._call_with_model(system, prompt, model_override=model_override))
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
        parsed = self._parse_json_response(self._call_with_model(system, prompt, model_override=model_override))
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
        parsed = self._parse_json_response(self._call_with_model(system, user_prompt, model_override=model_override))
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
        parsed = self._parse_json_response(self._call_with_model(system, prompt, model_override=model_override))
        if isinstance(parsed, dict):
            return parsed
        return {}
