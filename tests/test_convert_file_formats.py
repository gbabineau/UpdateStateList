from unittest.mock import MagicMock, patch

from update_state_list.convert_file_formats import (
    convert_html_to_pdf,
    convert_xls_to_html,
)


class TestConvertXlsToHtml:
    @patch("update_state_list.convert_file_formats.xlsx2html")
    @patch("builtins.print")
    def test_convert_xls_to_html_success(self, mock_print, mock_xlsx2html):
        excel_file = "test.xlsx"
        html_file = "test.html"

        convert_xls_to_html(excel_file, html_file)

        mock_xlsx2html.assert_called_once_with(excel_file, html_file)
        mock_print.assert_called_once_with(f"HTML generated {html_file}.")

    @patch("update_state_list.convert_file_formats.xlsx2html")
    @patch("builtins.print")
    def test_convert_xls_to_html_with_different_paths(
        self, mock_print, mock_xlsx2html
    ):
        excel_file = "/path/to/file.xlsx"
        html_file = "/path/to/output.html"

        convert_xls_to_html(excel_file, html_file)

        mock_xlsx2html.assert_called_once_with(excel_file, html_file)
        mock_print.assert_called_once_with(f"HTML generated {html_file}.")


class TestConvertHtmlToPdf:
    @patch("update_state_list.convert_file_formats.HTML")
    @patch("builtins.print")
    def test_convert_html_to_pdf_success(self, mock_print, mock_html):
        html_file = "test.html"
        pdf_file = "test.pdf"

        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        convert_html_to_pdf(html_file, pdf_file)

        mock_html.assert_called_once_with(filename=html_file)
        mock_html_instance.write_pdf.assert_called_once_with(pdf_file)
        mock_print.assert_called_once_with(f"PDF generated {pdf_file}.")
