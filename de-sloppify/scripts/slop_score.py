# /// script
# dependencies = [
#   "nltk",
#   "google-genai",
# ]
# ///

import sys
import re
import math
import json
import os

# Deterministic dependencies
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk import pos_tag, word_tokenize
    
    # Ensure data is present
    for resource in ['stopwords', 'punkt', 'averaged_perceptron_tagger_eng', 'universal_tagset', 'punkt_tab']:
        try:
            nltk.data.find(f'corpora/{resource}' if resource == 'stopwords' else f'taggers/{resource}' if 'tagger' in resource else f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)
            
    STOP_WORDS = set(stopwords.words('english'))
except ImportError:
    STOP_WORDS = {"the", "is", "at", "which", "on", "in", "a", "an", "and", "or", "but", "of", "to", "for", "with"}
    pos_tag = None


# --- CONSOLIDATED DICTIONARIES ---
LEXICAL_SLOP_DICT = {
    "delve", "tapestry", "landscape", "nuance", "testament", "beacon", "catalyst", 
    "paradigm", "realm", "embark", "journey", "navigating", "intricate", "myriad",
    "unleash", "unprecedented", "game-changing", "revolutionary", "supercharge", 
    "unlock", "groundbreaking", "disruptive", "pioneering", "stellar", "killer feature",
    "powerhouse", "synergy", "holistic", "leverage", "robust", "transformative", 
    "seamless", "cutting-edge", "next-gen", "paramount", "optimal", "dynamic", 
    "proactive", "accelerator", "bleeding edge", "invaluable", "scarce", 
    "boilerplate", "wired up", "strategic", "real-world", "capabilities", 
    "specialised", "procedural", "deterministic", "rigorous", "relentless"
}

# --- COMPILED REGEX UNIONS ---
CLICHE_PATTERNS = [
    r"in today'?s .* world", r"let'?s dive in", r"whether you'?re", r"look no further",
    r"at the end of the day", r"only time will tell", r"in this article, we",
    r"this post details", r"let'?s have a closer look", r"let'?s take a closer look",
    r"the key to success", r"hope you enjoyed this article", r"leave your comments below",
    r"feel free to reach out", r"a crucial aspect",
    # Heavy formats
    r"\bthe[ \t]+(?:[a-z0-9\-]+[ \t]+){0,4}[a-z0-9\-]+[ \t]*:[ \t]*(?:the[ \t]+)?(?:[a-z0-9\-]+[ \t]+){0,4}[a-z0-9\-]+\b",
    r"\b(?:[a-z0-9\-]+[ \t]+){1,5}\(the[ \t]+(?:[a-z0-9\-]+[ \t]+){0,4}[a-z0-9\-]+\)",
    # Chained fragments: <text>-<text>-<text>
    r"\b[a-z0-9]+[\s]*[—-][\s]*[a-z0-9]+[\s]*[—-][\s]*[a-z0-9]+\b"
]
ANALOGY_BRIDGES = [r"think of .* as", r"akin to", r"similar to", r"like a", r"imagine a"]
ANALOGY_TARGETS = {"orchestra", "conductor", "blueprint", "engine", "symphony", "canvas", "maestro", "brain"}

STRUCTURAL_REGEX = re.compile("|".join(CLICHE_PATTERNS + ANALOGY_BRIDGES), re.IGNORECASE)

def normalize_smooth(val, perfect_val, slop_val):
    if perfect_val < slop_val:
        if val <= perfect_val: return 0.0
        if val >= slop_val: return 100.0
        x = (val - perfect_val) / (slop_val - perfect_val)
    else:
        if val >= perfect_val: return 0.0
        if val <= slop_val: return 100.0
        x = (perfect_val - val) / (perfect_val - slop_val)
    return round((x ** 1.2) * 100.0, 2)

def calculate_slop_score(text):
    lower_text = text.lower()
    if pos_tag:
        all_tokens = word_tokenize(text)
        words = [t.lower() for t in all_tokens if t.isalnum()]
    else:
        words = re.findall(r'\b\w+\b', lower_text)
    
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    total_w, total_s = len(words), len(sentences)
    if total_w == 0: return {"error": "Invalid text"}
    
    results = {}

    # 1. LEXICAL ANALYSIS (Single Pass)
    lex_slop_count = 0
    filler_count = 0
    for w in words:
        if w in LEXICAL_SLOP_DICT: lex_slop_count += 1
        if w in STOP_WORDS: filler_count += 1
    
    lex_density = (lex_slop_count / total_w) * 1000
    results["lexical_slop"] = {"score": normalize_smooth(lex_density, 1.0, 8.0), "raw": round(lex_density, 2)}
    
    filler_ratio = filler_count / total_w
    results["filler_words"] = {"score": normalize_smooth(filler_ratio, 0.35, 0.55), "raw": round(filler_ratio, 3)}

    # 2. STRUCTURAL PATTERNS
    struct_matches = STRUCTURAL_REGEX.findall(text)
    actual_struct_count = 0
    for m in struct_matches:
        is_analogy_bridge = any(re.search(b, m, re.I) for b in ANALOGY_BRIDGES)
        if is_analogy_bridge:
            if any(t in lower_text for t in ANALOGY_TARGETS):
                actual_struct_count += 1
        else:
            actual_struct_count += 1
            
    dash_count = text.count("—") + text.count("--")
    dash_density = (dash_count / total_w) * 1000
    if dash_density > 5:
        actual_struct_count += int((dash_density - 5) / 2)

    struct_density = (actual_struct_count / total_w) * 1000
    results["structural_cliches"] = {"score": normalize_smooth(struct_density, 0.5, 4.0), "raw": round(struct_density, 2)}

    # 3. RHYTHM VARIANCE
    cv = 0.0
    if total_s > 1:
        lens = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        mean = sum(lens) / total_s
        if mean > 0: cv = (math.sqrt(sum((l - mean)**2 for l in lens) / total_s)) / mean
    results["rhythm_variance"] = {"score": normalize_smooth(cv, 0.75, 0.35), "raw": round(cv, 3)}

    # 4. SYNTACTIC VOICE (Full Text)
    if pos_tag:
        tagged = pos_tag(all_tokens, tagset='universal')
        n = sum(1 for _, tag in tagged if tag == 'NOUN')
        p = sum(1 for _, tag in tagged if tag == 'PRON')
        pni = (n - p) / len(tagged) if len(tagged) else 0
        results["syntactic_voice"] = {"score": normalize_smooth(pni, 0.08, 0.22), "raw": round(pni, 3)}
    else:
        results["syntactic_voice"] = {"score": 0.0, "raw": "Skipped"}

    # FINAL CONSOLIDATED SCORE
    final = round(sum(i["score"] for i in results.values()) / len(results), 2)
    return {"criteria": results, "overall_slop_score": final}

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    with open(sys.argv[1], 'r') as f: print(json.dumps(calculate_slop_score(f.read()), indent=2))
