"""
Seed script — pre-populates the database with demo-ready data.

Usage:
    cd backend && source .venv/bin/activate && python seed.py
"""

import asyncio
import json
import sys
from datetime import date, datetime, timezone

from sqlalchemy import text

from app.database import AsyncSessionLocal, init_db
from app.models.chat import ChatMessage, MessageRole
from app.models.learning_path import LearningPath, LearningStep, StepStatus
from app.models.material import Concept, Material, MaterialStatus, MaterialType, Section
from app.models.progress import ConceptMastery, MaterialProgress
from app.models.quiz import Quiz, QuizAttempt, QuizDifficulty, QuizQuestion, QuestionType
from app.models.revision import RevisionPlan, RevisionTask, TaskStatus


# ── concept data ──────────────────────────────────────────────────────────────

_PY_SECTIONS = [
    {
        "title": "Variables and Data Types",
        "concepts": [
            {
                "name": "Variables",
                "definition": "A variable is a named storage location that holds a value which can change during program execution.",
                "examples": [
                    "x = 10\nname = 'Alice'\npi = 3.14",
                    "age = 25\nage = age + 1  # age is now 26",
                ],
            },
            {
                "name": "Data Types",
                "definition": "Data types classify the kind of value a variable can hold, such as integers, floats, strings, or booleans.",
                "examples": [
                    "x = 42          # int\ny = 3.14        # float\nz = 'hello'     # str\nflag = True     # bool",
                    "print(type(42))    # <class 'int'>\nprint(type(3.14))  # <class 'float'>",
                ],
            },
            {
                "name": "Type Casting",
                "definition": "Type casting converts a value from one data type to another using built-in functions like int(), float(), or str().",
                "examples": [
                    "n = int('42')     # string → int\ns = str(3.14)     # float → string",
                    "x = float('3.14') # string → float\ny = int(3.99)     # float → int (truncates)",
                ],
            },
            {
                "name": "Constants",
                "definition": "Constants are values intended never to change. Python uses ALL_CAPS naming by convention (no enforcement).",
                "examples": [
                    "MAX_SIZE = 100\nPI = 3.14159",
                    "DATABASE_URL = 'sqlite:///app.db'\nVERSION = '1.0.0'",
                ],
            },
        ],
    },
    {
        "title": "Control Flow",
        "concepts": [
            {
                "name": "if/elif/else",
                "definition": "Conditional statements that execute different code blocks depending on whether a condition evaluates to True or False.",
                "examples": [
                    "score = 75\nif score >= 90:\n    grade = 'A'\nelif score >= 70:\n    grade = 'B'\nelse:\n    grade = 'C'",
                    "x = 0\nif x > 0:\n    print('positive')\nelif x < 0:\n    print('negative')\nelse:\n    print('zero')",
                ],
            },
            {
                "name": "for Loop",
                "definition": "A for loop iterates over a sequence (list, range, string, etc.) executing a block for each item.",
                "examples": [
                    "for i in range(5):\n    print(i)  # prints 0 1 2 3 4",
                    "fruits = ['apple', 'banana', 'cherry']\nfor fruit in fruits:\n    print(fruit)",
                ],
            },
            {
                "name": "while Loop",
                "definition": "A while loop repeats a block of code as long as its condition remains True.",
                "examples": [
                    "count = 0\nwhile count < 5:\n    print(count)\n    count += 1",
                    "user_input = ''\nwhile user_input != 'quit':\n    user_input = input('Enter command: ')",
                ],
            },
            {
                "name": "break/continue",
                "definition": "break exits the current loop immediately; continue skips the rest of the current iteration and moves to the next.",
                "examples": [
                    "for i in range(10):\n    if i == 5:\n        break\n    print(i)  # prints 0–4",
                    "for i in range(10):\n    if i % 2 == 0:\n        continue\n    print(i)  # prints odd numbers",
                ],
            },
        ],
    },
    {
        "title": "Functions",
        "concepts": [
            {
                "name": "Function Definition",
                "definition": "A function is a reusable block of code defined with the def keyword that performs a specific task.",
                "examples": [
                    "def greet():\n    print('Hello, World!')\n\ngreet()  # Hello, World!",
                    "def add(a, b):\n    return a + b\n\nresult = add(3, 4)  # 7",
                ],
            },
            {
                "name": "Parameters and Arguments",
                "definition": "Parameters are placeholders in a function definition; arguments are the actual values passed when calling the function.",
                "examples": [
                    "def power(base, exp):  # base, exp are parameters\n    return base ** exp\n\npower(2, 3)  # 2, 3 are arguments",
                    "def full_name(first, last):\n    return f'{first} {last}'\n\nfull_name('Ada', 'Lovelace')",
                ],
            },
            {
                "name": "Return Values",
                "definition": "The return statement sends a value back from a function to the caller. Without return, a function returns None.",
                "examples": [
                    "def square(n):\n    return n * n\n\nx = square(5)  # x is 25",
                    "def divide(a, b):\n    if b == 0:\n        return None\n    return a / b",
                ],
            },
            {
                "name": "Default Arguments",
                "definition": "Default arguments provide fallback values for parameters when the caller does not supply them.",
                "examples": [
                    "def greet(name='World'):\n    print(f'Hello, {name}!')\n\ngreet()         # Hello, World!\ngreet('Alice')  # Hello, Alice!",
                    "def repeat(text, times=2):\n    return text * times\n\nrepeat('ha')     # 'haha'\nrepeat('ha', 3)  # 'hahaha'",
                ],
            },
        ],
    },
    {
        "title": "Data Structures",
        "concepts": [
            {
                "name": "Lists",
                "definition": "An ordered, mutable sequence of items. Lists support indexing, slicing, and many built-in methods.",
                "examples": [
                    "nums = [1, 2, 3, 4, 5]\nnums.append(6)\nprint(nums[0])   # 1",
                    "squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]",
                ],
            },
            {
                "name": "Dictionaries",
                "definition": "An unordered collection of key–value pairs. Keys must be unique and hashable; values can be any type.",
                "examples": [
                    "person = {'name': 'Alice', 'age': 30}\nprint(person['name'])  # Alice",
                    "scores = {}\nscores['math'] = 95\nscores['english'] = 88",
                ],
            },
            {
                "name": "Tuples",
                "definition": "An ordered, immutable sequence of items. Use tuples for data that should not change after creation.",
                "examples": [
                    "point = (3, 4)\nx, y = point  # unpacking",
                    "rgb = (255, 128, 0)\nprint(rgb[0])  # 255 — but rgb[0] = 1 would raise TypeError",
                ],
            },
            {
                "name": "Sets",
                "definition": "An unordered collection of unique items. Useful for membership tests and mathematical set operations.",
                "examples": [
                    "unique = {1, 2, 3, 2, 1}  # {1, 2, 3}\nunique.add(4)",
                    "a = {1, 2, 3}\nb = {2, 3, 4}\nprint(a & b)  # {2, 3} — intersection",
                ],
            },
        ],
    },
]

