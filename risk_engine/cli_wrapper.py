#!/usr/bin/env python3
"""
Enhanced CLI wrapper with authentication and dashboard.
"""

import sys
from pathlib import Path


def main():
    """Enhanced main entry point with auth and dashboard."""
    
    # Special commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "login":
            from risk_engine.auth import login_prompt
            success = login_prompt()
            return 0 if success else 1
        
        elif cmd == "register":
            from risk_engine.auth import register_prompt
            register_prompt()
            return 0
        
        elif cmd == "logout":
            from risk_engine.auth import AuthManager
            auth = AuthManager()
            auth.logout()
            print("\\n✅ Logged out successfully.")
            return 0
        
        elif cmd == "viewer":
            import argparse
            parser = argparse.ArgumentParser(description="View analysis results in web browser")
            parser.add_argument("-o", "--output-dir", required=True, help="Output directory to visualize")
            parser.add_argument("-p", "--port", type=int, default=8080, help="Port number (default: 8080)")
            args = parser.parse_args(sys.argv[2:])
            
            from risk_engine.web_viewer import start_web_viewer
            start_web_viewer(args.output_dir, args.port)
            return 0
        
        elif cmd in ("-h", "--help", "-v", "--version", "-i", "--input"):
            # Pass through to original CLI
            from risk_engine.cli.main import main as original_main
            return original_main()
    
    # No arguments = Dashboard mode
    if len(sys.argv) == 1:
        from risk_engine.auth import AuthManager
        auth = AuthManager()
        session = auth.get_current_session()
        
        if not session:
            print("\\n⚠️  You need to login first.")
            print("   Run: risk-engine login")
            print("   Or:  risk-engine register (for new users)\\n")
            return 1
        
        # Show dashboard
        from risk_engine.dashboard import Dashboard, show_history
        from risk_engine.cli.main import interactive_mode, generate_charts
        from risk_engine.engine import run_engine
        import json
        
        dashboard = Dashboard(session['email'])
        
        while True:
            choice = dashboard.show_menu()
            
            if choice == "1":
                # Run new analysis
                try:
                    config = interactive_mode()
                    
                    run_engine(
                        input_file=config["input_file"],
                        output_dir=config["output_dir"],
                        threshold=config["threshold"],
                        simulation=config["simulation"],
                        chunk_size=500_000,
                        quiet=False,
                        workers=config["workers"]
                    )
                    
                    if config["generate_graphs"]:
                        generate_charts(config["output_dir"], quiet=False)
                    
                    # Record in history
                    try:
                        summary_file = Path(config['output_dir']) / 'summary.json'
                        if summary_file.exists():
                            summary = json.loads(summary_file.read_text())
                            dashboard.add_analysis_record(
                                config['input_file'],
                                config['output_dir'],
                                summary.get('total_flagged', 0),
                                summary.get('total_transactions', 0)
                            )
                    except:
                        pass
                    
                    print("\\n" + "="*60)
                    print("  ✅ Analysis Complete!")
                    print("="*60)
                    
                    # Offer web viewer
                    view_choice = input("\\n🌐 Open results in web browser? [Y/n]: ").strip().lower()
                    if view_choice not in ('n', 'no'):
                        from risk_engine.web_viewer import start_web_viewer
                        print("\\nStarting web viewer...")
                        start_web_viewer(config["output_dir"])
                    
                except KeyboardInterrupt:
                    print("\\n\\nOperation cancelled.")
                except Exception as e:
                    print(f"\\n❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
                
                input("\\nPress Enter to return to dashboard...")
            
            elif choice == "2":
                show_history()
            
            elif choice == "3":
                # Web viewer
                print("\\n📂 Enter output directory to visualize:")
                recent = dashboard.get_recent_analyses(1)
                if recent:
                    default_dir = recent[0]['output_dir']
                    output_dir = input(f"   [{default_dir}]: ").strip() or default_dir
                else:
                    output_dir = input("   Path: ").strip()
                
                if output_dir and Path(output_dir).exists():
                    print("\\n🌐 Starting web viewer...")
                    from risk_engine.web_viewer import start_web_viewer
                    start_web_viewer(output_dir)
                else:
                    input("❌ Directory not found. Press Enter to continue...")
            
            elif choice == "4":
                auth.logout()
                print("\\n👋 Logged out successfully.\\n")
                return 0
            
            else:
                input("Invalid choice. Press Enter to continue...")
    
    # Pass through to original CLI for other cases
    from risk_engine.cli.main import main as original_main
    return original_main()


if __name__ == "__main__":
    sys.exit(main())
