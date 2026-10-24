#!/usr/bin/env python3
"""
lint_agent_config.py
Deterministic validator for root instruction files (e.g. AGENTS.md, CLAUDE.md) and Agent Skills (SKILL.md).
"""

import re
import sys
from pathlib import Path

NAME_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIRST_SECOND_PERSON_PREFIXES = (
    "i ", "i can", "i will", "we ", "we can",
    "you ", "you can", "you should", "use this to",
)
FENCED_BLOCK_REGEX = re.compile(r"^(`{3,}|~{3,}).*?^\1", re.MULTILINE | re.DOTALL)
MD_LINK_REGEX = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def strip_fenced_code_blocks(text: str) -> str:
    return FENCED_BLOCK_REGEX.sub("", text)


def extract_local_md_links(text: str) -> list[tuple[int, str]]:
    """Return (line_number, link_path) for local .md links outside fenced code blocks."""
    results: list[tuple[int, str]] = []
    in_fence = False
    fence_marker = ""

    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if not in_fence:
            m = re.match(r"^(`{3,}|~{3,})", stripped)
            if m:
                in_fence = True
                fence_marker = m.group(1)
                continue
        else:
            if stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            continue

        for match in MD_LINK_REGEX.finditer(line):
            raw_target = match.group(1).strip().split()[0]
            if any(raw_target.startswith(scheme) for scheme in ("http://", "https://", "mailto:", "conversation://", "#")):
                continue
            target_no_anchor = raw_target.split("#", 1)[0]
            if target_no_anchor.lower().endswith(".md"):
                results.append((idx, target_no_anchor))

    return results


def lint_reference_file(ref_path: Path, label: str) -> list[str]:
    errors: list[str] = []
    try:
        ref_text = ref_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [f"Could not read reference file '{label}': {e}"]

    ref_lines = ref_text.splitlines()
    if len(ref_lines) > 300:
        errors.append(
            f"Reference file '{label}' is {len(ref_lines)} lines (max 300). "
            "Split topics into separate files under 300 lines."
        )

    for line_no, linked_md in extract_local_md_links(ref_text):
        errors.append(
            f"Reference file '{label}' (line {line_no}) links to another markdown file ('{linked_md}'). "
            "Keep references one hop deep from the root file."
        )

    return errors


def lint_root_instructions(root_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = root_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Could not read {root_path}: {e}"]

    lines = text.splitlines()
    if len(lines) > 200:
        errors.append(f"Root instruction file '{root_path.name}' is {len(lines)} lines (max 200).")

    seen_refs: set[Path] = set()
    for line_no, rel_link in extract_local_md_links(text):
        if rel_link.startswith("file:///"):
            ref_path = Path(rel_link.removeprefix("file:///"))
        else:
            ref_path = (root_path.parent / rel_link).resolve()

        if ref_path == root_path.resolve() or ref_path in seen_refs:
            continue
        seen_refs.add(ref_path)

        if not ref_path.exists():
            errors.append(f"Line {line_no}: Linked reference file '{rel_link}' does not exist.")
            continue

        errors.extend(lint_reference_file(ref_path, rel_link))

    return errors


def lint_skill(skill_dir: Path, skill_md_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Could not read {skill_md_path}: {e}"]

    lines = text.splitlines()
    if len(lines) > 500:
        errors.append(f"SKILL.md is {len(lines)} lines (max 500). Move detailed guides into references/.")

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not fm_match:
        errors.append("SKILL.md is missing valid YAML frontmatter enclosed between '---' delimiters.")
        return errors

    fm_raw, _ = fm_match.groups()
    fm: dict[str, str] = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("'\"")

    name = fm.get("name")
    if not name:
        errors.append("Frontmatter missing required 'name' field.")
    else:
        if len(name) > 64:
            errors.append(f"'name' is {len(name)} characters (max 64).")
        if not NAME_REGEX.match(name):
            errors.append(f"'name' ('{name}') must be lowercase alphanumeric and hyphens only (^[a-z0-9]+(-[a-z0-9]+)*$).")
        if skill_dir.name != name:
            errors.append(f"'name' ('{name}') does not match directory name ('{skill_dir.name}').")

    desc = fm.get("description")
    if not desc:
        errors.append("Frontmatter missing required 'description' field.")
    else:
        if len(desc) > 1024:
            errors.append(f"'description' is {len(desc)} characters (max 1,024).")
        if re.search(r"<[^>]+>", desc):
            errors.append("'description' contains raw XML tags. Strip XML from frontmatter.")
        desc_lower = desc.strip().lower()
        for prefix in FIRST_SECOND_PERSON_PREFIXES:
            if desc_lower.startswith(prefix):
                errors.append(f"'description' starts with '{prefix}'. Must be written in third person.")
                break

    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_file in sorted(refs_dir.glob("*.md")):
            errors.extend(lint_reference_file(ref_file, f"{refs_dir.name}/{ref_file.name}"))

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python lint_agent_config.py <path_to_root_instruction_file_or_skill_dir>")
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(f"Error: Target path '{target}' does not exist.")
        sys.exit(1)

    if target.is_file():
        if target.name.lower() == "skill.md":
            errors = lint_skill(target.parent, target)
        else:
            errors = lint_root_instructions(target)
    elif target.is_dir():
        skill_md = target / "SKILL.md"
        if skill_md.exists():
            errors = lint_skill(target, skill_md)
        else:
            agents_md = target / "AGENTS.md"
            if agents_md.exists():
                errors = lint_root_instructions(agents_md)
            else:
                print(f"No SKILL.md or AGENTS.md found in directory '{target}'. Pass the root instruction file path directly.")
                sys.exit(1)
    else:
        print(f"Error: Invalid target '{target}'.")
        sys.exit(1)

    if errors:
        print(f"[FAIL] Found {len(errors)} error(s) in {target.name}:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"[PASS] {target.name} satisfied all deterministic checks.")
        sys.exit(0)


if __name__ == "__main__":
    main()
