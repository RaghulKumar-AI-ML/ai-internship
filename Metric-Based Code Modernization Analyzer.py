#!/usr/bin/env python3
"""
Metric-based Code Analysis Tool
Extracts structured signals from Python source code and assigns risk levels
to support modernization decisions.
"""

import re
import ast
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(Enum):
    """Issue severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AntiPattern:
    """Represents a detected anti-pattern"""
    name: str
    severity: str
    description: str
    line_number: int = 0


@dataclass
class CodeSmell:
    """Represents a detected code smell"""
    name: str
    location: str
    description: str


@dataclass
class Recommendation:
    """Represents a modernization recommendation"""
    priority: str
    action: str
    reason: str


@dataclass
class CodeMetrics:
    """Structured code metrics"""
    lines_of_code: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    cyclomatic_complexity: int
    dependencies: List[str]
    anti_patterns: List[AntiPattern]
    code_smells: List[CodeSmell]
    python_version: str
    class_count: int
    function_count: int
    maintainability_index: float
    technical_debt_score: float
    average_function_length: float
    max_nesting_depth: int


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity"""
    
    def __init__(self):
        self.complexity = 0
        self.function_complexities = {}
        self.current_function = None
        self.max_nesting = 0
        self.current_nesting = 0
        
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        old_nesting = self.current_nesting
        
        self.current_function = node.name
        self.current_nesting = 0
        self.complexity += 1  # Base complexity for function
        
        self.generic_visit(node)
        
        self.current_function = old_function
        self.current_nesting = old_nesting
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_If(self, node):
        self.complexity += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
        
    def visit_For(self, node):
        self.complexity += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
        
    def visit_While(self, node):
        self.complexity += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
        
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


