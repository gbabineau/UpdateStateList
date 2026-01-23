"""
Main function for the generate_field_checklist application
"""

import csv
import logging
from datetime import date

import xlsxwriter

from update_state_list import (
    convert_file_formats,
    create_links,
    parse_common_arguments,
)

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




def _get_code(state_status: str) -> tuple:
    if state_status == "":
        return ("", "")
    elif "(" in state_status:
        return (
            state_status.split("(")[1].split(")")[0],
            state_status.split()[0][:3],
        )
    else:
        return "", state_status[:3]


def generate_field_checklist(official_list_file) -> None:
    """
    Generate a formatted xlsx document from a CSV file containing official bird
    species data.

    Args:
        official_list_file: Path to the CSV file containing bird species data.
    """
    # Read CSV data
    with open(official_list_file, "r", encoding="utf-8") as f:
        birds_data = list(csv.DictReader(f))
    official_filename = (
        "reports/" + official_list_file.split("/")[-1].split("\\")[-1]
    )

    xlsx_output_file = official_filename.replace(
        ".csv", "_field_checklist.xlsx"
    )
    pdf_output_file = official_filename.replace(".csv", "_field_checklist.pdf")
    html_output_file = official_filename.replace(
        ".csv", "_field_checklist.html"
    )
    workbook = xlsxwriter.Workbook(xlsx_output_file)
    worksheet = workbook.add_worksheet()
    columns = 6
    rows = 45
    column = 0
    row = 0
    pages=2
    page=0
    data_table = [[[None] * rows] * columns]*pages
    for bird in birds_data:
        abundance, status = _get_code(bird["State Status"])
        # indent any subspecies
        name = (
            bird["comName"]
            if bird["subspecies"] == 'False'
            else f"  {bird['comName']}"
        )
        if status != "4":
            data_table[page][column][row]= [f"{name} {abundance} {status}", "_"]
            column = column+1
            if column == columns:
                column = 0
                row = row + 1
                if row == rows:
                    row = 0
                    page = page+1
    # add page 1
    worksheet.add_table(
        0,
        0,
        rows,
        columns*2,
        {
            "header_row": False,
            "data": data_table[0],
            "style": "Table Style Light 11",  # Apply a specific Excel table style
            "autofilter": False,  # Turn off the default autofilter
        },
    )
    worksheet.h_pagebreaks([columns])
    # add page 2
    worksheet.add_table(
        0,
        0,
        rows,
        columns * 2,
        {
            "header_row": False,
            "data": data_table[1],
            "style": "Table Style Light 11",  # Apply a specific Excel table style
            "autofilter": False,  # Turn off the default autofilter
        },
    )
    border_format = workbook.add_format(
        {"border": 1, "align": "left", "font_size": 10}
    )
    worksheet.conditional_format(
        0, 0, len(data_table), 2, {"type": "no_blanks", "format": border_format}
    )
    today = date.today().strftime("%B %d, %Y")

    worksheet.write_comment(
        "A1",
        f"This table was generated on {today} programmatically by "
        "https://github.com/gbabineau/UpdateStateList",
    )

    worksheet.autofit()
    workbook.close()
    logging.info("Document saved as %s", xlsx_output_file)
    convert_file_formats.convert_xls_to_html(
        excel_file=xlsx_output_file, html_file=html_output_file
    )
    convert_file_formats.convert_html_to_pdf(
        html_file=html_output_file, pdf_file=pdf_output_file
    )


def main():
    """
    Main function for the generate_field_checklist application.
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
    generate_field_checklist(args.official_list_csv)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
