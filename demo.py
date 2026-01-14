from rag_engine import SimpleRAG

rag = SimpleRAG("knowledge_base.txt")

while True:
    q = input("Ask: ")
    if q == "exit":
        break
    print(rag.answer(q))
