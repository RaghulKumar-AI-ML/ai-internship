from rag_engine import SimpleRAG

rag = SimpleRAG("knowledge_base.txt")

print("Code Modernization RAG Assistant")
print("Type 'exit' to quit\n")

while True:
    q = input("Ask: ")
    if q.lower() == "exit":
        break
    print("Answer:", rag.answer(q))
