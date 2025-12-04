"""
Main function for the generate_docx application
plumages.
"""

import argparse
import csv
import logging
from datetime import date

import tomllib

TR_START = "<tr>\n"
TR_END = "</tr>\n"

def write_taxonomy_header(file_pointer, color, font_size, level, text):
    """
    Write a taxonomy header row to an HTML table.

    Args:
        file_pointer: File object to write the HTML content to.
        color (str): Background color of the header cell (hex code or name).
        font_size (str): Font size for the header text.
        level (str): Taxonomy level or category label.
        text (str): Header text content to display.

    Returns:
        None
    """
    file_pointer.writelines(
        [
            TR_START,
            f'  <td colspan=6 bgcolor="{color}"><font size="{font_size}">'
            f"&nbsp&nbsp{level} {text}</font></td>",
            TR_END,
        ]
    )


def write_order_header(file_pointer, text):
    """
    Write an order-level header to an HTML file.

    Args:
        file_pointer: File object to write the header to.
        text (str): The text content for the order header.

    Returns:
        None
    """
    write_taxonomy_header(file_pointer, "#D9D9D9", "4", "Order", text)


def write_family_header(file_pointer, text):
    """
    Write a family-level taxonomy header to an HTML file.

    Args:
        file_pointer: File object opened in write mode to write the HTML output.
        text (str): The family name text to be displayed in the header.

    Returns:
        None
    """
    write_taxonomy_header(file_pointer, "#B8CCE4", "4", "Family", text)


def write_taxon(
    file_pointer,
    species_code,
    index_text,
    common_name,
    scientific_name,
    state_status,
):
    """
    Write a table row with taxon information to an HTML file.

    This function generates an HTML table row containing species information
    including the species index, common name (linked to eBird species page),
    scientific name, state status, and links to eBird distribution map and
    species chart.

    Args:
        file_pointer: File object opened in write mode to write HTML content.
        species_code (str): The eBird species code used to construct eBird URLs.
        index_text (str): The index or row number to display in first column.
        common_name (str): The common name of the species.
        scientific_name (str): The scientific name in italic format.
        state_status (str): The presence status of the species in the state.

    Returns:
        None

    Note:
        The function writes HTML for Virginia (US-VA) state specifically. URLs
        are hardcoded with Virginia coordinates and state parameters. The table
        row includes columns for index, common name (as link), scientific name,
        status, map link, and chart link.
    """
    file_pointer.writelines(
        [
            TR_START,
            f'  <td align="center">{index_text}</font></td>\n',
            f'  <td align="center"><a href="https://ebird.org/species/{species_code}/US-VA" target="_blank">{common_name}</a></td>\n',
            f'  <td align="left">&nbsp&nbsp<i>{scientific_name}</font></td>\n',
            f'  <td align="center">{state_status}</font></td>\n',
            f'  <td align="center"><a href="http://ebird.org/ebird/map/{species_code}?neg=true&env.minX=-84.70&env.minY=36.20&env.maxX=-70.95&env.maxY=37.22&zh=true&gp=true&ev=Z&mr=1-12&bmo=1&emo=12&yr=all" target="_blank">Map</a></td>\n',
            f'  <td align="center"><a href="http://ebird.org/ebird/GuideMe?cmd=decisionPage&speciesCodes={species_code}&getLocations=states&states=US-VA&bYear=1900&eYear=Cur&bMonth=1&eMonth=12&reportType=species&parentState=US-VA" target="_blank">Chart</a></td>\n',
            TR_END,
        ]
    )


def generate_html(official_list_file) -> None:
    """
    Generate a formatted HTML document from a CSV file containing official bird
    species data.

    Args:
        official_list_file: Path to the CSV file containing bird species data.
    """
    # Read CSV data
    with open(official_list_file, "r", encoding="utf-8") as f:
        birds_data = list(csv.DictReader(f))
    output_file = official_list_file.replace(".csv", ".html")

    with open(output_file, "wt", encoding="utf-8") as html_file:
        today = date.today().strftime("%B %d, %Y")
        table_definition = [
            f"<!-- This table was generated on {today} programmatically by https://github.com/gbabineau/UpdateStateList -->",
            '<table style="width:100%">\n',
            '<table border="3">\n',
            TR_START,
            '  <td style="width:2%" align="center"><font size="5">#</font></td>\n',
            '  <td style="width:25%" align="center"><font size="5">Species</font></td>\n',
            '  <td style="width:22%" align="center"><font size="5">Scientific Name</font></td>\n',
            '  <td style="width:12%" align="center"><font size="5">State Status</font></td>\n',
            '  <td style="width:19%" align="center"><font size="5">Spatial Distribution</font></td>\n',
            '  <td style="width:20%" align="center"><font size="5">Counts & Seasonality</font></td>\n',
            TR_END,
        ]
        html_file.writelines(table_definition)

        # Add data rows
        current_order = current_family = ""
        index = 1
        historically_occurring_section = False
        for bird in birds_data:
            # Add historical species row if first occurrence
            state_status = bird.get("State Status", "")
            if state_status == "(4)" and not historically_occurring_section:
                html_file.writelines(
                    '<tr><td align="center" colspan=6><font size="5">Species Believed to Have Occurred Historically</font></td></tr>\n'
                )
                historically_occurring_section = True
            # Add order row if changed
            if bird.get("order", "") != current_order:
                current_order = bird["order"]
                current_family = ""
                write_order_header(html_file, current_order)

            # Add family row if changed
            if bird.get("familyComName", "") != current_family:
                current_family = bird["familyComName"]
                write_family_header(html_file, current_family)

            # Add species row
            species_code = bird.get("speciesCode", "")

            if (
                bird.get("subspecies", "False").lower() == "false"
                and not historically_occurring_section
            ):
                index_text = str(index)
                index += 1
            else:
                index_text = ""

            write_taxon(
                html_file,
                species_code,
                index_text,
                bird.get("comName"),
                bird.get("sciName", ""),
                state_status,
            )
    logging.info("Document saved as %s", output_file)


def main():
    """
    Main function for the generate_html application.
    This function sets up command-line argument parsing for the
    update-state-list program. It reads the version from pyproject.toml,
    configures logging based on verbosity, and processes the official list CSV
    file to generate a HTML document.
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
    arg_parser = argparse.ArgumentParser(
        prog="generate-html",
        description="Generate a HTML document from an official list CSV.",
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
        "--official_list_csv",
        required=True,
        help="csv of official list created by update_state_list",
    )
    args = arg_parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    generate_html(args.official_list_csv)


if __name__ == "__main__":
    main()
