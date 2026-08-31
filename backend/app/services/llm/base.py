"""
LLM service abstraction layer.

BaseLLMService defines the interface contract every LLM provider must satisfy.
get_llm_service() is the factory that returns the correct implementation based
on the LLM_PROVIDER environment variable.

Method signatures mirror the five capabilities Study Buddy requires:
  1. analyse_content   — extract structure and concepts from raw text
  2. explain_topic     — produce learner-friendly explanations
  3. generate_quiz     — create quiz questions for concepts
  4. generate_learning_path — propose an ordered study plan
  5. answer_question   — chatbot Q&A with optional material context
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ── Shared data-transfer objects ─────────────────────────────────────────────

@dataclass
class ContentAnalysis:
    """Result of analyse_content()."""
    summary: str
    sections: list[dict[str, Any]] = field(default_factory=list)
    # Each section: {"title": str, "summary": str, "concepts": [{"name": str, "definition": str, ...}]}


@dataclass
class TopicExplanation:
    """Result of explain_topic()."""
    topic: str
    explanation: str
    examples: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    analogies: list[str] = field(default_factory=list)


@dataclass
class GeneratedQuiz:
    """Result of generate_quiz()."""
    title: str
    difficulty: str
    questions: list[dict[str, Any]] = field(default_factory=list)
    # Each question: {
    #   "question_text": str,
    #   "question_type": str,
    #   "options": list[str] | None,
    #   "correct_answer": str,
    #   "explanation": str,
    #   "difficulty": str
    # }


@dataclass
class GeneratedLearningPath:
    """Result of generate_learning_path()."""
    title: str
    description: str
    estimated_duration_minutes: int
    steps: list[dict[str, Any]] = field(default_factory=list)
    # Each step: {
    #   "title": str,
    #   "description": str,
    #   "order_index": int,
    #   "estimated_minutes": int,
    #   "concept_name": str | None,
    #   "prerequisites": list[int]
    # }


@dataclass
class ChatAnswer:
    """Result of answer_question()."""
    answer: str
    sources: list[str] = field(default_factory=list)
    follow_up_suggestions: list[str] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0


# ── Abstract interface ────────────────────────────────────────────────────────

class BaseLLMService(ABC):
    """
    Abstract base class that every LLM provider must implement.

    Implementations:
      - DemoLLMService   (this session)
      - WatsonxLLMService (TODO — next session)
    """

    @abstractmethod
    async def analyse_content(
        self,
        raw_text: str,
        title: str = "",
    ) -> ContentAnalysis:
        """
        Extract structure and concepts from raw document text.

        Args:
            raw_text: The full text content of the study material.
            title: Optional title hint to guide extraction.

        Returns:
            ContentAnalysis with summary, sections, and concepts.
        """
        ...

    @abstractmethod
    async def explain_topic(
        self,
        topic_name: str,
        context: str = "",
        difficulty_level: str = "intermediate",
    ) -> TopicExplanation:
        """
        Generate a learner-friendly explanation of a concept or topic.

        Args:
            topic_name: The concept/topic to explain.
            context: Surrounding text or section content for context.
            difficulty_level: "beginner" | "intermediate" | "advanced"

        Returns:
            TopicExplanation with explanation, examples, key points, and analogies.
        """
        ...

    @abstractmethod
    async def generate_quiz(
        self,
        concepts: list[dict[str, Any]],
        num_questions: int = 5,
        difficulty: str = "mixed",
    ) -> GeneratedQuiz:
        """
        Generate quiz questions from a list of concept objects.

        Args:
            concepts: List of concept dicts with at least "name" and "definition".
            num_questions: Number of questions to generate.
            difficulty: "easy" | "medium" | "hard" | "mixed"

        Returns:
            GeneratedQuiz with questions and metadata.
        """
        ...

    @abstractmethod
    async def generate_learning_path(
        self,
        material_title: str,
        sections: list[dict[str, Any]],
        learner_goal: str = "",
    ) -> GeneratedLearningPath:
        """
        Propose an ordered, step-by-step learning path for a material.

        Args:
            material_title: Title of the study material.
            sections: List of section dicts with titles and concept names.
            learner_goal: Optional free-text learning objective from the user.

        Returns:
            GeneratedLearningPath with ordered steps and time estimates.
        """
        ...

    @abstractmethod
    async def answer_question(
        self,
        question: str,
        session_history: list[dict[str, str]],
        material_context: str = "",
    ) -> ChatAnswer:
        """
        Answer a learner's question in chatbot mode.

        Args:
            question: The user's question text.
            session_history: Prior messages: [{"role": "user"|"assistant", "content": str}]
            material_context: Relevant extracted text from the material, if any.

        Returns:
            ChatAnswer with the response, source references, and follow-up suggestions.
        """
        ...


# ── Factory ───────────────────────────────────────────────────────────────────

def get_llm_service() -> BaseLLMService:
    """
    Factory function — returns the LLM service configured by LLM_PROVIDER.

    Supported providers:
      "demo"    → DemoLLMService (deterministic, no API calls)
      "watsonx" → WatsonxLLMService (TODO — implement in next session)
    """
    from app.config import get_settings

    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "demo":
        from app.services.llm.demo import DemoLLMService
        return DemoLLMService()

    if provider == "watsonx":
        # TODO (Session 2): Implement WatsonxLLMService
        # Expected constructor signature:
        #   WatsonxLLMService(
        #       api_key: str = settings.WATSONX_API_KEY,
        #       project_id: str = settings.WATSONX_PROJECT_ID,
        #       url: str = settings.WATSONX_URL,
        #       model_id: str = settings.WATSONX_MODEL_ID,
        #   )
        # Use the ibm-watsonx-ai SDK:
        #   from ibm_watsonx_ai.foundation_models import ModelInference
        raise NotImplementedError(
            "WatsonxLLMService is not yet implemented. "
            "Set LLM_PROVIDER=demo to use the demo provider."
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. "
        "Valid values: 'demo', 'watsonx'."
    )
