class SimpleRAG:
    def __init__(self, knowledge_file):
        with open(knowledge_file) as f:
            self.data = f.read().lower()

    def answer(self, query: str):
        q = query.lower()

        if "risk" in q:
            return "The code is risky due to high complexity and unsafe patterns like eval()."

        if "modernize" in q:
            return "Modernization includes removing eval(), migrating to Python 3, and reducing complexity."

        return "Based on analysis, the code needs refactoring for maintainability."
