# Hermes Venv Python Path Reference

## Exact Paths (macOS)

```bash
# Python binary
~/.hermes/hermes-agent/venv/bin/python
# or fully qualified:
/Users/abdurrahmanjahfali/.hermes/hermes-agent/venv/bin/python

# pip
~/.hermes/hermes-agent/venv/bin/pip
```

## Why This Matters

System Python (`/usr/local/bin/python3`, v3.13) and Hermes venv Python (v3.11) have incompatible package versions. Installing packages with system `pip3` or running with system `python3` causes:

```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

## Always Use These Commands

```bash
# Install packages
~/.hermes/hermes-agent/venv/bin/pip install <package>

# Run scripts
~/.hermes/hermes-agent/venv/bin/python <script.py>

# One-liner tests
~/.hermes/hermes-agent/venv/bin/python -c "from supabase import create_client; print('OK')"
```

## Do NOT Use

- ❌ `python3` (system Python 3.13)
- ❌ `pip3` (system pip)
- ❌ `/usr/local/bin/python3`
- ❌ `/usr/local/bin/pip3`
