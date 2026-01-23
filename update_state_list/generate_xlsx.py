"""
Main function for the generate_xlsx application
"""

import csv
import logging
from datetime import date

import xlsxwriter

from update_state_list import parse_common_arguments, create_links

STATE_STATUS = "State Status"

headers = [
    "Level",
    "Count",
    "Species",
    "Species Information Link",
    "Scientific Name",
    "Category",
    STATE_STATUS,
    "Map Link",
    "Chart Link",
]


def write_taxonomy_header(worksheet, row, level, text, header_format):
    """
    Write a  taxonomy header.

    Args:
        worksheet: File object opened in write mode to write the output.
        row : row in worksheet to write
        text (str): The family name text to be displayed in the header.
        header_format : format to use for the header
    Returns:
        None
    """
    worksheet.write(row, headers.index("Level"), level)
    worksheet.write(row, headers.index("Species"), text)
    worksheet.set_row(row, None, header_format)  # None for default height


def write_taxon(
    worksheet,
    row,
    species_code,
    index_text,
    common_name,
    scientific_name,
    state_status,
):
    """
    Write a table row with taxon information to an xlsx file.

    This function generates an xlsx table row containing species information
    including the species index, common name (linked to eBird species page),
    scientific name, state status, and links to eBird distribution map and
    species chart.

    Args:
        worksheet: File object opened in write mode to write xlsx content.
        row : row to add
        species_code (str): The eBird species code used to construct eBird URLs.
        index_text (str): The index or row number to display in first column.
        common_name (str): The common name of the species.
        scientific_name (str): The scientific name in italic format.
        state_status (str): The presence status of the species in the state.

    Returns:
        None

    Note:
        The function writes xlsx for Virginia (US-VA) state specifically. URLs
        are hardcoded with Virginia coordinates and state parameters. The table
        row includes columns for index, common name (as link), scientific name,
        status, map link, and chart link.
    """
    if "." in index_text:
        worksheet.write(row, headers.index("Level"), "Subspecies")
    else:
        worksheet.write(row, headers.index("Level"), "Species")

    worksheet.write(row, headers.index("Count"), index_text)
    worksheet.write(row, headers.index("Species"), common_name)
    worksheet.write_url(
        row,
        headers.index("Species Information Link"),
        create_links.ebird_species_information(species_code),
        string=common_name,
    )
    worksheet.write(row, headers.index("Scientific Name"), scientific_name)
    if '(' in state_status:
        category = state_status.split("(")[1].split(")")[0]
    else:
        category = "1"
    worksheet.write(row, headers.index("Category"), category)
    worksheet.write(row, headers.index(STATE_STATUS), state_status)
    worksheet.write_url(
        row,
        headers.index("Map Link"),
        create_links.ebird_map_link(species_code),
        string="Map",
    )
    worksheet.write_url(
        row,
        headers.index("Chart Link"),
        create_links.ebird_chart_link(species_code),
        string="Chart",
    )


def generate_xlsx(official_list_file) -> None:
    """
    Generate a formatted xlsx document from a CSV file containing official bird
    species data.

    Args:
        official_list_file: Path to the CSV file containing bird species data.
    """
    # Read CSV data
    with open(official_list_file, "r", encoding="utf-8") as f:
        birds_data = list(csv.DictReader(f))
    output_file = official_list_file.replace(".csv", ".xlsx")
    workbook = xlsxwriter.Workbook(output_file)
    light_gray_format = workbook.add_format({"bg_color": "#D3D3D3"})
    worksheet = workbook.add_worksheet()
    today = date.today().strftime("%B %d, %Y")
    header_format = workbook.add_format(
        {"bold": True, "bottom": 1}
    )
    for col_num, value in enumerate(headers):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_row(0, None, light_gray_format)
    worksheet.write_comment(
        "A1",
        f"This table was generated on {today} programmatically by "
        "https://github.com/gbabineau/UpdateStateList",
    )

    row = 1
    # Add data rows
    current_order = current_family = ""
    index = 1
    historically_occurring_section = False
    for bird in birds_data:
        # Add historical species row if first occurrence
        state_status = bird.get(STATE_STATUS, "")
        if state_status == "(4)" and not historically_occurring_section:
            write_taxonomy_header(
                worksheet, row, "", "Historically Occurring", light_gray_format
            )
            row = row + 1
            historically_occurring_section = True
        # Add order row if changed
        if bird.get("order", "") != current_order:
            current_order = bird["order"]
            current_family = ""
            write_taxonomy_header(
                worksheet, row, "Order", current_order, light_gray_format
            )
            row = row + 1

        # Add family row if changed
        if bird.get("familyComName", "") != current_family:
            current_family = bird["familyComName"]
            write_taxonomy_header(
                worksheet, row, "Family", current_family, light_gray_format
            )
            row = row + 1

        # Add species row
        species_code = bird.get("speciesCode", "")

        if (
            bird.get("subspecies", "False").lower() == "false"
            and not historically_occurring_section
        ):
            index_text = str(index)
            index += 1
            subspecies_count = 1
        elif not historically_occurring_section:
            index_text = f"{index}.{subspecies_count}"
            subspecies_count = subspecies_count + 1
        else:
            index_text = ""
        write_taxon(
            worksheet,
            row,
            species_code,
            index_text,
            bird.get("comName"),
            bird.get("sciName", ""),
            state_status,
        )
        row = row + 1
    worksheet.autofilter(0, 0, row-1, len(headers)-1)
    worksheet.autofit()
    workbook.close()
    logging.info("Document saved as %s", output_file)


def main():
    """
    Main function for the generate_xlsx application.
    This function sets up command-line argument parsing for the
    update-state-list program. It reads the version from pyproject.toml,
    configures logging based on verbosity, and processes the official list CSV
    file to generate a xlsx document.
    Args:
        None (uses command-line arguments via argparse)
    Command-line Arguments:
        --version: Display the program version and exit
        --verbose: Enable verbose logging output (INFO level)
        --official_list_csv: Path to the CSV file of the list created by
                            update_state_list (required)
    Returns:
        None
    Raises:
        FileNotFoundError: If pyproject.toml or the specified CSV is not found
        tomllib.TOMLDecodeError: If pyproject.toml contains invalid TOML syntax
    """
    arg_parser = parse_common_arguments.parse_common_arguments(
        program_name="generate-xlsx",
        description="Generate a xlsx document from an official list CSV.",
    )
    arg_parser.add_argument(
        "--official_list_csv",
        required=True,
        help="csv of official list created by update_state_list",
    )
    args = arg_parser.parse_args()
    generate_xlsx(args.official_list_csv)


if __name__ == "__main__":
    main()
