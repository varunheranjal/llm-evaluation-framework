"""Build a self-contained, shareable local HTML report from DeepEval test results."""

import html
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "reports" / "results"
OUT = PROJECT_ROOT / "reports" / "rag_quality_report.html"


def esc(value):
    return html.escape(str(value if value is not None else ""))


def main():
    files = sorted(RESULT_DIR.glob("*.json"))
    if not files:
        raise SystemExit("No result files found. Run local DeepEval tests first.")
    cases = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    cards = []
    passed = 0
    for case in cases:
        metrics = case["metrics"]
        good = case["failure"] is None and bool(metrics) and all(
            m["score"] is not None and m["error"] is None and float(m["score"]) >= float(m["threshold"])
            for m in metrics
        )
        passed += int(good)
        rows = "".join(
            f"<tr><td>{esc(m['name'])}</td><td>{esc(m['score'])}</td><td>{esc(m['threshold'])}</td>"
            f"<td>{'PASS' if m['score'] is not None and not m['error'] and float(m['score']) >= float(m['threshold']) else 'FAIL / ERROR'}</td>"
            f"<td>{esc(m['reason'] or m['error'])}</td></tr>"
            for m in metrics
        )
        cards.append(
            f"<section><h2>{esc(case['case_id'])} <span class={'pass' if good else 'fail'}>"
            f"{'PASS' if good else 'FAIL'}</span></h2>"
            f"<p><strong>Question:</strong> {esc(case['question'])}</p>"
            f"<p><strong>Expected:</strong> {esc(case['expected_answer'])}</p>"
            f"<p><strong>Actual:</strong> {esc(case['actual_answer'])}</p>"
            f"<p><strong>Retrieved chunks:</strong> {esc(case['retrieved_chunk_count'])}</p>"
            f"{'<p class=fail><strong>Error:</strong> ' + esc(case['failure']) + '</p>' if case['failure'] else ''}"
            f"<table><thead><tr><th>Metric</th><th>Score</th><th>Threshold</th><th>Status</th><th>Judge explanation</th></tr></thead><tbody>{rows}</tbody></table></section>"
        )
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><title>RAG Quality Report</title>
<style>
body{{font:14px/1.55 system-ui,Arial,sans-serif;max-width:1100px;margin:45px auto;padding:0 22px;color:#172636}}
h1{{color:#14314f;margin-bottom:3px}} .sub{{color:#667789}}section{{margin:25px 0;padding:18px 22px;border:1px solid #d9e0e6;border-radius:10px;break-inside:avoid}}
table{{border-collapse:collapse;width:100%;font-size:12px;table-layout:fixed}}td,th{{padding:8px;border-bottom:1px solid #e5eaf0;text-align:left;vertical-align:top;word-break:break-word}}
th{{background:#f2f6fa}}td:first-child{{width:18%}}td:nth-child(2),td:nth-child(3),td:nth-child(4){{width:7%}}
.pass{{color:#16723e}}.fail{{color:#a32626}}button{{background:#153c5e;color:white;padding:10px 14px;border:none;border-radius:6px;cursor:pointer}}
@media print{{button{{display:none}}body{{margin:15mm auto}}section{{break-inside:avoid}}}}
</style></head><body><button onclick="window.print()">Print / Save as PDF</button>
<h1>RAG Quality Evaluation</h1><div class="sub">Local DeepEval run · Generated {esc(datetime.now().strftime('%Y-%m-%d %H:%M'))} · {passed}/{len(cases)} test cases passed</div>
<p>Blocking gates: Contextual Recall, Contextual Precision, Answer Correctness, Groundedness, and Answer Relevancy for answerable questions. Missing-information cases use Unknown/Refusal Correctness and Answer Relevancy. Contextual Relevancy is tracked separately by <code>python -m evals.run_eval</code> and is not a blocking gate.</p>
{''.join(cards)}<p class="sub">Scores are LLM-judged and may vary between runs. This report records one local test execution, not a production certification.</p></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"Created {OUT} ({passed}/{len(cases)} cases passed)")


if __name__ == "__main__":
    main()
