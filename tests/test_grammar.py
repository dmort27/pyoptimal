"""Tests for grammar module."""

import pytest
import tempfile
import os
from pathlib import Path
from pyoptimal.grammar import Grammar, Constraint, Example


def test_constraint_creation():
    c = Constraint("NOCODA", "No codas")
    assert c.name == "NOCODA"
    assert c.description == "No codas"


def test_constraint_equality():
    c1 = Constraint("MAX")
    c2 = Constraint("MAX")
    c3 = Constraint("DEP")
    assert c1 == c2
    assert c1 != c3


def test_example_creation():
    e = Example("/pat/", "pa.ta", True, {"NOCODA": 0, "DEP": 1})
    assert e.input_form == "/pat/"
    assert e.output_form == "pa.ta"
    assert e.optimal is True
    assert e.violations["DEP"] == 1


def test_grammar_creation():
    constraints = [
        Constraint("NOCODA"),
        Constraint("MAX"),
        Constraint("DEP")
    ]
    examples = [
        Example("/pat/", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1})
    ]
    grammar = Grammar(constraints, examples)
    
    assert len(grammar.constraints) == 3
    assert len(grammar.examples) == 1
    assert grammar.get_constraint("NOCODA") is not None


def test_grammar_yaml_roundtrip():
    constraints = [
        Constraint("NOCODA", "No codas"),
        Constraint("MAX", "No deletion")
    ]
    examples = [
        Example("/pat/", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1})
    ]
    grammar = Grammar(constraints, examples)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name
    
    try:
        grammar.to_yaml(temp_path)
        loaded_grammar = Grammar.from_yaml(temp_path)
        
        assert len(loaded_grammar.constraints) == len(grammar.constraints)
        assert len(loaded_grammar.examples) == len(grammar.examples)
        assert loaded_grammar.constraints[0].name == "NOCODA"
        assert loaded_grammar.examples[0].input_form == "/pat/"
    finally:
        os.unlink(temp_path)


def test_grammar_add_example():
    grammar = Grammar([Constraint("NOCODA")])
    assert len(grammar.examples) == 0
    
    grammar.add_example(Example("/pat/", "pat", False, {"NOCODA": 1}))
    assert len(grammar.examples) == 1
