#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Generates a standard-compliant /llms.txt from markdown posts.
Follows the official specification at https://llmstxt.org/.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parses YAML frontmatter supporting inline and block lists, multiline strings, and scalars."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    yaml_block = parts[1].strip()
    body = parts[2].strip()

    frontmatter: Dict[str, Any] = {}
    current_key: Optional[str] = None
    is_multiline_str = False
    is_list_mode = False
    multiline_val: List[str] = []
    current_list: List[str] = []

    for line in yaml_block.split("\n"):
        raw_line = line
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("- "):
            item_val = line[2:].strip().strip("'\"")
            if is_list_mode and current_key:
                current_list.append(item_val)
                continue

        if is_multiline_str:
            if raw_line.startswith("  ") or raw_line.startswith("\t"):
                multiline_val.append(line)
                continue
            else:
                if current_key:
                    frontmatter[current_key] = " ".join(multiline_val).strip()
                is_multiline_str = False
                multiline_val = []

        if is_list_mode and current_key:
            frontmatter[current_key] = current_list
            is_list_mode = False
            current_list = []

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if not val:
                current_key = key
                is_list_mode = True
                current_list = []
                continue

            if val in (">", "|", ">-", "|-"):
                current_key = key
                is_multiline_str = True
                multiline_val = []
                continue

            if val.startswith("[") and val.endswith("]"):
                items = val[1:-1].split(",")
                cleaned = [it.strip().strip("'\"") for it in items if it.strip()]
                frontmatter[key] = cleaned
            elif val.startswith(('"', "'")) and val.endswith(('"', "'")):
                frontmatter[key] = val[1:-1]
            elif val.lower() == "true":
                frontmatter[key] = True
            elif val.lower() == "false":
                frontmatter[key] = False
            else:
                frontmatter[key] = val
            current_key = key

    if is_multiline_str and current_key:
        frontmatter[current_key] = " ".join(multiline_val).strip()
    if is_list_mode and current_key:
        frontmatter[current_key] = current_list

    return frontmatter, body


def generate_llms_txt(
    content_dir: str,
    base_url: str = "https://example.com",
    site_title: str = "Developer Documentation & Engineering Blog",
    site_summary: str = "Curated technical articles, developer guides, and engineering field notes."
) -> str:
    """Scans posts and outputs a spec-compliant llms.txt string."""
    path = Path(content_dir)
    posts = []

    for md_file in path.glob("**/index.md"):
        content = md_file.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)

        # Skip drafts
        if fm.get("draft") is True:
            continue

        title = fm.get("title", md_file.parent.name)
        desc = fm.get("description") or fm.get("summary") or ""
        cat = fm.get("categories", ["General"])
        if isinstance(cat, list) and cat:
            cat = cat[0]
        else:
            cat = str(cat) if cat else "General"

        # Calculate URL path
        rel_parent = md_file.parent.relative_to(path)
        slug = str(rel_parent).strip("/")
        url = f"{base_url.rstrip('/')}/posts/{slug}/"

        posts.append({
            "title": title,
            "description": desc,
            "category": cat,
            "url": url,
            "date": fm.get("date", ""),
        })

    # Sort posts by category then date descending
    posts.sort(key=lambda p: (p["category"], str(p["date"])), reverse=True)

    # Group by category
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for p in posts:
        cat = p["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)

    lines = [
        f"# {site_title}",
        "",
        f"> {site_summary}",
        "",
        "This file provides an index of technical posts and guides formatted for LLMs and AI coding agents.",
        "",
    ]

    for cat_name, cat_posts in sorted(by_category.items()):
        lines.append(f"## {cat_name}")
        for p in cat_posts:
            desc_part = f": {p['description']}" if p["description"] else ""
            lines.append(f"- [{p['title']}]({p['url']}){desc_part}")
        lines.append("")

    lines.extend([
        "## Optional",
        f"- [About]({base_url.rstrip('/')}/about/): Author bio and background.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate llms.txt standard index from markdown posts.")
    parser.add_argument("--content-dir", default="content/posts", help="Directory containing posts")
    parser.add_argument("--output", default="static/llms.txt", help="Output file path")
    parser.add_argument("--base-url", default="https://example.com", help="Site base URL")
    parser.add_argument("--site-title", default="Engineering Blog", help="Site title")

    args = parser.parse_args()

    content_path = Path(args.content_dir)
    if not content_path.exists():
        print(f"Error: Content directory '{args.content_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    llms_content = generate_llms_txt(
        content_dir=args.content_dir,
        base_url=args.base_url,
        site_title=args.site_title,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(llms_content, encoding="utf-8")
    print(f"Generated spec-compliant llms.txt at {out_path} ({len(llms_content.splitlines())} lines)")


if __name__ == "__main__":
    main()
