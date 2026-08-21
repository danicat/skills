#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "google-auth>=2.0.0",
#     "pyyaml>=6.0",
# ]
# ///
"""
Gemini Token Counter & Specification Auditor for Agent Skills
Audits skills against the 3-Tier Progressive Disclosure specification:
  - Tier 1: Routing Signal (name <= 64 chars, description <= 1024 chars, routing tokens <= 150)
  - Tier 2: Skill Body (SKILL.md body <= 5,000 tokens / <= 500 lines)
  - Tier 3: Resources (references/ loaded on demand)
"""

import argparse
import json
import os
import sys
from pathlib import Path
import yaml


# Specification & Best Practice Constraints
NAME_CHAR_LIMIT = 64
DESCRIPTION_CHAR_LIMIT = 1024
ROUTING_TOKEN_WARN_LIMIT = 150
BODY_TOKEN_LIMIT = 5000
BODY_LINE_LIMIT = 500


def get_genai_client(location: str = "global", project: str | None = None):
    """
    Initialize GenAI client with ADC (Vertex AI) or API key.
    Prefers API key if GEMINI_API_KEY is explicitly set; otherwise defaults to ADC on Vertex AI.
    """
    from google import genai

    if os.environ.get("GEMINI_API_KEY"):
        return genai.Client(), "gemini-api-key"

    # Fallback to Application Default Credentials (ADC) via Vertex AI
    if not project:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    if not project:
        try:
            import google.auth
            _, project = google.auth.default()
        except Exception:
            project = None

    client = genai.Client(vertexai=True, project=project, location=location)
    auth_label = f"adc (vertexai, project={project or 'default'}, location={location})"
    return client, auth_label


def count_tokens(client, text: str, model: str, use_heuristic: bool) -> tuple[int, str]:
    """Count tokens via Gemini API or fallback heuristic."""
    if not text.strip():
        return 0, "empty"

    if use_heuristic:
        return max(1, round(len(text) / 4)), "heuristic (~4 chars/token)"

    try:
        response = client.models.count_tokens(
            model=model,
            contents=text,
        )
        return response.total_tokens, f"api ({model})"
    except Exception as e:
        sys.stderr.write(f"Warning: Gemini API call failed: {e}\n")
        return max(1, round(len(text) / 4)), "heuristic_fallback"


def split_frontmatter_and_body(content: str) -> tuple[str, str, dict]:
    """Splits SKILL.md into frontmatter string, body string, and parsed dict."""
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", content, {}

    end_idx = -1
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = idx
            break

    if end_idx == -1:
        return "", content, {}

    frontmatter_text = "".join(lines[: end_idx + 1])
    body_text = "".join(lines[end_idx + 1 :])
    
    yaml_content = "".join(lines[1:end_idx])
    try:
        parsed_yaml = yaml.safe_load(yaml_content) or {}
    except Exception:
        parsed_yaml = {}

    return frontmatter_text, body_text, parsed_yaml


