"""
DemoLLMService — deterministic, realistic-looking responses.

Designed so every feature can be built and tested without a real LLM.
All responses use the Python Programming Fundamentals sample material as
a reference so they produce believable, domain-consistent output.

No network calls are made. All results are synchronous behind the async
interface so they can be awaited naturally.
"""

from __future__ import annotations

import json
from typing import Any

from app.services.llm.base import (
    BaseLLMService,
    ChatAnswer,
    ContentAnalysis,
    GeneratedLearningPath,
    GeneratedQuiz,
    TopicExplanation,
)


class DemoLLMService(BaseLLMService):
    """
    Deterministic demo provider.

    Returns pre-formed, realistic responses based on the Python Programming
    Fundamentals sample material. The response shapes are identical to what
    a real LLM provider would return, so service and UI code can be built
    against them immediately.
    """

    # ── analyse_content ───────────────────────────────────────────────────────

    async def analyse_content(
        self,
        raw_text: str,
        title: str = "",
    ) -> ContentAnalysis:
        """
        Returns a realistic analysis mimicking Python Programming Fundamentals.
        The actual raw_text is not used by the demo — it always returns the
        same shaped response so downstream code can be tested.
        """
        display_title = title or "Python Programming Fundamentals"
        return ContentAnalysis(
            summary=(
                f"'{display_title}' is a comprehensive introduction to Python covering "
                "core programming concepts. It begins with variables and data types, "
                "progresses through control flow (conditions, loops), and builds up to "
                "functions and data structures (lists, dictionaries). Suitable for "
                "absolute beginners with no prior programming experience."
            ),
            sections=[
                {
                    "title": "Variables and Data Types",
                    "order_index": 0,
                    "summary": "Introduction to Python variables, assignment, and the built-in types: int, float, str, bool.",
                    "concepts": [
                        {
                            "name": "Variables",
                            "definition": "Named storage locations that hold a value.",
                            "examples": ["x = 10", "name = 'Alice'"],
                            "order_index": 0,
                        },
                        {
                            "name": "Data Types",
                            "definition": "Categories of values: int, float, str, bool, NoneType.",
                            "examples": ["type(42) == int", "type(3.14) == float"],
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "title": "Conditions",
                    "order_index": 1,
                    "summary": "Conditional logic using if, elif, and else statements.",
                    "concepts": [
                        {
                            "name": "if / elif / else",
                            "definition": "Execute code blocks conditionally based on boolean expressions.",
                            "examples": ["if x > 0:\n    print('positive')"],
                            "order_index": 0,
                        },
                        {
                            "name": "Comparison Operators",
                            "definition": "Operators that compare values: ==, !=, <, >, <=, >=.",
                            "examples": ["5 == 5  # True", "3 != 4  # True"],
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "title": "Loops",
                    "order_index": 2,
                    "summary": "Iteration using for and while loops.",
                    "concepts": [
                        {
                            "name": "for Loop",
                            "definition": "Iterate over a sequence (list, range, string, etc.).",
                            "examples": ["for i in range(5):\n    print(i)"],
                            "order_index": 0,
                        },
                        {
                            "name": "while Loop",
                            "definition": "Repeat a block while a condition is True.",
                            "examples": ["while count < 10:\n    count += 1"],
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "title": "Functions",
                    "order_index": 3,
                    "summary": "Defining and calling reusable blocks of code.",
                    "concepts": [
                        {
                            "name": "Function Definition",
                            "definition": "Use def to declare a function with parameters.",
                            "examples": ["def greet(name):\n    return f'Hello, {name}!'"],
                            "order_index": 0,
                        },
                        {
                            "name": "Return Values",
                            "definition": "Functions return data to the caller using return.",
                            "examples": ["def add(a, b):\n    return a + b"],
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "title": "Lists",
                    "order_index": 4,
                    "summary": "Ordered, mutable sequences and their methods.",
                    "concepts": [
                        {
                            "name": "List Creation",
                            "definition": "Create a list with square brackets.",
                            "examples": ["fruits = ['apple', 'banana', 'cherry']"],
                            "order_index": 0,
                        },
                        {
                            "name": "List Methods",
                            "definition": "Built-in methods: append, remove, pop, sort, len.",
                            "examples": ["fruits.append('date')", "fruits.sort()"],
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "title": "Dictionaries",
                    "order_index": 5,
                    "summary": "Key-value data structures.",
                    "concepts": [
                        {
                            "name": "Dictionary Creation",
                            "definition": "Create a dict with curly braces and key: value pairs.",
                            "examples": ["person = {'name': 'Alice', 'age': 30}"],
                            "order_index": 0,
                        },
                        {
                            "name": "Accessing and Modifying",
                            "definition": "Read values with [] or .get(); modify with assignment.",
                            "examples": ["person['name']", "person['email'] = 'alice@example.com'"],
                            "order_index": 1,
                        },
                    ],
                },
            ],
        )

    # ── explain_topic ─────────────────────────────────────────────────────────

    async def explain_topic(
        self,
        topic_name: str,
        context: str = "",
        difficulty_level: str = "intermediate",
    ) -> TopicExplanation:
        """Returns a realistic, readable explanation for any topic name."""
        return TopicExplanation(
            topic=topic_name,
            explanation=(
                f"**{topic_name}** is a fundamental concept in Python programming. "
                f"At the {difficulty_level} level, understanding {topic_name} means "
                "grasping how Python represents, stores, and manipulates this kind of "
                "information in memory. It forms the building block for more complex "
                "programs and is used in virtually every real-world Python application."
            ),
            examples=[
                f"# Example 1 — basic usage of {topic_name}",
                f"# Example 2 — {topic_name} in a real-world context",
                f"# Example 3 — common pitfall with {topic_name} and how to avoid it",
            ],
            key_points=[
                f"{topic_name} is built into Python — no imports needed.",
                f"Understanding {topic_name} helps you write cleaner, bug-free code.",
                f"Practice {topic_name} daily to build muscle memory.",
            ],
            analogies=[
                f"Think of {topic_name} like a labelled container in a kitchen — "
                "each container holds exactly one type of ingredient."
            ],
        )

    # ── generate_quiz ─────────────────────────────────────────────────────────

    async def generate_quiz(
        self,
        concepts: list[dict[str, Any]],
        num_questions: int = 5,
        difficulty: str = "mixed",
    ) -> GeneratedQuiz:
        """Returns a realistic multiple-choice quiz for the given concepts."""
        # Build one question per concept (up to num_questions)
        concept_slice = concepts[:num_questions]
        questions = []
        difficulty_cycle = ["easy", "medium", "hard"]

        for idx, concept in enumerate(concept_slice):
            name = concept.get("name", f"Concept {idx + 1}")
            definition = concept.get("definition", "a key Python concept")
            q_difficulty = difficulty if difficulty != "mixed" else difficulty_cycle[idx % 3]
            questions.append(
                {
                    "question_text": f"Which of the following best describes '{name}' in Python?",
                    "question_type": "multiple_choice",
                    "options": [
                        definition,
                        f"A built-in Python function called {name.lower()}()",
                        f"A special module imported with 'import {name.lower()}'",
                        f"A type error raised when using {name.lower()} incorrectly",
                    ],
                    "correct_answer": definition,
                    "explanation": (
                        f"'{name}' is correctly defined as: {definition}. "
                        "The other options describe related but distinct Python concepts."
                    ),
                    "difficulty": q_difficulty,
                    "order_index": idx,
                }
            )

        return GeneratedQuiz(
            title=f"Quiz — {concepts[0].get('name', 'Python Concepts') if concepts else 'Python Concepts'}",
            difficulty=difficulty,
            questions=questions,
        )

    # ── generate_learning_path ────────────────────────────────────────────────

    async def generate_learning_path(
        self,
        material_title: str,
        sections: list[dict[str, Any]],
        learner_goal: str = "",
    ) -> GeneratedLearningPath:
        """Returns a realistic ordered learning path for the given material."""
        steps = []
        cumulative_minutes = 0

        for idx, section in enumerate(sections):
            section_title = section.get("title", f"Section {idx + 1}")
            concepts = section.get("concepts", [])
            estimated = max(10, len(concepts) * 8)  # ~8 min per concept
            cumulative_minutes += estimated
            steps.append(
                {
                    "title": f"Study: {section_title}",
                    "description": (
                        f"Read through '{section_title}', take notes on key concepts, "
                        "and complete the practice examples."
                    ),
                    "order_index": idx * 2,
                    "estimated_minutes": estimated,
                    "concept_name": None,
                    "prerequisites": [idx * 2 - 2] if idx > 0 else [],
                }
            )
            steps.append(
                {
                    "title": f"Practice: {section_title} Quiz",
                    "description": (
                        f"Test your understanding of '{section_title}' with a short quiz. "
                        "Aim for at least 80% before moving on."
                    ),
                    "order_index": idx * 2 + 1,
                    "estimated_minutes": max(5, len(concepts) * 3),
                    "concept_name": None,
                    "prerequisites": [idx * 2],
                }
            )

        goal_note = (
            f" Goal: {learner_goal}." if learner_goal else ""
        )
        return GeneratedLearningPath(
            title=f"Learning Path: {material_title}",
            description=(
                f"A structured, step-by-step path through '{material_title}' "
                f"covering all sections with study and practice phases.{goal_note}"
            ),
            estimated_duration_minutes=cumulative_minutes,
            steps=steps,
        )

    # ── answer_question ───────────────────────────────────────────────────────

    async def answer_question(
        self,
        question: str,
        session_history: list[dict[str, str]],
        material_context: str = "",
    ) -> ChatAnswer:
        """Returns a realistic-looking chatbot answer for any question."""
        turn_count = len(session_history)
        context_note = (
            " I'm drawing on the study material loaded in this session."
            if material_context
            else ""
        )
        return ChatAnswer(
            answer=(
                f"Great question!{context_note} Based on what we've covered so far "
                f"(this is turn {turn_count + 1} of our conversation), here's my "
                f"explanation of '{question[:60]}{'...' if len(question) > 60 else ''}':\n\n"
                "In Python, this concept works by following a set of well-defined rules "
                "that the interpreter applies at runtime. The key insight is that Python "
                "evaluates expressions left-to-right and uses dynamic typing, which means "
                "you don't need to declare types explicitly — Python infers them.\n\n"
                "A practical way to remember this: think of Python as an eager assistant "
                "that does exactly what you tell it, one line at a time."
            ),
            sources=(
                ["Python Programming Fundamentals — Section 1", "Python docs: Built-in Types"]
                if material_context
                else []
            ),
            follow_up_suggestions=[
                "Can you give me a concrete code example?",
                "What are common mistakes beginners make here?",
                "How does this relate to the next topic?",
            ],
            prompt_tokens=0,   # Demo provider — no real token usage
            completion_tokens=0,
        )
