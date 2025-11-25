"""
Learning algorithms for constraint ranking.
"""

from typing import List, Dict, Set, Tuple, Optional
from .grammar import Grammar, Constraint
from .candidate import Candidate


class PartialOrder:
    """Represents a partial order over constraints."""
    
    def __init__(self, constraints: List[Constraint]):
        self.constraints = constraints
        self._dominance: Dict[Constraint, Set[Constraint]] = {c: set() for c in constraints}
    
    def add_dominance(self, higher: Constraint, lower: Constraint) -> None:
        """Add a dominance relation: higher >> lower."""
        self._dominance[higher].add(lower)
    
    def dominates(self, c1: Constraint, c2: Constraint) -> bool:
        """Check if c1 >> c2 (transitively)."""
        if c2 in self._dominance[c1]:
            return True
        for intermediate in self._dominance[c1]:
            if self.dominates(intermediate, c2):
                return True
        return False
    
    def get_strata(self) -> List[Set[Constraint]]:
        """Get stratified ranking (constraints at same level have no dominance relation)."""
        remaining = set(self.constraints)
        strata = []
        
        while remaining:
            current_stratum = set()
            for c in remaining:
                if not any(self.dominates(other, c) for other in remaining if other != c):
                    current_stratum.add(c)
            
            if not current_stratum:
                break
            
            strata.append(current_stratum)
            remaining -= current_stratum
        
        if remaining:
            strata.append(remaining)
        
        return strata
    
    def __str__(self) -> str:
        strata = self.get_strata()
        return " >> ".join([
            "{" + ", ".join(sorted(c.name for c in stratum)) + "}"
            if len(stratum) > 1 else list(stratum)[0].name
            for stratum in strata
        ])


class Learner:
    """Base class for constraint ranking learners."""
    
    def __init__(self, grammar: Grammar, algorithm: str = "ot"):
        self.grammar = grammar
        self.algorithm = algorithm.lower()
        self.partial_order: Optional[PartialOrder] = None
    
    def train(self) -> PartialOrder:
        """Train the learner on the grammar's examples."""
        if self.algorithm == "ot":
            return self._train_ot()
        elif self.algorithm == "hg":
            return self._train_hg()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
    
    def _train_ot(self) -> PartialOrder:
        """Train using Optimality Theory approach."""
        from .ot import OTLearner
        learner = OTLearner(self.grammar)
        self.partial_order = learner.learn()
        return self.partial_order
    
    def _train_hg(self) -> PartialOrder:
        """Train using Harmonic Grammar approach."""
        from .hg import HGLearner
        learner = HGLearner(self.grammar)
        self.partial_order = learner.learn()
        return self.partial_order
    
    def get_ranking(self) -> Optional[PartialOrder]:
        """Get the learned constraint ranking."""
        return self.partial_order
