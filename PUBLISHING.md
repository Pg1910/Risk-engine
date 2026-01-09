# Publishing to PyPI

This guide shows how to publish the `risk-engine` package to PyPI so users can install it with `pip install risk-engine`.

## Prerequisites

1. **Create PyPI accounts**:
   - Production: https://pypi.org/account/register/
   - Test (optional but recommended): https://test.pypi.org/account/register/

2. **Install build tools**:
   ```bash
   pip install --upgrade build twine
   ```

3. **Set up API tokens** (more secure than passwords):
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope for this project
   - Save the token securely (starts with `pypi-`)

## Publishing Steps

### 1. Update Version Number

Edit `pyproject.toml` and increment the version:
```toml
version = "1.0.1"  # Change this
```

### 2. Clean Previous Builds

```bash
cd risk_engine
rm -rf dist/ build/ *.egg-info
```

### 3. Build the Package

```bash
python -m build
```

This creates two files in `dist/`:
- `risk_engine-1.0.0.tar.gz` (source distribution)
- `risk_engine-1.0.0-py3-none-any.whl` (wheel distribution)

### 4. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps risk-engine
```

### 5. Upload to Production PyPI

```bash
python -m twine upload dist/*
```

Enter your PyPI username and API token when prompted (username is `__token__`, password is your API token).

### 6. Verify Installation

```bash
pip install risk-engine
risk-engine --help
```

## Using API Tokens

### Option 1: Interactive Upload
```bash
python -m twine upload dist/*
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

### Option 2: Configure .pypirc
Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Then simply run:
```bash
python -m twine upload dist/*
```

## Automated Publishing with GitHub Actions

See `.github/workflows/publish.yml` for automated publishing on GitHub releases.

To use it:
1. Add your PyPI API token to GitHub Secrets as `PYPI_API_TOKEN`
2. Create a new release on GitHub
3. The workflow automatically builds and publishes to PyPI

## Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Example: `1.0.0` → `1.0.1` (bug fix) → `1.1.0` (new feature) → `2.0.0` (breaking change)

## Checklist Before Publishing

- [ ] All tests pass
- [ ] README is up to date
- [ ] Version number incremented in `pyproject.toml`
- [ ] CHANGELOG updated (if you have one)
- [ ] Previous builds cleaned (`rm -rf dist/`)
- [ ] Tested on TestPyPI (optional)
- [ ] Git commit and tag created

## Troubleshooting

**"File already exists"**: You cannot re-upload the same version. Increment the version number and rebuild.

**"Invalid credentials"**: Make sure username is `__token__` and password is your full API token starting with `pypi-`.

**"Package name already taken"**: Choose a different name in `pyproject.toml` (e.g., `risk-engine-yourname`).

## Quick Reference

```bash
# Complete publishing workflow
cd risk_engine
rm -rf dist/ build/ *.egg-info
python -m build
python -m twine upload dist/*
```
