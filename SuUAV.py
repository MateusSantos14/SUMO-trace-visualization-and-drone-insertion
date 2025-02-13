import argparse
from funcs.parser import parse_config_and_run
from interface.InteractivePlot import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SuUAV Application")
    parser.add_argument('--run', action='store_true', help="Start the application with the run configuration")
    parser.add_argument('--setup', action='store_true', help="Start the setup with the setup configuration")
    parser.add_argument('--setup-input', type=str, help="Path to the input file for setup")
    parser.add_argument('--run-input', type=str, help="Path to the input file for run")
    args = parser.parse_args()

    if args.setup:
        if args.setup_input:
            run(args.setup_input)
        else:
            print("Error: --setup-input argument is required for --setup")
    if args.run:
        if args.run_input:
            parse_config_and_run(args.run_input)
        else:
            print("Error: --run-input argument is required for --run")