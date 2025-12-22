"""
This module is used to update a state list from a input list (in csv format)
containing the common name and state status. It checks that against the
eBird taxonomy and collects information from eBird for producing information
for the state list including order and family. This is output as a csv which
can in turn be used for input by the generate_docx utility to create
a document.
"""

import csv
import logging
import re

from update_state_list import (
    get_ebird_api_key,
    get_taxonomy,
    parse_common_arguments,
)


def create_output_file(updated_bird_data, common_names_file) -> None:
    """
    Create an output CSV file with updated bird data sorted by taxonomic order.
    This function takes the updated bird data and writes it to a new CSV file
    with a standardized set of fields. The output filename is derived from the
    input common names file by appending '_updated' before the file extension.
    Args:
        updated_bird_data (list[dict]): A list of dictionaries with bird data.
            Each dictionary should contain keys like 'comName', 'sciName',
            'State Status', 'speciesCode', 'order', 'familyComName',
            'taxonOrder', and 'subspecies'.
        common_names_file (str): The path to the original common names CSV file.
            Used to determine the output filename.
    Returns:
        None: This function does not return a value but writes data to a file
            and logs the operation.
    """
    # Sort updated_bird_data by taxonOrder
    # Sort by taxonOrder, but place birds with State Status "(4)" at the end
    updated_bird_data.sort(
        key=lambda x: (
            x.get("State Status") == "(4)",
            float(x.get("taxonOrder", 0)),
        )
    )
    # updated_bird_data.sort(key=lambda x: float(x.get("taxonOrder", 0)))

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
                "Sort as",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_bird_data)
    logging.info("Updated data written to %s", output_file)


def get_taxonomy_of_interest(api_key) -> list:
    """
    Retrieves and filters the eBird taxonomy to include only birds of interest.

    This function fetches the complete eBird taxonomy using the provided API
    key, then filters out hybrid and domestic bird species, returning only wild
    species that are relevant for state bird lists.

    Args:
        api_key (str): A valid eBird API key for authentication.

    Returns:
        list: A list of dictionaries containing taxonomy information for each
            species.
    """
    taxonomy = get_taxonomy.ebird_taxonomy(api_key)
    # remove hybrids and domestic birds from the taxonomy as they are not in the state list
    taxonomy = [
        t
        for t in taxonomy
        if t.get("category") != "hybrid" and t.get("category") != "domestic"
    ]
    return taxonomy


def read_input_file(common_names_file) -> list:
    """
    Read bird data from a CSV file and return it as a list of dictionaries.

    Args:
        common_names_file (str): Path to the CSV file with state records

    Returns:
        list: A list of dictionaries where each dictionary represents a row from
            the CSV file, with column headers as keys and cell values as values.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be accessed due to permissions.
        UnicodeDecodeError: If the file cannot be decoded with UTF-8 encoding.
    """
    birds_data = []
    with open(common_names_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        birds_data = list(reader)
    return birds_data


def get_matching_taxon(common_name, taxonomy) -> tuple[list, bool]:
    """
    Find a matching taxon entry from the taxonomy list based on common name.
    This function attempts to find a taxon in the taxonomy list by matching the
    common name. If an exact match is not found, it tries to match using a base
    name (the part before the first non-alphabetic character, excluding spaces
    and hyphens).
    Args:
        common_name (str): The common name of the species to search for.
        taxonomy (list): A list of dictionaries containing taxonomic information, where each
                            dictionary should have at least a "comName" key.
    Returns:
        tuple[list, bool]: A tuple containing:
            - matching_taxon (dict or None): The matching taxonomy dictionary.
            - non_issf_subspecies (bool): This is to handle subspecies which
            are in the state record but not in the eBird taxonomy.
    Raises:
        None: Logs an error message if no matching taxon is found.
    """
    matching_taxon = next(
        (t for t in taxonomy if t.get("comName") == common_name), None
    )

    if matching_taxon:
        non_issf_subspecies = False
    else:
        # Try to find a match using only the part before the first non-alphabetic character
        base_name = re.split(r"[^a-zA-Z\s\-]", common_name)[0].strip()
        matching_taxon = next(
            (t for t in taxonomy if t.get("comName", "").startswith(base_name)),
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
    """
    Update bird state list data with taxonomy information from eBird API.
    This function reads a file containing bird common names, retrieves the
    corresponding taxonomy data from the eBird API, and updates each bird record
    with scientific names, species codes, taxonomic order, and family
    information. It handles both regular species and non-ISSF  subspecies by
    adjusting their taxonomic order values.
    Args:
        common_names_file: Path to the input file with bird common names data.
    Returns:
        None. The function writes the updated bird data to an output file.
    Notes:
        - Non-ISSF subspecies are assigned incremental taxon order offsets
          to maintain proper ordering relative to their parent species.
    """
    api_key = get_ebird_api_key.get_ebird_api_key()
    taxonomy = get_taxonomy_of_interest(api_key)
    birds_data = read_input_file(common_names_file)
    updated_bird_data = []
    non_issf_subspecies_order_keeper = 0
    for bird in birds_data:
        if sort_as := bird.get("Sort as"):
            bird_for_search = sort_as
        else:
            bird_for_search = bird.get("comName", "")

        matching_taxon, non_issf_subspecies = get_matching_taxon(
            bird_for_search, taxonomy=taxonomy
        )
        if matching_taxon is None:
            logging.error("No matching taxon for %s", bird.get("comName"))
        else:
            non_issf_subspecies = non_issf_subspecies or "(" in bird.get(
                "comName"
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
                non_issf_subspecies_order_keeper = (
                    non_issf_subspecies_order_keeper + 0.01
                )
                bird["taxonOrder"] = (
                    bird["taxonOrder"] + non_issf_subspecies_order_keeper
                )
                bird["subspecies"] = True
            else:
                non_issf_subspecies_order_keeper = 0
                bird["subspecies"] = matching_taxon.get("category") == "issf"

            updated_bird_data.append(bird)

    create_output_file(updated_bird_data, common_names_file)


def main():
    """
    Main function for the app.
    This function sets up the command-line argument parser for the
    update-state-list tool, which updates elements of a state list. It reads
    the version from pyproject.toml, configures logging based on verbosity flag,
    and calls update_state_list with the provided common names file.
    Args:
        None
    Returns:
        None
    Command-line Arguments:
        --version: Display the program version and exit
        --verbose: Enable verbose logging output
        --common_names_file: Path to the file containing list of birds for a
        region/time frame (required)
    Raises:
        FileNotFoundError: If pyproject.toml or common_names_file are not found
        tomllib.TOMLDecodeError: If pyproject.toml is not valid TOML format
    """
    arg_parser = parse_common_arguments.parse_common_arguments(
        program_name="update-state-list",
        description="Update elements of a state list."
    )
    arg_parser.add_argument(
        "--common_names_file",
        required=True,
        help="list of birds had for a region/time frame",
    )
    args = arg_parser.parse_args()
    update_state_list(args.common_names_file)


if __name__ == "__main__":
    main()
