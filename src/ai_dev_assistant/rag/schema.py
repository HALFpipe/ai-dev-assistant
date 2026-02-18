"""
schema.py

This file defines the data structure used to represent a single
piece ("chunk") of code extracted from the repository.

At this stage, a chunk is JUST DATA.
No AI, no embeddings, no processing.
"""

from dataclasses import dataclass


@dataclass
class CodeChunk:
    """
    Represents one meaningful piece of code.

    Think of this as:
    "One thing we might want to talk about later."

    Examples:
    - a class
    - a method inside a class
    - a standalone function
    - a module-level overview
    """

    # A unique identifier for this chunk.
    # We build this from file path + symbol name.
    # This ID lets us refer to the same chunk later
    # (for docstrings, embeddings, retrieval, etc.).
    id: str

    # The file this chunk came from.
    # Example: "halfpipeline/core/workflow.py"
    file: str

    # What kind of chunk this is.
    # We keep this explicit so later stages
    # can treat methods differently from classes.
    #
    # Expected values:
    # - "module"
    # - "class"
    # - "method"
    # - "function"
    type: str

    # Human-readable name of the thing.
    #
    # Examples:
    # - "Workflow"
    # - "Workflow.run"
    # - "load_config"
    symbol: str

    # The ACTUAL SOURCE CODE TEXT for this chunk.
    #
    # This is what will later be:
    # - summarized
    # - embedded
    # - shown to ChatGPT
    text: str

