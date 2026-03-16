"""A lightweight facade for resume analysis.

This module exists to provide a stable import path used by the web app
(e.g., `from resume_analyzer import analyze_resume`).

It delegates to the NLP engine implementation in Dataset/nlp_engine.py.
"""

from Dataset.nlp_engine import analyze_resume