def analyze_skill(skill_file: Path, client, model: str, use_heuristic: bool) -> dict:
    content = skill_file.read_text(encoding="utf-8")
    fm_text, body_text, fm_data = split_frontmatter_and_body(content)

    skill_name = str(fm_data.get("name") or skill_file.parent.name)
    description = str(fm_data.get("description") or "").strip()

    # Routing payload (what agent orchestrators inject into system prompts at startup)
    routing_payload = f"name: {skill_name}\ndescription: {description}\n"
    routing_tokens, routing_method = count_tokens(client, routing_payload, model, use_heuristic)
    
    # Total frontmatter tokens & Catalog metadata tokens
    fm_tokens, _ = count_tokens(client, fm_text, model, use_heuristic)
    catalog_tokens = max(0, fm_tokens - routing_tokens)

    # Skill body tokens
    body_tokens, body_method = count_tokens(client, body_text, model, use_heuristic)
    body_lines = len(body_text.splitlines())

    alerts = []
    warnings = []

    # 1. Routing checks
    if len(skill_name) > NAME_CHAR_LIMIT:
        alerts.append(f"Skill name exceeds {NAME_CHAR_LIMIT} chars ({len(skill_name)} chars).")
    if len(description) > DESCRIPTION_CHAR_LIMIT:
        alerts.append(f"Description exceeds {DESCRIPTION_CHAR_LIMIT} chars ({len(description)} chars).")
    elif len(description) < 20:
        warnings.append(f"Description is very short ({len(description)} chars); add decisive triggers.")

    if routing_tokens > ROUTING_TOKEN_WARN_LIMIT:
        warnings.append(f"Routing tokens ({routing_tokens}) exceed recommended budget (<= {ROUTING_TOKEN_WARN_LIMIT} tokens).")

    # 2. Body checks
    if body_tokens > BODY_TOKEN_LIMIT:
        alerts.append(f"Skill body exceeds token limit ({body_tokens} > {BODY_TOKEN_LIMIT} tokens).")
    if body_lines > BODY_LINE_LIMIT:
        alerts.append(f"Skill body exceeds line limit ({body_lines} > {BODY_LINE_LIMIT} lines).")

    # 3. References inspection
    references = []
    skill_dir = skill_file.parent
    ref_dir = skill_dir / "references"

    if ref_dir.is_dir():
        for ref_file in sorted(ref_dir.glob("**/*")):
            if ref_file.is_file() and not ref_file.name.startswith("."):
                ref_text = ref_file.read_text(encoding="utf-8", errors="ignore")
                ref_tokens, _ = count_tokens(client, ref_text, model, use_heuristic)
                references.append({
                    "file": str(ref_file.relative_to(skill_dir)),
                    "path": str(ref_file),
                    "lines": len(ref_text.splitlines()),
                    "characters": len(ref_text),
                    "tokens": ref_tokens,
                })

    total_skill_tokens = fm_tokens + body_tokens
    ref_tokens_total = sum(r["tokens"] for r in references)
    total_package_tokens = total_skill_tokens + ref_tokens_total

    if alerts:
        overall_status = "ALERT"
    elif warnings:
        overall_status = "WARN"
    else:
        overall_status = "PASS"

    return {
        "skill_dir": str(skill_dir),
        "skill_file": str(skill_file),
        "name": skill_name,
        "method": body_method,
        "routing": {
            "name_chars": len(skill_name),
            "description_chars": len(description),
            "tokens": routing_tokens,
            "status": "PASS" if routing_tokens <= ROUTING_TOKEN_WARN_LIMIT and len(description) <= DESCRIPTION_CHAR_LIMIT else "WARN",
        },
        "catalog": {
            "tokens": catalog_tokens,
            "canonical": fm_data.get("metadata", {}).get("canonical", "none"),
        },
        "body": {
            "lines": body_lines,
            "characters": len(body_text),
            "tokens": body_tokens,
            "status": "PASS" if body_tokens <= BODY_TOKEN_LIMIT and body_lines <= BODY_LINE_LIMIT else "ALERT",
        },
        "references": references,
        "references_total_tokens": ref_tokens_total,
        "total_skill_tokens": total_skill_tokens,
        "total_package_tokens": total_package_tokens,
        "overall_status": overall_status,
        "alerts": alerts,
        "warnings": warnings,
    }


