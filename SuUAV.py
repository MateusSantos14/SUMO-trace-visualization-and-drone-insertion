from funcs.parser import *
from interface.api import run as run_web
import argparse

# Exemplo de uso
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SuUAV Application")
    parser.add_argument('--setup', action='store_true', help="Start the setup interface in the browser")
    args = parser.parse_args()

    if args.setup:
        run_web()
    else:
        parse_config_and_run("config.ini")