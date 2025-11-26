"""
Main function for the generate_docx application
plumages.
"""

import argparse
import csv
import logging
import tomllib

from docx import Document, opc
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from docx.shared import Inches


def add_hyperlink(paragraph, url, text, color, underline):
    """
    Add a hyperlink to a paragraph in a Word document.

    Args:
        paragraph: The paragraph object to add the hyperlink to.
        url (str): The URL that the hyperlink should point to.
        text (str): The display text for the hyperlink.
        color (str, optional): The color of the hyperlink text
        underline (bool): Whether the hyperlink should be underlined.

    Returns:
        OxmlElement: The hyperlink XML element that was created and added to
        the paragraph.

    Notes:
        This function uses python-docx's low-level XML manipulation to create
        hyperlinks with custom styling options that aren't available through the
        high-level API.
    """
    part = paragraph.part
    r_id = part.relate_to(
        url, opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(
        qn("r:id"),
        r_id,
    )
    new_run = OxmlElement("w:r")
    rpr_element = OxmlElement("w:rpr_element")
    if color is not None:
        c = OxmlElement("w:color")
        c.set(qn("w:val"), color)
        rpr_element.append(c)
    if not underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "none")
        rpr_element.append(u)
    new_run.append(rpr_element)
    new_run.text = text
    hyperlink.append(new_run)
    # pylint: disable=W0212
    paragraph._p.append(hyperlink)
    return hyperlink


def generate_docx(official_list_file) -> None:
    """
    Generate a formatted Word document from a CSV file containing official bird
    species data. This function reads bird species data from a CSV file and
    creates a structured Word document with a table containing species
    information organized by taxonomic order and family. The document includes
    hyperlinks to eBird species accounts, distribution maps, and seasonal charts.
    Args:
        official_list_file (str): Path to the CSV file containing bird species data. The CSV
            should include columns: speciesCode, order, familyComName, comName, sciName,
            State Status, and subspecies.
    Returns:
        None: The function saves the generated document to disk with a .docx extension.
    """
    with open(official_list_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        birds_data = list(reader)
    current_order = ""
    current_family = ""
    doc = Document()

    # Add title
    title = doc.add_heading(
        "The Birds of Virginia and its Offshore Waters: The Official List", 0
    )
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Create table with header row
    table = doc.add_table(rows=1, cols=6)

    table.style = "Light Grid Accent 1"

    # Set header row
    header_cells = table.rows[0].cells
    headers = [
        "#",
        "Species",
        "Scientific Name",
        "State Status",
        "Spatial Distribution",
        "Counts & Seasonality",
    ]
    # Set column widths
    table.columns[0].width = Inches(0.5)  # Narrow column for number
    table.columns[1].width = Inches(1.1)  # Species
    table.columns[2].width = Inches(1.1)  # Scientific Name
    table.columns[3].width = Inches(1.1)  # State Status
    table.columns[4].width = Inches(1.1)  # Spatial Distribution
    table.columns[5].width = Inches(1.1)  # Counts & Seasonality
    for i, header in enumerate(headers):
        header_cells[i].text = header
        header_cells[i].paragraphs[0].runs[0].bold = True

    # Add data rows
    index = 1
    for bird in birds_data:
        species_code = bird.get("speciesCode", "")
        if bird.get("order", "") != current_order:
            current_order = bird.get("order", "")
            current_family = ""
            order_row = table.add_row().cells
            order_cell = order_row[0].merge(order_row[5])
            order_cell.text = f"Order: {current_order}"
            order_cell.paragraphs[0].runs[0].bold = True
            shading_elm = OxmlElement("w:shd")
            shading_elm.set(qn("w:fill"), "D3D3D3")  # Light gray
            # pylint: disable=W0212
            order_cell._element.get_or_add_tcPr().append(shading_elm)

        if bird.get("familyComName", "") != current_family:
            current_family = bird.get("familyComName", "")
            family_row = table.add_row().cells
            family_cell = family_row[0].merge(family_row[5])
            family_cell.text = f"Family: {current_family}"
            family_cell.paragraphs[0].runs[0].bold = True
            shading_elm = OxmlElement("w:shd")
            shading_elm.set(qn("w:fill"), "ADD8E6")  # Light blue
            # pylint: disable=W0212
            family_cell._element.get_or_add_tcPr().append(shading_elm)
        row_cells = table.add_row().cells
        if bird.get("subspecies", "False").lower() == "false":
            row_cells[0].text = str(index)
            index = index + 1
        # add hyperlink for common name that provides species account
        add_hyperlink(
            row_cells[1].paragraphs[0],
            f"https://ebird.org/species/{species_code}/US-VA",
            bird.get("comName"),
            "0000FF",
            False,
        )
        row_cells[2].text = bird.get("sciName", "")
        row_cells[3].text = bird.get("State Status", "")
        # Add hyperlinks for Spatial Distribution and Counts & Seasonality
        add_hyperlink(
            row_cells[4].paragraphs[0],
            f"http://ebird.org/ebird/map/{species_code}?neg=true&env.minX="
            "-84.70&env.minY=36.20&env.maxX=-70.95&env.maxY=37.22&zh=true&"
            "gp=true&ev=Z&mr=1-12&bmo=1&emo=12&yr=all&getLocations=states&"
            "states=US-VA",
            "Map",
            "0000FF",
            False,
        )

        add_hyperlink(
            row_cells[5].paragraphs[0],
            "http://ebird.org/ebird/GuideMe?cmd=decisionPage&speciesCodes="
            f"{species_code}&getLocations=states&states=US-VA&bYear=1900&eYear="
            "Cur&bMonth=1&eMonth=12&reportType=species&parentState=US-VA",
            "Chart",
            "0000FF",
            False,
        )

    # Save document
    output_file = official_list_file.replace(".csv", ".docx")
    doc.save(output_file)
    logging.info("Document saved as %s", output_file)


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
        "--official_list_csv",
        required=True,
        help="csv of official list created by update_state_list",
    )
    args = arg_parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    generate_docx(args.official_list_csv)


if __name__ == "__main__":
    main()
