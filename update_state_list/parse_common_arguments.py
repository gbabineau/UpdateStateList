
import argparse
import tomllib
import logging

def parse_common_arguments(
        program_name : str,
        description : str
    ) ->argparse.ArgumentParser:
    """
    Parse common command-line arguments for the applications.

    Args:
        prog (str) : The name of the program/script
        description (str): The description to display in the argument parser
            help message.

    Returns:
        argparse.ArgumentParser: Configured argument parser with version and
            verbose options.
    """
    arg_parser = argparse.ArgumentParser(
        prog=program_name, description=description
    )
    with open("pyproject.toml", "rb") as f:
        pyproject_data = tomllib.load(f)
    version = (
        pyproject_data.get("tool", {}).get("poetry", {}).get("version", "0.0.0")
    )
    arg_parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version}"
    )
    arg_parser.add_argument(
        "--verbose", action="store_true", help="increase verbosity"
    )
    args, _ = arg_parser.parse_known_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    return arg_parser
