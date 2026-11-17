#!/usr/bin/env python3
# Copyright 2026 Daniela Petruzalek
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
Generates a standard-compliant /llms.txt (and optional /llms-full.txt) from markdown posts.
Follows the official specification at https://llmstxt.org/.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

TRANSLATION_STEM_RE = re.compile(r"^.+\.[a-z]{2}(?:-[a-z]{2,4})?$")


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


def collect_posts(
    content_dir: str,
    base_url: str = "https://example.com",
    url_prefix: str = "posts",
    include_translations: bool = False,
) -> Dict[str, List[Dict[str, Any]]]:
    """Scans page bundles and standalone markdown files and groups non-draft posts by category."""
    path = Path(content_dir)
    base = base_url.rstrip("/")
    prefix = url_prefix.strip("/")
    by_category: Dict[str, List[Dict[str, Any]]] = {}

    for md_file in sorted(path.glob("**/*.md")):
        # Skip section landing files (_index.md, _index.ja.md)
        if md_file.stem == "_index" or md_file.stem.startswith("_index."):
            continue
        if not include_translations and TRANSLATION_STEM_RE.match(md_file.stem):
            continue

        content = md_file.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)

        if fm.get("draft") is True:
            continue

        if md_file.name == "index.md":
            rel_slug = md_file.parent.relative_to(path)
        else:
            rel_slug = md_file.relative_to(path).with_suffix("")

        slug = "" if str(rel_slug) in ("", ".") else str(rel_slug).replace(os.sep, "/").strip("/")
        url_parts = [p for p in (prefix, slug) if p]
        url = f"{base}/{'/'.join(url_parts)}/" if url_parts else f"{base}/"

        title = str(fm.get("title") or (md_file.parent.name if md_file.name == "index.md" else md_file.stem))
        desc = str(fm.get("description") or fm.get("summary") or "")
        cat_val = fm.get("categories", ["General"])
        if isinstance(cat_val, list) and cat_val:
            cat = str(cat_val[0])
        else:
            cat = str(cat_val) if cat_val else "General"

        post = {
            "title": title,
            "description": desc,
            "category": cat,
            "url": url,
            "date": str(fm.get("date", "")),
            "body": body,
        }
        by_category.setdefault(cat, []).append(post)

    for cat in by_category:
        by_category[cat].sort(key=lambda p: (p["date"], p["title"]), reverse=True)

    return by_category


def format_llms_txt(
    by_category: Dict[str, List[Dict[str, Any]]],
    base_url: str = "https://example.com",
    site_title: str = "Developer Documentation and Engineering Blog",
    site_summary: str = "Curated technical articles, developer guides, and engineering field notes.",
) -> str:
    """Formats collected posts into a spec-compliant llms.txt index."""
    lines = [
        f"# {site_title}",
        "",
        f"> {site_summary}",
        "",
        "This file provides an index of technical posts and guides formatted for LLMs and AI coding agents.",
        "",
    ]

    for cat_name in sorted(by_category):
        lines.append(f"## {cat_name}")
        for p in by_category[cat_name]:
            desc_part = f": {p['description']}" if p["description"] else ""
            lines.append(f"- [{p['title']}]({p['url']}){desc_part}")
        lines.append("")

    lines.extend([
        "## Optional",
        f"- [About]({base_url.rstrip('/')}/about/): Author bio and background.",
        "",
    ])

    return "\n".join(lines)


def format_llms_full_txt(
    by_category: Dict[str, List[Dict[str, Any]]],
    site_title: str = "Developer Documentation and Engineering Blog",
    site_summary: str = "Curated technical articles, developer guides, and engineering field notes.",
) -> str:
    """Formats collected posts into a full-text llms-full.txt Markdown corpus."""
    lines = [
        f"# {site_title}",
        "",
        f"> {site_summary}",
        "",
    ]

    for cat_name in sorted(by_category):
        lines.append(f"## {cat_name}")
        lines.append("")
        for p in by_category[cat_name]:
            lines.append(f"### {p['title']}")
            lines.append(f"Source: {p['url']}")
            if p["description"]:
                lines.append(f"Summary: {p['description']}")
            lines.append("")
            lines.append(p["body"])
            lines.append("")

    return "\n".join(lines)


def generate_llms_txt(
    content_dir: str,
    base_url: str = "https://example.com",
    site_title: str = "Developer Documentation and Engineering Blog",
    site_summary: str = "Curated technical articles, developer guides, and engineering field notes.",
    url_prefix: str = "posts",
    include_translations: bool = False,
) -> str:
    """Scans posts and outputs a spec-compliant llms.txt string."""
    by_category = collect_posts(
        content_dir=content_dir,
        base_url=base_url,
        url_prefix=url_prefix,
        include_translations=include_translations,
    )
    return format_llms_txt(
        by_category=by_category,
        base_url=base_url,
        site_title=site_title,
        site_summary=site_summary,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate llms.txt standard index from markdown posts.")
    parser.add_argument("--content-dir", default="content/posts", help="Directory containing posts")
    parser.add_argument("--output", default="static/llms.txt", help="Output file path")
    parser.add_argument("--llms-full", default=None, help="Optional output path for full-text llms-full.txt corpus")
    parser.add_argument("--base-url", default="https://example.com", help="Site base URL")
    parser.add_argument("--url-prefix", default="posts", help="URL path prefix under base-url (default: posts)")
    parser.add_argument("--site-title", default="Engineering Blog", help="Site title")
    parser.add_argument("--include-translations", action="store_true", help="Include suffixed locale files such as .ja.md")

    args = parser.parse_args()

    content_path = Path(args.content_dir)
    if not content_path.exists():
        print(f"Error: Content directory '{args.content_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    by_category = collect_posts(
        content_dir=args.content_dir,
        base_url=args.base_url,
        url_prefix=args.url_prefix,
        include_translations=args.include_translations,
    )
    llms_content = format_llms_txt(
        by_category=by_category,
        base_url=args.base_url,
        site_title=args.site_title,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(llms_content, encoding="utf-8")
    print(f"Generated spec-compliant llms.txt at {out_path} ({len(llms_content.splitlines())} lines)")

    if args.llms_full:
        full_content = format_llms_full_txt(
            by_category=by_category,
            site_title=args.site_title,
        )
        full_path = Path(args.llms_full)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(full_content, encoding="utf-8")
        print(f"Generated llms-full.txt at {full_path} ({len(full_content.splitlines())} lines)")


if __name__ == "__main__":
    main()