_ML_SECTIONS = [
    {
        "title": "Supervised Learning",
        "concepts": [
            {
                "name": "Linear Regression",
                "definition": "A supervised algorithm that models the relationship between input features and a continuous output by fitting a straight line.",
                "examples": [
                    "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)",
                    "y_pred = model.predict(X_test)\n# MSE = mean((y_pred - y_test)^2)",
                ],
            },
            {
                "name": "Classification",
                "definition": "The task of predicting a discrete class label for an input, such as spam/not-spam or cat/dog.",
                "examples": [
                    "from sklearn.linear_model import LogisticRegression\nclf = LogisticRegression()\nclf.fit(X_train, y_train)",
                    "labels = clf.predict(X_test)\nprob   = clf.predict_proba(X_test)",
                ],
            },
            {
                "name": "Decision Trees",
                "definition": "A tree-structured model that splits data using feature thresholds to reach leaf-node predictions.",
                "examples": [
                    "from sklearn.tree import DecisionTreeClassifier\ntree = DecisionTreeClassifier(max_depth=4)\ntree.fit(X, y)",
                    "importances = tree.feature_importances_\n# higher value → more informative feature",
                ],
            },
        ],
    },
    {
        "title": "Neural Networks",
        "concepts": [
            {
                "name": "Perceptron",
                "definition": "The simplest neural network unit: takes weighted inputs, sums them, applies a step function, outputs a binary result.",
                "examples": [
                    "output = 1 if (w1*x1 + w2*x2 + bias) > 0 else 0",
                    "# Learns via: w += lr * (target - output) * input",
                ],
            },
            {
                "name": "Backpropagation",
                "definition": "An algorithm that computes gradients of the loss with respect to each weight using the chain rule, enabling gradient descent.",
                "examples": [
                    "loss = cross_entropy(y_pred, y_true)\nloss.backward()  # computes gradients",
                    "optimizer.step()  # updates weights using computed gradients",
                ],
            },
            {
                "name": "Activation Functions",
                "definition": "Non-linear functions applied to neuron outputs to enable the network to learn complex patterns.",
                "examples": [
                    "import torch.nn as nn\nrelu = nn.ReLU()    # max(0, x)\nsigmoid = nn.Sigmoid()  # 1/(1+e^-x)",
                    "softmax = nn.Softmax(dim=1)  # probabilities summing to 1 (multi-class)",
                ],
            },
        ],
    },
    {
        "title": "Model Evaluation",
        "concepts": [
            {
                "name": "Accuracy",
                "definition": "The fraction of predictions that are correct. Can be misleading on imbalanced datasets.",
                "examples": [
                    "accuracy = correct_predictions / total_predictions",
                    "from sklearn.metrics import accuracy_score\nacc = accuracy_score(y_true, y_pred)",
                ],
            },
            {
                "name": "Precision/Recall",
                "definition": "Precision measures how many positive predictions are correct; recall measures how many actual positives were found.",
                "examples": [
                    "precision = TP / (TP + FP)\nrecall    = TP / (TP + FN)",
                    "from sklearn.metrics import precision_score, recall_score\np = precision_score(y_true, y_pred)\nr = recall_score(y_true, y_pred)",
                ],
            },
            {
                "name": "Cross-Validation",
                "definition": "A resampling technique that evaluates model performance on multiple train/test splits to reduce variance in the estimate.",
                "examples": [
                    "from sklearn.model_selection import cross_val_score\nscores = cross_val_score(model, X, y, cv=5)",
                    "# cv=5 → 5 folds; average scores for final metric",
                ],
            },
        ],
    },
]

