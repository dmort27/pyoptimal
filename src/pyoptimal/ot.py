"""
Optimality Theory specific learning algorithms.
"""

from typing import List, Set, Tuple, Dict
import random
import math
from .grammar import Grammar, Constraint, Example
from .learner import PartialOrder


class OTLearner:
    """Learner for Optimality Theory constraint rankings (basic constraint demotion)."""
    
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


class RCDLearner:
    """Recursive Constraint Demotion (Tesar 1995, Tesar & Smolensky 2000)."""
    
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
    
    def learn(self) -> PartialOrder:
        """
        Learn a stratified constraint ranking using RCD.
        
        RCD recursively identifies constraints that never prefer losers over winners,
        places them in the current stratum, then recurses on remaining constraints.
        """
        partial_order = PartialOrder(self.grammar.constraints)
        
        # Get all winner-loser pairs
        wl_pairs = self._get_winner_loser_pairs()
        
        # Build strata iteratively
        unranked = set(self.grammar.constraints)
        strata = []
        
        while unranked:
            # Find constraints that never prefer loser over winner
            current_stratum = set()
            for constraint in unranked:
                if self._can_be_top(constraint, wl_pairs):
                    current_stratum.add(constraint)
            
            if not current_stratum:
                # No constraint is safe - ranking conflict
                # Place all remaining in last stratum
                current_stratum = unranked.copy()
            
            strata.append(current_stratum)
            unranked -= current_stratum
            
            # Remove satisfied winner-loser pairs
            wl_pairs = [wl for wl in wl_pairs if not self._pair_satisfied(wl, current_stratum)]
        
        # Convert strata to partial order (each stratum dominates all lower strata)
        for i, stratum in enumerate(strata):
            for lower_stratum in strata[i+1:]:
                for higher_c in stratum:
                    for lower_c in lower_stratum:
                        partial_order.add_dominance(higher_c, lower_c)
        
        return partial_order
    
    def _get_winner_loser_pairs(self) -> List[Tuple[Example, Example]]:
        """Get all winner-loser pairs from the data."""
        pairs = []
        for winner in self.grammar.examples:
            if not winner.optimal:
                continue
            for loser in self.grammar.examples:
                if loser.input_form == winner.input_form and not loser.optimal:
                    pairs.append((winner, loser))
        return pairs
    
    def _can_be_top(self, constraint: Constraint, wl_pairs: List[Tuple[Example, Example]]) -> bool:
        """Check if constraint can be in top stratum (never prefers loser)."""
        for winner, loser in wl_pairs:
            winner_viols = winner.violations.get(constraint.name, 0)
            loser_viols = loser.violations.get(constraint.name, 0)
            if winner_viols > loser_viols:
                return False
        return True
    
    def _pair_satisfied(self, wl_pair: Tuple[Example, Example], stratum: Set[Constraint]) -> bool:
        """Check if winner-loser pair is satisfied by any constraint in stratum."""
        winner, loser = wl_pair
        for constraint in stratum:
            winner_viols = winner.violations.get(constraint.name, 0)
            loser_viols = loser.violations.get(constraint.name, 0)
            if loser_viols > winner_viols:
                return True
        return False


