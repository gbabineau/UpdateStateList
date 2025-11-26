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


def update_state_list(common_names_file) -> None:
    api_key = get_ebird_api_key.get_ebird_api_key()
    taxonomy = get_taxonomy.ebird_taxonomy(api_key)
    # remove hybrids and domestic birds from the taxonomy as they are not in the state list
    taxonomy = [
        t
        for t in taxonomy
        if t.get("category") != "hybrid" and t.get("category") != "domestic"
    ]
    birds_data = []
    with open(common_names_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        birds_data = list(reader)
    updated_bird_data = []
    non_issf_subspecies_order_keeper = 0
    for bird in birds_data:
        common_name = bird.get("comName", "")
        matching_taxon = next(
            (t for t in taxonomy if t.get("comName") == common_name), None
        )

        if matching_taxon:
            for copied_field in [
                "sciName",
                "speciesCode",
                "order",
                "familyComName",
                "taxonOrder",
            ]:
                bird[copied_field] = matching_taxon.get(copied_field)
            bird["speciesCode"] = matching_taxon.get("speciesCode")
            # ISSF stands for Identifiable Subspecific Forms. These are
            # taxonomic groups below the species level, used to identify and
            # report distinct subspecies or groups of subspecies, especially
            # when they can be distinguished visually or otherwise.
            bird["subspecies"] = matching_taxon.get("category") == "issf"
            if not bird["subspecies"]:
                non_issf_subspecies_order_keeper = 0
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

            if matching_taxon:
                logging.warning(
                    "Partial match found for '%s' using base name '%s': matched to '%s'",
                    common_name,
                    base_name,
                    matching_taxon.get("comName"),
                )
                for copied_field in [
                    "sciName",
                    "speciesCode",
                    "order",
                    "familyComName",
                    "taxonOrder",
                ]:
                    bird[copied_field] = matching_taxon.get(copied_field)
                non_issf_subspecies_order_keeper = non_issf_subspecies_order_keeper + .01
                bird["taxonOrder"] = bird["taxonOrder"] + non_issf_subspecies_order_keeper
                bird["subspecies"] = True
            else:
                logging.error(
                    "No match found for '%s' (base name: '%s').",
                    common_name,
                    base_name,
                )
        updated_bird_data.append(bird)

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
