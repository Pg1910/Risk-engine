import argparse
from risk_engine.engine import run_engine

def main():
    parser = argparse.ArgumentParser(
        description="Explainable Risk-Based Transaction Anomaly Engine"
    )

    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output-dir", required=True, help="Directory to write outputs")
    parser.add_argument("--threshold", type=int, default=4, help="Risk score threshold")
    parser.add_argument(
        "--simulation",
        choices=["on", "off"],
        default="off",
        help="Enable velocity simulation"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500_000,
        help="Rows per processing chunk"
    )

    args = parser.parse_args()

    run_engine(
        input_file=args.input,
        output_dir=args.output_dir,
        threshold=args.threshold,
        simulation=(args.simulation == "on"),
        chunk_size=args.chunk_size
    )

if __name__ == "__main__":
    main()
