"""
Candidate representation for OT/HG evaluation.
"""

from typing import Dict


class Candidate:
    """Represents a candidate output with constraint violations."""
    
    def __init__(self, input_form: str, output_form: str, violations: Dict[str, int]):
        self.input_form = input_form
        self.output_form = output_form
        self.violations = violations
    
    def get_violation(self, constraint_name: str) -> int:
        """Get the number of violations for a specific constraint."""
        return self.violations.get(constraint_name, 0)
    
    def __repr__(self) -> str:
        return f"Candidate(input='{self.input_form}', output='{self.output_form}', violations={self.violations})"
    
    def __str__(self) -> str:
        return f"{self.input_form} → {self.output_form}"
