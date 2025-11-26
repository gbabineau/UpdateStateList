""" """

import argparse
import csv
import logging
import tomllib
import re

from update_state_list import (
    get_ebird_api_key,
    get_taxonomy,
)

def create_output_file(updated_bird_data, common_names_file) -> None:
    # Sort updated_bird_data by taxonOrder
    updated_bird_data.sort(key=lambda x: float(x.get("taxonOrder", 0)))

    output_file = common_names_file.replace(".csv", "_updated.csv")
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        if updated_bird_data:
            fieldnames = [
                "comName",
                "sciName",
                "State Status",
                "speciesCode",
                "order",
                "familyComName",
                "taxonOrder",
                "subspecies",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_bird_data)
    logging.info("Updated data written to %s", output_file)

def get_taxonomy_of_interest(api_key) -> list:
    taxonomy = get_taxonomy.ebird_taxonomy(api_key)
    # remove hybrids and domestic birds from the taxonomy as they are not in the state list
    taxonomy = [
        t
        for t in taxonomy
        if t.get("category") != "hybrid" and t.get("category") != "domestic"
    ]
    return taxonomy

def read_input_file(common_names_file) -> list:
    birds_data = []
    with open(common_names_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        birds_data = list(reader)
    return birds_data

def get_matching_taxon(
            common_name, taxonomy) -> tuple[list, bool]:
    matching_taxon = next(
        (t for t in taxonomy if t.get("comName") == common_name), None
    )

    if matching_taxon:
        non_issf_subspecies = False
    else:
        # Try to find a match using only the part before the first non-alphabetic character
        base_name = re.split(r"[^a-zA-Z\s\-]", common_name)[0].strip()
        matching_taxon = next(
            (
                t
                for t in taxonomy
                if t.get("comName", "").startswith(base_name)
            ),
            None,
        )
        non_issf_subspecies = True
        if not matching_taxon:
            logging.error(
                "No match found for '%s' (base name: '%s').",
                common_name,
                base_name,
            )
    return matching_taxon, non_issf_subspecies

def update_state_list(common_names_file) -> None:
    api_key = get_ebird_api_key.get_ebird_api_key()
    taxonomy = get_taxonomy_of_interest(api_key)
    birds_data = read_input_file(common_names_file)
    updated_bird_data = []
    non_issf_subspecies_order_keeper = 0
    for bird in birds_data:
        matching_taxon, non_issf_subspecies = get_matching_taxon(
            bird.get("comName", ""),
            taxonomy=taxonomy
        )
        for copied_field in [
            "sciName",
            "speciesCode",
            "order",
            "familyComName",
            "taxonOrder",
        ]:
            bird[copied_field] = matching_taxon.get(copied_field)
        if non_issf_subspecies:
            non_issf_subspecies_order_keeper = non_issf_subspecies_order_keeper + .01
            bird["taxonOrder"] = bird["taxonOrder"] + non_issf_subspecies_order_keeper
            bird["subspecies"] = True
        else:
            non_issf_subspecies_order_keeper = 0
            bird["subspecies"] = matching_taxon.get("category") == "issf"



        updated_bird_data.append(bird)

    create_output_file(updated_bird_data, common_names_file)


def main():
    """Main function for the app."""
    arg_parser = argparse.ArgumentParser(
        prog="update-state-list", description="Update elements of a state list."
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
    arg_parser.add_argument(
        "--common_names_file",
        required=True,
        help="list of birds had for a region/time frame",
    )
    args = arg_parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    update_state_list(args.common_names_file)


if __name__ == "__main__":
    main()
