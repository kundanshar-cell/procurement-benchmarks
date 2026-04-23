# procurement-benchmarks

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

> *50 real-world Q&A pairs for benchmarking LLMs on procurement domain accuracy.*  
> *Spend categorisation · Vendor risk · PO interpretation · Three-way match · Invoice processing*

---

## The Researcher Who Couldn't Evaluate Anything

James is writing his PhD on LLMs for enterprise document understanding.

He needs to benchmark GPT-4, Claude, and Llama on procurement tasks. Does the model correctly interpret a purchase order? Can it identify a pricing anomaly? Does it know what a blanket order is? Does it understand the difference between a two-way and three-way match?

He has no dataset. None exists.

He posts on Reddit: *"Does anyone have a procurement Q&A dataset for LLM evaluation?"*

Nothing.

He ends up writing 200 generic questions that don't test real procurement understanding. His paper is weaker for it. The reviewers notice.

**This dataset is for James.**

500 pairs coming. This is v0.1 — 50 pairs across five categories, written by someone who has spent 15 years answering these questions for real clients on real ERP systems.

---

## What's in the dataset

| Category | Questions | What it tests |
|----------|-----------|---------------|
| `spend_categorisation` | 10 | UNSPSC code assignment, category boundaries, common misclassifications |
| `vendor_risk` | 10 | Fraud patterns, supply chain risk, compliance, sanctions |
| `po_interpretation` | 10 | PO types, ERP document categories, account assignment, item categories |
| `three_way_match` | 10 | Match process, variances, tolerances, service POs, credit memos |
| `invoice_processing` | 10 | SAP/JDE/D365 invoice flows, VAT, ERS, payment terms, duplicates |

Difficulty distribution: **easy / medium / hard** — labelled on every question.

ERP coverage: **SAP ECC, JDE E1, D365 F&O, and ERP-agnostic.**

---

## Sample questions

**Spend categorisation — easy**
> A purchase order line reads 'Cutting fluid for CNC machines'. What UNSPSC commodity code best describes this?

**Vendor risk — hard**
> Your spend analytics team flags that a single vendor has received 47 purchase orders in one quarter, all just below the £10,000 approval threshold. Total spend is £438,000. What does this pattern indicate?

**Three-way match — hard**
> A service PO in SAP uses item category D (service). The vendor invoices £20,000 but the approved service entry sheet (SES) is only £18,000. What happens in MIRO and what are the options?

**Invoice processing — hard**
> An AP clerk posts a vendor invoice in SAP via MIRO but uses the wrong tax code. The invoice is already paid. What is the correct remediation?

---

## Data format

Each benchmark file is a JSON array. Every entry follows this structure:

```json
{
  "id": "spend-001",
  "category": "spend_categorisation",
  "difficulty": "easy",
  "question": "A purchase order line reads 'Cutting fluid for CNC machines'. What UNSPSC commodity code best describes this?",
  "context": null,
  "answer": "12191507 — Cutting oils",
  "reasoning": "Cutting fluid used in CNC machining is a metalworking fluid classified under UNSPSC segment 12...",
  "unspsc_code": "12191507",
  "erp": "Agnostic",
  "tags": ["unspsc", "manufacturing", "indirect-spend"]
}
```

Full schema: [`schema/benchmark_schema.json`](schema/benchmark_schema.json)

---

## Running evaluations

Use the included script to benchmark any model:

```bash
# Benchmark GPT-4o on spend categorisation
OPENAI_API_KEY=sk-... python scripts/evaluate.py \
  --provider openai \
  --model gpt-4o \
  --category spend_categorisation \
  --output results/gpt4o_spend.json

# Benchmark Claude on all categories
ANTHROPIC_API_KEY=sk-... python scripts/evaluate.py \
  --provider anthropic \
  --model claude-opus-4-7 \
  --category all \
  --output results/claude_all.json
```

The script outputs structured JSON with questions, ground-truth answers, and model responses — ready for automated scoring or human review.

---

## Roadmap

**v0.2 (coming)**
- 50 more pairs: Oracle Fusion, Coupa, Ariba-specific questions
- Automated scoring script with keyword-match and LLM-as-judge options
- Leaderboard of published model results

**v0.3**
- Multi-hop reasoning questions (chains of procurement logic)
- Scenario-based questions with full PO/invoice document context
- Translation of top questions into French, German, Spanish

---

## Contributing

Have procurement domain expertise? PRs are very welcome — especially:
- Questions from Oracle Fusion or Coupa environments
- Edge cases you've seen in real implementations
- Questions in non-English procurement contexts

Please follow the schema in [`schema/benchmark_schema.json`](schema/benchmark_schema.json) and include `reasoning` for every answer.

---

## Related projects

- **[unspsc-python](https://github.com/kundanshar-cell/unspsc-python)** — UNSPSC v26.0801 lookup, hierarchy, and fuzzy matching. Useful for validating spend categorisation answers programmatically.

---

## License

[CC BY 4.0](LICENSE) — free to use, share, and adapt with attribution.

Cite as:
```
Kundan Sharma. procurement-benchmarks: Real-world Q&A pairs for benchmarking LLMs on procurement domain accuracy. 2026. https://github.com/kundanshar-cell/procurement-benchmarks
```

---

*Built by [Kundan Sharma](https://github.com/kundanshar-cell) — IT & Digital Solution Architect, 15 years in enterprise procurement and ERP.*  
*Because James shouldn't have to write 200 generic questions that don't actually test procurement understanding.*
