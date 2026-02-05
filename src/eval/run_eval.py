from src.pipeline.rag_pipeline import RagPipeline
import json

pipeline = RagPipeline()

with open("eval/eval_cases.json") as f:
    cases = json.load(f)

failures = 0

for case in cases:
    result = pipeline.answer_question(case["query"])
    sources = result["sources"]
    answer = result["answer"].lower()

    if case["expected_source"] not in sources:
        print("❌ Source mismatch:", case["query"])
        failures += 1

    if case["expected_contains"] not in answer:
        print("❌ Content mismatch:", case["query"])
        failures += 1

if failures == 0:
    print("✅ All RAG tests passed")
else:
    print(f"❌ {failures} failures detected")