class CodeAnalyzer:
    """Main code analyzer class"""
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        
    def analyze(self) -> CodeMetrics:
        """Perform complete code analysis"""
        
        # Basic metrics
        loc = len(self.lines)
        comment_lines = self._count_comment_lines()
        blank_lines = self._count_blank_lines()
        code_lines = loc - comment_lines - blank_lines
        
        # Complexity analysis
        complexity, max_nesting = self._calculate_complexity()
        
        # Extract dependencies
        dependencies = self._extract_dependencies()
        
        # Detect issues
        anti_patterns = self._detect_anti_patterns()
        code_smells = self._detect_code_smells()
        
        # Python version detection
        python_version = self._detect_python_version()
        
        # Count classes and functions
        class_count = len(re.findall(r'^\s*class\s+\w+', self.code, re.MULTILINE))
        function_count = len(re.findall(r'^\s*def\s+\w+', self.code, re.MULTILINE))
        
        # Calculate average function length
        avg_func_length = self._calculate_avg_function_length()
        
        # Calculate maintainability index
        maintainability = self._calculate_maintainability(
            code_lines, comment_lines, complexity, len(anti_patterns), len(code_smells)
        )
        
        # Calculate technical debt
        tech_debt = self._calculate_technical_debt(
            complexity, len(anti_patterns), len(code_smells), loc
        )
        
        return CodeMetrics(
            lines_of_code=loc,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=complexity,
            dependencies=dependencies,
            anti_patterns=anti_patterns,
            code_smells=code_smells,
            python_version=python_version,
            class_count=class_count,
            function_count=function_count,
            maintainability_index=maintainability,
            technical_debt_score=tech_debt,
            average_function_length=avg_func_length,
            max_nesting_depth=max_nesting
        )
    
    def _count_comment_lines(self) -> int:
        """Count lines that are comments"""
        return sum(1 for line in self.lines if line.strip().startswith('#'))
    
    def _count_blank_lines(self) -> int:
        """Count blank lines"""
        return sum(1 for line in self.lines if not line.strip())
    
    def _calculate_complexity(self) -> tuple:
        """Calculate cyclomatic complexity using AST"""
        try:
            tree = ast.parse(self.code)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            return visitor.complexity, visitor.max_nesting
        except SyntaxError:
            # Fallback to regex-based calculation
            patterns = [
                r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
                r'\band\b', r'\bor\b', r'\bexcept\b', r'\bwith\b'
            ]
            complexity = 1
            for pattern in patterns:
                complexity += len(re.findall(pattern, self.code))
            return complexity, 0
    
    def _extract_dependencies(self) -> List[str]:
        """Extract imported modules"""
        deps = set()
        
        # Standard imports
        for match in re.finditer(r'^import\s+([\w.]+)', self.code, re.MULTILINE):
            deps.add(match.group(1).split('.')[0])
        
        # From imports
        for match in re.finditer(r'^from\s+([\w.]+)\s+import', self.code, re.MULTILINE):
            deps.add(match.group(1).split('.')[0])
        
        return sorted(list(deps))
    
    def _detect_python_version(self) -> str:
        """Detect Python version based on code patterns"""
        py2_patterns = [
            r'print\s+[^(]',  # Print statement
            r'\bxrange\b',
            r'\.iteritems\(\)',
            r'\.iterkeys\(\)',
            r'\.itervalues\(\)',
        ]
        
        py3_patterns = [
            r'print\(',
            r'\basync\s+def\b',
            r'\bnonlocal\b',
            r':=',  # Walrus operator
            r'\basync\s+for\b',
        ]
        
        py2_score = sum(1 for pattern in py2_patterns if re.search(pattern, self.code))
        py3_score = sum(1 for pattern in py3_patterns if re.search(pattern, self.code))
        
        if py2_score > py3_score:
            return "Python 2 (Legacy - EOL)"
        elif py3_score > 0:
            return "Python 3"
        return "Unknown"
    
    def _detect_anti_patterns(self) -> List[AntiPattern]:
        """Detect common anti-patterns"""
        anti_patterns = []
        
        # Excessive global variables
        global_matches = list(re.finditer(r'^global\s+', self.code, re.MULTILINE))
        if len(global_matches) > 3:
            anti_patterns.append(AntiPattern(
                name="Excessive Global Variables",
                severity=Severity.HIGH.value,
                description=f"Found {len(global_matches)} global variable declarations",
                line_number=self.code[:global_matches[0].start()].count('\n') + 1
            ))
        
        # Bare except clause
        bare_except = list(re.finditer(r'except\s*:', self.code))
        for match in bare_except:
            line_num = self.code[:match.start()].count('\n') + 1
            anti_patterns.append(AntiPattern(
                name="Bare Except Clause",
                severity=Severity.MEDIUM.value,
                description="Using except without specifying exception type",
                line_number=line_num
            ))
        
        # Mutable default arguments
        mutable_defaults = list(re.finditer(r'def\s+\w+\([^)]*=\s*(\[\]|\{\})', self.code))
        for match in mutable_defaults:
            line_num = self.code[:match.start()].count('\n') + 1
            anti_patterns.append(AntiPattern(
                name="Mutable Default Arguments",
                severity=Severity.HIGH.value,
                description="Using mutable objects (list/dict) as default arguments",
                line_number=line_num
            ))
        
        # Star imports
        star_imports = list(re.finditer(r'from\s+\w+\s+import\s+\*', self.code))
        for match in star_imports:
            line_num = self.code[:match.start()].count('\n') + 1
            anti_patterns.append(AntiPattern(
                name="Wildcard Import",
                severity=Severity.MEDIUM.value,
                description="Wildcard imports pollute namespace",
                line_number=line_num
            ))
        
        # eval/exec usage
        dangerous_funcs = list(re.finditer(r'\b(eval|exec)\s*\(', self.code))
        for match in dangerous_funcs:
            line_num = self.code[:match.start()].count('\n') + 1
            anti_patterns.append(AntiPattern(
                name=f"Dangerous {match.group(1).upper()} Usage",
                severity=Severity.CRITICAL.value,
                description=f"Using {match.group(1)}() can execute arbitrary code",
                line_number=line_num
            ))
        
        # Old-style string formatting
        old_format = list(re.finditer(r'%\s*[sd(]', self.code))
        if len(old_format) > 2:
            anti_patterns.append(AntiPattern(
                name="Old-Style String Formatting",
                severity=Severity.LOW.value,
                description="Consider using f-strings or .format() instead of % formatting",
                line_number=self.code[:old_format[0].start()].count('\n') + 1
            ))
        
        return anti_patterns
    
    def _detect_code_smells(self) -> List[CodeSmell]:
        """Detect code smells"""
        smells = []
        
        # Long functions
        func_pattern = r'def\s+(\w+)'
        for match in re.finditer(func_pattern, self.code):
            func_name = match.group(1)
            func_start = match.start()
            
            # Find function end (simplified heuristic)
            remaining = self.code[func_start:]
            func_lines = 0
            for line in remaining.split('\n')[1:]:
                if line and not line[0].isspace():
                    break
                func_lines += 1
            
            if func_lines > 50:
                smells.append(CodeSmell(
                    name="Long Function",
                    location=f"Function '{func_name}'",
                    description=f"Function is {func_lines} lines long (recommended: <50)"
                ))
        
        # Long lines
        for idx, line in enumerate(self.lines, 1):
            if len(line) > 120:
                smells.append(CodeSmell(
                    name="Long Line",
                    location=f"Line {idx}",
                    description=f"Line is {len(line)} characters (PEP 8 recommends 79-120)"
                ))
        
        # Deep nesting
        for idx, line in enumerate(self.lines, 1):
            if line and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                if indent > 20:  # More than 5 levels of 4-space indentation
                    smells.append(CodeSmell(
                        name="Deep Nesting",
                        location=f"Line {idx}",
                        description=f"Code is nested {indent // 4} levels deep"
                    ))
        
        # Commented code
        commented_code = [
            line for line in self.lines 
            if line.strip().startswith('#') and any(c in line for c in '({[=;')
        ]
        if len(commented_code) > 5:
            smells.append(CodeSmell(
                name="Commented Code",
                location="Multiple locations",
                description=f"Found {len(commented_code)} lines of commented-out code"
            ))
        
        # Too many dependencies
        deps = self._extract_dependencies()
        if len(deps) > 15:
            smells.append(CodeSmell(
                name="Too Many Dependencies",
                location="Module level",
                description=f"Module imports {len(deps)} different packages"
            ))
        
        return smells
    
    def _calculate_avg_function_length(self) -> float:
        """Calculate average function length"""
        functions = re.findall(r'def\s+\w+', self.code)
        if not functions:
            return 0.0
        
        total_lines = 0
        for match in re.finditer(r'def\s+\w+', self.code):
            func_start = match.start()
            remaining = self.code[func_start:]
            func_lines = 0
            for line in remaining.split('\n')[1:]:
                if line and not line[0].isspace():
                    break
                func_lines += 1
            total_lines += func_lines
        
        return total_lines / len(functions) if functions else 0.0
    
    def _calculate_maintainability(self, code_lines: int, comment_lines: int, 
                                   complexity: int, anti_pattern_count: int, 
                                   smell_count: int) -> float:
        """Calculate maintainability index (0-100, higher is better)"""
        comment_ratio = comment_lines / max(code_lines, 1)
        avg_complexity = complexity / max(code_lines / 10, 1)
        
        maintainability = 100
        maintainability -= avg_complexity * 3
        maintainability -= anti_pattern_count * 5
        maintainability -= smell_count * 2
        maintainability += comment_ratio * 15
        
        return max(0.0, min(100.0, maintainability))
    
    def _calculate_technical_debt(self, complexity: int, anti_pattern_count: int,
                                  smell_count: int, loc: int) -> float:
        """Calculate technical debt score (0-100, lower is better)"""
        debt = 0
        debt += complexity * 0.5
        debt += anti_pattern_count * 10
        debt += smell_count * 5
        debt += (loc / 100) * 2  # Penalize large files
        
        return min(100.0, debt)


