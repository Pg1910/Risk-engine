# Risk Engine - Authentication & Dashboard Guide

## New Features

The Risk Engine now includes:
- 🔐 **Email-based authentication** - Secure user login system
- 📊 **Interactive dashboard** - Terminal-based UI showing your analysis history and stats  
- 🌐 **Web visualization viewer** - Beautiful web interface to view charts and results
- 📋 **Analysis history tracking** - Keep track of all your analyses

## Quick Start

### 1. Register a New User

```bash
risk-engine register
```

You'll be prompted for:
- Email address
- Password (min 6 characters)
- Role (analyst or admin)

### 2. Login

```bash
risk-engine login
```

Enter your email and password. Sessions last for 24 hours.

### 3. Use the Dashboard

Once logged in, just run:

```bash
risk-engine
```

This launches the interactive dashboard where you can:
- **Run New Analysis** - Process transaction files
- **View History** - See all your past analyses
- **Open Web Viewer** - Visualize results in your browser
- **Logout** - End your session

## Command Reference

| Command | Description |
|---------|-------------|
| `risk-engine` | Launch dashboard (requires login) |
| `risk-engine login` | Login to your account |
| `risk-engine register` | Register new user |
| `risk-engine logout` | Logout current user |
| `risk-engine -i file.csv -o out/` | Run analysis (bypasses dashboard) |
| `risk-engine viewer -o out/` | Open web viewer for results |
| `risk-engine --help` | Show all CLI options |

## Dashboard Features

### Statistics Tracking
The dashboard shows:
- Total analyses run
- Total transactions processed
- Total flagged transactions
- Average flag rate

### Recent Analyses
View your 5 most recent analyses with:
- Timestamp
- Input/output files
- Flagged transaction counts
- Flag rates

### Web Viewer
Launch a local web server to view:
- **Summary statistics** - Key metrics from your analysis
- **Visual charts** - Risk score distributions, anomaly reasons, etc.
- **Flagged transactions table** - Browse suspicious transactions
- **Auto-refresh** - Data updates every 30 seconds

## Web Viewer

The web viewer provides a beautiful interface to visualize your results:

```bash
# From dashboard (option 3)
risk-engine
> 3

# Or directly
risk-engine viewer -o risk_engine_output/
```

Features:
- Responsive design
- Summary cards with key stats
- Image gallery of all generated charts
- Table of flagged transactions
- Runs on `http://localhost:8080` by default

## Authentication Details

### User Data Storage
All user data is stored securely in:
```
~/.risk_engine/
├── users.json           # User credentials (passwords are hashed)
├── session.json         # Current session info
└── analysis_history.json # Analysis records
```

### Security
- Passwords are hashed using SHA-256
- Sessions expire after 24 hours
- No plaintext passwords are stored

### Roles
- **analyst**: Standard user (default)
- **admin**: Admin privileges (for future features)

## Workflow Example

```bash
# First time setup
risk-engine register
# Email: analyst@bank.com
# Password: ******
# Role: analyst

# Login
risk-engine login
# Email: analyst@bank.com
# Password: ******

# Use dashboard
risk-engine
# Choose option 1 to run analysis
# Choose option 3 to view in browser
# Choose option 4 to logout
```

## Tips

💡 **Tip 1**: Sessions persist across terminal sessions, so you don't need to login every time.

💡 **Tip 2**: The web viewer automatically opens in your default browser.

💡 **Tip 3**: You can still use the old CLI commands (e.g., `risk-engine -i file.csv`) without logging in.

💡 **Tip 4**: Analysis history is shared across all users on the same machine.

## Troubleshooting

**"You need to login first"**
- Run `risk-engine login` first
- Or register with `risk-engine register` if you're a new user

**Web viewer port already in use**
- Use a different port: `risk-engine viewer -o out/ -p 8081`

**Can't find analysis history**
- Check `~/.risk_engine/analysis_history.json` exists
- Run at least one analysis to populate history

## Advanced Usage

### Custom Port for Web Viewer
```bash
risk-engine viewer -o results/ -p 9000
```

### Session Management
```bash
# Check if logged in (no output if not logged in)
ls ~/.risk_engine/session.json

# Force logout
risk-engine logout

# Or manually delete session
rm ~/.risk_engine/session.json
```

### Multi-User Setup
Each user should:
1. Register their own account
2. Login with their credentials  
3. Their analyses are tracked separately in the dashboard

---

**Need Help?** Check the main [README.md](README.md) for analysis options and configuration details.
