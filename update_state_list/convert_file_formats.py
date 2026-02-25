from xlsx2html import xlsx2html
from weasyprint import HTML


def convert_xls_to_html(excel_file: str, html_file: str):
    # Convert the Excel file to HTML and save it
    xlsx2html(excel_file, html_file)

    print(f"HTML generated {html_file}.")

def convert_html_to_pdf(html_file: str, pdf_file: str):
    HTML(filename=html_file).write_pdf(pdf_file)
    print(f"PDF generated {pdf_file}.")