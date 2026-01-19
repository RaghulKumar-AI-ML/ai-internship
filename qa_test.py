from rag_engine import SimpleRAG

rag = SimpleRAG("knowledge_base.txt")

tests = [
    {
        "question": "Why is eval dangerous?",
        "expected_keyword": "eval"
    },
    {
        "question": "How should legacy Python be modernized?",
        "expected_keyword": "python"
    },
    {
        "question": "What increases technical debt?",
        "expected_keyword": "complexity"
    }
]

passed = 0

for test in tests:
    answer = rag.answer(test["question"]).lower()
    if test["expected_keyword"] in answer:
        passed += 1
        print(f"PASS: {test['question']}")
    else:
        print(f"FAIL: {test['question']}")

accuracy = (passed / len(tests)) * 100
print(f"\nRAG Accuracy: {accuracy:.2f}%")
