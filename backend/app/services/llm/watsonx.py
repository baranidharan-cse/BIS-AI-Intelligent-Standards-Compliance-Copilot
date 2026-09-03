"""
WatsonxLLMService — IBM watsonx.ai implementation of BaseLLMService.

Uses the ibm-watsonx-ai SDK to call a foundation model (default:
ibm/granite-13b-instruct-v2) for all five Study Buddy LLM operations.

Each method:
  1. Builds a JSON-output prompt via a _build_prompt_* helper.
  2. Calls self._model.generate_text() with tuned GenParams.
  3. Parses the response as JSON, with a regex fallback and a safe default.
  4. Returns the appropriate DTO.
"""

from __future__ import annotations

import json
import re
from typing import Any

try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
except ImportError as _ibm_err:  # noqa: F841
    APIClient = None  # type: ignore[assignment,misc]
    Credentials = None  # type: ignore[assignment,misc]
    ModelInference = None  # type: ignore[assignment,misc]
    GenParams = None  # type: ignore[assignment,misc]

from app.services.llm.base import (
    BaseLLMService,
    ChatAnswer,
    ContentAnalysis,
    GeneratedLearningPath,
    GeneratedQuiz,
    TopicExplanation,
)


class WatsonxLLMService(BaseLLMService):
    """
    IBM watsonx.ai provider.

    Initialise with your project credentials; all five methods delegate to
    a shared ModelInference instance and parse the model's JSON output.
    """

    def __init__(
        self,
        api_key: str,
        project_id: str,
        url: str,
        model_id: str,
    ) -> None:
        if ModelInference is None:
            raise ImportError(
                "ibm-watsonx-ai is not installed. "
                "Run: pip install ibm-watsonx-ai>=1.0.0"
            )
        credentials = Credentials(api_key=api_key, url=url)
        client = APIClient(credentials=credentials)
        self._model = ModelInference(
            model_id=model_id,
            api_client=client,
            project_id=project_id,
        )

    # ── JSON parsing helpers ──────────────────────────────────────────────────

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """
        Parse *raw* as JSON.

        Strategy:
          1. Try the whole string directly.
          2. Extract the first {...} block with a DOTALL regex.
          3. Raise ValueError if both fail (caller provides safe default).
        """
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse JSON from model response: {raw[:200]!r}")

    @staticmethod
    def _token_counts(response: Any) -> tuple[int, int]:
        """Extract (prompt_tokens, completion_tokens) from the raw SDK response."""
        try:
            result = response.get("results", [{}])[0]
            completion = result.get("generated_token_count", 0)
            prompt = result.get("input_token_count", 0)
            return prompt, completion
        except (AttributeError, IndexError, KeyError):
            return 0, 0

    def _generate(self, prompt: str, max_tokens: int = 1024) -> tuple[str, Any]:
        """
        Call the model and return (generated_text, raw_response).

        The SDK's generate_text() with raw_response=True returns the full
        response dict; generated_text is extracted from it.
        """
        params = {
            GenParams.MAX_NEW_TOKENS: max_tokens,
            GenParams.TEMPERATURE: 0.7,
        }
        raw_response = self._model.generate(prompt=prompt, params=params)
        generated_text: str = (
            raw_response.get("results", [{}])[0].get("generated_text", "")
        )
        return generated_text, raw_response

    # ── Prompt builders ───────────────────────────────────────────────────────

    @staticmethod
    def _build_prompt_analyse(raw_text: str, title: str) -> str:
        return (
            "You are an expert educator. Analyse this study material and extract structured content.\n\n"
            f"Title: {title}\n"
            f"Text: {raw_text[:3000]}\n\n"
            "Respond with ONLY valid JSON in this exact format:\n"
            "{\n"
            '  "summary": "2-3 sentence overview",\n'
            '  "sections": [\n'
            "    {\n"
            '      "title": "Section Title",\n'
            '      "order_index": 0,\n'
            '      "summary": "Section summary",\n'
            '      "concepts": [\n'
            "        {\n"
            '          "name": "Concept Name",\n'
            '          "definition": "Clear definition",\n'
            '          "examples": ["example1", "example2"],\n'
            '          "order_index": 0\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

    @staticmethod
    def _build_prompt_explain(
        topic_name: str,
        context: str,
        difficulty_level: str,
    ) -> str:
        ctx_text = context[:500] if context else "General explanation"
        return (
            f"You are a patient tutor explaining concepts to a {difficulty_level} student.\n"
            f"Explain: {topic_name}\n"
            f"Context: {ctx_text}\n\n"
            "Respond with ONLY valid JSON:\n"
            "{\n"
            '  "explanation": "Clear 2-paragraph explanation",\n'
            '  "examples": ["code or text example 1", "example 2", "example 3"],\n'
            '  "key_points": ["point 1", "point 2", "point 3"],\n'
            '  "analogies": ["real-world analogy"]\n'
            "}"
        )

    @staticmethod
    def _build_prompt_quiz(
        concepts: list[dict[str, Any]],
        num_questions: int,
        difficulty: str,
    ) -> str:
        concepts_json = json.dumps(concepts[:10])
        return (
            f"Generate {num_questions} quiz questions at {difficulty} difficulty.\n"
            f"Concepts: {concepts_json}\n\n"
            "Respond with ONLY valid JSON:\n"
            "{\n"
            '  "title": "Quiz title",\n'
            '  "questions": [\n'
            "    {\n"
            '      "question_text": "...",\n'
            '      "question_type": "multiple_choice",\n'
            '      "options": ["A", "B", "C", "D"],\n'
            '      "correct_answer": "A",\n'
            '      "explanation": "Why A is correct",\n'
            '      "difficulty": "medium",\n'
            '      "order_index": 0\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    @staticmethod
    def _build_prompt_learning_path(
        material_title: str,
        sections: list[dict[str, Any]],
        learner_goal: str,
    ) -> str:
        goal = learner_goal or "Master all concepts"
        section_titles = json.dumps([s.get("title", "") for s in sections])
        return (
            f"Create a structured learning path for: {material_title}\n"
            f"Goal: {goal}\n"
            f"Sections: {section_titles}\n\n"
            "Respond with ONLY valid JSON:\n"
            "{\n"
            f'  "title": "Learning Path: {material_title}",\n'
            '  "description": "Overview",\n'
            '  "estimated_duration_minutes": 120,\n'
            '  "steps": [\n'
            "    {\n"
            '      "title": "Step title",\n'
            '      "description": "What to do",\n'
            '      "order_index": 0,\n'
            '      "estimated_minutes": 15,\n'
            '      "concept_name": null,\n'
            '      "prerequisites": []\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    @staticmethod
    def _build_prompt_answer(
        question: str,
        session_history: list[dict[str, str]],
        material_context: str,
    ) -> str:
        history_lines = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in session_history[-6:]  # Keep last 6 turns to stay within token budget
        )
        ctx_block = (
            f"Material context: {material_context[:1000]}\n" if material_context else ""
        )
        return (
            "You are Study Buddy, a helpful AI tutor.\n"
            f"{ctx_block}"
            "Conversation history:\n"
            f"{history_lines}\n\n"
            f"User question: {question}\n\n"
            "Respond with ONLY valid JSON:\n"
            "{\n"
            '  "answer": "Detailed helpful answer",\n'
            '  "sources": ["source1"],\n'
            '  "follow_up_suggestions": ["suggestion1", "suggestion2", "suggestion3"]\n'
            "}"
        )

    # ── Public interface ──────────────────────────────────────────────────────

    async def analyse_content(
        self,
        raw_text: str,
        title: str = "",
    ) -> ContentAnalysis:
        prompt = self._build_prompt_analyse(raw_text, title)
        text, _ = self._generate(prompt, max_tokens=2048)
        try:
            data = self._parse_json(text)
        except ValueError:
            data = {
                "summary": f"Content analysis of '{title or 'document'}'.",
                "sections": [],
            }
        return ContentAnalysis(
            summary=data.get("summary", ""),
            sections=data.get("sections", []),
        )

    async def explain_topic(
        self,
        topic_name: str,
        context: str = "",
        difficulty_level: str = "intermediate",
    ) -> TopicExplanation:
        prompt = self._build_prompt_explain(topic_name, context, difficulty_level)
        text, _ = self._generate(prompt, max_tokens=1024)
        try:
            data = self._parse_json(text)
        except ValueError:
            data = {
                "explanation": f"Explanation of {topic_name}.",
                "examples": [],
                "key_points": [],
                "analogies": [],
            }
        return TopicExplanation(
            topic=topic_name,
            explanation=data.get("explanation", ""),
            examples=data.get("examples", []),
            key_points=data.get("key_points", []),
            analogies=data.get("analogies", []),
        )

    async def generate_quiz(
        self,
        concepts: list[dict[str, Any]],
        num_questions: int = 5,
        difficulty: str = "mixed",
    ) -> GeneratedQuiz:
        prompt = self._build_prompt_quiz(concepts, num_questions, difficulty)
        text, _ = self._generate(prompt, max_tokens=2048)
        try:
            data = self._parse_json(text)
        except ValueError:
            data = {"title": "Quiz", "questions": []}
        return GeneratedQuiz(
            title=data.get("title", "Quiz"),
            difficulty=difficulty,
            questions=data.get("questions", []),
        )

    async def generate_learning_path(
        self,
        material_title: str,
        sections: list[dict[str, Any]],
        learner_goal: str = "",
    ) -> GeneratedLearningPath:
        prompt = self._build_prompt_learning_path(material_title, sections, learner_goal)
        text, _ = self._generate(prompt, max_tokens=2048)
        try:
            data = self._parse_json(text)
        except ValueError:
            data = {
                "title": f"Learning Path: {material_title}",
                "description": "",
                "estimated_duration_minutes": 0,
                "steps": [],
            }
        return GeneratedLearningPath(
            title=data.get("title", f"Learning Path: {material_title}"),
            description=data.get("description", ""),
            estimated_duration_minutes=int(data.get("estimated_duration_minutes", 0)),
            steps=data.get("steps", []),
        )

    async def answer_question(
        self,
        question: str,
        session_history: list[dict[str, str]],
        material_context: str = "",
    ) -> ChatAnswer:
        prompt = self._build_prompt_answer(question, session_history, material_context)
        text, raw_response = self._generate(prompt, max_tokens=1024)
        prompt_tokens, completion_tokens = self._token_counts(raw_response)
        try:
            data = self._parse_json(text)
        except ValueError:
            data = {
                "answer": text or "I was unable to generate a response. Please try again.",
                "sources": [],
                "follow_up_suggestions": [],
            }
        return ChatAnswer(
            answer=data.get("answer", ""),
            sources=data.get("sources", []),
            follow_up_suggestions=data.get("follow_up_suggestions", []),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
