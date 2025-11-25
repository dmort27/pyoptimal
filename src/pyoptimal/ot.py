"""
Optimality Theory specific learning algorithms.
"""

from typing import List, Set, Tuple
from .grammar import Grammar, Constraint, Example
from .learner import PartialOrder


class OTLearner:
    """Learner for Optimality Theory constraint rankings."""
    
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
    
    def learn(self) -> PartialOrder:
        """
        Learn a partial order over constraints using constraint demotion.
        
        This implements a simplified version of the constraint demotion algorithm
        (Tesar & Smolensky 1998, 2000).
        """
        partial_order = PartialOrder(self.grammar.constraints)
        
        for example in self.grammar.examples:
            if not example.optimal:
                continue
            
            optimal_violations = example.violations
            
            for other_example in self.grammar.examples:
                if other_example.input_form == example.input_form and not other_example.optimal:
                    losing_violations = other_example.violations
                    
                    crucial_constraints = self._find_crucial_constraints(
                        optimal_violations,
                        losing_violations
                    )
                    
                    for higher_c_name, lower_c_names in crucial_constraints:
                        higher_c = self.grammar.get_constraint(higher_c_name)
                        if higher_c:
                            for lower_c_name in lower_c_names:
                                lower_c = self.grammar.get_constraint(lower_c_name)
                                if lower_c and not partial_order.dominates(lower_c, higher_c):
                                    partial_order.add_dominance(higher_c, lower_c)
        
        return partial_order
    
    def _find_crucial_constraints(
        self,
        optimal_violations: dict,
        losing_violations: dict
    ) -> List[Tuple[str, List[str]]]:
        """
        Find constraints that prefer the optimal candidate over the losing candidate.
        
        Returns pairs of (constraint_favoring_optimal, [constraints_favoring_loser])
        """
        crucial = []
        
        all_constraints = set(optimal_violations.keys()) | set(losing_violations.keys())
        
        for c_name in all_constraints:
            opt_viol = optimal_violations.get(c_name, 0)
            lose_viol = losing_violations.get(c_name, 0)
            
            if lose_viol > opt_viol:
                lower_constraints = []
                for other_c in all_constraints:
                    other_opt = optimal_violations.get(other_c, 0)
                    other_lose = losing_violations.get(other_c, 0)
                    if other_opt > other_lose:
                        lower_constraints.append(other_c)
                
                if lower_constraints:
                    crucial.append((c_name, lower_constraints))
        
        return crucial
