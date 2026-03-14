"""
Email Configuration Manager

Supports multiple email delivery methods:
  1. Gmail (SMTP with app-specific password)
  2. Corporate/Domain SMTP 
  3. Local testing (saves to file)
"""

import os
import json
from typing import Optional, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SMTPConfig:
    """SMTP Configuration"""
    server: str
    port: int
    use_tls: bool = True
    username: Optional[str] = None
    password: Optional[str] = None
    from_email: str = "piddy@autonomous.local"
    
    def is_configured(self) -> bool:
        """Check if SMTP credentials are set"""
        if self.server == "localhost":
            return True
        return bool(self.username and self.password)


class EmailConfigManager:
    """Manages email configuration across multiple services"""
    
    CONFIG_FILE = Path("config/email_config.json")
    
    # Predefined SMTP profiles
    PROFILES = {
        "gmail": {
            "server": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "description": "Gmail with app-specific password",
            "setup_instructions": """
    1. Enable 2-Factor Authentication on your Google Account
    2. Go to https://myaccount.google.com/apppasswords
    3. Select Mail and Windows Computer
    4. Copy the generated 16-character password
    5. Use that password (without spaces) in config
            """
        },
        "ghostai": {
            "server": "mail.ghostai.solutions",  # Example domain
            "port": 587,
            "use_tls": True,
            "description": "GhostAI corporate email",
            "setup_instructions": "Contact IT for SMTP credentials"
        },
        "localhost": {
            "server": "localhost",
            "port": 1025,
            "use_tls": False,
            "description": "Local testing (saves emails to file)",
            "setup_instructions": "Run: python -m smtpd -n -c DebuggingServer localhost:1025"
        }
    }
    
    @classmethod
    def get_default_config(cls) -> SMTPConfig:
        """Get default localhost config"""
        return SMTPConfig(
            server="localhost",
            port=1025,
            use_tls=False,
            from_email="piddy@autonomous.local"
        )
    
    @classmethod
    def create_config_file(cls, profile: str, username: Optional[str] = None, 
                          password: Optional[str] = None) -> Dict:
        """Create email configuration file from preset profile"""
        
        if profile not in cls.PROFILES:
            return {
                "error": f"Unknown profile: {profile}",
                "available_profiles": list(cls.PROFILES.keys())
            }
        
        profile_config = cls.PROFILES[profile].copy()
        
        if profile != "localhost":
            if not username:
                return {
                    "error": f"Profile '{profile}' requires username",
                    "setup_instructions": profile_config.get("setup_instructions", "")
                }
            if not password:
                return {
                    "error": f"Profile '{profile}' requires password",
                    "setup_instructions": profile_config.get("setup_instructions", "")
                }
            profile_config["username"] = username
            profile_config["password"] = password
        
        # Create config directory
        cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "profile": profile,
            "smtp": {
                "server": profile_config["server"],
                "port": profile_config["port"],
                "use_tls": profile_config["use_tls"],
                "username": profile_config.get("username"),
                "password": profile_config.get("password"),
                "from_email": "piddy@autonomous.local"
            },
            "recipients": {
                "primary": "stephen.burch@ghostai.solutions",
                "secondary": "burchsl4@gmail.com"
            }
        }
        
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {"success": True, "config_file": str(cls.CONFIG_FILE)}
    
    @classmethod
    def load_config(cls) -> SMTPConfig:
        """Load email configuration from file or return default"""
        
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
                    smtp = config_data.get("smtp", {})
                    return SMTPConfig(
                        server=smtp.get("server", "localhost"),
                        port=smtp.get("port", 1025),
                        use_tls=smtp.get("use_tls", False),
                        username=smtp.get("username"),
                        password=smtp.get("password"),
                        from_email=smtp.get("from_email", "piddy@autonomous.local")
                    )
            except Exception as e:
                print(f"Error loading email config: {e}")
        
        return cls.get_default_config()
    
    @classmethod
    def print_setup_guide(cls):
        """Print setup guide for email configuration"""
        print("""
╔════════════════════════════════════════════════════════════════════╗
║         PIDDY EMAIL CONFIGURATION SETUP GUIDE                      ║
╚════════════════════════════════════════════════════════════════════╝

Choose your email delivery method:

1️⃣  GMAIL (Recommended for quick setup)
   - Set up app-specific password
   - Command: python src/email_config.py --profile gmail --username your.email@gmail.com --password APP_PASSWORD
   - Instructions: https://myaccount.google.com/apppasswords

2️⃣  GHOSTAI CORPORATE EMAIL
   - Use your corporate SMTP settings
   - Command: python src/email_config.py --profile ghostai --username your.email@ghostai.solutions --password YOUR_PASSWORD
   - Contact IT for credentials

3️⃣  LOCALHOST (Testing only - saves emails to file)
   - No credentials needed
   - Command: python src/email_config.py --profile localhost
   - Emails saved to: data/email_notifications/

CURRENT STATUS:
   Config file: {config_file}
   Exists: {exists}
   Using: {profile}

NEXT STEPS:
   1. Choose a profile above
   2. Run the configuration command
   3. Start the background service
   4. Check your email for approval requests!
        """.format(
            config_file=cls.CONFIG_FILE,
            exists="✅ Yes" if cls.CONFIG_FILE.exists() else "❌ Not yet",
            profile="Localhost (demo mode)" if not cls.CONFIG_FILE.exists() else "Configured"
        ))


def main():
    """CLI for email configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Configure PIDDY email settings")
    parser.add_argument("--profile", choices=["gmail", "ghostai", "localhost"], 
                       help="Email provider profile")
    parser.add_argument("--username", help="Email address or username")
    parser.add_argument("--password", help="App password or password")
    parser.add_argument("--show", action="store_true", help="Show current config")
    parser.add_argument("--help-setup", action="store_true", help="Show setup guide")
    
    args = parser.parse_args()
    
    if args.help_setup:
        EmailConfigManager.print_setup_guide()
        return
    
    if args.show:
        if EmailConfigManager.CONFIG_FILE.exists():
            with open(EmailConfigManager.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print("\n📧 Current Email Configuration:")
                print(f"   Profile: {config.get('profile', 'custom')}")
                print(f"   Server: {config['smtp']['server']}")
                print(f"   Port: {config['smtp']['port']}")
                print(f"   Primary: {config['recipients']['primary']}")
                print(f"   Secondary: {config['recipients']['secondary']}")
        else:
            print("❌ No email configuration file found")
            print("   Run: python src/email_config.py --help-setup")
        return
    
    if args.profile:
        result = EmailConfigManager.create_config_file(
            args.profile,
            args.username,
            args.password
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "setup_instructions" in result:
                print(f"\nℹ️  {result['setup_instructions']}")
        elif "success" in result and result["success"]:
            print(f"✅ Configuration saved to: {result['config_file']}")
            print("\n📧 Email Configuration Complete!")
            print(f"   Profile: {args.profile}")
            if args.profile != "localhost":
                print(f"   Sender: piddy@autonomous.local")
                print(f"   Via: {EmailConfigManager.PROFILES[args.profile]['server']}")
            print("\n🚀 Next steps:")
            print("   1. Start background service: python src/autonomous_background_service.py")
            print("   2. Watch for approval requests in your email")
            print("   3. Open dashboard: http://localhost:8000")
    else:
        EmailConfigManager.print_setup_guide()


if __name__ == "__main__":
    main()
