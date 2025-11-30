"""Tests for learner module."""

import pytest
from pyoptimal.grammar import Grammar, Constraint, Example
from pyoptimal.learner import Learner, PartialOrder


def create_simple_grammar():
    """Create a simple test grammar."""
    constraints = [
        Constraint("NOCODA"),
        Constraint("MAX"),
        Constraint("DEP")
    ]
    examples = [
        Example("/pat/", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1}),
        Example("/pat/", "pat", False, {"NOCODA": 1, "MAX": 0, "DEP": 0}),
        Example("/pat/", "pa", False, {"NOCODA": 0, "MAX": 1, "DEP": 0}),
    ]
    return Grammar(constraints, examples)


def test_partial_order_creation():
    constraints = [Constraint("A"), Constraint("B"), Constraint("C")]
    po = PartialOrder(constraints)
    assert len(po.constraints) == 3


def test_partial_order_dominance():
    constraints = [Constraint("A"), Constraint("B"), Constraint("C")]
    po = PartialOrder(constraints)
    
    po.add_dominance(constraints[0], constraints[1])
    assert po.dominates(constraints[0], constraints[1])
    assert not po.dominates(constraints[1], constraints[0])


def test_partial_order_transitive():
    constraints = [Constraint("A"), Constraint("B"), Constraint("C")]
    po = PartialOrder(constraints)
    
    po.add_dominance(constraints[0], constraints[1])
    po.add_dominance(constraints[1], constraints[2])
    
    assert po.dominates(constraints[0], constraints[2])


def test_partial_order_strata():
    constraints = [Constraint("A"), Constraint("B"), Constraint("C")]
    po = PartialOrder(constraints)
    
    po.add_dominance(constraints[0], constraints[2])
    po.add_dominance(constraints[1], constraints[2])
    
    strata = po.get_strata()
    assert len(strata) >= 2
    assert constraints[2] in strata[-1] or constraints[2] in strata[-2]


def test_learner_ot():
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="ot")
    ranking = learner.train()
    
    assert ranking is not None
    assert isinstance(ranking, PartialOrder)


def test_learner_hg():
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="hg")
    ranking = learner.train()
    
    assert ranking is not None
    assert isinstance(ranking, PartialOrder)


def test_learner_invalid_algorithm():
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="invalid")
    
    with pytest.raises(ValueError):
        learner.train()


def test_learner_rcd():
    """Test RCD (Recursive Constraint Demotion) algorithm."""
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="rcd")
    ranking = learner.train()
    
    assert ranking is not None
    assert isinstance(ranking, PartialOrder)
    # RCD should produce a stratified ranking
    strata = ranking.get_strata()
    assert len(strata) > 0


def test_learner_edcd():
    """Test EDCD (Error-Driven Constraint Demotion) algorithm."""
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="edcd")
    ranking = learner.train()
    
    assert ranking is not None
    assert isinstance(ranking, PartialOrder)


def test_learner_gla():
    """Test GLA (Gradual Learning Algorithm)."""
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="gla")
    ranking = learner.train()
    
    assert ranking is not None
    assert isinstance(ranking, PartialOrder)


def test_learner_maxent():
    """Test MaxEnt (Maximum Entropy) algorithm."""
    grammar = create_simple_grammar()
    learner = Learner(grammar, algorithm="maxent")
    ranking = learner.train()
    
    assert ranking is not None
    assert isinstance(ranking, PartialOrder)
