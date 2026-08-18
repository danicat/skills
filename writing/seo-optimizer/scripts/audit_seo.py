#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
SEO & Generative Engine Optimization (GEO) Auditor for Technical Markdown Articles.
Audits frontmatter, heading hierarchy, image alt text, direct answer density,
GEO extractability, and link quality according to official Google Search Central standards.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Forbidden AI slop terms and phrases
SLOP_TERMS = [
    "delve", "game-changer", "game changer", "revolutionary",
    "testament to", "tapestry", "in today's fast-paced world",
    "fast-paced", "beacon of", "vital role", "seamlessly",
    "unlock the power", "furthermore", "moreover", "embark on",
    "dive deep", "harnessing the power", "look no further"
]

GENERIC_ALTS = {
    "image", "img", "screenshot", "screen shot", "diagram",
    "photo", "picture", "untitled", "image.png", "screenshot.png",
    "figure", "visual", "graphic", "icon"
}

GENERIC_ANCHORS = {
    "click here", "here", "link", "this link", "read more",
    "this post", "article", "page", "source"
}


@dataclass
class AuditFinding:
    category: str
    severity: str  # "ERROR", "WARNING", "INFO", "PASS"
    message: str
    context: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class AuditReport:
    file_path: str
    score: int
    passed: bool
    findings: List[AuditFinding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


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

        # Check for list items: "- value"
        if line.startswith("- "):
            item_val = line[2:].strip().strip("'\"")
            if is_list_mode and current_key:
                current_list.append(item_val)
                continue

        # Check for multiline string continuation
        if is_multiline_str:
            if raw_line.startswith("  ") or raw_line.startswith("\t"):
                multiline_val.append(line)
                continue
            else:
                if current_key:
                    frontmatter[current_key] = " ".join(multiline_val).strip()
                is_multiline_str = False
                multiline_val = []

        # Flush previous list mode if moving to a new key
        if is_list_mode and current_key:
            frontmatter[current_key] = current_list
            is_list_mode = False
            current_list = []

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if not val:
                # Potential start of a block list or nested structure
                current_key = key
                is_list_mode = True
                current_list = []
                continue

            if val in (">", "|", ">-", "|-"):
                current_key = key
                is_multiline_str = True
                multiline_val = []
                continue

            # Parse array inline: tags: ["a", "b"] or [a, b]
            if val.startswith("[") and val.endswith("]"):
                items = val[1:-1].split(",")
                cleaned = [it.strip().strip("'\"") for it in items if it.strip().strip("'\"")]
                frontmatter[key] = cleaned
            elif val.startswith('"') and val.endswith('"'):
                frontmatter[key] = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                frontmatter[key] = val[1:-1]
            elif val.lower() == "true":
                frontmatter[key] = True
            elif val.lower() == "false":
                frontmatter[key] = False
            elif val.isdigit():
                frontmatter[key] = int(val)
            else:
                frontmatter[key] = val
            current_key = key

    # Final flushes
    if is_multiline_str and current_key:
        frontmatter[current_key] = " ".join(multiline_val).strip()
    if is_list_mode and current_key:
        frontmatter[current_key] = current_list

    return frontmatter, body


def is_cjk(text: str) -> bool:
    """Detects if a string contains significant CJK characters (Japanese/Chinese)."""
    cjk_count = len(re.findall(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
    return cjk_count > 5


def calculate_semantic_length(text: str, is_japanese: bool) -> int:
    """Calculates equivalent character length for CJK vs Latin text."""
    if is_japanese:
        # 1 Japanese char ~ 2.5 English characters in information density
        cjk_chars = len(re.findall(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
        latin_chars = len(re.findall(r"[a-zA-Z0-9\s]", text))
        return int(cjk_chars * 2.2 + latin_chars)
    return len(text)


def count_words_or_characters(text: str, is_japanese: bool) -> int:
    """Counts words for English/Portuguese or characters for Japanese."""
    if is_japanese:
        return len(re.findall(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
    return len(text.split())


def audit_article(file_path: str, valid_categories: Optional[set] = None) -> AuditReport:
    """Performs a comprehensive SEO and GEO audit on a markdown article."""
    path = Path(file_path)
    if not path.exists():
        return AuditReport(
            file_path=file_path,
            score=0,
            passed=False,
            findings=[AuditFinding("File", "ERROR", f"File not found: {file_path}")],
        )

    content = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    is_ja = path.name.endswith(".ja.md") or is_cjk(content[:500])

    findings: List[AuditFinding] = []
    penalties = 0

    # ----------------------------------------------------
    # 1. Frontmatter Title Check
    # ----------------------------------------------------
    title = str(fm.get("title", "")).strip()
    if not title:
        findings.append(AuditFinding("Title", "ERROR", "Missing 'title' in frontmatter", fix_suggestion="Add a title: 'Your High-Signal Article Title'"))
        penalties += 20
    else:
        semantic_len = calculate_semantic_length(title, is_ja)
        raw_len = len(title)
        if semantic_len < 30:
            findings.append(AuditFinding("Title", "WARNING", f"Title is short ({raw_len} chars, effective semantic {semantic_len}). Target 40-60 chars for maximum search impact.", context=title))
            penalties += 5
        elif semantic_len > 75:
            findings.append(AuditFinding("Title", "WARNING", f"Title is long ({raw_len} chars, effective semantic {semantic_len}). May truncate in SERPs (limit: 60 chars).", context=title))
            penalties += 5
        else:
            findings.append(AuditFinding("Title", "PASS", f"Title length optimal ({raw_len} chars, effective {semantic_len})", context=title))

    # ----------------------------------------------------
    # 2. Frontmatter Description vs Summary Check
    # ----------------------------------------------------
    description = str(fm.get("description", "")).strip()
    summary = str(fm.get("summary", "")).strip()

    if not description and not summary:
        findings.append(AuditFinding("Metadata", "ERROR", "Missing both 'description' and 'summary' in frontmatter", fix_suggestion="Add distinct 'description' (for search) and 'summary' (for human cards)."))
        penalties += 20
    elif not description:
        findings.append(AuditFinding("Metadata", "WARNING", "Missing 'description' in frontmatter (falling back to summary).", fix_suggestion="Add 'description' optimized with direct-answer keywords (120-160 chars)."))
        penalties += 10
    elif not summary:
        findings.append(AuditFinding("Metadata", "INFO", "'summary' not explicitly set; theme will fall back to description.", fix_suggestion="Add an engaging 'summary' hook (80-180 chars) for UI card feeds."))
    else:
        # Both present, check for duplicate content
        if description.lower() == summary.lower():
            findings.append(AuditFinding("Metadata", "WARNING", "'description' and 'summary' are identical. Differentiate search snippet from human card hook.", context=description))
            penalties += 5
        else:
            findings.append(AuditFinding("Metadata", "PASS", "Distinct 'description' and 'summary' properly defined."))

        desc_semantic_len = calculate_semantic_length(description, is_ja)
        desc_raw_len = len(description)
        if desc_semantic_len < 80:
            findings.append(AuditFinding("Description", "WARNING", f"Description is short ({desc_raw_len} chars). Target 120-160 chars.", context=description))
            penalties += 5
        elif desc_semantic_len > 185:
            findings.append(AuditFinding("Description", "WARNING", f"Description is long ({desc_raw_len} chars). May truncate in Google snippets (>160 chars).", context=description))
            penalties += 5
        else:
            findings.append(AuditFinding("Description", "PASS", f"Description length optimal ({desc_raw_len} chars, semantic {desc_semantic_len})", context=description))

    # Check for ignored keywords meta
    if "keywords" in fm:
        findings.append(AuditFinding("Metadata", "INFO", "'keywords' in frontmatter is ignored by Google Search. Focus on title and description instead."))

    # ----------------------------------------------------
    # 3. Taxonomy & Tag Discipline
    # ----------------------------------------------------
    categories = fm.get("categories", [])
    if isinstance(categories, str):
        categories = [categories]
    categories = [c.strip() for c in categories if str(c).strip()]

    if not categories:
        findings.append(AuditFinding("Taxonomy", "WARNING", "No 'categories' defined in frontmatter."))
        penalties += 5
    elif len(categories) > 1:
        findings.append(AuditFinding("Taxonomy", "WARNING", f"Multiple categories defined ({categories}). Standard specifies exactly 1 primary category."))
        penalties += 5
    else:
        cat_name = categories[0]
        if valid_categories:
            if cat_name in valid_categories:
                findings.append(AuditFinding("Taxonomy", "PASS", f"Valid primary category: '{cat_name}'"))
            else:
                findings.append(AuditFinding("Taxonomy", "WARNING", f"Non-standard category '{cat_name}'. Allowed categories: {sorted(list(valid_categories))}"))
                penalties += 5
        else:
            findings.append(AuditFinding("Taxonomy", "PASS", f"Primary category defined: '{cat_name}'"))

    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tags = [t.strip() for t in tags if str(t).strip()]

    if not tags:
        findings.append(AuditFinding("Tags", "WARNING", "No 'tags' defined in frontmatter."))
        penalties += 5
    else:
        # Check alphabetical sorting
        sorted_tags = sorted(tags)
        if tags != sorted_tags:
            findings.append(AuditFinding("Tags", "WARNING", f"Tags are not sorted alphabetically. Should be: {sorted_tags}", context=str(tags)))
            penalties += 3

        # Check kebab-case
        for t in tags:
            if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", t):
                findings.append(AuditFinding("Tags", "WARNING", f"Tag '{t}' is not lowercase kebab-case.", fix_suggestion=f"Change '{t}' to lowercase alphanumeric kebab-case."))
                penalties += 3

        # Check category duplication
        if categories:
            cat_slug = categories[0].lower().replace(" ", "-")
            if cat_slug in tags:
                findings.append(AuditFinding("Tags", "WARNING", f"Tag '{cat_slug}' duplicates primary category '{categories[0]}'. Remove redundant tag."))
                penalties += 3

    # ----------------------------------------------------
    # 4. Heading Hierarchy & Structure
    # ----------------------------------------------------
    # Ignore code blocks when searching for headings
    cleaned_body = re.sub(r"```[\s\S]*?```", "", body)
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    headings = heading_pattern.findall(cleaned_body)

    h1_headings = [h for h in headings if len(h[0]) == 1]
    if len(h1_headings) > 0:
        findings.append(AuditFinding("Headings", "WARNING", f"Found {len(h1_headings)} '# H1' in markdown body. In Hugo, frontmatter title renders as H1; body headings should start at '## H2'.", context=h1_headings[0][1]))
        penalties += 10

    # Check level jumps
    last_level = 1
    for h in headings:
        level = len(h[0])
        if level > last_level + 1:
            findings.append(AuditFinding("Headings", "WARNING", f"Skipped heading level: jumped from H{last_level} to H{level} ('{h[1]}'). Maintain sequential nesting."))
            penalties += 5
            break
        last_level = level

    if len(headings) >= 2:
        findings.append(AuditFinding("Headings", "PASS", f"Document structure contains {len(headings)} well-nested section headings."))

    # ----------------------------------------------------
    # 5. Image Alt Text & Accessibility
    # ----------------------------------------------------
    img_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
    images = img_pattern.findall(body)

    for alt, src in images:
        alt_clean = alt.strip().lower()
        if not alt_clean:
            findings.append(AuditFinding("Images", "ERROR", f"Image with empty alt text: '{src}'", fix_suggestion="Add a descriptive alt text explaining the diagram or screenshot."))
            penalties += 10
        elif alt_clean in GENERIC_ALTS or alt_clean.endswith(".png") or alt_clean.endswith(".jpg"):
            findings.append(AuditFinding("Images", "WARNING", f"Image has generic alt text: '{alt}' for '{src}'", fix_suggestion="Provide a 40-100 character explanation of what the image shows."))
            penalties += 5
        else:
            findings.append(AuditFinding("Images", "PASS", f"Image has descriptive alt text: '{alt}'"))

    # ----------------------------------------------------
    # 6. Generative Engine Optimization (GEO) & Direct Answer
    # ----------------------------------------------------
    content_metric = count_words_or_characters(body, is_ja)
    metric_label = "characters" if is_ja else "words"

    # Lead paragraph check (first 200 words or 400 Japanese chars)
    lead_sample = body[:600]
    has_bold_definition = bool(re.search(r"\*\*[^\n*]{5,60}\*\*", lead_sample))
    has_code_snippet = "```" in body
    has_markdown_table = bool(re.search(r"\|.*\|.*\n\|[-:\s|]+\|", body))

    geo_score = 0
    if has_bold_definition:
        geo_score += 25
        findings.append(AuditFinding("GEO", "PASS", "Lead text contains bolded key definition/direct-answer hook."))
    else:
        findings.append(AuditFinding("GEO", "INFO", "Consider bolding key terms or definitions in the opening paragraph for AI snippet extraction."))

    if has_code_snippet:
        geo_score += 25
        findings.append(AuditFinding("GEO", "PASS", "Contains fenced code blocks for technical extraction."))

    if has_markdown_table:
        geo_score += 25
        findings.append(AuditFinding("GEO", "PASS", "Contains structured Markdown comparison/specification table."))

    min_threshold = 800 if is_ja else 400
    if content_metric >= min_threshold:
        geo_score += 25
    else:
        findings.append(AuditFinding("Content", "WARNING", f"Short article length ({content_metric} {metric_label}). May struggle to compete for deep technical queries."))
        penalties += 5

    # ----------------------------------------------------
    # 7. AI Slop & Cliché Detection
    # ----------------------------------------------------
    body_lower = body.lower()
    slop_matches = []
    for term in SLOP_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", body_lower):
            slop_matches.append(term)

    if slop_matches:
        findings.append(AuditFinding("Writing", "WARNING", f"Found {len(slop_matches)} AI writing cliché(s): {slop_matches[:4]}", fix_suggestion="Replace with direct, concrete developer language."))
        penalties += min(len(slop_matches) * 3, 15)
    else:
        findings.append(AuditFinding("Writing", "PASS", "Zero AI slop buzzwords detected."))

    # ----------------------------------------------------
    # 8. Link & Anchor Text Quality
    # ----------------------------------------------------
    link_pattern = re.compile(r"\[(.*?)\]\((.*?)\)")
    links = link_pattern.findall(body)

    for anchor, url in links:
        if anchor.startswith("!"):
            continue
        anchor_clean = anchor.strip().lower()
        if anchor_clean in GENERIC_ANCHORS:
            findings.append(AuditFinding("Links", "WARNING", f"Generic anchor text: '[{anchor}]({url})'", fix_suggestion="Use descriptive anchor text with target topic/title."))
            penalties += 3

    # ----------------------------------------------------
    # 9. HTML Directives, Meta Tags & data-nosnippet Checks
    # ----------------------------------------------------
    # Check for meta-refresh anti-pattern in raw HTML snippets
    if re.search(r'<meta\s+[^>]*http-equiv=["\']refresh["\']', body, re.IGNORECASE):
        findings.append(AuditFinding("HTML", "ERROR", "Found '<meta http-equiv=\"refresh\">'. Violates WCAG accessibility and SEO standards. Use server-side 301/308 redirects.", fix_suggestion="Replace meta-refresh with HTTP 301 redirect."))
        penalties += 15

    # Check for invalid data-nosnippet tags (only valid on span, div, section)
    nosnippet_tags = re.findall(r'<([a-zA-Z0-9]+)\s+[^>]*data-nosnippet', body, re.IGNORECASE)
    valid_nosnippet_tags = {"span", "div", "section"}
    for tag in nosnippet_tags:
        if tag.lower() not in valid_nosnippet_tags:
            findings.append(AuditFinding("HTML", "WARNING", f"'data-nosnippet' attribute used on invalid tag '<{tag}>'. Google only supports data-nosnippet on <span>, <div>, and <section>.", fix_suggestion=f"Wrap content in a <div>, <span>, or <section> and attach data-nosnippet to that wrapper."))
            penalties += 5

    # Check for date / lastmod ISO 8601 formatting in frontmatter
    for date_key in ("date", "lastmod", "publishDate"):
        if date_key in fm:
            date_val = str(fm[date_key])
            if not re.match(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)?)?$", date_val):
                findings.append(AuditFinding("Metadata", "WARNING", f"'{date_key}' value '{date_val}' is not valid ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).", fix_suggestion="Use standard ISO 8601 formatting for publication timestamps."))
                penalties += 3

    # Calculate overall score
    final_score = max(0, min(100, 100 - penalties))
    passed = final_score >= 80

    metrics = {
        f"content_length_{metric_label}": content_metric,
        "is_japanese": is_ja,
        "heading_count": len(headings),
        "image_count": len(images),
        "link_count": len(links),
        "geo_readiness_score": geo_score,
        "title_length": len(title),
        "description_length": len(description),
        "summary_length": len(summary),
    }

    return AuditReport(
        file_path=str(path.resolve()),
        score=final_score,
        passed=passed,
        findings=findings,
        metrics=metrics,
    )


def format_markdown_report(report: AuditReport) -> str:
    """Formats an audit report as readable markdown."""
    status_emoji = "✅ PASS" if report.passed else "⚠️ NEEDS OPTIMIZATION"
    is_ja = report.metrics.get("is_japanese", False)
    len_label = "characters" if is_ja else "words"
    len_val = report.metrics.get(f"content_length_{len_label}", 0)

    lines = [
        f"# SEO & GEO Audit Report: `{os.path.basename(report.file_path)}`",
        "",
        f"**Status:** {status_emoji}  ",
        f"**Overall Score:** `{report.score}/100`  ",
        f"**Content Length:** {len_val} {len_label} | **GEO Readiness:** `{report.metrics.get('geo_readiness_score', 0)}/100`",
        "",
        "---",
        "",
        "## Key Findings & Recommendations",
        "",
        "| Category | Severity | Message | Recommendation |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for f in report.findings:
        sev_icon = {"PASS": "🟢", "INFO": "🔵", "WARNING": "🟡", "ERROR": "🔴"}.get(f.severity, "⚪")
        fix = f.fix_suggestion or "-"
        lines.append(f"| {f.category} | {sev_icon} {f.severity} | {f.message} | {fix} |")

    lines.extend([
        "",
        "---",
        "## Metadata Metrics",
        "",
        f"- **Title Length:** {report.metrics.get('title_length', 0)} characters (Target: 40–60)",
        f"- **Description Length:** {report.metrics.get('description_length', 0)} characters (Target: 120–160)",
        f"- **Summary Length:** {report.metrics.get('summary_length', 0)} characters (Target: 80–180)",
        f"- **Headings:** {report.metrics.get('heading_count', 0)} | **Images:** {report.metrics.get('image_count', 0)} | **Links:** {report.metrics.get('link_count', 0)}",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit technical Markdown for SEO and Generative Engine Optimization (GEO).")
    parser.add_argument("target", help="Path to a markdown file or directory of markdown files")
    parser.add_argument("--categories", help="Comma-separated list of allowed primary categories (optional)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--quiet", action="store_true", help="Only output if errors or warnings exist")

    args = parser.parse_args()
    target_path = Path(args.target)

    if not target_path.exists():
        print(f"Error: Target '{args.target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    valid_cats = None
    if args.categories:
        valid_cats = {c.strip() for c in args.categories.split(",") if c.strip()}

    files_to_audit = []
    if target_path.is_file():
        files_to_audit.append(target_path)
    elif target_path.is_dir():
        files_to_audit.extend(sorted(list(target_path.glob("**/*.md"))))

    reports = []
    for f in files_to_audit:
        reports.append(audit_article(str(f), valid_categories=valid_cats))

    if args.json:
        out = [asdict(r) for r in reports]
        print(json.dumps(out, indent=2))
        return

    for r in reports:
        print(format_markdown_report(r))
        print("\n" + "=" * 60 + "\n")

    if any(not r.passed for r in reports):
        sys.exit(1)


if __name__ == "__main__":
    main()