_PY_QUIZ_QUESTIONS = [
    {
        "question_text": "Which of the following correctly declares an integer variable in Python?",
        "question_type": QuestionType.MULTIPLE_CHOICE,
        "options": ["int x = 5", "x = 5", "var x = 5", "x := 5"],
        "correct_answer": "x = 5",
        "explanation": "Python uses dynamic typing — just assign a value with =. No type keyword needed.",
        "difficulty": QuizDifficulty.EASY,
    },
    {
        "question_text": "What does the `range(1, 6)` expression produce?",
        "question_type": QuestionType.MULTIPLE_CHOICE,
        "options": ["[1, 2, 3, 4, 5, 6]", "[0, 1, 2, 3, 4, 5]", "[1, 2, 3, 4, 5]", "[1, 6]"],
        "correct_answer": "[1, 2, 3, 4, 5]",
        "explanation": "range(start, stop) includes start but excludes stop.",
        "difficulty": QuizDifficulty.EASY,
    },
    {
        "question_text": "What keyword is used to define a function in Python?",
        "question_type": QuestionType.MULTIPLE_CHOICE,
        "options": ["func", "function", "def", "define"],
        "correct_answer": "def",
        "explanation": "Python uses the 'def' keyword to define functions.",
        "difficulty": QuizDifficulty.EASY,
    },
    {
        "question_text": "Which data structure maps unique keys to values?",
        "question_type": QuestionType.MULTIPLE_CHOICE,
        "options": ["List", "Tuple", "Set", "Dictionary"],
        "correct_answer": "Dictionary",
        "explanation": "Python dictionaries store key–value pairs with unique keys.",
        "difficulty": QuizDifficulty.MEDIUM,
    },
    {
        "question_text": "What is the output of `bool(0)` in Python?",
        "question_type": QuestionType.MULTIPLE_CHOICE,
        "options": ["True", "False", "0", "None"],
        "correct_answer": "False",
        "explanation": "In Python, 0, empty strings, empty lists, and None are all falsy.",
        "difficulty": QuizDifficulty.MEDIUM,
    },
]


