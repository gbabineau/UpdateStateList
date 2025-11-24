"""
Main function for the photo_id application which presents a quiz of bird photos
based on a definition of species, and time of year (to handle different)
plumages.
"""

import argparse
import csv
import logging
import tomllib
from difflib import get_close_matches

from update_state_list import (
    get_ebird_api_key,
    get_taxonomy,
)

def update_state_list(common_names_file) -> None:
    api_key = get_ebird_api_key.get_ebird_api_key()
    taxonomy = get_taxonomy.ebird_taxonomy(api_key)
    # remove hybrids and domestic birds from the taxonomy as they are not in the state list
    taxonomy = [t for t in taxonomy if t.get('category') != 'hybrid' and t.get('category') != 'domestic']
    birds_data = []
    with open(common_names_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        birds_data = list(reader)
    updated_bird_data = []
    for bird in birds_data:
        common_name = bird.get('comName', '')
        matching_taxon = next((t for t in taxonomy if t.get('comName') == common_name), None)

        if matching_taxon:
            bird['sciName'] = matching_taxon.get('sciName')
            bird["speciesCode"] = matching_taxon.get('speciesCode')
            updated_bird_data.append(bird)
        else:
            logging.warning(
                "No match for '%s'.",
                common_name,
            )
            updated_bird_data.append(bird)

    # add map and chart and remove species code since it is not needed anymore
    birds_with_map_and_chart = []
    for bird in updated_bird_data:
        if code := bird.get('speciesCode'):
            bird["Spatial Distribution"] = (
                f"http://ebird.org/ebird/map/{code}?neg=true&env.minX=-84.70&env.minY=36.20&env.maxX=-70.95&env.maxY=37.22&zh=true&gp=true&ev=Z&mr=1-12&bmo=1&emo=12&yr=all&getLocations=states&states=US-VA"
            )
            bird["Counts & Seasonality"] = (
                f"http://ebird.org/ebird/GuideMe?cmd=decisionPage&speciesCodes={code}&getLocations=states&states=US-VA&bYear=1900&eYear=Cur&bMonth=1&eMonth=12&reportType=species&parentState=US-VA"
            )
        if 'speciesCode' in bird:
            del bird['speciesCode']
        birds_with_map_and_chart.append(bird)

    output_file = common_names_file.replace('.csv', '_updated.csv')
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        if updated_bird_data:
            fieldnames = ["comName", "sciName", "State Status", "Spatial Distribution", "Counts & Seasonality"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(birds_with_map_and_chart)
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
