"""
Grammar and constraint definitions for OT/HG.
"""

from typing import List, Dict, Any, Optional
import yaml


class Constraint:
    """Represents a single constraint in the grammar."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __repr__(self) -> str:
        return f"Constraint(name='{self.name}')"
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constraint):
            return NotImplemented
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class Example:
    """Represents a training example with input, output, and optimality judgment."""
    
    def __init__(
        self,
        input_form: str,
        output_form: str,
        optimal: bool,
        violations: Optional[Dict[str, int]] = None
    ):
        self.input_form = input_form
        self.output_form = output_form
        self.optimal = optimal
        self.violations = violations or {}
    
    def __repr__(self) -> str:
        return f"Example(input='{self.input_form}', output='{self.output_form}', optimal={self.optimal})"


class Grammar:
    """Represents a constraint-based grammar with training examples."""
    
    def __init__(self, constraints: List[Constraint], examples: Optional[List[Example]] = None):
        self.constraints = constraints
        self.examples = examples or []
        self._constraint_map = {c.name: c for c in constraints}
    
    def get_constraint(self, name: str) -> Optional[Constraint]:
        """Get a constraint by name."""
        return self._constraint_map.get(name)
    
    def add_example(self, example: Example) -> None:
        """Add a training example to the grammar."""
        self.examples.append(example)
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "Grammar":
        """Load grammar from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        constraints = []
        for c_data in data.get('constraints', []):
            constraint = Constraint(
                name=c_data['name'],
                description=c_data.get('description', '')
            )
            constraints.append(constraint)
        
        examples = []
        for e_data in data.get('examples', []):
            example = Example(
                input_form=e_data['input'],
                output_form=e_data['output'],
                optimal=e_data.get('optimal', False),
                violations=e_data.get('violations', {})
            )
            examples.append(example)
        
        return cls(constraints=constraints, examples=examples)
    
    def to_yaml(self, filepath: str) -> None:
        """Save grammar to a YAML file."""
        data = {
            'constraints': [
                {
                    'name': c.name,
                    'description': c.description
                }
                for c in self.constraints
            ],
            'examples': [
                {
                    'input': e.input_form,
                    'output': e.output_form,
                    'optimal': e.optimal,
                    'violations': e.violations
                }
                for e in self.examples
            ]
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def __repr__(self) -> str:
        return f"Grammar(constraints={len(self.constraints)}, examples={len(self.examples)})"
