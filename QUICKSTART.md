# PyOptimal Quick Start Guide

## Installation

The package is already installed in editable mode. If you need to reinstall:

```bash
pip install -e ".[dev]"
```

## Running Examples

### Optimality Theory (OT)

```bash
pyoptimal examples/simple_ot.yaml -v
```

This will learn a constraint ranking like: `{MAX, NOCODA} >> DEP`

### Harmonic Grammar (HG)

```bash
pyoptimal examples/simple_hg.yaml -a hg -v
```

This will learn constraint weights and show the resulting ranking.

### Complex Example

```bash
pyoptimal examples/complex_ot.yaml -v
```

## Using the Python API

```python
from pyoptimal import Grammar, Learner

# Load grammar from YAML
grammar = Grammar.from_yaml("examples/simple_ot.yaml")

# Create and train learner
learner = Learner(grammar, algorithm="ot")
ranking = learner.train()

# Display ranking
print(f"Learned ranking: {ranking}")
```

## Creating Your Own Grammar Files

Create a YAML file with the following structure:

```yaml
constraints:
  - name: CONSTRAINT_NAME
    description: "Description of the constraint"
  - name: ANOTHER_CONSTRAINT
    description: "Another description"

examples:
  - input: /underlying_form/
    output: surface_form
    optimal: true
    violations:
      CONSTRAINT_NAME: 0
      ANOTHER_CONSTRAINT: 1
  
  - input: /underlying_form/
    output: alternative_form
    optimal: false
    violations:
      CONSTRAINT_NAME: 1
      ANOTHER_CONSTRAINT: 0
```

### Important Notes:

1. **Violations**: You must specify the number of violations for each constraint for each candidate
2. **Optimal**: Mark the winning candidate as `optimal: true`, others as `optimal: false`
3. **Input grouping**: Include multiple candidates for the same input to establish rankings

## Running Tests

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=pyoptimal --cov-report=term-missing
```

## Code Formatting

Format code with Black:

```bash
black src/ tests/
```

Check style with flake8:

```bash
flake8 src/ tests/
```

## Understanding the Output

### OT Rankings

The output shows a partial order using `>>` for dominance:
- `A >> B` means constraint A dominates constraint B
- `{A, B} >> C` means A and B are unranked relative to each other, but both dominate C

### HG Weights

For Harmonic Grammar, the output shows:
1. The partial order (derived from weights)
2. The actual numerical weights learned for each constraint

Higher weights mean more important constraints.

## Project Structure

```
pyoptimal/
├── src/pyoptimal/      # Main source code
│   ├── grammar.py      # Grammar and constraint definitions
│   ├── candidate.py    # Candidate representation
│   ├── learner.py      # Main learning interface
│   ├── ot.py          # OT-specific algorithms
│   ├── hg.py          # HG-specific algorithms
│   ├── utils.py       # Utility functions
│   └── cli.py         # Command-line interface
├── tests/             # Test suite
├── examples/          # Example grammar files
└── pyproject.toml     # Project configuration
```

## Next Steps

1. Modify the example YAML files to experiment with different grammars
2. Add your own linguistic data and constraints
3. Explore the Python API for programmatic access
4. Extend the learners with additional algorithms as needed

## Algorithms Implemented

### Optimality Theory (OT)
- Based on constraint demotion (Tesar & Smolensky)
- Learns strict dominance hierarchies
- Works well with categorical data

### Harmonic Grammar (HG)
- Based on gradual learning algorithm (Boersma)
- Learns numerical weights
- Can model gradient patterns

## Common Issues

### All constraints unranked
This may happen if your examples don't provide enough contrasts. Make sure you include:
- Multiple candidates for each input
- Clear winners and losers
- Violations that differ between candidates

### Learning doesn't converge (HG)
Try adjusting the learning rate when creating the HGLearner programmatically:

```python
from pyoptimal.hg import HGLearner

learner = HGLearner(grammar, learning_rate=0.01)
ranking = learner.learn()
```
