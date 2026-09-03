"""
DemoLLMService — deterministic, realistic-looking responses.

Designed so every feature can be built and tested without a real LLM.
Responses adapt to the title / topic / question passed in, covering
multiple subject domains (Python, maths, history, biology) and generic
fallback content derived from the raw text.

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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _title_domain(title: str) -> str:
    """Return a short domain key derived from keyword matching in *title*."""
    t = title.lower()
    if any(k in t for k in ("python", "programming", "code", "software")):
        return "python"
    if any(k in t for k in ("math", "calculus", "algebra", "geometry", "statistics")):
        return "math"
    if "history" in t:
        return "history"
    if any(k in t for k in ("biology", "science", "chemistry", "physics")):
        return "biology"
    return "generic"


# ── Section catalogues ────────────────────────────────────────────────────────

_PYTHON_SECTIONS: list[dict[str, Any]] = [
    {
        "title": "Variables and Data Types",
        "order_index": 0,
        "summary": "Introduction to Python variables, assignment, and the built-in types: int, float, str, bool.",
        "concepts": [
            {
                "name": "Variables",
                "definition": "Named storage locations that hold a value assigned with =.",
                "examples": ["x = 10", "name = 'Alice'"],
                "order_index": 0,
            },
            {
                "name": "Data Types",
                "definition": "Categories of values: int, float, str, bool, NoneType.",
                "examples": ["type(42) == int", "type(3.14) == float"],
                "order_index": 1,
            },
            {
                "name": "Type Casting",
                "definition": "Converting a value from one type to another using int(), str(), float().",
                "examples": ["int('42')  # 42", "str(3.14)  # '3.14'"],
                "order_index": 2,
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
        "title": "Lists and Dictionaries",
        "order_index": 4,
        "summary": "Core Python collection types.",
        "concepts": [
            {
                "name": "List",
                "definition": "An ordered, mutable sequence created with square brackets.",
                "examples": ["fruits = ['apple', 'banana']", "fruits.append('cherry')"],
                "order_index": 0,
            },
            {
                "name": "Dictionary",
                "definition": "An unordered mapping of key: value pairs.",
                "examples": ["person = {'name': 'Alice', 'age': 30}", "person['name']"],
                "order_index": 1,
            },
        ],
    },
]

_MATH_SECTIONS: list[dict[str, Any]] = [
    {
        "title": "Limits",
        "order_index": 0,
        "summary": "The foundation of calculus — what a function approaches as its input approaches a value.",
        "concepts": [
            {
                "name": "Limit Definition",
                "definition": "lim(x→a) f(x) = L means f(x) gets arbitrarily close to L as x approaches a.",
                "examples": ["lim(x→2) x² = 4", "lim(x→0) sin(x)/x = 1"],
                "order_index": 0,
            },
            {
                "name": "One-Sided Limits",
                "definition": "Left-hand limit (x→a⁻) and right-hand limit (x→a⁺) must agree for the limit to exist.",
                "examples": ["lim(x→0⁺) 1/x = +∞", "lim(x→0⁻) 1/x = −∞"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Derivatives",
        "order_index": 1,
        "summary": "Measuring the instantaneous rate of change of a function.",
        "concepts": [
            {
                "name": "Derivative",
                "definition": "f′(x) = lim(h→0) [f(x+h) − f(x)] / h — the slope of the tangent line at x.",
                "examples": ["d/dx(x²) = 2x", "d/dx(sin x) = cos x"],
                "order_index": 0,
            },
            {
                "name": "Chain Rule",
                "definition": "d/dx[f(g(x))] = f′(g(x)) · g′(x) — differentiating composite functions.",
                "examples": ["d/dx(sin(x²)) = cos(x²) · 2x"],
                "order_index": 1,
            },
            {
                "name": "Product Rule",
                "definition": "(fg)′ = f′g + fg′ — differentiating a product of two functions.",
                "examples": ["d/dx(x · sin x) = sin x + x cos x"],
                "order_index": 2,
            },
        ],
    },
    {
        "title": "Integrals",
        "order_index": 2,
        "summary": "Accumulation and area under a curve.",
        "concepts": [
            {
                "name": "Definite Integral",
                "definition": "∫[a,b] f(x) dx represents the net signed area between f and the x-axis from a to b.",
                "examples": ["∫[0,1] x dx = 1/2"],
                "order_index": 0,
            },
            {
                "name": "Fundamental Theorem of Calculus",
                "definition": "If F′ = f, then ∫[a,b] f(x) dx = F(b) − F(a).",
                "examples": ["∫[0,π] sin x dx = [−cos x] from 0 to π = 2"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Applications",
        "order_index": 3,
        "summary": "Using calculus to solve optimisation, physics, and geometry problems.",
        "concepts": [
            {
                "name": "Optimisation",
                "definition": "Find local maxima/minima by setting f′(x) = 0 and applying the second derivative test.",
                "examples": ["f(x) = x²  →  f′(x) = 2x = 0  →  x = 0 (minimum)"],
                "order_index": 0,
            },
            {
                "name": "Related Rates",
                "definition": "Differentiate both sides of an equation with respect to time to relate rates of change.",
                "examples": ["If V = (4/3)πr³, then dV/dt = 4πr² · dr/dt"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Series",
        "order_index": 4,
        "summary": "Infinite sums and their convergence.",
        "concepts": [
            {
                "name": "Taylor Series",
                "definition": "Approximates a function as an infinite polynomial: f(x) = Σ f⁽ⁿ⁾(a)/n! · (x−a)ⁿ.",
                "examples": ["e^x = 1 + x + x²/2! + x³/3! + …"],
                "order_index": 0,
            },
            {
                "name": "Convergence Tests",
                "definition": "Methods (ratio test, integral test, comparison test) to determine if a series converges.",
                "examples": ["Σ 1/n² converges (p-series, p=2>1)"],
                "order_index": 1,
            },
        ],
    },
]

_HISTORY_SECTIONS: list[dict[str, Any]] = [
    {
        "title": "Causes",
        "order_index": 0,
        "summary": "The underlying political, economic, and social forces that led to the event.",
        "concepts": [
            {
                "name": "Long-term Causes",
                "definition": "Deep structural factors — economic inequality, imperial rivalry, ideological conflict — that built tension over decades.",
                "examples": ["Nationalism in the Balkans pre-1914", "Colonial competition in Africa"],
                "order_index": 0,
            },
            {
                "name": "Short-term Triggers",
                "definition": "Immediate incidents that ignited the conflict when underlying tensions were already critical.",
                "examples": ["Assassination of Archduke Franz Ferdinand (1914)", "Stock market crash (1929)"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Key Events",
        "order_index": 1,
        "summary": "The pivotal moments and turning points of the period.",
        "concepts": [
            {
                "name": "Opening Phase",
                "definition": "The initial mobilisation, declarations, or policy changes that set events in motion.",
                "examples": ["German Schlieffen Plan execution", "Allied Expeditionary Force deployment"],
                "order_index": 0,
            },
            {
                "name": "Turning Point",
                "definition": "The decisive battle, election, or treaty that shifted the balance of power.",
                "examples": ["Battle of Stalingrad (1942–43)", "D-Day landings (1944)"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Major Figures",
        "order_index": 2,
        "summary": "The leaders, reformers, and individuals who shaped events.",
        "concepts": [
            {
                "name": "Political Leaders",
                "definition": "Heads of state and government ministers whose decisions steered nations.",
                "examples": ["Winston Churchill", "Franklin D. Roosevelt"],
                "order_index": 0,
            },
            {
                "name": "Military Commanders",
                "definition": "Generals and admirals whose strategies determined battlefield outcomes.",
                "examples": ["Eisenhower as Supreme Commander", "Rommel in North Africa"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Consequences",
        "order_index": 3,
        "summary": "The immediate aftermath and direct outcomes of the period.",
        "concepts": [
            {
                "name": "Political Consequences",
                "definition": "Territorial changes, new states, and shifts in government following the events.",
                "examples": ["Redrawing of European borders at Versailles (1919)", "UN founded (1945)"],
                "order_index": 0,
            },
            {
                "name": "Economic Consequences",
                "definition": "War reparations, reconstruction costs, and changes to trade systems.",
                "examples": ["German hyperinflation 1923", "Marshall Plan 1948"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Legacy",
        "order_index": 4,
        "summary": "Long-term influence on culture, politics, and memory.",
        "concepts": [
            {
                "name": "Cultural Memory",
                "definition": "How the event is commemorated, taught, and represented in art and literature.",
                "examples": ["War memorials and Remembrance Day", "Holocaust education programmes"],
                "order_index": 0,
            },
            {
                "name": "Institutional Legacy",
                "definition": "Lasting organisations, laws, or norms born out of the period.",
                "examples": ["NATO (1949)", "Geneva Conventions updates (1949)"],
                "order_index": 1,
            },
        ],
    },
]

_BIOLOGY_SECTIONS: list[dict[str, Any]] = [
    {
        "title": "Cell Biology",
        "order_index": 0,
        "summary": "The structure and function of the fundamental unit of life.",
        "concepts": [
            {
                "name": "Cell Membrane",
                "definition": "A phospholipid bilayer that controls what enters and exits the cell.",
                "examples": ["Selective permeability allows glucose in", "Receptor proteins bind hormones"],
                "order_index": 0,
            },
            {
                "name": "Mitochondria",
                "definition": "The organelle that produces ATP through cellular respiration.",
                "examples": ["Glucose + O₂ → ATP + CO₂ + H₂O", "Muscle cells are rich in mitochondria"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Genetics",
        "order_index": 1,
        "summary": "Heredity, DNA, and the mechanisms of inheritance.",
        "concepts": [
            {
                "name": "DNA Structure",
                "definition": "A double helix of nucleotide base pairs (A-T, C-G) encoding genetic information.",
                "examples": ["Watson and Crick model (1953)", "Human genome ≈ 3 billion base pairs"],
                "order_index": 0,
            },
            {
                "name": "Mendelian Inheritance",
                "definition": "Traits are passed via dominant and recessive alleles following Mendel's laws.",
                "examples": ["Pea plant height (T = tall dominant over t)", "Punnett square analysis"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Evolution",
        "order_index": 2,
        "summary": "How species change over time through natural selection.",
        "concepts": [
            {
                "name": "Natural Selection",
                "definition": "Individuals with heritable traits better suited to the environment reproduce more.",
                "examples": ["Peppered moth colour change in industrial England", "Antibiotic resistance"],
                "order_index": 0,
            },
            {
                "name": "Speciation",
                "definition": "The formation of new species when populations become reproductively isolated.",
                "examples": ["Darwin's finches on the Galápagos Islands", "Allopatric speciation via mountain range"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Ecology",
        "order_index": 3,
        "summary": "Interactions between organisms and their environment.",
        "concepts": [
            {
                "name": "Food Web",
                "definition": "Interconnected food chains showing energy flow from producers to consumers.",
                "examples": ["Grass → Rabbit → Fox → Decomposers", "Phytoplankton → Krill → Whale"],
                "order_index": 0,
            },
            {
                "name": "Ecosystem Services",
                "definition": "Benefits that healthy ecosystems provide: clean air, water filtration, pollination.",
                "examples": ["Bees pollinating crops", "Wetlands filtering run-off"],
                "order_index": 1,
            },
        ],
    },
    {
        "title": "Physiology",
        "order_index": 4,
        "summary": "How the body's organ systems function and interact.",
        "concepts": [
            {
                "name": "Homeostasis",
                "definition": "The maintenance of a stable internal environment despite external changes.",
                "examples": ["Thermoregulation: shivering when cold", "Blood glucose regulation by insulin"],
                "order_index": 0,
            },
            {
                "name": "Negative Feedback",
                "definition": "A regulatory loop where the output reduces the stimulus, keeping a variable near a set-point.",
                "examples": ["High blood glucose → insulin release → glucose falls", "Thyroid hormone regulation"],
                "order_index": 1,
            },
        ],
    },
]


def _generic_sections(raw_text: str, title: str) -> list[dict[str, Any]]:
    """Build generic sections using context from *raw_text*."""
    ctx = (raw_text[:200].strip() or title or "the material").replace("\n", " ")
    section_defs = [
        ("Introduction", f"Overview of {title or 'the subject'} and why it matters.", [
            ("Background", f"Historical and conceptual background that motivated the study of {title or 'this topic'}.", ["Core motivation", "Historical development"]),
            ("Scope", "What the material covers and what it deliberately leaves out.", ["In scope", "Out of scope"]),
        ]),
        ("Core Concepts", "The fundamental ideas you must master before going further.", [
            ("Key Terminology", f"Precise definitions of the vocabulary used throughout {title or 'the text'}.", ["Term A", "Term B"]),
            ("Foundational Principles", "The rules or laws that underpin everything else in this domain.", ["Principle 1", "Principle 2"]),
        ]),
        ("Applications", "How the concepts are used to solve real problems.", [
            ("Worked Examples", f"Step-by-step solutions showing {title or 'the concepts'} in action.", ["Example 1", "Example 2"]),
            ("Case Studies", "Real-world scenarios where these ideas have been applied.", ["Case A", "Case B"]),
        ]),
        ("Advanced Topics", "Extensions and nuances for learners who have mastered the basics.", [
            ("Edge Cases", "Situations where the standard rules break down or require modification.", ["Edge case 1", "Edge case 2"]),
            ("Current Research", "Open questions and cutting-edge developments in the field.", ["Research direction 1", "Research direction 2"]),
        ]),
        ("Summary", "A concise recap of everything covered.", [
            ("Key Takeaways", f"The three most important things to remember from {title or 'this material'}.", [ctx[:80]]),
            ("Next Steps", "Recommended resources and follow-on topics.", ["Further reading", "Practice problems"]),
        ]),
    ]
    sections = []
    for idx, (sec_title, sec_summary, concepts_raw) in enumerate(section_defs):
        concepts = [
            {
                "name": c_name,
                "definition": c_def,
                "examples": c_examples,
                "order_index": c_idx,
            }
            for c_idx, (c_name, c_def, c_examples) in enumerate(concepts_raw)
        ]
        sections.append({
            "title": sec_title,
            "order_index": idx,
            "summary": sec_summary,
            "concepts": concepts,
        })
    return sections


# ── Topic explanation lookup ──────────────────────────────────────────────────

_TOPIC_LOOKUP: dict[str, dict[str, Any]] = {
    "variable": {
        "explanation": (
            "A **variable** is a named binding between an identifier and a value stored in memory. "
            "In Python, you create one with a simple assignment: `x = 42`. Unlike statically typed "
            "languages, Python infers the type automatically, so the same name can be rebound to a "
            "different type later.\n\n"
            "Variables are central to every program — they let you store intermediate results, "
            "pass data into functions, and give meaningful names to otherwise cryptic numbers or strings."
        ),
        "examples": [
            "x = 10          # integer variable",
            "name = 'Alice'  # string variable",
            "pi = 3.14159    # float variable",
        ],
        "key_points": [
            "Python variables are dynamically typed — no declaration needed.",
            "Names are case-sensitive: `Score` and `score` are different.",
            "Use snake_case for variable names by convention (PEP 8).",
        ],
        "analogies": [
            "A variable is like a labelled sticky note on a whiteboard — you can change "
            "what's written on it at any time, and the label tells you what it refers to."
        ],
    },
    "function": {
        "explanation": (
            "A **function** is a reusable, named block of code that takes optional inputs (parameters) "
            "and optionally returns a value. Defining a function with `def` does not run it — you call "
            "it by name, supplying arguments.\n\n"
            "Functions are the primary tool for avoiding repetition (DRY principle) and for breaking a "
            "large program into small, testable pieces. Every well-structured Python program is built "
            "around functions."
        ),
        "examples": [
            "def greet(name):\n    return f'Hello, {name}!'",
            "def add(a, b):\n    return a + b\n\nresult = add(3, 4)  # 7",
            "def is_even(n):\n    return n % 2 == 0",
        ],
        "key_points": [
            "Parameters are local to the function body.",
            "`return` exits the function and sends a value back to the caller.",
            "Functions without an explicit return statement return None.",
        ],
        "analogies": [
            "A function is like a recipe card — you write it once and can use it every time you bake, "
            "with different ingredients (arguments) each time."
        ],
    },
    "derivative": {
        "explanation": (
            "The **derivative** of a function measures its instantaneous rate of change at any point. "
            "Formally, f′(x) = lim(h→0) [f(x+h) − f(x)] / h. Geometrically it is the slope of the "
            "tangent line to the curve at x.\n\n"
            "Derivatives are the backbone of differential calculus. They appear in physics (velocity as "
            "the derivative of position), economics (marginal cost), and machine learning (gradient descent "
            "minimises a loss function by following the negative gradient)."
        ),
        "examples": [
            "d/dx(x²) = 2x  — power rule",
            "d/dx(sin x) = cos x",
            "d/dx(eˣ) = eˣ  — e is its own derivative",
        ],
        "key_points": [
            "The power rule: d/dx(xⁿ) = n·xⁿ⁻¹.",
            "The chain rule handles composite functions: d/dx[f(g(x))] = f′(g(x))·g′(x).",
            "A zero derivative at a point indicates a local extremum (max or min).",
        ],
        "analogies": [
            "Think of the derivative as a speedometer reading — it tells you how fast something is "
            "changing right now, not on average."
        ],
    },
    "natural selection": {
        "explanation": (
            "**Natural selection** is the mechanism by which heritable traits that improve an "
            "organism's survival and reproduction become more common in a population over generations. "
            "Proposed by Charles Darwin in *On the Origin of Species* (1859), it requires three "
            "conditions: variation among individuals, heritability of that variation, and differential "
            "reproductive success.\n\n"
            "Over many generations, natural selection can produce dramatic adaptations — from the "
            "streamlined body of a dolphin to antibiotic-resistant bacteria — because even small "
            "reproductive advantages compound across thousands of generations."
        ),
        "examples": [
            "Peppered moths: dark forms became prevalent in industrial Britain where soot darkened tree bark.",
            "MRSA: bacteria with resistance mutations survive antibiotic exposure and reproduce.",
            "Darwin's finches: beak shapes diverged to exploit different food sources on different islands.",
        ],
        "key_points": [
            "Selection acts on phenotypes but evolution occurs in genotypes.",
            "Natural selection is not goal-directed — it has no foresight.",
            "Genetic drift, mutation, and gene flow are other evolutionary forces alongside selection.",
        ],
        "analogies": [
            "Natural selection is like a sieve that only lets certain shapes of pebble through — "
            "the environment is the sieve, and organisms are the pebbles."
        ],
    },
    "recursion": {
        "explanation": (
            "**Recursion** is a programming technique where a function calls itself to solve a smaller "
            "sub-problem of the same type. Every recursive solution needs a **base case** (a condition "
            "that stops the recursion) and a **recursive case** (the self-referential call).\n\n"
            "Recursion elegantly expresses problems that have a naturally self-similar structure — "
            "tree traversal, divide-and-conquer algorithms (merge sort, quicksort), and mathematical "
            "definitions like factorials and Fibonacci numbers."
        ),
        "examples": [
            "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)",
            "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
            "# Tree traversal\ndef inorder(node):\n    if node:\n        inorder(node.left)\n        print(node.val)\n        inorder(node.right)",
        ],
        "key_points": [
            "Always define a base case to prevent infinite recursion.",
            "Python's default recursion limit is 1000; use sys.setrecursionlimit() to change it.",
            "Many recursive solutions can be rewritten iteratively with a stack for better performance.",
        ],
        "analogies": [
            "Recursion is like Russian nesting dolls — each doll contains a smaller version of itself, "
            "until you reach the smallest doll that contains nothing."
        ],
    },
    "photosynthesis": {
        "explanation": (
            "**Photosynthesis** is the process by which plants, algae, and some bacteria convert light "
            "energy into chemical energy stored as glucose. The overall reaction is:\n"
            "6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂\n\n"
            "It occurs in two stages: the light-dependent reactions (in the thylakoid membranes, "
            "producing ATP and NADPH) and the Calvin cycle (in the stroma, using that energy to fix "
            "carbon dioxide into sugar). Photosynthesis is the primary source of oxygen in Earth's "
            "atmosphere and the base of nearly every food chain."
        ),
        "examples": [
            "A leaf capturing sunlight to build glucose from CO₂ and water.",
            "Phytoplankton in the ocean producing roughly 50% of Earth's oxygen.",
            "C4 plants (maize, sugarcane) using an adapted pathway to reduce water loss in hot climates.",
        ],
        "key_points": [
            "Chlorophyll absorbs red and blue light most efficiently, reflecting green.",
            "Light reactions produce ATP and NADPH; the Calvin cycle uses them to fix CO₂.",
            "The rate of photosynthesis increases with light intensity, CO₂ concentration, and temperature — up to an optimum.",
        ],
        "analogies": [
            "Photosynthesis is like a solar panel connected to a battery — the panel captures light "
            "energy (light reactions) and stores it as chemical energy (glucose) for later use."
        ],
    },
    "world war 1": {
        "explanation": (
            "**World War I** (1914–1918) was a global conflict centred in Europe that grew from a "
            "complex web of alliances, imperial rivalries, and nationalist tensions. The assassination "
            "of Archduke Franz Ferdinand in Sarajevo on 28 June 1914 was the immediate trigger, but "
            "the underlying causes had been building for decades.\n\n"
            "The war introduced industrial-scale killing through trench warfare, poison gas, artillery "
            "barrages, and early aerial combat. It ended with the armistice of 11 November 1918 and the "
            "Treaty of Versailles (1919), which reshaped the map of Europe, dissolved empires, and — "
            "arguably — planted the seeds of World War II."
        ),
        "examples": [
            "The Schlieffen Plan: Germany's strategy for a two-front war via a rapid sweep through Belgium.",
            "Battle of the Somme (1916): over one million casualties in five months.",
            "The Zimmermann Telegram (1917): Germany's secret proposal to Mexico, accelerating US entry.",
        ],
        "key_points": [
            "The alliance system (Triple Entente vs. Triple Alliance) turned a regional crisis into a world war.",
            "The war accelerated technological change: tanks, aircraft, and chemical weapons all debuted.",
            "The Russian Revolution (1917) removed Russia from the war and reshaped global politics for decades.",
        ],
        "analogies": [
            "The alliances of 1914 were like a chain of dominoes — once one fell (Austria-Hungary declaring "
            "war on Serbia), all the others toppled in rapid succession."
        ],
    },
    "integral": {
        "explanation": (
            "An **integral** is the mathematical operation that accumulates a quantity over an interval. "
            "The definite integral ∫[a,b] f(x) dx gives the net signed area between the curve f(x) and "
            "the x-axis from x = a to x = b. The indefinite integral ∫f(x) dx gives the antiderivative F(x) "
            "such that F′(x) = f(x).\n\n"
            "Integrals are used wherever you need to sum infinitely many infinitesimally small quantities — "
            "calculating distances from velocity, volumes of solids, work done by a variable force, and "
            "probability under a continuous distribution."
        ),
        "examples": [
            "∫x dx = x²/2 + C",
            "∫[0,2] x² dx = [x³/3] from 0 to 2 = 8/3",
            "∫sin(x) dx = −cos(x) + C",
        ],
        "key_points": [
            "The Fundamental Theorem of Calculus links integration and differentiation.",
            "Integration by substitution and integration by parts are the two main manual techniques.",
            "Always add the constant of integration C for indefinite integrals.",
        ],
        "analogies": [
            "An integral is like summing the miles on a road-trip odometer — you're adding up infinitely "
            "many tiny distance increments to get the total."
        ],
    },
    "oop": {
        "explanation": (
            "**Object-Oriented Programming (OOP)** is a programming paradigm that organises code around "
            "*objects* — bundles of data (attributes) and behaviour (methods). A **class** is the blueprint; "
            "an **instance** (object) is one concrete realisation of that blueprint.\n\n"
            "OOP's four pillars are encapsulation (hiding internal state), inheritance (sharing behaviour "
            "between related classes), polymorphism (treating different types uniformly via shared interfaces), "
            "and abstraction (exposing only what is necessary). Python supports all four."
        ),
        "examples": [
            "class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        raise NotImplementedError",
            "class Dog(Animal):\n    def speak(self):\n        return 'Woof!'",
            "animals = [Dog('Rex'), Cat('Whiskers')]\nfor a in animals:\n    print(a.speak())  # polymorphism",
        ],
        "key_points": [
            "Use `self` to refer to instance attributes and methods inside a class.",
            "Prefer composition over inheritance when relationships are 'has-a' rather than 'is-a'.",
            "Dunder methods (__str__, __len__, etc.) let you customise built-in behaviour.",
        ],
        "analogies": [
            "A class is like a cookie cutter — it defines the shape, but each cookie (instance) is "
            "separate and you can decorate each one differently."
        ],
    },
    "algorithm": {
        "explanation": (
            "An **algorithm** is a finite, unambiguous sequence of steps that transforms an input into "
            "an output and is guaranteed to terminate. Algorithms are language-independent — the same "
            "algorithm can be implemented in Python, Java, or pseudocode.\n\n"
            "Algorithms are evaluated by their **time complexity** (how the run-time scales with input size) "
            "and **space complexity** (how much memory they need). Big-O notation (O(n), O(log n), O(n²)) "
            "is the standard tool for this analysis."
        ),
        "examples": [
            "Binary search: O(log n) — repeatedly halve the search space.",
            "Bubble sort: O(n²) — repeatedly swap adjacent out-of-order elements.",
            "Merge sort: O(n log n) — divide, sort recursively, then merge.",
        ],
        "key_points": [
            "Always consider worst-case, average-case, and best-case complexity separately.",
            "A correct algorithm that is too slow for large inputs may be useless in practice.",
            "Greedy, dynamic programming, and divide-and-conquer are common algorithm design strategies.",
        ],
        "analogies": [
            "An algorithm is like a recipe — a precise list of steps that, if followed faithfully, "
            "always produces the same dish (output) from the same ingredients (input)."
        ],
    },
}


def _explain_from_lookup(topic_name: str) -> dict[str, Any] | None:
    """Return the lookup entry for *topic_name*, case-insensitive partial match."""
    key = topic_name.lower().strip()
    if key in _TOPIC_LOOKUP:
        return _TOPIC_LOOKUP[key]
    for k, v in _TOPIC_LOOKUP.items():
        if k in key or key in k:
            return v
    return None


def _depth_note(difficulty_level: str) -> str:
    if difficulty_level == "beginner":
        return " Explained here in plain language, skipping technical jargon."
    if difficulty_level == "advanced":
        return " The explanation below assumes familiarity with prerequisites and goes into technical depth."
    return ""


# ── Question templates ────────────────────────────────────────────────────────

_MC_TEMPLATES = [
    "Which of the following best describes '{name}'?",
    "What is the primary purpose of '{name}'?",
    "How does '{name}' work in this context?",
    "Which statement about '{name}' is correct?",
]

_TF_TEMPLATES = [
    "True or False: '{name}' is {definition_start}.",
    "True or False: Understanding '{name}' is essential in this domain.",
    "True or False: '{name}' can be used to {use_verb} data.",
]

_SA_TEMPLATES = [
    "Explain briefly: what is '{name}' and why does it matter?",
    "Why is '{name}' important in this field?",
    "How would you apply '{name}' in a real-world situation?",
]

_USE_VERBS = ["process", "store", "analyse", "transform", "describe"]


def _mc_question(concept: dict, q_idx: int, difficulty: str) -> dict[str, Any]:
    name = concept.get("name", f"Concept {q_idx + 1}")
    definition = concept.get("definition", f"a key concept called {name}")
    template = _MC_TEMPLATES[q_idx % len(_MC_TEMPLATES)]
    distractors = [
        f"A built-in operation that automatically applies {name.lower()} to all elements",
        f"An error type raised when {name.lower()} is used incorrectly",
        f"A special keyword that imports the {name.lower()} module",
    ]
    return {
        "question_text": template.format(name=name),
        "question_type": "multiple_choice",
        "options": [definition] + distractors[:3],
        "correct_answer": definition,
        "explanation": (
            f"'{name}' is defined as: {definition}. "
            "The other options describe related but distinct ideas."
        ),
        "difficulty": difficulty,
        "order_index": q_idx,
    }


def _tf_question(concept: dict, q_idx: int, difficulty: str) -> dict[str, Any]:
    name = concept.get("name", f"Concept {q_idx + 1}")
    definition = concept.get("definition", "")
    def_start = (definition[:40].rstrip() + "…") if len(definition) > 40 else definition
    use_verb = _USE_VERBS[q_idx % len(_USE_VERBS)]
    template = _TF_TEMPLATES[q_idx % len(_TF_TEMPLATES)]
    question_text = template.format(
        name=name,
        definition_start=def_start,
        use_verb=use_verb,
    )
    return {
        "question_text": question_text,
        "question_type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "explanation": (
            f"This is true. {name} is indeed {def_start}."
        ),
        "difficulty": difficulty,
        "order_index": q_idx,
    }


def _sa_question(concept: dict, q_idx: int, difficulty: str) -> dict[str, Any]:
    name = concept.get("name", f"Concept {q_idx + 1}")
    definition = concept.get("definition", f"a key concept called {name}")
    template = _SA_TEMPLATES[q_idx % len(_SA_TEMPLATES)]
    return {
        "question_text": template.format(name=name),
        "question_type": "short_answer",
        "options": [],
        "correct_answer": definition,
        "explanation": (
            f"A good answer should mention: {definition}"
        ),
        "difficulty": difficulty,
        "order_index": q_idx,
    }


# ── Answer templates ──────────────────────────────────────────────────────────

def _build_answer(
    question: str,
    session_history: list[dict[str, str]],
    material_context: str,
) -> str:
    q_lower = question.lower()
    ctx_note = (
        " Drawing on the study material loaded in this session."
        if material_context
        else ""
    )
    is_technical = any(
        kw in q_lower
        for kw in ("code", "function", "class", "loop", "algorithm", "implement", "python", "syntax")
    )

    def _code_block() -> str:
        if not is_technical:
            return ""
        return (
            "\n\n```python\n"
            "# Illustrative example\n"
            "def example():\n"
            "    # Your implementation here\n"
            "    pass\n"
            "```"
        )

    if "difference between" in q_lower or "compare" in q_lower or "vs" in q_lower:
        # Comparison template
        return (
            f"Good question about differences!{ctx_note}\n\n"
            "The two ideas share a common goal but differ in approach. The first concept "
            "focuses on how data is *structured* — it defines the shape and rules. The second "
            "concept focuses on how data is *used* — it describes the operations you perform. "
            "Understanding both together gives you a complete picture.\n\n"
            "A simple rule of thumb: if you're asking 'what does it look like?', you're thinking "
            "about the first. If you're asking 'what can I do with it?', you're thinking about the second.\n\n"
            "In practice, they are complementary rather than competing — most real solutions "
            f"need both.{_code_block()}"
        )

    if q_lower.startswith("why") or "why is" in q_lower or "why does" in q_lower:
        # Explanation of purpose
        return (
            f"Great 'why' question!{ctx_note}\n\n"
            f"The underlying reason is rooted in how systems are designed to be efficient and maintainable. "
            "When you understand the motivation, the mechanics become much easier to remember.\n\n"
            "Think of it this way: every rule or concept in a well-designed system exists to solve a "
            "specific problem. Once you identify the problem it solves, the concept becomes obvious.\n\n"
            f"In the context of '{question[:60]}{'...' if len(question) > 60 else ''}': "
            "the reason is primarily about clarity, correctness, and avoiding common failure modes "
            f"that would otherwise occur.{_code_block()}"
        )

    if q_lower.startswith("how") or "how does" in q_lower or "how to" in q_lower:
        # Process / how-to template
        return (
            f"Here's a step-by-step breakdown:{ctx_note}\n\n"
            "**Step 1 — Understand the inputs.** Identify what data or state the process starts with. "
            "Getting the inputs right is half the battle.\n\n"
            "**Step 2 — Apply the transformation.** The core mechanism maps the input through a set of "
            "well-defined rules. In most cases this happens automatically, but knowing what is happening "
            "internally helps you debug when things go wrong.\n\n"
            "**Step 3 — Verify the output.** Always check that the result matches your expectations. "
            f"A small test case goes a long way.{_code_block()}"
        )

    if "example" in q_lower or "show me" in q_lower or "demonstrate" in q_lower:
        # Example-focused template
        return (
            f"Here are concrete examples:{ctx_note}\n\n"
            "**Example 1 — Minimal case.** Start with the simplest possible scenario where you can "
            "see the concept in isolation, without noise from the surrounding code.\n\n"
            "**Example 2 — Realistic case.** A slightly more complex situation that resembles what "
            "you would encounter in a real project. Notice how the pattern from Example 1 extends "
            "naturally.\n\n"
            "**Example 3 — Common pitfall.** The mistake most beginners make, and why it happens. "
            f"Knowing this in advance saves you hours of debugging.{_code_block()}"
        )

    if len(question) < 40:
        # Short factual question
        return (
            f"Here's a concise answer:{ctx_note}\n\n"
            f"'{question.strip()}' refers to a well-established concept where the key insight is that "
            "the system follows a predictable, rule-based behaviour. Once you internalise the rule, "
            "everything else follows logically.\n\n"
            "The most important thing to remember is the base case or definition — from there, you can "
            "derive everything else.\n\n"
            "Would you like a worked example or a deeper explanation of any particular aspect?"
        )

    # Default / long question template
    turn = len(session_history) + 1
    return (
        f"Based on your question (turn {turn} of our conversation):{ctx_note}\n\n"
        "The concept you're asking about operates on a fundamental principle that is consistent "
        "across many domains: **inputs are transformed by a well-defined process into outputs**, "
        "and understanding that process is the key to mastery.\n\n"
        "At its core, this works because the underlying system was designed to be both powerful and "
        "predictable. The designers made deliberate trade-offs — favouring clarity over raw performance "
        "in some areas, and vice versa in others.\n\n"
        "A practical way to remember this: think of each concept as a small machine. Feed it the right "
        f"inputs, follow the rules, and you will always get the expected output.{_code_block()}"
    )


# ── Service class ─────────────────────────────────────────────────────────────

class DemoLLMService(BaseLLMService):
    """
    Deterministic demo provider.

    Returns pre-formed, realistic responses that adapt to the domain
    indicated by the title / topic / question. The response shapes are
    identical to what a real LLM provider would return, so service and
    UI code can be built and tested against them immediately.
    """

    # ── analyse_content ───────────────────────────────────────────────────────

    async def analyse_content(
        self,
        raw_text: str,
        title: str = "",
    ) -> ContentAnalysis:
        domain = _title_domain(title)
        display_title = title or "Study Material"

        if domain == "python":
            summary = (
                f"'{display_title}' is a comprehensive introduction to Python covering "
                "core programming concepts — variables, control flow, functions, and "
                "data structures. Suitable for absolute beginners with no prior experience."
            )
            sections = _PYTHON_SECTIONS
        elif domain == "math":
            summary = (
                f"'{display_title}' covers the fundamental pillars of calculus and mathematical "
                "analysis: limits, derivatives, integrals, real-world applications, and infinite "
                "series. Each topic builds on the previous, culminating in a unified framework for "
                "continuous change."
            )
            sections = _MATH_SECTIONS
        elif domain == "history":
            summary = (
                f"'{display_title}' provides a structured historical analysis covering the causes, "
                "key events, major figures, consequences, and lasting legacy of the period. "
                "Primary sources and historiographical perspectives are integrated throughout."
            )
            sections = _HISTORY_SECTIONS
        elif domain == "biology":
            summary = (
                f"'{display_title}' surveys the core disciplines of modern biology: cell biology, "
                "genetics, evolution, ecology, and physiology. The material connects molecular "
                "mechanisms to organism-level and ecosystem-level phenomena."
            )
            sections = _BIOLOGY_SECTIONS
        else:
            summary = (
                f"'{display_title}' introduces the essential ideas in this domain, progressing from "
                "foundational concepts through practical applications to advanced topics. "
                f"Context excerpt: {raw_text[:120].strip()!r}…" if raw_text else
                f"'{display_title}' provides a thorough treatment of the subject from introductory "
                "principles to advanced applications."
            )
            sections = _generic_sections(raw_text, display_title)

        return ContentAnalysis(summary=summary, sections=sections)

    # ── explain_topic ─────────────────────────────────────────────────────────

    async def explain_topic(
        self,
        topic_name: str,
        context: str = "",
        difficulty_level: str = "intermediate",
    ) -> TopicExplanation:
        entry = _explain_from_lookup(topic_name)
        depth_note = _depth_note(difficulty_level)

        if entry:
            explanation = entry["explanation"] + depth_note
            examples = entry["examples"]
            key_points = entry["key_points"]
            analogies = entry["analogies"]
        else:
            if difficulty_level == "beginner":
                explanation = (
                    f"**{topic_name}** is a concept you will encounter often in this field.{depth_note} "
                    f"In simple terms, {topic_name.lower()} is about organising or processing information "
                    "in a consistent, repeatable way. You do not need any special background to understand "
                    "it — start with the examples below and the definition will click naturally.\n\n"
                    f"Once you are comfortable with {topic_name.lower()}, you will notice it appearing "
                    "everywhere in the subject, often as a building block for more complex ideas."
                )
            elif difficulty_level == "advanced":
                explanation = (
                    f"**{topic_name}** is a concept with both theoretical depth and practical importance.{depth_note} "
                    f"At an advanced level, {topic_name.lower()} can be analysed in terms of its formal "
                    "properties: invariants, edge cases, computational complexity, and interaction with "
                    "other components of the system.\n\n"
                    f"Mastery of {topic_name.lower()} requires not just knowing the definition but being "
                    "able to derive consequences from it, identify when it applies, and recognise when an "
                    "apparent instance of it is actually a different phenomenon."
                )
            else:
                explanation = (
                    f"**{topic_name}** is a fundamental concept in this field.{depth_note} "
                    f"At the intermediate level, understanding {topic_name.lower()} means grasping how "
                    "it represents, organises, or transforms information in a well-defined way. "
                    "It forms a building block for more complex operations and appears in virtually "
                    "every real application of the subject.\n\n"
                    f"The key to {topic_name.lower()} is identifying the pattern it encodes — once you "
                    "see the pattern, applications become straightforward."
                )
            examples = [
                f"# Example 1 — basic usage of {topic_name}",
                f"# Example 2 — {topic_name} applied in a realistic scenario",
                f"# Example 3 — common pitfall with {topic_name} and how to avoid it",
            ]
            key_points = [
                f"{topic_name} follows consistent, predictable rules — learn the rules first.",
                f"Understanding {topic_name} unlocks many related concepts in the same field.",
                f"Practise with small examples before applying {topic_name} in complex settings.",
            ]
            analogies = [
                f"Think of {topic_name} like a standardised container in a warehouse — it has a "
                "defined shape and rules for what can go inside, making the whole system predictable."
            ]

        ctx_hint = f" (context: {context[:60]}…)" if context and len(context) > 10 else ""
        return TopicExplanation(
            topic=topic_name + ctx_hint,
            explanation=explanation,
            examples=examples,
            key_points=key_points,
            analogies=analogies,
        )

    # ── generate_quiz ─────────────────────────────────────────────────────────

    async def generate_quiz(
        self,
        concepts: list[dict[str, Any]],
        num_questions: int = 5,
        difficulty: str = "mixed",
    ) -> GeneratedQuiz:
        concept_slice = concepts[:num_questions]
        n = len(concept_slice)
        mc_end = max(1, n // 3)
        tf_end = max(mc_end + 1, mc_end + n // 3)

        difficulty_cycle = ["easy", "medium", "hard"]
        questions = []

        for idx, concept in enumerate(concept_slice):
            q_difficulty = (
                difficulty if difficulty != "mixed" else difficulty_cycle[idx % 3]
            )
            if idx < mc_end:
                q = _mc_question(concept, idx, q_difficulty)
            elif idx < tf_end:
                q = _tf_question(concept, idx, q_difficulty)
            else:
                q = _sa_question(concept, idx, q_difficulty)
            questions.append(q)

        quiz_title = (
            f"Quiz — {concepts[0].get('name', 'Concepts')}" if concepts else "Quiz"
        )
        return GeneratedQuiz(
            title=quiz_title,
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
        steps = []
        total_minutes = 0
        order = 0

        for idx, section in enumerate(sections):
            section_title = section.get("title", f"Section {idx + 1}")
            concepts = section.get("concepts", [])
            n_concepts = len(concepts)

            read_mins = max(15, n_concepts * 8)
            practice_mins = max(10, n_concepts * 3)
            reflect_mins = 5

            prereq_read = [order - 3] if order >= 3 else []

            # Read step
            steps.append({
                "title": f"Read: {section_title}",
                "description": (
                    f"Work through '{section_title}' carefully. "
                    f"Focus on the {n_concepts} core concept(s): "
                    + (", ".join(c.get("name", "") for c in concepts[:3]) or "key ideas")
                    + ". Take notes in your own words and highlight anything unclear."
                ),
                "order_index": order,
                "estimated_minutes": read_mins,
                "concept_name": None,
                "prerequisites": prereq_read,
            })
            order += 1
            total_minutes += read_mins

            # Practise step
            steps.append({
                "title": f"Practise: {section_title}",
                "description": (
                    f"Complete the quiz for '{section_title}'. "
                    "Aim for at least 80% before moving on. "
                    "Review any questions you got wrong immediately."
                ),
                "order_index": order,
                "estimated_minutes": practice_mins,
                "concept_name": None,
                "prerequisites": [order - 1],
            })
            order += 1
            total_minutes += practice_mins

            # Reflect step
            steps.append({
                "title": f"Reflect: {section_title}",
                "description": (
                    f"Write a 3-sentence summary of '{section_title}' in your own words "
                    "without looking at the material. Then compare it with your notes. "
                    "This active recall step cements long-term retention."
                ),
                "order_index": order,
                "estimated_minutes": reflect_mins,
                "concept_name": None,
                "prerequisites": [order - 1],
            })
            order += 1
            total_minutes += reflect_mins

        goal_note = f" Goal: {learner_goal}." if learner_goal else ""
        return GeneratedLearningPath(
            title=f"Learning Path: {material_title}",
            description=(
                f"A structured, three-phase path through '{material_title}' — "
                f"read, practise, and reflect for each section.{goal_note}"
            ),
            estimated_duration_minutes=total_minutes,
            steps=steps,
        )

    # ── answer_question ───────────────────────────────────────────────────────

    async def answer_question(
        self,
        question: str,
        session_history: list[dict[str, str]],
        material_context: str = "",
    ) -> ChatAnswer:
        answer_text = _build_answer(question, session_history, material_context)
        sources = (
            [f"Study Material — Context excerpt", "General domain knowledge"]
            if material_context
            else []
        )
        return ChatAnswer(
            answer=answer_text,
            sources=sources,
            follow_up_suggestions=[
                "Can you give me a concrete worked example?",
                "What are the most common mistakes to avoid here?",
                "How does this connect to the next topic in the material?",
            ],
            prompt_tokens=0,
            completion_tokens=0,
        )
