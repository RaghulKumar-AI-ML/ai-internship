import re

class SimpleRAG:
    def __init__(self, knowledge_file):
        with open(knowledge_file, "r") as f:
            self.documents = [
                line.strip()
                for line in f.readlines()
                if line.strip()
            ]

    def retrieve(self, query):
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self.documents:
            doc_words = set(doc.lower().split())
            score = len(query_words & doc_words)
            scored_docs.append((score, doc))

        scored_docs.sort(reverse=True)
        return scored_docs[0][1] if scored_docs else None

    def answer(self, query):
        context = self.retrieve(query)

        if not context:
            return "No relevant information found."

        if "risk" in query.lower():
            return f"The code is risky because: {context}"

        if "modernize" in query.lower():
            return f"Recommended modernization steps: {context}"

        return f"Relevant information: {context}"