def print_skill_report(report: dict):
    status_badge = {
        "PASS": "✅ PASS",
        "WARN": "⚠️ WARN",
        "ALERT": "❌ ALERT",
    }.get(report["overall_status"], report["overall_status"])

    print("\n" + "=" * 94)
    print(f"Skill: {report['skill_file']}  [{status_badge}]  Method: {report['method']}")
    print("=" * 94)
    print(f"{'Tier / Component':<32} {'Metric / Length':<18} {'Tokens':>10} {'Status':>10} {'Spec Limit / Target':<20}")
    print("-" * 94)

    # Tier 1: Routing
    r = report["routing"]
    r_badge = "✅ PASS" if r["status"] == "PASS" else "⚠️ WARN"
    desc_chars_str = f"{r['description_chars']} chars"
    print(f"{'Tier 1: Routing (name+desc)':<32} {desc_chars_str:<18} {r['tokens']:>10} {r_badge:>10} {'<= 150 tok / <= 1024 ch':<20}")

    # Catalog metadata
    cat = report["catalog"]
    print(f"{'  ↳ Catalog Info (URLs/author)':<32} {'(standalone)':<18} {cat['tokens']:>10} {'INFO':>10} {'<= 50 tokens (1 URL)':<20}")

    # Tier 2: Skill Body
    b = report["body"]
    b_badge = "✅ PASS" if b["status"] == "PASS" else "❌ ALERT"
    lines_str = f"{b['lines']} lines"
    print(f"{'Tier 2: Body (SKILL.md)':<32} {lines_str:<18} {b['tokens']:>10} {b_badge:>10} {'<= 5000 tok / <= 500 ln':<20}")

    print("-" * 94)
    print(f"{'SKILL.md Total Context':<32} {'':<18} {report['total_skill_tokens']:>10} {status_badge:>10} {'<= 5000 tokens total':<20}")

    # Tier 3: References
    if report["references"]:
        print("\nTier 3: Resources (Loaded on demand):")
        for ref in report["references"]:
            print(f"  📄 {ref['file']:<35} {ref['lines']:>6} ln  {ref['characters']:>8} ch  {ref['tokens']:>8} tokens")
        print(f"  {'References Subtotal':<38} {report['references_total_tokens']:>26} tokens")
        print(f"\n  📦 Total Package (Skill + References): {report['total_package_tokens']} tokens")
    else:
        print("\nTier 3: Resources: (No reference files in references/)")

    if report["alerts"] or report["warnings"]:
        print("\n🚨 FINDINGS & RECOMMENDATIONS:")
        for alert in report["alerts"]:
            print(f"  • ❌ ALERT: {alert}")
        for warn in report["warnings"]:
            print(f"  • ⚠️  WARN:  {warn}")
    print("=" * 94)


def main():
    parser = argparse.ArgumentParser(
        description="Audit Agent Skills against the 3-Tier Progressive Disclosure token specification."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Path(s) to SKILL.md file(s) or directories to scan. Reads stdin if omitted.",
    )
    parser.add_argument(
        "--model",
        default="gemini-3.7-flash",
        help="Gemini model to use for token calculation (default: gemini-3.7-flash)",
    )
    parser.add_argument(
        "--location",
        default="global",
        help="Vertex AI location for ADC authentication (default: global)",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="GCP Project ID for Vertex AI ADC auth (defaults to ADC / GOOGLE_CLOUD_PROJECT)",
    )
    parser.add_argument(
        "--heuristic-only",
        action="store_true",
        help="Use character-based heuristic (~4 chars/token) without making network calls.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in machine-readable JSON format.",
    )

    args = parser.parse_args()

    client = None
    auth_label = "heuristic"
    use_heuristic = args.heuristic_only

    if not use_heuristic:
        try:
            client, auth_label = get_genai_client(location=args.location, project=args.project)
        except Exception as e:
            sys.stderr.write(f"Warning: Could not initialize Gemini GenAI client ({e}).\n")
            sys.stderr.write("Falling back to offline heuristic (~4 chars/token).\n")
            use_heuristic = True

    results = []
    IGNORE_DIRS = {"_site", ".git", "node_modules", ".venv", "dist", "build"}

    if not args.paths:
        parser.print_help()
        sys.exit(1)
    else:
        target_files = []
        for path_str in args.paths:
            p = Path(path_str)
            if p.is_file():
                target_files.append(p)
            elif p.is_dir():
                for skill_path in sorted(p.glob("**/SKILL.md")):
                    if not any(part in IGNORE_DIRS for part in skill_path.parts):
                        target_files.append(skill_path)
            else:
                sys.stderr.write(f"Error: Path not found: {path_str}\n")

        for f in target_files:
            results.append(analyze_skill(f, client, args.model, use_heuristic))

    if args.json:
        print(json.dumps(results, indent=2))
        return

    for r in results:
        print_skill_report(r)

    alert_count = sum(1 for r in results if r["overall_status"] == "ALERT")
    warn_count = sum(1 for r in results if r["overall_status"] == "WARN")
    if len(results) > 1:
        print(f"\nAudited {len(results)} skills: {len(results) - alert_count - warn_count} passed, {warn_count} warnings, {alert_count} alerts.")


if __name__ == "__main__":
    main()
