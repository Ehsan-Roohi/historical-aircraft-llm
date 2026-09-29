"""Repeatable editorial gate for the non-submission-ready JoA draft.

Counts are only a screening proxy; TeX layout, reference correctness and
technical validity still require a human editorial review.
"""

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "paper/article_journal_of_aircraft.tex"
REFERENCES = ROOT / "paper/references_journal_of_aircraft.tex"
OUT = ROOT / "analysis/results/joa_editorial_gate01.json"


def readable_words(tex):
    tex = re.sub(r"(?<!\\)%[^\n]*", "", tex)
    tex = re.sub(r"\\begin\{(?:equation|align|gather|displaymath)\}.*?\\end\{(?:equation|align|gather|displaymath)\}", " ", tex, flags=re.S)
    tex = re.sub(r"\$.*?\$", " ", tex, flags=re.S)
    tex = re.sub(r"\\(?:url|includegraphics)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\[A-Za-z]+(?:\[[^]]*\])?", " ", tex)
    return re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", tex)


def main():
    tex = ARTICLE.read_text(encoding="utf-8")
    refs = REFERENCES.read_text(encoding="utf-8")
    sections = []
    matches = list(re.finditer(r"\\section\{([^}]+)\}", tex))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else tex.find(r"\section*{Data availability}", match.end())
        if end < 0:
            end = len(tex)
        sections.append({"name": match.group(1), "screening_word_count": len(readable_words(tex[match.end():end]))})
    entries = re.findall(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})", refs, flags=re.S)
    result = {
        "scope": "Editorial screen, not TeX compilation or peer-review acceptance",
        "article_rough_word_count_excluding_reference_file": len(readable_words(tex)),
        "main_sections": sections,
        "reference_count": len(entries),
        "reference_keys_with_et_al_in_list": [key for key, body in entries if "et al." in body],
        "source_reference_order_matches_citation_order": list(dict.fromkeys(k.strip() for cite in re.findall(r"\\cite\{([^}]+)\}", tex) for k in cite.split(","))) == [key for key, _ in entries],
        "hard_gates_not_checked": ["PDF compilation and page visual QA", "all-reference source and metadata verification", "installed-aircraft flight and stability"]
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT.name, result["article_rough_word_count_excluding_reference_file"], "words", result["reference_count"], "references")


if __name__ == "__main__":
    main()
