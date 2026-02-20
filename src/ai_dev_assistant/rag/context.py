# rag/context.py

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

from ai_dev_assistant.tools.defaults import get_chunks_path, get_embeddings_path


@dataclass(frozen=True)
class ContextOptions:
    prefer_full_code: bool = False
    expand_inheritance_depth: int = 0
    inject_project_overview: bool = True


def extract_parents_from_overview(text: str) -> list[str]:
    """
    Extract parent class names from class overview text.
    """
    lines = text.splitlines()
    parents = []

    capture = False
    for line in lines:
        line = line.strip()

        if line.startswith("Inherits from"):
            capture = True
            continue

        if capture:
            if line.startswith("- "):
                parents.append(line[2:].strip())
            else:
                break

    return parents


def find_parent_overviews(parent_names, emb_by_id):
    """
    Find overview records for parent class names.
    """
    parents = []

    for record in emb_by_id.values():
        if record["type"] != "class_overview":
            continue

        if record["symbol"] in parent_names:
            parents.append(record)

    return parents


# ============================================================
# LOADERS
# ============================================================


def load_embeddings() -> List[Dict]:
    return json.loads(get_embeddings_path().read_text())


def load_chunks() -> List[Dict]:
    return json.loads(get_chunks_path().read_text())


# ============================================================
# HELPERS
# ============================================================


def collect_parent_overviews(
    start_overview: dict,
    emb_by_id: dict[str, dict],
    max_depth: int,
) -> list[dict]:
    """
    Collect parent class overviews up to a given inheritance depth.
    """
    collected = []
    visited = set()

    current_level = [start_overview]
    depth = 0

    while current_level and depth < max_depth:
        next_level = []

        for overview in current_level:
            parents = extract_parents_from_overview(overview["text"])

            for parent in find_parent_overviews(parents, emb_by_id):
                if parent["id"] in visited:
                    continue

                visited.add(parent["id"])
                collected.append(parent)
                next_level.append(parent)

        current_level = next_level
        depth += 1

    return collected


# ============================================================
# BUILD CONTEXT (Overview + Full Code)
# ============================================================


def build_context(
    results,
    options: ContextOptions,
):
    embeddings = load_embeddings()
    chunks = load_chunks()

    emb_by_id = {r["id"]: r for r in embeddings}
    chunk_by_id = {c["id"]: c for c in chunks}

    project_overview = next(
        (c for c in chunks if c["type"] == "project"),
        None,
    )

    context_blocks = []
    used_ids = set()

    for chunk_id, score in results:
        overview = emb_by_id.get(chunk_id)
        if not overview:
            continue
        parent_blocks = []

        if options.expand_inheritance_depth > 0 and overview["type"] == "class_overview":
            parent_overviews = collect_parent_overviews(
                start_overview=overview,
                emb_by_id=emb_by_id,
                max_depth=options.expand_inheritance_depth,
            )

            for parent in parent_overviews:
                parent_base_id = parent["id"].replace("::overview", "")
                parent_full = chunk_by_id.get(parent_base_id)

                if parent_full and parent_full["id"] in used_ids:
                    continue

                if parent_full:
                    used_ids.add(parent_full["id"])

                pb = [
                    f"[PARENT: {parent['symbol']}]\nFile: {parent['file']}\n",
                    "\n--- Overview ---\n" + parent["text"],
                ]

                if parent_full and options.prefer_full_code:
                    pb.append("\n--- Full Code ---\n" + parent_full["text"])

                parent_blocks.append("\n".join(pb))

        base_id = chunk_id.replace("::overview", "")
        full = chunk_by_id.get(base_id)

        if full and full["id"] in used_ids:
            continue

        if full:
            used_ids.add(full["id"])

        block = []

        block.append(f"[{overview['symbol']}]\nFile: {overview['file']}\nScore: {score:.3f}\n")

        block.append("\n--- Overview ---\n" + overview["text"])

        if full and options.prefer_full_code:
            block.append("\n--- Full Code ---\n" + full["text"])

        context_blocks.extend(parent_blocks)
        context_blocks.append("\n".join(block))

    final_parts = []

    if options.inject_project_overview and project_overview:
        final_parts.append("================ PROJECT STRUCTURE ================\n\n" + project_overview["text"])

    if context_blocks:
        final_parts.append(
            "\n\n================ RELEVANT CODE ================\n\n"
            + "\n\n--------------------------------------------------\n\n".join(context_blocks)
        )

    return "\n\n".join(final_parts)
