# PyOptimal - Project Summary

## ✅ Complete Python Package Created

A fully functional Python package for learning constraint rankings in Optimality Theory (OT) and Harmonic Grammar (HG) from YAML input files.

## 📦 What's Included

### Core Modules (src/pyoptimal/)
- `grammar.py` - Grammar, Constraint, and Example classes with YAML I/O
- `candidate.py` - Candidate representation with violation profiles
- `learner.py` - Main learner interface and PartialOrder class
- `ot.py` - Optimality Theory learning algorithm (constraint demotion)
- `hg.py` - Harmonic Grammar learning algorithm (gradual learning)
- `utils.py` - Utility functions (graph algorithms)
- `cli.py` - Command-line interface

### Test Suite (tests/)
- 16 unit tests covering all major functionality
- All tests passing ✓
- 67% code coverage

### Examples (examples/)
- `simple_ot.yaml` - Basic OT syllable structure
- `simple_hg.yaml` - Basic HG example
- `complex_ot.yaml` - Voicing + syllable structure
- `api_example.py` - Working Python API examples

### Documentation
- `README.md` - Full project documentation
- `QUICKSTART.md` - Quick reference guide
- `LICENSE` - MIT License
- `pyproject.toml` - Modern Python package configuration

## 🚀 Quick Usage

### Command Line
```bash
# Learn OT ranking
pyoptimal examples/simple_ot.yaml -v

# Learn HG weights
pyoptimal examples/simple_hg.yaml -a hg -v
```

### Python API
```python
from pyoptimal import Grammar, Learner

grammar = Grammar.from_yaml("grammar.yaml")
learner = Learner(grammar, algorithm="ot")
ranking = learner.train()
print(ranking)  # Shows: {CONSTRAINT1, CONSTRAINT2} >> CONSTRAINT3
```

## ✨ Key Features

1. **Dual Algorithm Support** - Both OT and HG learning
2. **YAML Input** - Human-readable grammar format
3. **Partial Orders** - Handles unranked constraints
4. **Flexible APIs** - CLI and Python interfaces
5. **Well-Tested** - Comprehensive test suite
6. **Documented** - README, QUICKSTART, and code examples

## 📊 Verification

All components tested and working:
- ✓ YAML loading and saving
- ✓ OT constraint demotion
- ✓ HG weight learning
- ✓ Partial order generation
- ✓ CLI interface
- ✓ Example files run successfully

## 📝 Example Output

```
$ pyoptimal examples/simple_ot.yaml -v
Loading grammar from examples/simple_ot.yaml...
Grammar loaded: 3 constraints, 5 examples
Training using OT algorithm...

Learned constraint ranking:
{MAX, NOCODA} >> DEP
```

## 🔧 Installation

The package is already installed. To reinstall or install elsewhere:

```bash
pip install -e ".[dev]"
```

## 📚 Next Steps

1. Modify example YAML files for your own grammars
2. Run tests: `pytest`
3. Format code: `black src/ tests/`
4. Extend algorithms in `ot.py` or `hg.py`

---

**Status**: ✅ Complete and ready to use!
