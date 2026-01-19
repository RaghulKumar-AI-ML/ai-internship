Overview

This project is a Python-based static code analysis tool designed to support legacy system modernization. It analyzes Python source code to extract structural metrics, detect risky patterns, assess modernization risk, and provide actionable recommendations.

The project is extended with a simple Retrieval-Augmented Generation (RAG) layer that allows interactive, human-readable explanations of analysis results.

The focus of this project is on clarity, explainability, and learning-oriented system design rather than production-scale optimization.

Motivation

Large enterprise systems often contain long-lived Python codebases with varying levels of complexity, technical debt, and legacy patterns. Before attempting modernization, teams must understand which components are risky and why.

This project demonstrates how source code can be transformed into structured insights that help prioritize modernization efforts.

What the Project Does
Static Code Analysis

Parses Python source code using the Abstract Syntax Tree (AST)

Computes structural metrics

Detects high-risk anti-patterns

Estimates maintainability and technical debt

Assigns an overall modernization risk level

Produces a structured JSON report

Retrieval-Augmented Generation (RAG)

Uses analysis insights as a knowledge base

Supports interactive question answering over analysis results

Generates explainable, rule-based responses for modernization guidance

Metrics Extracted

Lines of code

Cyclomatic complexity

Number of classes and functions

Maintainability index

Technical debt score

Detected Python version (Python 2 or Python 3)

Issues Detected
Anti-Patterns

Use of eval() or similar unsafe constructs

Legacy Python 2 syntax

Code Smells

High logical complexity

Hard-to-maintain structure

Risk Assessment

The tool assigns one of the following risk levels:

Low

Medium

High

Critical

These levels help determine which code should be modernized first.

RAG Layer

The RAG layer operates on top of the analyzer output. It retrieves relevant insights from stored analysis results and generates natural language explanations and recommendations. This allows users to query the analysis interactively without reading raw metrics.


Code Modernization RAG VS Code Extension

This extension allows users to ask natural language questions about
Python code modernization and receive answers powered by a RAG system.

Usage:
- Open Command Palette
- Run "Ask Code Modernization Question"
- Enter your question

