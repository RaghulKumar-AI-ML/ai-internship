#!/usr/bin/env python3
"""
Metric-based Code Analysis Tool
Extracts structured signals from Python source code and assigns risk levels
to support modernization decisions.
"""

import re
import ast
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


# ---------------- ENUMS ----------------

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------- DATA MODELS ----------------

@dataclass
class AntiPattern:
    name: str
    severity: str
    description: str
    line_number: int


@dataclass
class CodeSmell:
    name: str
    location: str
    description: str


@dataclass
class CodeMetrics:
    lines_of_code: int
    cyclomatic_complexity: int
    class_count: int
    function_count: int
    maintainability_index: float
    technical_debt_score: float
    python_version: str
    anti_patterns: List[AntiPattern]
    code_smells: List[CodeSmell]


# ---------------- AST COMPLEXITY ----------------

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)


# ---------------- ANALYZER ----------------

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code

    def analyze(self) -> Dict[str, Any]:
        tree = ast.parse(self.code)
        visitor = ComplexityVisitor()
        visitor.visit(tree)

        loc = len(self.code.splitlines())
        classes = len(re.findall(r'^class ', self.code, re.MULTILINE))
        functions = len(re.findall(r'^def ', self.code, re.MULTILINE))

        python_version = "Python 2 (Legacy)" if re.search(r'print\s+[^(]', self.code) else "Python 3"

        anti_patterns = []
        if "eval(" in self.code:
            anti_patterns.append(
                AntiPattern(
                    "Dangerous eval usage",
                    Severity.CRITICAL.value,
                    "eval() can execute arbitrary code",
                    0
                )
            )

        code_smells = []
        if visitor.complexity > 15:
            code_smells.append(
                CodeSmell(
                    "High Complexity",
                    "Module",
                    f"Complexity score is {visitor.complexity}"
                )
            )

        maintainability = max(0, 100 - visitor.complexity * 4)
        tech_debt = min(100, visitor.complexity * 5 + len(anti_patterns) * 20)

        result = {
            "risk_level": self._calculate_risk(tech_debt),
            "metrics": {
                "lines_of_code": loc,
                "cyclomatic_complexity": visitor.complexity,
                "class_count": classes,
                "function_count": functions,
                "maintainability_index": maintainability,
                "technical_debt_score": tech_debt,
                "python_version": python_version
            },
            "anti_patterns": [ap.__dict__ for ap in anti_patterns],
            "code_smells": [cs.__dict__ for cs in code_smells]
        }

        with open("analysis_report.json", "w") as f:
            json.dump(result, f, indent=2)

        return result

    def _calculate_risk(self, debt):
        if debt > 70:
            return RiskLevel.CRITICAL.value
        if debt > 40:
            return RiskLevel.HIGH.value
        if debt > 20:
            return RiskLevel.MEDIUM.value
        return RiskLevel.LOW.value


# ---------------- RUN ----------------

if __name__ == "__main__":
    sample_code = """
def calculate(x, y):
    return eval("x + y")

print "hello"
"""
    analyzer = CodeAnalyzer(sample_code)
    report = analyzer.analyze()
    print("Analysis complete. Risk:", report["risk_level"])