async def main() -> None:
    # 1. Create tables
    await init_db()

    async with AsyncSessionLocal() as session:
        # 2. Guard: skip if already seeded
        result = await session.execute(text("SELECT COUNT(*) FROM materials"))
        count = result.scalar()
        if count and count > 0:
            print("Already seeded — skipping.")
            return

        today = date.today()

        # ── Material 1: Python Programming Fundamentals ───────────────────────
        mat1 = Material(
            title="Python Programming Fundamentals",
            material_type=MaterialType.TEXT,
            status=MaterialStatus.READY,
            summary=(
                "A comprehensive introduction to Python covering variables, data types, "
                "control flow, functions, and data structures. Perfect for absolute beginners."
            ),
            raw_text="Python variables, data types, control flow, functions, and data structures.",
        )
        session.add(mat1)
        await session.flush()

        # Sections + concepts for material 1
        py_sections = []
        py_concepts = []  # flat list in order
        for sec_idx, sec_data in enumerate(_PY_SECTIONS):
            sec = Section(
                material_id=mat1.id,
                title=sec_data["title"],
                order_index=sec_idx,
            )
            session.add(sec)
            await session.flush()
            py_sections.append(sec)

            for con_idx, con_data in enumerate(sec_data["concepts"]):
                con = Concept(
                    section_id=sec.id,
                    name=con_data["name"],
                    definition=con_data["definition"],
                    examples=json.dumps(con_data["examples"]),
                    order_index=con_idx,
                )
                session.add(con)
                await session.flush()
                py_concepts.append(con)

        # 4. LearningPath for material 1 — 8 steps (Read + Practise × 4 sections)
        lp = LearningPath(
            material_id=mat1.id,
            title="Python Programming Fundamentals — Learning Path",
            description="Step-by-step guide through all four sections.",
            estimated_duration_minutes=160,
        )
        session.add(lp)
        await session.flush()

        _step_statuses = [
            StepStatus.COMPLETED,   # 0
            StepStatus.COMPLETED,   # 1
            StepStatus.IN_PROGRESS, # 2
            StepStatus.IN_PROGRESS, # 3
            StepStatus.NOT_STARTED, # 4
            StepStatus.NOT_STARTED, # 5
            StepStatus.NOT_STARTED, # 6
            StepStatus.NOT_STARTED, # 7
        ]
        for step_idx, (sec, status) in enumerate(zip(
            py_sections + py_sections,  # read then practise
            _step_statuses,
        )):
            verb = "Read" if step_idx < 4 else "Practise"
            step = LearningStep(
                learning_path_id=lp.id,
                section_id=sec.id if step_idx < 4 else py_sections[step_idx - 4].id,
                title=f"{verb}: {py_sections[step_idx % 4].title}",
                description=f"{verb} the {py_sections[step_idx % 4].title} section.",
                order_index=step_idx,
                estimated_minutes=20,
                status=status,
            )
            session.add(step)
        await session.flush()

        # 5. Quiz for material 1 — 5 questions
        quiz = Quiz(
            material_id=mat1.id,
            title="Python Programming Fundamentals — Quiz",
            difficulty=QuizDifficulty.MIXED,
        )
        session.add(quiz)
        await session.flush()

        questions = []
        for q_idx, q_data in enumerate(_PY_QUIZ_QUESTIONS):
            q = QuizQuestion(
                quiz_id=quiz.id,
                question_type=q_data["question_type"],
                question_text=q_data["question_text"],
                options=json.dumps(q_data["options"]),
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                difficulty=q_data["difficulty"],
                order_index=q_idx,
            )
            session.add(q)
            await session.flush()
            questions.append(q)

        # 6. QuizAttempt — first 3 correct, last 2 wrong
        attempt_answers = {}
        for i, q in enumerate(questions):
            if i < 3:
                attempt_answers[str(q.id)] = q.correct_answer
            else:
                attempt_answers[str(q.id)] = "wrong answer"

        attempt = QuizAttempt(
            quiz_id=quiz.id,
            answers=json.dumps(attempt_answers),
            score=0.6,
            total_questions=5,
            correct_count=3,
            completed=True,
            completed_at=datetime.now(timezone.utc),
        )
        session.add(attempt)
        await session.flush()

        # 7. ConceptMastery — sections 0 and 1 (8 concepts)
        mastery_scores = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.5, 0.6]
        concepts_01 = py_concepts[:8]  # first 2 sections × 4 concepts each
        for con, score in zip(concepts_01, mastery_scores):
            cm = ConceptMastery(
                concept_id=con.id,
                score=score,
                review_count=2,
                last_reviewed_at=datetime.now(timezone.utc),
            )
            session.add(cm)
        await session.flush()

        # 8. MaterialProgress for material 1
        mp = MaterialProgress(
            material_id=mat1.id,
            steps_completion=0.25,
            mastery_score=0.55,
            time_studied_minutes=45,
        )
        session.add(mp)
        await session.flush()

        # 9. RevisionPlan with 5 pending tasks
        rev_plan = RevisionPlan(
            material_id=mat1.id,
            title="Python Programming Fundamentals — Revision Plan",
            description="Spaced-repetition review for key concepts.",
            start_date=today,
            end_date=today,
        )
        session.add(rev_plan)
        await session.flush()

        for con in py_concepts[:5]:
            task = RevisionTask(
                revision_plan_id=rev_plan.id,
                concept_id=con.id,
                title=f"Review: {con.name}",
                due_date=today,
                status=TaskStatus.PENDING,
                interval_days=1,
                completed=False,
            )
            session.add(task)
        await session.flush()

        # 10. ChatMessages
        chat_data = [
            (MessageRole.USER, "What is a variable?"),
            (
                MessageRole.ASSISTANT,
                "A variable is a named storage location that holds a value which can change "
                "during program execution. In Python you simply write `x = 10` — no type "
                "declaration needed.",
            ),
            (MessageRole.USER, "Can you show me an example with a for loop?"),
        ]
        for role, content in chat_data:
            msg = ChatMessage(
                session_id="demo-session",
                material_id=mat1.id,
                role=role,
                content=content,
            )
            session.add(msg)
        await session.flush()

        # ── Material 2: Machine Learning Basics ──────────────────────────────
        mat2 = Material(
            title="Machine Learning Basics",
            material_type=MaterialType.TEXT,
            status=MaterialStatus.READY,
            summary=(
                "Introduction to machine learning concepts including supervised learning, "
                "neural networks, and model evaluation."
            ),
            raw_text="Machine learning, supervised learning, neural networks, model evaluation.",
        )
        session.add(mat2)
        await session.flush()

        ml_concepts = []
        for sec_idx, sec_data in enumerate(_ML_SECTIONS):
            sec = Section(
                material_id=mat2.id,
                title=sec_data["title"],
                order_index=sec_idx,
            )
            session.add(sec)
            await session.flush()

            for con_idx, con_data in enumerate(sec_data["concepts"]):
                con = Concept(
                    section_id=sec.id,
                    name=con_data["name"],
                    definition=con_data["definition"],
                    examples=json.dumps(con_data["examples"]),
                    order_index=con_idx,
                )
                session.add(con)
                await session.flush()
                ml_concepts.append(con)

        # ConceptMastery score=0.0 for all ML concepts
        for con in ml_concepts:
            cm = ConceptMastery(
                concept_id=con.id,
                score=0.0,
                review_count=0,
            )
            session.add(cm)
        await session.flush()

        await session.commit()

    print("✓ Seeded database:")
    print(f"  2 materials (12 sections, ~{len(py_concepts) + len(ml_concepts)} concepts)")
    print("  1 learning path (8 steps, 2 completed)")
    print("  1 quiz (5 questions, 1 attempt: 3/5 correct)")
    print("  5 revision tasks due today")
    print("  3 chat messages")


if __name__ == "__main__":
    asyncio.run(main())
