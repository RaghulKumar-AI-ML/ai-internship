🧠 Metric-Based Code Modernization Analyzer
📌 Overview

This project is a metric-based code analysis tool that analyzes Python source code and helps assess its modernization risk.
It is designed as a validation module to understand how enterprise modernization tools first extract structured signals from legacy code before applying advanced techniques like AST analysis or machine learning.

The tool focuses on learning and explainability, not perfection.

🎯 Problem Statement

Large Python codebases (such as ERP systems) often contain:

High complexity

Legacy patterns (Python 2 syntax, globals, eval)

Deep nesting

Poor maintainability

Before modernizing such systems, teams need to answer:

Which parts of the code are risky and should be addressed first?

This project provides an automated, rule-based way to answer that question.

🛠️ What This Tool Does

The analyzer:

Reads Python source code

Extracts structural metrics

Detects anti-patterns and code smells

Calculates maintainability and technical debt

Assigns an overall risk level

Generates modernization recommendations

📊 Metrics Extracted

The tool calculates:

Lines of code (total, code, comments, blanks)

Cyclomatic complexity (using AST)

Maximum nesting depth

Number of functions and classes

Imported dependencies

Average function length

Maintainability Index (0–100)

Technical Debt Score (0–100)

Detected Python version (2 vs 3)

⚠️ Issues Detected
Anti-Patterns

Examples:

eval() / exec() usage

Bare except: blocks

Excessive global variables

Wildcard imports (from x import *)

Mutable default arguments

Code Smells

Examples:

Long functions

Long lines

Deep nesting

Commented-out code

Too many dependencies

⚖️ Risk Assessment

Based on all metrics, the tool assigns a risk level:

Risk Level	Meaning
🟢 Low	Easy to maintain
🟡 Medium	Some refactoring needed
🟠 High	Difficult to maintain
🔴 Critical	Immediate modernization required

This mirrors enterprise modernization patterns where teams prioritize high-risk components first.

💡 Modernization Recommendations

The tool generates actionable recommendations, such as:

Migrate Python 2 code to Python 3

Reduce cyclomatic complexity

Refactor long or deeply nested functions

Remove dangerous constructs

Improve documentation and structure
