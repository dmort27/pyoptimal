# PyOptimal

A Python tool for learning constraint rankings in Optimality Theory (OT) and Harmonic Grammar (HG).

## Overview

PyOptimal takes YAML files containing constraint systems and training examples, then generates a partial order over the constraints. This is useful for linguistic research in phonology and morphology where constraint-based grammars are used to model language patterns.

## Features

- **YAML-based input**: Define grammars and training data in human-readable YAML format
- **Optimality Theory support**: Learn constraint rankings for OT grammars
- **Harmonic Grammar support**: Learn constraint weights for HG grammars
- **Partial order output**: Generate constraint hierarchies that explain the training data
- **LaTeX tableau generation**: Automatically generate publication-ready tableaux using the tabularray package

## Installation

### From source

```bash
git clone <repository-url>
cd pyoptimal
pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

Basic usage:
```bash
pyoptimal input_grammar.yaml
```

With LaTeX tableau generation:
```bash
# Generate OT tableaux
pyoptimal examples/simple_ot.yaml --tableaux --tableaux-dir tableaux_output

# Generate HG tableaux with weights
pyoptimal examples/simple_hg.yaml -a hg --tableaux --tableaux-dir tableaux_output

# Generate compact tableaux without input column
pyoptimal examples/simple_ot.yaml --tableaux --no-input-column
```

### Python API

Learning constraint rankings:
```python
from pyoptimal import Grammar, Learner

# Load grammar from YAML
grammar = Grammar.from_yaml("grammar.yaml")

# Create learner
learner = Learner(grammar, algorithm="ot")

# Train on examples
learner.train()

# Get constraint ranking
ranking = learner.get_ranking()
print(ranking)
```

Generating LaTeX tableaux:
```python
from pyoptimal.grammar import Grammar
from pyoptimal.tableau import generate_tableaux_from_yaml, generate_tableaux_from_grammar
from pyoptimal.hg import HGLearner

# Generate OT tableaux
tableau_files = generate_tableaux_from_yaml(
    yaml_path="examples/simple_ot.yaml",
    output_dir="tableaux_output",
    algorithm="ot",
    include_input_column=True
)

# Generate HG tableaux with weights
grammar = Grammar.from_yaml("examples/simple_hg.yaml")
learner = HGLearner(grammar)
learner.learn()
weights = learner.get_weights()

tableau_files = generate_tableaux_from_grammar(
    grammar=grammar,
    output_dir="tableaux_output",
    algorithm="hg",
    weights=weights
)

# Compile the generated LaTeX files
# pdflatex tableaux_output/tableau_01_*.tex
# or use xelatex for better Unicode support:
# xelatex tableaux_output/tableau_01_*.tex
```

## YAML Format

### Grammar File Structure

```yaml
# Define constraints
constraints:
  - name: NOCODA
    description: "Syllables must not have codas"
  - name: MAX
    description: "Input segments must have output correspondents"
  - name: DEP
    description: "Output segments must have input correspondents"

# Define training examples
examples:
  - input: /pat/
    output: pa.ta
    optimal: true
  - input: /pat/
    output: pat
    optimal: false
```

## Project Structure

```
pyoptimal/
├── src/
│   └── pyoptimal/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── grammar.py          # Grammar and constraint definitions
│       ├── candidate.py        # Candidate representation
│       ├── learner.py          # Learning algorithms
│       ├── ot.py              # Optimality Theory specific code
│       ├── hg.py              # Harmonic Grammar specific code
│       ├── tableau.py         # LaTeX tableau generation
│       └── utils.py           # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_grammar.py
│   ├── test_learner.py
│   ├── test_tableau.py
│   └── fixtures/              # Test YAML files
├── examples/
│   ├── simple_ot.yaml
│   ├── simple_hg.yaml
│   └── tableau_example.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## Testing

```bash
pytest
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
