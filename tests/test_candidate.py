"""Tests for candidate module."""

import pytest
from pyoptimal.candidate import Candidate


def test_candidate_creation():
    violations = {"NOCODA": 1, "MAX": 0, "DEP": 0}
    candidate = Candidate("/pat/", "pat", violations)
    
    assert candidate.input_form == "/pat/"
    assert candidate.output_form == "pat"
    assert candidate.violations == violations


def test_candidate_get_violation():
    violations = {"NOCODA": 1, "MAX": 0}
    candidate = Candidate("/pat/", "pat", violations)
    
    assert candidate.get_violation("NOCODA") == 1
    assert candidate.get_violation("MAX") == 0
    assert candidate.get_violation("DEP") == 0


def test_candidate_str():
    candidate = Candidate("/pat/", "pat", {})
    assert str(candidate) == "/pat/ → pat"
