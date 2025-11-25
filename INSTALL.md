# Installation Instructions for PyOptimal

## Method 1: Install with pip (Recommended)

This will install the `pyoptimal` command globally in your Python environment:

```bash
pip install -e ".[dev]"
```

After installation, you can run `pyoptimal` from anywhere:

```bash
pyoptimal examples/simple_ot.yaml
pyoptimal /path/to/any/grammar.yaml -a hg -v
```

## Method 2: Use the standalone script

If you don't want to install the package, you can use the `pyoptimal` script directly from the project root:

```bash
# From the project root directory
./pyoptimal examples/simple_ot.yaml
```

**Note**: The standalone script requires that dependencies (PyYAML, NumPy) are installed in your Python environment.

## Method 3: Add to PATH

To run the script from anywhere without pip installation:

### On macOS/Linux:

1. **Make sure dependencies are installed:**
   ```bash
   pip install pyyaml numpy
   ```

2. **Option A: Create a symlink in /usr/local/bin**
   ```bash
   sudo ln -s $(pwd)/pyoptimal /usr/local/bin/pyoptimal
   ```

3. **Option B: Add project root to PATH**
   
   Add this line to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`:
   ```bash
   export PATH="/Users/mortensen/Projects/pyoptimal:$PATH"
   ```
   
   Then reload your shell:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

### On Windows:

1. **Install dependencies:**
   ```cmd
   pip install pyyaml numpy
   ```

2. **Add to PATH:**
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", edit "Path"
   - Add: `C:\path\to\pyoptimal\project`

## Verifying Installation

Test that it works:

```bash
pyoptimal --help
pyoptimal examples/simple_ot.yaml -v
```

You should see the constraint ranking output.

## Troubleshooting

### "No module named 'pyoptimal'"
- Make sure you've installed the package with `pip install -e .`
- Or make sure you're running the script from the project root directory

### "No module named 'yaml'" or "No module named 'numpy'"
- Install dependencies: `pip install pyyaml numpy`
- Or install the full package: `pip install -e ".[dev]"`

### "command not found: pyoptimal"
- Make sure the script is executable: `chmod +x pyoptimal`
- Make sure the directory is in your PATH
- Or use the full path: `/path/to/pyoptimal/pyoptimal`

### Python version issues
- The package requires Python 3.8+
- Check your version: `python3 --version`
- Make sure the shebang points to a Python 3 interpreter: `head -1 pyoptimal`

## Development Setup

For development with all tools:

```bash
# Clone/navigate to project
cd pyoptimal

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Check types
mypy src/
```

## Uninstalling

If you installed with pip:
```bash
pip uninstall pyoptimal
```

If you created a symlink:
```bash
sudo rm /usr/local/bin/pyoptimal
```

If you added to PATH, remove the line from your shell configuration file.
