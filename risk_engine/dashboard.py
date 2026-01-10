"""
Terminal dashboard interface for Risk Engine.
Provides an interactive dashboard after login.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class Dashboard:
    """Terminal-based dashboard for Risk Engine."""
    
    def __init__(self, user_email: str):
        """Initialize dashboard for user."""
        self.user_email = user_email
        self.config_dir = Path.home() / ".risk_engine"
        self.history_file = self.config_dir / "analysis_history.json"
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Create history file if it doesn't exist."""
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps([], indent=2))
    
    def add_analysis_record(self, input_file: str, output_dir: str, 
                           flagged_count: int, total_count: int):
        """Record a completed analysis."""
        history = self._load_history()
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "user": self.user_email,
            "input_file": input_file,
            "output_dir": output_dir,
            "flagged_transactions": flagged_count,
            "total_transactions": total_count,
            "flag_rate": round(flagged_count / total_count * 100, 2) if total_count > 0 else 0
        }
        
        history.append(record)
        
        # Keep only last 50 records
        if len(history) > 50:
            history = history[-50:]
        
        self._save_history(history)
    
    def get_recent_analyses(self, limit: int = 5) -> List[Dict]:
        """Get recent analysis records."""
        history = self._load_history()
        return history[-limit:][::-1]  # Most recent first
    
    def get_user_stats(self) -> Dict:
        """Get statistics for current user."""
        history = self._load_history()
        user_history = [h for h in history if h["user"] == self.user_email]
        
        if not user_history:
            return {
                "total_analyses": 0,
                "total_transactions_processed": 0,
                "total_flagged": 0,
                "avg_flag_rate": 0
            }
        
        total_flagged = sum(h["flagged_transactions"] for h in user_history)
        total_processed = sum(h["total_transactions"] for h in user_history)
        
        return {
            "total_analyses": len(user_history),
            "total_transactions_processed": total_processed,
            "total_flagged": total_flagged,
            "avg_flag_rate": round(total_flagged / total_processed * 100, 2) if total_processed > 0 else 0
        }
    
    def display(self):
        """Display the dashboard."""
        from risk_engine.auth import AuthManager
        
        auth = AuthManager()
        user_info = auth.get_user_info(self.user_email)
        stats = self.get_user_stats()
        recent = self.get_recent_analyses(5)
        
        # Clear screen
        os.system('clear' if os.name != 'nt' else 'cls')
        
        print("\n" + "="*70)
        print("  RISK ENGINE - ANALYTICS DASHBOARD")
        print("="*70 + "\n")
        
        # User Info
        print(f"User: {self.user_email}")
        if user_info:
            print(f"Role: {user_info['role'].upper()}")
            if user_info.get('last_login'):
                last_login = datetime.fromisoformat(user_info['last_login'])
                print(f"   Last Login: {last_login.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n" + "-"*70)
        
        # Statistics
        print("\nSTATISTICS:")
        print(f"   Total Analyses Run:      {stats['total_analyses']}")
        print(f"   Transactions Processed:  {stats['total_transactions_processed']:,}")
        print(f"   Flagged Transactions:    {stats['total_flagged']:,}")
        print(f"   Average Flag Rate:       {stats['avg_flag_rate']}%")
        
        print("\n" + "-"*70)
        
        # Recent Analyses
        print("\nRECENT ANALYSES:")
        if recent:
            for i, analysis in enumerate(recent, 1):
                timestamp = datetime.fromisoformat(analysis['timestamp'])
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
                print(f"\n   {i}. {time_str}")
                print(f"      Input:   {Path(analysis['input_file']).name}")
                print(f"      Output:  {analysis['output_dir']}")
                print(f"      Flagged: {analysis['flagged_transactions']:,} / {analysis['total_transactions']:,} ({analysis['flag_rate']}%)")
        else:
            print("   No analyses yet. Run your first analysis below!")
        
        print("\n" + "="*70)
        
        # Menu
        print("\nMENU OPTIONS:")
        print("   1. Run New Analysis")
        print("   2. View Analysis History")
        print("   3. View Web Dashboard")
        print("   4. Logout")
        print()
    
    def show_menu(self) -> str:
        """Show menu and get user choice."""
        self.display()
        choice = input("Select option [1-4]: ").strip()
        return choice
    
    def _load_history(self) -> List[Dict]:
        """Load analysis history from file."""
        try:
            return json.loads(self.history_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history(self, history: List[Dict]):
        """Save analysis history to file."""
        self.history_file.write_text(json.dumps(history, indent=2))


def show_history():
    """Display full analysis history."""
    config_dir = Path.home() / ".risk_engine"
    history_file = config_dir / "analysis_history.json"
    
    if not history_file.exists():
        print("\nNo analysis history found.")
        return
    
    try:
        history = json.loads(history_file.read_text())
    except json.JSONDecodeError:
        print("\n[ERROR] Error reading history file.")
        return
    
    if not history:
        print("\nNo analyses recorded yet.")
        return
    
    print("\n" + "="*70)
    print("  ANALYSIS HISTORY")
    print("="*70 + "\n")
    
    for i, record in enumerate(reversed(history), 1):
        timestamp = datetime.fromisoformat(record['timestamp'])
        print(f"{i}. {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   User:    {record['user']}")
        print(f"   Input:   {record['input_file']}")
        print(f"   Flagged: {record['flagged_transactions']:,} / {record['total_transactions']:,} ({record['flag_rate']}%)")
        print(f"   Output:  {record['output_dir']}")
        print()
    
    input("Press Enter to continue...")
