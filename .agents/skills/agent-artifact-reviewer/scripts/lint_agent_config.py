#!/usr/bin/env python3
"""
lint_agent_config.py
Deterministic validator for AGENTS.md and Agent Skills (SKILL.md).
"""

import sys
import re
from pathlib import Path

NAME_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIRST_SECOND_PERSON_PREFIXES = (
    "i ", "i can", "i will", "we ", "we can",
    "you ", "you can", "you should", "use this to",
)

def lint_agents_md(path: Path) -> list[str]:
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Could not read {path}: {e}"]

    lines = text.splitlines()

    # Rule: <= 200 lines
    if len(lines) > 200:
        errors.append(f"AGENTS.md is {len(lines)} lines. Hard ceiling is 200 lines to prevent instruction fatigue.")

    # Rule: Unix forward slashes in links
    for idx, line in enumerate(lines, start=1):
        if re.search(r"\[.*?\]\([^\)]*\\[^\)]*\)", line):
            errors.append(f"Line {idx}: Found Windows backslash in markdown link. Use forward slashes (/) exclusively.")

    return errors

def lint_skill(skill_dir: Path, skill_md_path: Path) -> list[str]:
    errors = []
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Could not read {skill_md_path}: {e}"]

    lines = text.splitlines()

    # Rule: Body <= 500 lines
    if len(lines) > 500:
        errors.append(f"SKILL.md is {len(lines)} lines. Must be under 500 lines; offload reference data into references/.")

    # Rule: Parse frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not fm_match:
        errors.append("SKILL.md is missing valid YAML frontmatter enclosed between '---' delimiters.")
        return errors

    fm_raw, body_raw = fm_match.groups()
    fm = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("'\"")

    # Name check
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

    # Description check
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

    # Forward slash check in SKILL.md
    for idx, line in enumerate(lines, start=1):
        if re.search(r"\[.*?\]\([^\)]*\\[^\)]*\)", line):
            errors.append(f"Line {idx}: Found Windows backslash in markdown link. Use forward slashes (/) exclusively.")

    # References directory checks
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_file in refs_dir.glob("*.md"):
            ref_text = ref_file.read_text(encoding="utf-8", errors="replace")
            ref_lines = ref_text.splitlines()

            # Rule: Table of contents if > 200 lines
            if len(ref_lines) > 200:
                header_window = "\n".join(ref_lines[:40]).lower()
                if "table of contents" not in header_window and "## contents" not in header_window and "# contents" not in header_window:
                    errors.append(
                        f"Reference file '{refs_dir.name}/{ref_file.name}' is {len(ref_lines)} lines (>200). "
                        "Add a Table of Contents near the top so agents can navigate line ranges efficiently."
                    )

            # Rule: Single-level reference depth (references must not link to other references)
            for idx, r_line in enumerate(ref_lines, start=1):
                if re.search(r"\[.*?\]\([^)]*(references/|\.md)[^)]*\)", r_line) and "http" not in r_line:
                    errors.append(
                        f"Reference file '{refs_dir.name}/{ref_file.name}' (line {idx}) links to another local markdown file. "
                        "Keep references strictly one level deep from SKILL.md."
                    )

    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python lint_agent_config.py <path_to_AGENTS.md_or_skill_dir>")
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(f"Error: Target path '{target}' does not exist.")
        sys.exit(1)

    errors = []

    if target.is_file():
        if target.name.lower() == "agents.md" or target.name.endswith(".md") and "agents" in target.name.lower():
            errors = lint_agents_md(target)
        elif target.name.lower() == "skill.md":
            errors = lint_skill(target.parent, target)
        else:
            print(f"Unrecognized file '{target.name}'. Expected AGENTS.md or SKILL.md.")
            sys.exit(1)
    elif target.is_dir():
        skill_md = target / "SKILL.md"
        if skill_md.exists():
            errors = lint_skill(target, skill_md)
        else:
            agents_md = target / "AGENTS.md"
            if agents_md.exists():
                errors = lint_agents_md(agents_md)
            else:
                print(f"No SKILL.md or AGENTS.md found in directory '{target}'.")
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