class EDCDLearner:
    """Error-Driven Constraint Demotion (Tesar & Smolensky 1993, 1998)."""
    
    def __init__(self, grammar: Grammar, max_iterations: int = 1000):
        self.grammar = grammar
        self.max_iterations = max_iterations
    
    def learn(self) -> PartialOrder:
        """
        Learn constraint ranking using error-driven approach.
        
        Iterates through examples, adjusting ranking only when errors occur.
        """
        partial_order = PartialOrder(self.grammar.constraints)
        
        # Get all examples
        examples = [ex for ex in self.grammar.examples if ex.optimal]
        
        for iteration in range(self.max_iterations):
            errors = False
            
            for winner in examples:
                # Check if current ranking correctly predicts this winner
                competitors = [ex for ex in self.grammar.examples 
                             if ex.input_form == winner.input_form]
                
                predicted_winner = self._predict_winner(competitors, partial_order)
                
                if predicted_winner != winner:
                    errors = True
                    # Make demotion: find crucial constraints
                    for loser in competitors:
                        if loser.optimal or loser == winner:
                            continue
                        
                        # Find constraints that prefer winner over loser
                        # and demote constraints that prefer loser over winner
                        self._demote_for_pair(winner, loser, partial_order)
            
            if not errors:
                break
        
        return partial_order
    
    def _predict_winner(self, candidates: List[Example], ranking: PartialOrder) -> Example:
        """Predict which candidate wins under current ranking."""
        strata = ranking.get_strata()
        
        remaining = candidates[:]
        for stratum in strata:
            if len(remaining) == 1:
                return remaining[0]
            
            # Find minimum violations for constraints in this stratum
            min_viols = {}
            for constraint in stratum:
                min_viols[constraint.name] = min(
                    cand.violations.get(constraint.name, 0) 
                    for cand in remaining
                )
            
            # Filter to candidates with minimum violations
            new_remaining = []
            for cand in remaining:
                keep = True
                for constraint in stratum:
                    if cand.violations.get(constraint.name, 0) > min_viols[constraint.name]:
                        keep = False
                        break
                if keep:
                    new_remaining.append(cand)
            
            remaining = new_remaining
        
        return remaining[0] if remaining else candidates[0]
    
    def _demote_for_pair(self, winner: Example, loser: Example, ranking: PartialOrder):
        """Adjust ranking to prefer winner over loser."""
        # Find constraints that prefer winner (W) and loser (L)
        w_constraints = []
        l_constraints = []
        
        for constraint in self.grammar.constraints:
            w_viols = winner.violations.get(constraint.name, 0)
            l_viols = loser.violations.get(constraint.name, 0)
            
            if l_viols > w_viols:
                w_constraints.append(constraint)
            elif w_viols > l_viols:
                l_constraints.append(constraint)
        
        # Demote L-preferring constraints below W-preferring constraints
        for w_constraint in w_constraints:
            for l_constraint in l_constraints:
                if not ranking.dominates(l_constraint, w_constraint):
                    ranking.add_dominance(w_constraint, l_constraint)


class GLALearner:
    """Gradual Learning Algorithm (Boersma 1997, Boersma & Hayes 2001)."""
    
    def __init__(self, grammar: Grammar, plasticity: float = 2.0, 
                 noise: float = 2.0, initial_ranking: float = 100.0,
                 max_iterations: int = 1000):
        self.grammar = grammar
        self.plasticity = plasticity
        self.noise = noise
        self.initial_ranking = initial_ranking
        self.max_iterations = max_iterations
        self.ranking_values = {c.name: initial_ranking for c in grammar.constraints}
    
    def learn(self) -> PartialOrder:
        """
        Learn constraint ranking values using GLA.
        
        Returns a partial order derived from the learned continuous values.
        """
        examples = [ex for ex in self.grammar.examples if ex.optimal]
        
        for iteration in range(self.max_iterations):
            random.shuffle(examples)
            
            for winner in examples:
                competitors = [ex for ex in self.grammar.examples 
                             if ex.input_form == winner.input_form]
                
                # Evaluate with noise
                noisy_rankings = {c: self.ranking_values[c] + random.gauss(0, self.noise)
                                 for c in self.ranking_values}
                
                predicted = self._predict_winner_gla(competitors, noisy_rankings)
                
                if predicted != winner:
                    # Update rankings
                    self._update_rankings(winner, predicted)
        
        # Convert continuous rankings to partial order
        return self._rankings_to_partial_order()
    
    def _predict_winner_gla(self, candidates: List[Example], rankings: Dict[str, float]) -> Example:
        """Predict winner using harmony scores."""
        best_candidate = None
        best_harmony = float('-inf')
        
        for candidate in candidates:
            harmony = -sum(rankings.get(c_name, 0) * viols 
                          for c_name, viols in candidate.violations.items())
            if harmony > best_harmony:
                best_harmony = harmony
                best_candidate = candidate
        
        return best_candidate
    
    def _update_rankings(self, winner: Example, loser: Example):
        """Update ranking values: promote winner-preferring, demote loser-preferring."""
        for constraint in self.grammar.constraints:
            w_viols = winner.violations.get(constraint.name, 0)
            l_viols = loser.violations.get(constraint.name, 0)
            
            if l_viols > w_viols:
                # Promote (increase ranking)
                self.ranking_values[constraint.name] += self.plasticity
            elif w_viols > l_viols:
                # Demote (decrease ranking)
                self.ranking_values[constraint.name] -= self.plasticity
    
    def _rankings_to_partial_order(self) -> PartialOrder:
        """Convert continuous rankings to partial order."""
        partial_order = PartialOrder(self.grammar.constraints)
        
        # Sort constraints by ranking value
        sorted_constraints = sorted(self.grammar.constraints, 
                                   key=lambda c: self.ranking_values[c.name], 
                                   reverse=True)
        
        # Add dominance relations based on ranking values
        for i, c1 in enumerate(sorted_constraints):
            for c2 in sorted_constraints[i+1:]:
                if self.ranking_values[c1.name] > self.ranking_values[c2.name]:
                    partial_order.add_dominance(c1, c2)
        
        return partial_order
    
    def get_ranking_values(self) -> Dict[str, float]:
        """Get the learned continuous ranking values."""
        return self.ranking_values.copy()