class ModernizationAdvisor:
    """Provides modernization recommendations based on analysis"""
    
    @staticmethod
    def generate_recommendations(metrics: CodeMetrics, risk_level: RiskLevel) -> List[Recommendation]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Python version
        if "Python 2" in metrics.python_version:
            recommendations.append(Recommendation(
                priority=Severity.CRITICAL.value,
                action="Migrate to Python 3",
                reason="Python 2 reached end-of-life in January 2020. Security updates are no longer provided."
            ))
        
        # Complexity
        if metrics.cyclomatic_complexity > 50:
            recommendations.append(Recommendation(
                priority=Severity.HIGH.value,
                action="Refactor complex code paths",
                reason=f"Cyclomatic complexity of {metrics.cyclomatic_complexity} makes code difficult to test and maintain"
            ))
        elif metrics.cyclomatic_complexity > 30:
            recommendations.append(Recommendation(
                priority=Severity.MEDIUM.value,
                action="Reduce code complexity",
                reason=f"Complexity score of {metrics.cyclomatic_complexity} is above recommended threshold of 30"
            ))
        
        # Anti-patterns
        critical_patterns = [p for p in metrics.anti_patterns if p.severity == Severity.CRITICAL.value]
        high_patterns = [p for p in metrics.anti_patterns if p.severity == Severity.HIGH.value]
        
        for pattern in critical_patterns:
            recommendations.append(Recommendation(
                priority=Severity.CRITICAL.value,
                action=f"Fix: {pattern.name}",
                reason=f"{pattern.description} (line {pattern.line_number})"
            ))
        
        for pattern in high_patterns[:3]:  # Limit to top 3
            recommendations.append(Recommendation(
                priority=Severity.HIGH.value,
                action=f"Fix: {pattern.name}",
                reason=f"{pattern.description} (line {pattern.line_number})"
            ))
        
        # Maintainability
        if metrics.maintainability_index < 40:
            recommendations.append(Recommendation(
                priority=Severity.HIGH.value,
                action="Improve code maintainability",
                reason=f"Maintainability index of {metrics.maintainability_index:.1f} is below acceptable threshold"
            ))
        elif metrics.maintainability_index < 60:
            recommendations.append(Recommendation(
                priority=Severity.MEDIUM.value,
                action="Add documentation and refactor",
                reason="Code maintainability could be improved with better structure and documentation"
            ))
        
        # Function length
        if metrics.average_function_length > 50:
            recommendations.append(Recommendation(
                priority=Severity.MEDIUM.value,
                action="Break down large functions",
                reason=f"Average function length of {metrics.average_function_length:.1f} lines exceeds recommended maximum"
            ))
        
        # Nesting depth
        if metrics.max_nesting_depth > 5:
            recommendations.append(Recommendation(
                priority=Severity.MEDIUM.value,
                action="Reduce nesting depth",
                reason=f"Maximum nesting depth of {metrics.max_nesting_depth} makes code hard to follow"
            ))
        
        # Code smells
        long_functions = [s for s in metrics.code_smells if s.name == "Long Function"]
        if len(long_functions) > 3:
            recommendations.append(Recommendation(
                priority=Severity.MEDIUM.value,
                action="Refactor long functions",
                reason=f"Found {len(long_functions)} functions exceeding recommended length"
            ))
        
        # Dependencies
        if len(metrics.dependencies) > 20:
            recommendations.append(Recommendation(
                priority=Severity.LOW.value,
                action="Review and reduce dependencies",
                reason=f"Module has {len(metrics.dependencies)} dependencies, consider splitting into smaller modules"
            ))
        
        return recommendations


