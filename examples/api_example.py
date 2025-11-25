#!/usr/bin/env python
"""
Example demonstrating how to use PyOptimal's Python API.
"""

from pyoptimal import Grammar, Learner, Constraint
from pyoptimal.grammar import Example


def example_1_load_from_yaml():
    """Load grammar from YAML and learn ranking."""
    print("=" * 60)
    print("Example 1: Loading from YAML")
    print("=" * 60)
    
    grammar = Grammar.from_yaml("examples/simple_ot.yaml")
    
    print(f"\nGrammar: {len(grammar.constraints)} constraints, {len(grammar.examples)} examples")
    print("Constraints:", [c.name for c in grammar.constraints])
    
    learner = Learner(grammar, algorithm="ot")
    ranking = learner.train()
    
    print(f"\nLearned ranking: {ranking}")
    print()


def example_2_create_grammar_programmatically():
    """Create grammar programmatically without YAML."""
    print("=" * 60)
    print("Example 2: Creating Grammar Programmatically")
    print("=" * 60)
    
    constraints = [
        Constraint("ONSET", "Syllables must have onsets"),
        Constraint("NOCODA", "Syllables must not have codas"),
        Constraint("DEP", "No epenthesis"),
    ]
    
    examples = [
        Example("/at/", "a.t", False, {"ONSET": 1, "NOCODA": 1, "DEP": 0}),
        Example("/at/", "Pat", True, {"ONSET": 0, "NOCODA": 1, "DEP": 1}),
        Example("/pat/", "pat", False, {"ONSET": 0, "NOCODA": 1, "DEP": 0}),
        Example("/pat/", "pa.ta", True, {"ONSET": 0, "NOCODA": 0, "DEP": 1}),
    ]
    
    grammar = Grammar(constraints, examples)
    
    print(f"\nCreated grammar with {len(constraints)} constraints")
    
    learner = Learner(grammar, algorithm="ot")
    ranking = learner.train()
    
    print(f"\nLearned ranking: {ranking}")
    print()


def example_3_harmonic_grammar():
    """Use Harmonic Grammar to learn weights."""
    print("=" * 60)
    print("Example 3: Harmonic Grammar with Weights")
    print("=" * 60)
    
    grammar = Grammar.from_yaml("examples/simple_hg.yaml")
    
    learner = Learner(grammar, algorithm="hg")
    ranking = learner.train()
    
    print(f"\nLearned ranking: {ranking}")
    
    from pyoptimal.hg import HGLearner
    hg_learner = HGLearner(grammar)
    hg_learner.learn()
    weights = hg_learner.get_weights()
    
    print("\nConstraint weights:")
    for c_name in sorted(weights.keys(), key=lambda k: weights[k], reverse=True):
        print(f"  {c_name:15s}: {weights[c_name]:7.4f}")
    print()


def example_4_partial_order_inspection():
    """Inspect the learned partial order in detail."""
    print("=" * 60)
    print("Example 4: Inspecting Partial Order")
    print("=" * 60)
    
    grammar = Grammar.from_yaml("examples/complex_ot.yaml")
    
    learner = Learner(grammar, algorithm="ot")
    ranking = learner.train()
    
    print(f"\nLearned ranking: {ranking}")
    
    print("\nStrata (constraints at same level are unranked):")
    strata = ranking.get_strata()
    for i, stratum in enumerate(strata, 1):
        print(f"  Stratum {i}: {{{', '.join(c.name for c in stratum)}}}")
    
    print("\nDominance relations:")
    for c1 in grammar.constraints:
        for c2 in grammar.constraints:
            if c1 != c2 and ranking.dominates(c1, c2):
                print(f"  {c1.name} >> {c2.name}")
    print()


if __name__ == "__main__":
    example_1_load_from_yaml()
    example_2_create_grammar_programmatically()
    example_3_harmonic_grammar()
    example_4_partial_order_inspection()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
