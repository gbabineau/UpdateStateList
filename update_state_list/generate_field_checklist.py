"""
Main function for the generate_field_checklist application
"""

import csv
import logging
from datetime import date
from dominate import (document, util)
from dominate.tags import (style, div, table, td, tr,p,a,ul,li)
import xlsxwriter

from update_state_list import (
    convert_file_formats,
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

def name_text(com_name, subspecies, abundance, status) -> str:

    # indent any subspecies
    name = (
        com_name
        if subspecies == "False"
        else f"   {com_name}"
    )
    if abundance != "":
        name = f"{name}({abundance[:3].lower()})"
    if status != "1":
        name = f"{name}-{status}"
    return name

def generate_field_checklist_html(official_list_file) -> None:
    """
    Generate a formatted html document from a CSV file containing official bird
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
    columns = 12
    # rows = 44
    rows = 56
    column = 0
    row = 0
    pages = 2
    page = 0
    data_table = [
        [["" for _ in range(columns)] for _ in range(rows)]
        for _ in range(pages)
    ]
    for bird in birds_data:
        abundance = bird.get("Abundance", "")
        status = bird.get("State Status", "1")
        if status != "4" and bird.get("subspecies") == "False":
            name = name_text(bird["comName"], bird["subspecies"], abundance, status)
            data_table[page][row][column] = name
            data_table[page][row][column + 1] = " "
            row = row + 1
            if row == rows:
                row = 0
                column = column + 2
                if column == columns:
                    row = 0
                    column = 0
                    page = page + 1
    max_row = row
    max_column = column
    doc = document(title="Virgina Field Checklist")
    with doc.head:
        # Optional: Add a simple CSS style for visibility
        style("""
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                padding: 1px;
                width: 100%;
                table-layout: fixed;
                page-break-inside: auto;
                margin-top: 10px;
                margin-bottom: 10px;
                margin-left: 10px;
                margin-right: 10px;
            }
            .preserve-spaces {
                white-space: pre;
            }
            .no-break {
                page-break-inside: avoid;
            }
            td:first-child {
                width: 80px; /* Target the first column */
            }
            td:nth-child(2) {
                width: 10px;
            }
            td:nth-child(3) {
                width: 80px;
            }
            td:nth-child(4) {
                width: 10px;
            }
            td:nth-child(5) {
                width: 80px;
            }
            td:nth-child(6) {
                width: 10px;
            }
            td:nth-child(7) {
                width: 80px;
            }
            td:nth-child(8) {
                width: 10px;
            }
            td:nth-child(9) {
                width: 80px;
            }
            td:nth-child(10) {
                width: 10px;
            }
            td:nth-child(11) {
                width: 80px;
            }
            td:nth-child(12) {
                width: 10px;
            }
        """)
        # style for a positioned text box
        style('body { margin: 0; } .text-box { position: absolute; }')

        # Define a CSS class for page breaks
        style("""
            .page-break {
                page-break-after: always;
            }
            /* Optional: Add a visual indicator for screen viewing */
            @media screen {
                .page-break::after {
                    content: "--- PAGE BREAK ---";
                    display: block;
                    margin: 20px 0;
                    color: #999;
                    text-align: center;
                }
            }
        """)
# Add the table to the body of the document
    with doc.body:
        simple_table = table()
        with simple_table:
            page = 0
            for row in range(rows):
                with tr():
                    for column in range(columns):
                        td(data_table[page][row][column])
        div(_class="page-break")

        simple_table = table()
        with simple_table:
            page = 1
            for row in range(rows):
                with tr():
                    for column in range(columns if row < max_row else max_column):
                        if not (column == max_column and row > max_row):
                            td(data_table[page][row][column])
        with div(cls="text-box", style="left: 84%; top: 130%;"):
            p("FIELD LIST - BIRDS OF VIRGINIA")
            p(
                "This list is provided consistent with the Virginia Society of Ornithology (VSO) official checklist of Virginia birds. " \
                "The list is maintained by VARCOM for the VSO. "
                "For more information including detailed descriptions of category and abundance codes visit:",
                a(
                    "https://www.virginiabirds.org/offical-state-checklist",
                    href="https://www.virginiabirds.org/offical-state-checklist",
                ),
                style="font-size: 80%;"
            )
            p(
                "Summary category and abundance definitions:",
                style="font-size: 80%;",
            )
            with ul():
                li("acc - accidental", style="font-size: 80%;")
                li("rar - rare", style="font-size: 80%;")
                li("occ - occasional", style="font-size: 80%;")
                li(
                    "All birds listed are category 1 unless otherwise noted",
                    style="font-size: 80%;",
                )
                with ul():
                    li(
                        "Category 2 - Less data than Category 1.",
                        style="font-size: 80%;",
                    )
                    li(
                        "Category 3,3a,3b - Provenance uncertain.",
                        style="font-size: 80%;",
                    )
                    li(
                        "Category 5 - Introduced. Self Sustaining.",
                        style="font-size: 80%;",
                    )
                    li(
                        "Category 6 - Introduced. Not self Sustaining.",
                        style="font-size: 80%;",
                    )
            p("NAME _______________________")
            p("DATE _______________________")
            p("LOCATION ___________________")
            p("")
            p("")
            p(
                "Copies of this list can be downloaded from:",
                a(
                    "https://www.virginiabirds.org",
                    href="https://www.virginiabirds.org",
                ),
                style="font-size: 80%;",
            )

            p(
                "Copyright February 2026, by the Virginia Society of Ornithology.",
                style="font-size: 80%;",
            )

    html_output_file = official_filename.replace(
        ".csv", "_field_checklist.html"
    )
    with open(html_output_file, "wt", encoding="utf-8") as f:
        f.write(doc.render())
    pdf_output_file = official_filename.replace(".csv", "_field_checklist.pdf")
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
    #generate_field_checklist_xlsx(args.official_list_csv)
    generate_field_checklist_html(args.official_list_csv)

if __name__ == "__main__":
    main()
