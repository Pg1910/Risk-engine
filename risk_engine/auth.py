"""
Authentication and user management for Risk Engine.
Provides secure email-based authentication for authorized users.
"""

import os
import json
import hashlib
import getpass
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict


class AuthManager:
    """Manages user authentication and sessions."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.config_dir = Path.home() / ".risk_engine"
        self.config_dir.mkdir(exist_ok=True)
        self.users_file = self.config_dir / "users.json"
        self.session_file = self.config_dir / "session.json"
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist."""
        if not self.users_file.exists():
            self.users_file.write_text(json.dumps({}, indent=2))
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email: str, password: str, role: str = "analyst") -> bool:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            role: User role (analyst, admin)
        
        Returns:
            True if registration successful, False otherwise
        """
        users = self._load_users()
        
        if email in users:
            return False
        
        users[email] = {
            "password_hash": self._hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_users(users)
        return True
    
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email
            password: User's password
        
        Returns:
            True if authentication successful
        """
        users = self._load_users()
        
        if email not in users:
            return False
        
        user = users[email]
        password_hash = self._hash_password(password)
        
        if user["password_hash"] == password_hash:
            # Update last login
            user["last_login"] = datetime.now().isoformat()
            self._save_users(users)
            return True
        
        return False
    
    def create_session(self, email: str, duration_hours: int = 24):
        """
        Create a session for authenticated user.
        
        Args:
            email: User's email
            duration_hours: Session duration in hours
        """
        session = {
            "email": email,
            "login_time": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        }
        self.session_file.write_text(json.dumps(session, indent=2))
    
    def get_current_session(self) -> Optional[Dict]:
        """
        Get current active session.
        
        Returns:
            Session dict if valid, None otherwise
        """
        if not self.session_file.exists():
            return None
        
        try:
            session = json.loads(self.session_file.read_text())
            expires_at = datetime.fromisoformat(session["expires_at"])
            
            if datetime.now() < expires_at:
                return session
            else:
                # Session expired
                self.logout()
                return None
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def logout(self):
        """Logout current user by removing session."""
        if self.session_file.exists():
            self.session_file.unlink()
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.get_current_session() is not None
    
    def get_user_info(self, email: str) -> Optional[Dict]:
        """Get user information."""
        users = self._load_users()
        if email in users:
            user = users[email].copy()
            user.pop("password_hash", None)  # Don't return password hash
            return user
        return None
    
    def list_users(self) -> Dict:
        """List all registered users (without password hashes)."""
        users = self._load_users()
        result = {}
        for email, data in users.items():
            result[email] = {
                "role": data["role"],
                "created_at": data["created_at"],
                "last_login": data["last_login"]
            }
        return result
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            return json.loads(self.users_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file."""
        self.users_file.write_text(json.dumps(users, indent=2))


def login_prompt() -> bool:
    """
    Interactive login prompt.
    
    Returns:
        True if login successful
    """
    auth = AuthManager()
    
    print("\n" + "="*60)
    print("  🔐 Risk Engine - Authentication")
    print("="*60 + "\n")
    
    email = input("📧 Email: ").strip()
    password = getpass.getpass("🔑 Password: ")
    
    if auth.authenticate(email, password):
        auth.create_session(email)
        print(f"\n✅ Welcome back, {email}!")
        return True
    else:
        print("\n❌ Authentication failed. Invalid credentials.")
        return False


def register_prompt():
    """Interactive registration prompt."""
    auth = AuthManager()
    
    print("\n" + "="*60)
    print("  📝 Risk Engine - Register New User")
    print("="*60 + "\n")
    
    email = input("📧 Email: ").strip()
    
    if not email or "@" not in email:
        print("❌ Invalid email address.")
        return
    
    password = getpass.getpass("🔑 Password: ")
    password_confirm = getpass.getpass("🔑 Confirm Password: ")
    
    if password != password_confirm:
        print("❌ Passwords do not match.")
        return
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters.")
        return
    
    role = input("👤 Role [analyst/admin] (default: analyst): ").strip().lower() or "analyst"
    
    if role not in ["analyst", "admin"]:
        print("❌ Invalid role. Must be 'analyst' or 'admin'.")
        return
    
    if auth.register_user(email, password, role):
        print(f"\n✅ User {email} registered successfully!")
        print(f"   Role: {role}")
    else:
        print(f"\n❌ User {email} already exists.")
