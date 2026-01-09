# Risk Engine v1.1.0 - New Features Summary

## What's Been Added

### 1. ✅ Email-Based Authentication System
**File**: [risk_engine/auth.py](risk_engine/auth.py)

- Secure user registration with email and password
- SHA-256 password hashing
- Session management (24-hour sessions)
- User roles (analyst/admin)
- Stored in `~/.risk_engine/users.json` and `~/.risk_engine/session.json`

**Commands:**
```bash
risk-engine register  # Create new account
risk-engine login     # Login to existing account
risk-engine logout    # End session
```

### 2. ✅ Interactive Terminal Dashboard
**File**: [risk_engine/dashboard.py](risk_engine/dashboard.py)

- Personal statistics tracking
- Recent analysis history (last 5)
- Analysis recording and metrics
- User-friendly menu interface

**Features:**
- Total analyses run
- Total transactions processed  
- Total flagged transactions
- Average flag rate per user
- Input/output tracking for each analysis

**Access:**
```bash
risk-engine  # After login
```

### 3. ✅ Web-Based Visualization Viewer
**File**: [risk_engine/web_viewer.py](risk_engine/web_viewer.py)

- Local web server for viewing results
- Beautiful responsive UI
- Summary statistics cards
- Image gallery of charts
- Flagged transactions table
- Auto-refresh every 30 seconds

**Launch:**
```bash
risk-engine viewer -o output_directory/
risk-engine viewer -o output_directory/ -p 9000  # Custom port
```

**Features:**
- Gradient background design
- Card-based layout
- Risk score distribution charts
- Anomaly reason breakdown charts
- Hourly distribution visualizations
- Top accounts analysis
- Amount distribution graphs

### 4. ✅ Enhanced CLI Wrapper
**File**: [risk_engine/cli_wrapper.py](risk_engine/cli_wrapper.py)

- Integrates authentication with existing CLI
- Dashboard mode when no arguments given
- Backwards compatible with old CLI commands
- Analysis history recording

**Entry Point Updated** in [pyproject.toml](pyproject.toml):
```toml
[project.scripts]
risk-engine = "risk_engine.cli_wrapper:main"
```

## File Structure

```
risk_engine/
├── auth.py              # NEW - Authentication system
├── dashboard.py         # NEW - Terminal dashboard
├── web_viewer.py        # NEW - Web visualization server
├── cli_wrapper.py       # NEW - Enhanced CLI entry point
├── cli/
│   └── main.py         # EXISTING - Original CLI (unchanged)
├── engine.py           # EXISTING - Core engine
├── rules.py            # EXISTING - Risk rules
├── stats.py            # EXISTING - Statistics
├── io.py               # EXISTING - I/O operations
└── utils.py            # EXISTING - Utilities
```

## User Data Storage

All user data stored in `~/.risk_engine/`:
```
~/.risk_engine/
├── users.json              # User credentials (passwords hashed)
├── session.json            # Current session (24hr expiry)
└── analysis_history.json   # Analysis records
```

## Usage Flow

### New User Flow:
1. `risk-engine register` → Create account
2. `risk-engine login` → Login
3. `risk-engine` → Access dashboard
4. Select "Run New Analysis" from menu
5. Complete analysis
6. View results in web browser (option 3)

### Returning User Flow:
1. `risk-engine` → Dashboard (auto-login if session valid)
2. View history and stats
3. Run analyses or view results

### Direct CLI Flow (No Login Required):
1. `risk-engine -i data.csv -o output/` → Direct analysis
2. `risk-engine viewer -o output/` → View results

## Documentation Files

- [README.md](README.md) - Updated with new features
- [AUTH_GUIDE.md](AUTH_GUIDE.md) - Complete authentication & dashboard guide
- [PUBLISHING.md](PUBLISHING.md) - PyPI publishing guide

## Version Updates

- **Version**: 1.0.0 → 1.1.0
- **Description**: Added "with authentication and dashboard"
- **Entry Point**: Changed to `cli_wrapper:main`

## PyPI Publishing

### Files Added for Distribution:
- [MANIFEST.in](MANIFEST.in) - Include README, LICENSE, pyproject.toml
- [.github/workflows/publish.yml](.github/workflows/publish.yml) - GitHub Actions workflow

### To Publish:
```bash
cd risk_engine
rm -rf dist/ build/ risk_engine.egg-info
python -m build
python -m twine upload dist/*
```

Or use GitHub release with trusted publishing.

## Testing

Install in development mode:
```bash
cd risk_engine
pip install -e .
```

Test commands:
```bash
risk-engine register
risk-engine login  
risk-engine
risk-engine -i test.csv -o out/
risk-engine viewer -o out/
```

## Backwards Compatibility

✅ All original CLI commands still work:
- `risk-engine -i file.csv -o out/`
- `risk-engine --threshold 5 --simulation on`
- `risk-engine --interactive`
- etc.

The new features are opt-in via the dashboard mode.

---

## Summary

You now have a complete, production-ready risk engine with:
- 🔐 Secure authentication
- 📊 Personal dashboard
- 🌐 Web visualizations  
- 📋 Analysis tracking
- 📦 PyPI publishing setup

Installation is now just: `pip install risk-engine`

Users can simply:
1. Register → Login → Analyze → Visualize
2. All from the terminal with beautiful web-based outputs!
