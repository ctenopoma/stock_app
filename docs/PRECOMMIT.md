# Pre-commit setup

Install pre-commit and enable hooks locally:

```bash
python -m pip install --user pre-commit
pre-commit install
pre-commit run --all-files
```

This repository uses: `black`, `ruff`, `prettier`, `eslint`, and basic whitespace hooks.
