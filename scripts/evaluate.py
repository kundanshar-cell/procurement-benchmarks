"""
Run a procurement benchmark against any LLM via OpenAI-compatible API.

Usage:
    # Using OpenAI
    OPENAI_API_KEY=sk-... python scripts/evaluate.py --model gpt-4o --category spend_categorisation

    # Using Anthropic Claude
    ANTHROPIC_API_KEY=sk-... python scripts/evaluate.py --provider anthropic --model claude-opus-4-7 --category all

    # Output results to file
    python scripts/evaluate.py --model gpt-4o --output results/gpt4o_results.json
"""

import argparse
import json
import os
import time
from pathlib import Path

BENCHMARKS_DIR = Path(__file__).parent.parent / "benchmarks"
RESULTS_DIR = Path(__file__).parent.parent / "results"

CATEGORIES = [
    "spend_categorisation",
    "vendor_risk",
    "po_interpretation",
    "three_way_match",
    "invoice_processing",
]

SYSTEM_PROMPT = """You are an expert procurement professional with deep knowledge of:
- UNSPSC spend classification (all four levels: segment, family, class, commodity)
- Vendor risk management and supplier due diligence
- Purchase order types, document categories, and ERP workflows
- Three-way match processes and invoice verification
- SAP MM/FI, JDE E1, and D365 F&O procurement modules

Answer the following procurement question accurately and concisely.
Provide your answer followed by a brief explanation of your reasoning."""


def load_benchmarks(category: str) -> list[dict]:
    if category == "all":
        items = []
        for cat in CATEGORIES:
            path = BENCHMARKS_DIR / f"{cat}.json"
            if path.exists():
                items.extend(json.loads(path.read_text()))
        return items
    path = BENCHMARKS_DIR / f"{category}.json"
    if not path.exists():
        raise FileNotFoundError(f"No benchmark file for category: {category}")
    return json.loads(path.read_text())


def call_openai(model: str, question: str, context: str | None) -> str:
    import openai
    client = openai.OpenAI()
    user_message = question
    if context:
        user_message = f"Context:\n{context}\n\nQuestion:\n{question}"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def call_anthropic(model: str, question: str, context: str | None) -> str:
    import anthropic
    client = anthropic.Anthropic()
    user_message = question
    if context:
        user_message = f"Context:\n{context}\n\nQuestion:\n{question}"
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def evaluate(provider: str, model: str, category: str, delay: float = 0.5) -> list[dict]:
    benchmarks = load_benchmarks(category)
    results = []

    call_fn = call_openai if provider == "openai" else call_anthropic

    for i, item in enumerate(benchmarks, 1):
        print(f"[{i}/{len(benchmarks)}] {item['id']} ({item['difficulty']}) ... ", end="", flush=True)
        try:
            response = call_fn(model, item["question"], item.get("context"))
            result = {
                "id": item["id"],
                "category": item["category"],
                "difficulty": item["difficulty"],
                "question": item["question"],
                "ground_truth": item["answer"],
                "model_response": response,
                "model": model,
                "provider": provider,
            }
            results.append(result)
            print("done")
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"id": item["id"], "error": str(e)})
        time.sleep(delay)

    return results


def main():
    parser = argparse.ArgumentParser(description="Run procurement benchmarks against an LLM")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
    parser.add_argument("--model", default="gpt-4o", help="Model name")
    parser.add_argument("--category", default="all", choices=CATEGORIES + ["all"])
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between API calls")
    args = parser.parse_args()

    print(f"Provider: {args.provider} | Model: {args.model} | Category: {args.category}")
    print("-" * 60)

    results = evaluate(args.provider, args.model, args.category, args.delay)

    summary = {
        "model": args.model,
        "provider": args.provider,
        "category": args.category,
        "total": len(results),
        "errors": sum(1 for r in results if "error" in r),
        "results": results,
    }

    if args.output:
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = Path(args.output)
        out_path.write_text(json.dumps(summary, indent=2))
        print(f"\nResults written to {out_path}")
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
