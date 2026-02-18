# rag/modes.py
"""
Conversation modes define *how* the assistant reasons, retrieves context,
and produces answers.

A mode is a policy:
- what kind of retrieval is preferred
- whether LLM reasoning is used
- how answers should be structured
- what the user's intent is assumed to be

Modes are explicit and selected by the user (or UI),
not inferred automatically (at least initially).

They are stored per conversation and affect:
- prompt construction
- context selection
- answer style
"""

from dataclasses import dataclass
from enum import Enum


class ConversationMode(str, Enum):
    """
    Enumeration of supported conversational modes.

    The value of each enum is a stable external identifier
    (safe to store in DB, JSON, URLs).
    """

    SEARCH = "search"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    CODING = "coding"
    ARCHITECTURE = "architecture"
    EXPLORATION = "exploration"
    FULL = "full"


@dataclass(frozen=True)
class ModePolicy:
    """
    Declarative policy describing how a mode behaves.

    This object contains NO logic.
    """

    use_retrieval: bool
    use_llm: bool
    prefer_full_code: bool
    expand_inheritance_depth: int
    inject_project_overview: bool
    conversational_directive: str
    description: str


MODE_POLICIES: dict[ConversationMode, ModePolicy] = {
    ConversationMode.SEARCH: ModePolicy(
        use_retrieval=True,
        use_llm=False,
        prefer_full_code=False,
        expand_inheritance_depth=0,
        inject_project_overview=False,
        conversational_directive=(
            "Locate relevant code elements and report where they are defined. Do not explain behavior unless explicitly asked."
        ),
        description="Fast semantic search for code locations.",
    ),
    ConversationMode.DOCUMENTATION: ModePolicy(
        use_retrieval=True,
        use_llm=True,
        prefer_full_code=False,
        expand_inheritance_depth=1,
        inject_project_overview=True,
        conversational_directive=(
            "Explain what the code does and how it is intended to be used. "
            "Focus on purpose and responsibilities, not implementation details."
        ),
        description="Generate documentation-style explanations.",
    ),
    ConversationMode.DEBUGGING: ModePolicy(
        use_retrieval=True,
        use_llm=True,
        prefer_full_code=True,
        expand_inheritance_depth=2,
        inject_project_overview=False,
        conversational_directive=(
            "Explain runtime behavior, edge cases, and failure modes. Focus on why things happen and what could go wrong."
        ),
        description="Reason about bugs, crashes, and unexpected behavior.",
    ),
    ConversationMode.CODING: ModePolicy(
        use_retrieval=True,
        use_llm=True,
        prefer_full_code=True,
        expand_inheritance_depth=1,
        inject_project_overview=False,
        conversational_directive=(
            "Provide concrete implementation guidance. Use code snippets where appropriate. Avoid vague advice."
        ),
        description="Assist with writing or modifying code.",
    ),
    ConversationMode.ARCHITECTURE: ModePolicy(
        use_retrieval=True,
        use_llm=True,
        prefer_full_code=False,
        expand_inheritance_depth=3,
        inject_project_overview=True,
        conversational_directive=(
            "Explain system structure and interactions between components. Focus on design intent and data flow."
        ),
        description="High-level system and architectural explanations.",
    ),
    ConversationMode.EXPLORATION: ModePolicy(
        use_retrieval=True,
        use_llm=True,
        prefer_full_code=False,
        expand_inheritance_depth=0,
        inject_project_overview=True,
        conversational_directive=("Explore the codebase and explain relevant parts clearly. Balance overview with detail."),
        description="General-purpose exploratory mode.",
    ),
    ConversationMode.FULL: ModePolicy(
        use_retrieval=True,
        use_llm=True,
        prefer_full_code=True,
        expand_inheritance_depth=3,
        inject_project_overview=True,
        conversational_directive=("Full details"),
        description="Full detailed mode",
    ),
}


def get_mode_policy(mode: ConversationMode) -> ModePolicy:
    """
    Retrieve the policy associated with a conversation mode.
    """
    return MODE_POLICIES[mode]


def list_modes() -> dict[str, str]:
    """
    Return available modes with descriptions (useful for UI).
    """
    return {mode.value: policy.description for mode, policy in MODE_POLICIES.items()}
