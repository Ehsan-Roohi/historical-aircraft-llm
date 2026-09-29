"""Mechanically package exact V9 and V10 response text into V11b prompts.

This fixes V11a's prompt defect: supplying only a hash, not the component ledger.
No engineering value is synthesized or edited here.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis" / "prompts_v11_design_candidate"
TARGET = ROOT / "analysis" / "prompts_v11b_context_restored"
PAIRS = {
    "gpt-6-astra": (
        "received_v9_65007436/gpt-6-astra/response.json",
        "received_v10_astra_postbilling_65012338/response.json"),
    "claude-fable-5-1": (
        "received_v9_retry_65009709/claude-fable-5-1/response.json",
        "received_v10_65011353/claude-fable-5-1/response.json"),
    "claude-opus-5-5": (
        "received_v9_retry_65009709/claude-opus-5-5/response.json",
        "received_v10_65011353/claude-opus-5-5/response.json"),
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    TARGET.mkdir(exist_ok=False)
    instructions = (SOURCE / "instructions.txt").read_bytes()
    (TARGET / "instructions.txt").write_bytes(instructions)
    index = {"reason": "V11a omitted full source content; all three models HOLD",
             "records": []}
    for model, paths in PAIRS.items():
        stem = model + ".prompt.txt"
        base = (SOURCE / stem).read_bytes()
        full = [base.decode("utf-8"),
                "\n\nCONTEXT RESTORATION: The first V11 request provided hashes and summaries but not the source component records. All three models correctly returned HOLD. The complete V3 baseline response and V10 correction response now follow. They are prior model claims, not measurements; retain provenance labels.\n"]
        row = {"model": model, "base_prompt_sha256": sha(base), "sources": []}
        for label, path in zip(("V3 baseline", "V10 correction"), paths):
            wrapper = (ROOT / path).read_bytes()
            response = json.loads(wrapper)["response"]
            full.append(f"\n--- BEGIN {label}; wrapper SHA-256 {sha(wrapper)} ---\n")
            full.append(response)
            full.append(f"\n--- END {label} ---\n")
            row["sources"].append({"label": label, "path": path,
                                   "wrapper_sha256": sha(wrapper),
                                   "response_text_sha256": sha(response.encode("utf-8"))})
        prompt = "".join(full).encode("utf-8")
        (TARGET / stem).write_bytes(prompt)
        row["composed_prompt_sha256"] = sha(prompt)
        row["composed_prompt_bytes"] = len(prompt)
        index["records"].append(row)
    (TARGET / "source_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(TARGET.name)


if __name__ == "__main__":
    main()