class RiskAssessment:
    """Assesses overall modernization risk"""
    
    @staticmethod
    def calculate_risk(metrics: CodeMetrics) -> tuple:
        """Calculate risk level and score"""
        risk_score = 0
        
        # Complexity risk
        if metrics.cyclomatic_complexity > 50:
            risk_score += 30
        elif metrics.cyclomatic_complexity > 30:
            risk_score += 20
        elif metrics.cyclomatic_complexity > 15:
            risk_score += 10
        
        # Anti-pattern risk
        critical_count = sum(1 for p in metrics.anti_patterns if p.severity == Severity.CRITICAL.value)
        high_count = sum(1 for p in metrics.anti_patterns if p.severity == Severity.HIGH.value)
        risk_score += critical_count * 25
        risk_score += high_count * 15
        risk_score += len(metrics.anti_patterns) * 3
        
        # Code smell risk
        risk_score += min(25, len(metrics.code_smells) * 2)
        
        # Size risk
        if metrics.lines_of_code > 1000:
            risk_score += 15
        elif metrics.lines_of_code > 500:
            risk_score += 10
        
        # Python version risk
        if "Python 2" in metrics.python_version:
            risk_score += 30
        
        # Maintainability risk
        if metrics.maintainability_index < 40:
            risk_score += 20
        elif metrics.maintainability_index < 60:
            risk_score += 10
        
        # Technical debt risk
        if metrics.technical_debt_score > 70:
            risk_score += 15
        elif metrics.technical_debt_score > 50:
            risk_score += 10
        
        # Determine risk level
        if risk_score >= 70:
            return RiskLevel.CRITICAL, risk_score
        elif risk_score >= 50:
            return RiskLevel.HIGH, risk_score
        elif risk_score >= 30:
            return RiskLevel.MEDIUM, risk_score
        else:
            return RiskLevel.LOW, risk_score


def analyze_code(code: str) -> Dict[str, Any]:
    """Main entry point for code analysis"""
    analyzer = CodeAnalyzer(code)
    metrics = analyzer.analyze()
    
    risk_level, risk_score = RiskAssessment.calculate_risk(metrics)
    recommendations = ModernizationAdvisor.generate_recommendations(metrics, risk_level)
    
    return {
        "risk_level": risk_level.value,
        "risk_score": risk_score,
        "metrics": {
            "lines_of_code": metrics.lines_of_code,
            "code_lines": metrics.code_lines,
            "comment_lines": metrics.comment_lines,
            "blank_lines": metrics.blank_lines,
            "cyclomatic_complexity": metrics.cyclomatic_complexity,
            "class_count": metrics.class_count,
            "function_count": metrics.function_count,
            "maintainability_index": round(metrics.maintainability_index, 2),
            "technical_debt_score": round(metrics.technical_debt_score, 2),
            "average_function_length": round(metrics.average_function_length, 2),
            "max_nesting_depth": metrics.max_nesting_depth,
            "python_version": metrics.python_version,
            "dependencies": metrics.dependencies
        },
        "anti_patterns": [
            {
                "name": ap.name,
                "severity": ap.severity,
                "description": ap.description,
                "line": ap.line_number
            }
            for ap in metrics.anti_patterns
        ],
        "code_smells": [
            {
                "name": cs.name,
                "location": cs.location,
                "description": cs.description
            }
            for cs in metrics.code_smells
        ],
        "recommendations": [
            {
                "priority": r.priority,
                "action": r.action,
                "reason": r.reason
            }
            for r in recommendations
        ]
    }


