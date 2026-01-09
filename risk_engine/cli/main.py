#!/usr/bin/env python3
"""
Command-line interface for the Risk Engine.

Usage:
    risk-engine                    # Dashboard mode (after login)
    risk-engine login              # Login to your account
    risk-engine register           # Register new user
    risk-engine -i data.csv        # Quick analysis mode
    risk-engine viewer -o out/     # View results in web browser
"""

import argparse
import os
import sys
import glob
from pathlib import Path

from risk_engine import __version__


def find_csv_files(directory: str = ".") -> list:
    """Find all CSV files in the given directory."""
    patterns = ["*.csv", "*.CSV"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(directory, pattern)))
    return sorted(files)


def interactive_mode() -> dict:
    """Run interactive prompts to gather user input."""
    print("\n" + "="*60)
    print("  🏦 Risk Engine - Transaction Anomaly Detection")
    print("="*60 + "\n")
    
    # Find CSV files
    csv_files = find_csv_files()
    
    # Input file selection
    if csv_files:
        print("📁 Found CSV files in current directory:")
        for i, f in enumerate(csv_files, 1):
            size_mb = os.path.getsize(f) / (1024 * 1024)
            print(f"   {i}. {os.path.basename(f)} ({size_mb:.1f} MB)")
        print(f"   {len(csv_files) + 1}. Enter custom path")
        print()
        
        while True:
            choice = input(f"Select file [1-{len(csv_files) + 1}]: ").strip()
            try:
                idx = int(choice)
                if 1 <= idx <= len(csv_files):
                    input_file = csv_files[idx - 1]
                    break
                elif idx == len(csv_files) + 1:
                    input_file = input("Enter full path to CSV file: ").strip()
                    break
            except ValueError:
                pass
            print("Invalid selection. Try again.")
    else:
        input_file = input("📁 Enter path to CSV file: ").strip()
    
    if not os.path.isfile(input_file):
        print(f"\n❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    print(f"\n✅ Selected: {input_file}")
    
    # Output directory
    default_output = "risk_engine_output"
    output_dir = input(f"\n📂 Output directory [{default_output}]: ").strip() or default_output
    print(f"   → Outputs will be saved to: {os.path.abspath(output_dir)}/")
    
    # Threshold
    print("\n🎯 Threshold Configuration")
    print("   Higher threshold = fewer flags, stricter detection")
    print("   Lower threshold = more flags, catches more edge cases")
    print("   Recommended: 4 (balanced)")
    
    while True:
        threshold_input = input("   Threshold [4]: ").strip() or "4"
        try:
            threshold = int(threshold_input)
            if 1 <= threshold <= 6:
                break
            print("   Please enter a number between 1 and 6.")
        except ValueError:
            print("   Invalid input. Enter a number.")
    
    # Simulation mode
    print("\n⚡ Velocity Simulation")
    print("   Detects rapid-fire transactions (multiple txns in short time)")
    sim_choice = input("   Enable simulation? [y/N]: ").strip().lower()
    simulation = sim_choice in ("y", "yes", "1", "true")
    print(f"   → Simulation: {'ON' if simulation else 'OFF'}")
    
    # Graphs
    print("\n📊 Visual Reports")
    graphs_choice = input("   Generate chart images? [Y/n]: ").strip().lower()
    generate_graphs = graphs_choice not in ("n", "no", "0", "false")
    print(f"   → Charts: {'ON' if generate_graphs else 'OFF'}")
    
    # Parallel processing
    import multiprocessing
    max_cores = multiprocessing.cpu_count()
    print(f"\n🚀 Parallel Processing")
    print(f"   Available CPU cores: {max_cores}")
    workers_choice = input(f"   Cores to use [{max_cores}]: ").strip() or str(max_cores)
    try:
        workers = min(max(1, int(workers_choice)), max_cores)
    except ValueError:
        workers = max_cores
    print(f"   → Using {workers} cores")
    
    print("\n" + "-"*60)
    print("Starting analysis...\n")
    
    return {
        "input_file": input_file,
        "output_dir": output_dir,
        "threshold": threshold,
        "simulation": simulation,
        "generate_graphs": generate_graphs,
        "workers": workers,
    }


def generate_charts(output_dir: str, quiet: bool = False):
    """Generate visualization charts from the processed data."""
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from collections import Counter
    
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    # Load flagged data
    flagged_file = os.path.join(output_dir, "flagged_transactions.csv")
    if not os.path.exists(flagged_file):
        return
    
    try:
        df = pd.read_csv(flagged_file)
    except Exception:
        return
    
    if not quiet:
        print("[INFO] Generating charts...")
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Chart 1: Anomaly Reasons Breakdown
    try:
        if "final_reasons" in df.columns:
            # Parse the reasons column (semicolon-separated or list)
            import ast
            all_reasons = []
            for reasons_str in df["final_reasons"].dropna():
                try:
                    if isinstance(reasons_str, str):
                        # Try semicolon-separated first (from CSV export)
                        if "; " in reasons_str:
                            reasons = [r.strip() for r in reasons_str.split("; ") if r.strip()]
                        else:
                            # Try parsing as Python list
                            try:
                                reasons = ast.literal_eval(reasons_str)
                            except:
                                reasons = [reasons_str]
                    elif isinstance(reasons_str, list):
                        reasons = reasons_str
                    else:
                        reasons = [str(reasons_str)]
                    all_reasons.extend(reasons)
                except:
                    pass
            
            if all_reasons:
                reason_counts = Counter(all_reasons)
                fig, ax = plt.subplots(figsize=(10, 6))
                reasons = list(reason_counts.keys())
                counts = list(reason_counts.values())
                colors = plt.cm.Reds([0.3 + 0.1*i for i in range(len(reasons))])
                bars = ax.barh(reasons, counts, color=colors)
                ax.set_xlabel('Count', fontsize=12)
                ax.set_title('Anomaly Reason Breakdown', fontsize=14, fontweight='bold')
                ax.bar_label(bars, padding=3)
                plt.tight_layout()
                plt.savefig(os.path.join(charts_dir, "01_anomaly_reasons.png"), dpi=150)
                plt.close()
    except Exception as e:
        if not quiet:
            print(f"[WARN] Could not generate reasons chart: {e}")
    
    # Chart 2: Risk Score Distribution
    try:
        if "final_risk_score" in df.columns:
            fig, ax = plt.subplots(figsize=(8, 6))
            score_counts = df["final_risk_score"].value_counts().sort_index()
            colors = ['#2ecc71' if s < 3 else '#f39c12' if s < 5 else '#e74c3c' for s in score_counts.index]
            bars = ax.bar(score_counts.index.astype(str), score_counts.values, color=colors)
            ax.set_xlabel('Risk Score', fontsize=12)
            ax.set_ylabel('Number of Transactions', fontsize=12)
            ax.set_title('Risk Score Distribution', fontsize=14, fontweight='bold')
            ax.bar_label(bars, padding=3)
            plt.tight_layout()
            plt.savefig(os.path.join(charts_dir, "02_risk_scores.png"), dpi=150)
            plt.close()
    except Exception as e:
        if not quiet:
            print(f"[WARN] Could not generate risk score chart: {e}")
    
    # Chart 3: Hourly Distribution
    try:
        if "hour" in df.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            hourly = df.groupby("hour").size()
            ax.fill_between(hourly.index, hourly.values, alpha=0.3, color='steelblue')
            ax.plot(hourly.index, hourly.values, 'o-', color='steelblue', linewidth=2)
            ax.set_xlabel('Hour of Day', fontsize=12)
            ax.set_ylabel('Number of Anomalies', fontsize=12)
            ax.set_title('Anomalies by Hour of Day', fontsize=14, fontweight='bold')
            ax.set_xticks(range(0, 24, 2))
            plt.tight_layout()
            plt.savefig(os.path.join(charts_dir, "03_hourly_distribution.png"), dpi=150)
            plt.close()
    except Exception as e:
        if not quiet:
            print(f"[WARN] Could not generate hourly chart: {e}")
    
    # Chart 4: Top Accounts
    try:
        if "sender_account" in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_accounts = df.groupby("sender_account").size().sort_values(ascending=True).tail(10)
            colors = plt.cm.Blues([0.4 + 0.06*i for i in range(len(top_accounts))])
            bars = ax.barh(top_accounts.index, top_accounts.values, color=colors)
            ax.set_xlabel('Number of Anomalies', fontsize=12)
            ax.set_title('Top 10 Accounts by Anomaly Count', fontsize=14, fontweight='bold')
            ax.bar_label(bars, padding=3)
            plt.tight_layout()
            plt.savefig(os.path.join(charts_dir, "04_top_accounts.png"), dpi=150)
            plt.close()
    except Exception as e:
        if not quiet:
            print(f"[WARN] Could not generate top accounts chart: {e}")
    
    # Chart 5: Amount Distribution (if available)
    try:
        if "amount" in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            amounts = df["amount"].dropna()
            if len(amounts) > 0:
                ax.hist(amounts, bins=30, color='coral', edgecolor='white', alpha=0.7)
                ax.axvline(amounts.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {amounts.mean():,.0f}')
                ax.axvline(amounts.median(), color='blue', linestyle='--', linewidth=2, label=f'Median: {amounts.median():,.0f}')
                ax.set_xlabel('Transaction Amount', fontsize=12)
                ax.set_ylabel('Frequency', fontsize=12)
                ax.set_title('Anomalous Transaction Amounts', fontsize=14, fontweight='bold')
                ax.legend()
                plt.tight_layout()
                plt.savefig(os.path.join(charts_dir, "05_amount_distribution.png"), dpi=150)
                plt.close()
    except Exception as e:
        if not quiet:
            print(f"[WARN] Could not generate amount chart: {e}")
    
    if not quiet:
        print(f"[INFO] Charts saved to: {charts_dir}/")


def main() -> int:
    """Main entry point for the CLI."""
    # Check if running in interactive mode (no args or just --interactive)
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ("--interactive", "-I")):
        try:
            config = interactive_mode()
            from risk_engine.engine import run_engine
            
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
            
            print("\n" + "="*60)
            print("  ✅ Analysis Complete!")
            print("="*60)
            print(f"\n📂 Results saved to: {os.path.abspath(config['output_dir'])}/")
            print("\n📄 Output files:")
            print("   • flagged_transactions.csv  - All suspicious transactions")
            print("   • summary.json              - Quick statistics")
            print("   • stats_reasons.csv         - Why transactions were flagged")
            if config["generate_graphs"]:
                print("   • charts/                   - Visual reports (PNG)")
            print("\n💡 Tip: Open flagged_transactions.csv to review suspicious activity.\n")
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            return 130
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1
    
    # Standard CLI mode
    parser = argparse.ArgumentParser(
        prog="risk-engine",
        description="Explainable Risk-Based Transaction Anomaly Detection Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Interactive (easiest):  risk-engine
  Quick with defaults:    risk-engine -i transactions.csv
  Full control:           risk-engine -i data.csv -o out/ -t 4 -s on --graphs

Examples:
  risk-engine -i transactions.csv
  risk-engine -i data.csv -o results/ --simulation on --graphs
  risk-engine -i large_file.csv -o out/ -t 3 -c 100000

Output Files:
  • flagged_transactions.csv     - All flagged anomalous transactions
  • flagged_transactions.parquet - Same data in Parquet format
  • stats_risk_scores.csv        - Distribution of risk scores
  • stats_reasons.csv            - Breakdown of anomaly reasons
  • summary.json                 - Overall processing summary
  • charts/                      - Visual reports (if --graphs enabled)
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--interactive", "-I",
        action="store_true",
        help="Run in interactive mode with prompts"
    )

    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Input CSV file containing transactions"
    )

    parser.add_argument(
        "--output-dir", "-o",
        metavar="DIR",
        default="risk_engine_output",
        help="Directory to write output files (default: risk_engine_output)"
    )

    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=4,
        metavar="N",
        help="Risk score threshold for flagging (default: 4)"
    )

    parser.add_argument(
        "--simulation", "-s",
        choices=["on", "off"],
        default="off",
        help="Enable velocity simulation for rapid-transaction detection (default: off)"
    )

    parser.add_argument(
        "--chunk-size", "-c",
        type=int,
        default=500_000,
        metavar="N",
        help="Rows per processing chunk (default: 500000)"
    )
    
    parser.add_argument(
        "--graphs", "-g",
        action="store_true",
        help="Generate visualization charts (PNG images)"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=None,
        metavar="N",
        help="Number of CPU cores to use for parallel processing (default: all cores)"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()
    
    # Check if input is provided
    if not args.input:
        print("Error: --input/-i is required (or run without arguments for interactive mode)")
        print("\nUsage:")
        print("  risk-engine                        # Interactive mode")
        print("  risk-engine -i transactions.csv    # Quick mode")
        return 1

    # Validate input file
    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Validate chunk size
    if args.chunk_size < 1000:
        print("Error: Chunk size must be at least 1000 rows", file=sys.stderr)
        return 1

    # Validate threshold
    if args.threshold < 1 or args.threshold > 6:
        print("Error: Threshold must be between 1 and 6", file=sys.stderr)
        return 1

    try:
        from risk_engine.engine import run_engine

        run_engine(
            input_file=args.input,
            output_dir=args.output_dir,
            threshold=args.threshold,
            simulation=(args.simulation == "on"),
            chunk_size=args.chunk_size,
            quiet=args.quiet,
            workers=args.workers
        )
        
        if args.graphs:
            generate_charts(args.output_dir, quiet=args.quiet)
        
        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