class MaxEntLearner:
    """Maximum Entropy learning (Goldwater & Johnson 2003, Hayes & Wilson 2008)."""
    
    def __init__(self, grammar: Grammar, learning_rate: float = 0.1, 
                 max_iterations: int = 1000, tolerance: float = 0.001):
        self.grammar = grammar
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.weights = {c.name: 0.0 for c in grammar.constraints}
    
    def learn(self) -> PartialOrder:
        """
        Learn constraint weights using Maximum Entropy.
        
        Uses gradient ascent to maximize log-likelihood of observed data.
        """
        # Group examples by input
        input_groups = {}
        for ex in self.grammar.examples:
            if ex.input_form not in input_groups:
                input_groups[ex.input_form] = []
            input_groups[ex.input_form].append(ex)
        
        # Gradient ascent
        for iteration in range(self.max_iterations):
            old_weights = self.weights.copy()
            
            # Calculate gradients
            gradients = {c: 0.0 for c in self.weights}
            
            for input_form, candidates in input_groups.items():
                # Find observed frequencies (1 for optimal, 0 for others)
                observed = {ex: (1.0 if ex.optimal else 0.0) for ex in candidates}
                
                # Calculate expected frequencies under current model
                expected = self._expected_frequencies(candidates)
                
                # Update gradients: observed - expected
                for candidate in candidates:
                    obs_freq = observed[candidate]
                    exp_freq = expected[candidate]
                    
                    for c_name, viols in candidate.violations.items():
                        gradients[c_name] += (obs_freq - exp_freq) * viols
            
            # Update weights
            for c_name in self.weights:
                self.weights[c_name] -= self.learning_rate * gradients[c_name]
            
            # Check convergence
            diff = sum(abs(self.weights[c] - old_weights[c]) for c in self.weights)
            if diff < self.tolerance:
                break
        
        return self._weights_to_partial_order()
    
    def _expected_frequencies(self, candidates: List[Example]) -> Dict[Example, float]:
        """Calculate expected frequencies (probabilities) under current weights."""
        # Calculate un-normalized probabilities
        scores = {}
        for candidate in candidates:
            harmony = -sum(self.weights.get(c_name, 0.0) * viols 
                          for c_name, viols in candidate.violations.items())
            scores[candidate] = math.exp(harmony)
        
        # Normalize
        total = sum(scores.values())
        if total == 0:
            # Uniform distribution if all scores are 0
            return {c: 1.0/len(candidates) for c in candidates}
        
        return {c: scores[c]/total for c in candidates}
    
    def _weights_to_partial_order(self) -> PartialOrder:
        """Convert weights to partial order based on weight values."""
        partial_order = PartialOrder(self.grammar.constraints)
        
        # Sort constraints by weight
        sorted_constraints = sorted(self.grammar.constraints, 
                                   key=lambda c: self.weights[c.name], 
                                   reverse=True)
        
        # Add dominance relations
        for i, c1 in enumerate(sorted_constraints):
            for c2 in sorted_constraints[i+1:]:
                if self.weights[c1.name] > self.weights[c2.name]:
                    partial_order.add_dominance(c1, c2)
        
        return partial_order
    
    def get_weights(self) -> Dict[str, float]:
        """Get the learned constraint weights."""
        return self.weights.copy()
