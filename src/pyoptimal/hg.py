"""
Harmonic Grammar specific learning algorithms.
"""

from typing import Dict
from .grammar import Grammar, Constraint
from .learner import PartialOrder
import numpy as np


class HGLearner:
    """Learner for Harmonic Grammar constraint weights."""
    
    def __init__(self, grammar: Grammar, learning_rate: float = 0.1):
        self.grammar = grammar
        self.learning_rate = learning_rate
        self.weights: Dict[str, float] = {c.name: 0.0 for c in grammar.constraints}
    
    def learn(self) -> PartialOrder:
        """
        Learn constraint weights using a perceptron-like algorithm.
        
        This implements a simplified version of the Gradual Learning Algorithm
        (Boersma 1997, Boersma & Hayes 2001).
        """
        max_iterations = 1000
        
        for iteration in range(max_iterations):
            updated = False
            
            for example in self.grammar.examples:
                if not example.optimal:
                    continue
                
                optimal_harmony = self._compute_harmony(example.violations)
                
                for other_example in self.grammar.examples:
                    if other_example.input_form == example.input_form and not other_example.optimal:
                        losing_harmony = self._compute_harmony(other_example.violations)
                        
                        if losing_harmony >= optimal_harmony:
                            for c_name in self.weights:
                                opt_viol = example.violations.get(c_name, 0)
                                lose_viol = other_example.violations.get(c_name, 0)
                                
                                delta = (lose_viol - opt_viol) * self.learning_rate
                                self.weights[c_name] += delta
                            
                            updated = True
            
            if not updated:
                break
        
        return self._weights_to_partial_order()
    
    def _compute_harmony(self, violations: Dict[str, int]) -> float:
        """Compute harmony score (negative weighted sum of violations)."""
        harmony = 0.0
        for c_name, viol_count in violations.items():
            harmony -= self.weights.get(c_name, 0.0) * viol_count
        return harmony
    
    def _weights_to_partial_order(self) -> PartialOrder:
        """Convert learned weights to a partial order."""
        partial_order = PartialOrder(self.grammar.constraints)
        
        sorted_constraints = sorted(
            self.grammar.constraints,
            key=lambda c: self.weights.get(c.name, 0.0),
            reverse=True
        )
        
        epsilon = 0.01
        for i, c1 in enumerate(sorted_constraints):
            for c2 in sorted_constraints[i+1:]:
                w1 = self.weights.get(c1.name, 0.0)
                w2 = self.weights.get(c2.name, 0.0)
                
                if abs(w1 - w2) > epsilon:
                    partial_order.add_dominance(c1, c2)
        
        return partial_order
    
    def get_weights(self) -> Dict[str, float]:
        """Get the learned constraint weights."""
        return self.weights.copy()