def print_analysis_report(result: Dict[str, Any]):
    """Print formatted analysis report"""
    print("\n" + "="*80)
    print("CODE MODERNIZATION ANALYSIS REPORT")
    print("="*80)
    
    # Risk Assessment
    risk_colors = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    risk_icon = risk_colors.get(result["risk_level"], "⚪")
    
    print(f"\n{risk_icon} RISK LEVEL: {result['risk_level'].upper()}")
    print(f"   Risk Score: {result['risk_score']}/100")
    
    # Metrics Summary
    metrics = result["metrics"]
    print("\n📊 METRICS SUMMARY")
    print("-" * 80)
    print(f"  Lines of Code:          {metrics['lines_of_code']}")
    print(f"  Code Lines:             {metrics['code_lines']}")
    print(f"  Comment Lines:          {metrics['comment_lines']}")
    print(f"  Cyclomatic Complexity:  {metrics['cyclomatic_complexity']}")
    print(f"  Maintainability Index:  {metrics['maintainability_index']}/100")
    print(f"  Technical Debt Score:   {metrics['technical_debt_score']}/100")
    print(f"  Python Version:         {metrics['python_version']}")
    print(f"  Classes:                {metrics['class_count']}")
    print(f"  Functions:              {metrics['function_count']}")
    print(f"  Avg Function Length:    {metrics['average_function_length']:.1f} lines")
    print(f"  Max Nesting Depth:      {metrics['max_nesting_depth']}")
    print(f"  Dependencies:           {len(metrics['dependencies'])}")
    
    # Anti-Patterns
    if result["anti_patterns"]:
        print("\n⚠️  ANTI-PATTERNS DETECTED")
        print("-" * 80)
        for ap in result["anti_patterns"][:10]:  # Show top 10
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}
            print(f"  {severity_icon.get(ap['severity'], '⚪')} {ap['name']} (Line {ap['line']})")
            print(f"     {ap['description']}")
    
    # Code Smells
    if result["code_smells"]:
        print("\n👃 CODE SMELLS DETECTED")
        print("-" * 80)
        for cs in result["code_smells"][:10]:  # Show top 10
            print(f"  • {cs['name']} - {cs['location']}")
            print(f"    {cs['description']}")
    
    # Recommendations
    if result["recommendations"]:
        print("\n💡 MODERNIZATION RECOMMENDATIONS")
        print("-" * 80)
        for idx, rec in enumerate(result["recommendations"], 1):
            priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}
            print(f"  {idx}. [{priority_icon.get(rec['priority'], '⚪')} {rec['priority'].upper()}] {rec['action']}")
            print(f"     {rec['reason']}")
    
    print("\n" + "="*80 + "\n")


# Example usage
if __name__ == "__main__":
    sample_code = """
# Legacy Python code with various issues
import sys
from os import *

global_counter = 0

def process_data(data, options={}):
    global global_counter
    try:
        results = []
        for item in data:
            if item:
                if item > 0:
                    if item < 100:
                        if item % 2 == 0:
                            if item % 4 == 0:
                                results.append(item * 2)
                        else:
                            results.append(item * 3)
        global_counter += 1
    except:
        pass
    return results

def calculate(x, y):
    result = eval("x + y")
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
    
    def process_all_items_with_complex_logic_and_transformations_that_really_should_be_broken_down(self):
        processed = []
        for item in self.data:
            if isinstance(item, int):
                if item > 0:
                    if item < 1000:
                        processed_item = item * 2
                        if processed_item > 100:
                            processed_item = processed_item / 2
                        processed.append(processed_item)
        return processed

# Commented out code that should be removed
# def old_function():
#     return "deprecated"

print "Hello World"  # Python 2 style print
"""
    
    # Analyze the code
    result = analyze_code(sample_code)
    
    # Print formatted report
    print_analysis_report(result)
    
    # Optionally, save as JSON
    import json
    with open('analysis_report.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("📄 Detailed report saved to: analysis_report.json")
