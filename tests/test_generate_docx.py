"""Tests for generate_docx module."""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from docx import Document
from docx.oxml import CT_Hyperlink

from update_state_list.generate_docx import add_hyperlink, generate_docx, main


class TestAddHyperlink:
    """Tests for add_hyperlink function."""

    def test_add_hyperlink_with_color_and_underline(self):
        """Test adding hyperlink with color and underline."""
        doc = Document()
        paragraph = doc.add_paragraph()

        hyperlink = add_hyperlink(
            paragraph,
            "https://example.com",
            "Test Link",
            "FF0000",
            True
        )

        assert hyperlink is not None
        assert isinstance(hyperlink, CT_Hyperlink)

    def test_add_hyperlink_without_underline(self):
        """Test adding hyperlink without underline."""
        doc = Document()
        paragraph = doc.add_paragraph()

        hyperlink = add_hyperlink(
            paragraph,
            "https://example.com",
            "Test Link",
            "0000FF",
            False
        )

        assert hyperlink is not None

    def test_add_hyperlink_without_color(self):
        """Test adding hyperlink without color."""
        doc = Document()
        paragraph = doc.add_paragraph()

        hyperlink = add_hyperlink(
            paragraph,
            "https://example.com",
            "Test Link",
            None,
            False
        )

        assert hyperlink is not None


class TestGenerateDocx:
    """Tests for generate_docx function."""

    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing."""
        return [
            {
                "speciesCode": "gockin",
                "order": "Passeriformes",
                "familyComName": "Kinglets",
                "comName": "Golden-crowned Kinglet",
                "sciName": "Regulus satrapa",
                "State Status": "Common",
                "subspecies": "False"
            },
            {
                "speciesCode": "rucroc",
                "order": "Passeriformes",
                "familyComName": "Kinglets",
                "comName": "Ruby-crowned Kinglet",
                "sciName": "Corthylio calendula",
                "State Status": "Common",
                "subspecies": "False"
            }
        ]

    @patch('update_state_list.generate_docx.Document')
    @patch("update_state_list.generate_docx.add_hyperlink")
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictReader')
    def test_generate_docx_creates_document(self, mock_csv, _, __ , mock_doc):
        """Test that generate_docx creates a document."""
        mock_csv.return_value = [
            {
                "speciesCode": "gockin",
                "order": "Passeriformes",
                "familyComName": "Kinglets",
                "comName": "Golden-crowned Kinglet",
                "sciName": "Regulus satrapa",
                "State Status": "Common",
                "subspecies": "False"
            }
        ]

        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance

        generate_docx("test.csv")

        mock_doc_instance.save.assert_called_once_with("test.docx")

    @patch('update_state_list.generate_docx.Document')
    @patch("update_state_list.generate_docx.add_hyperlink")
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictReader')
    def test_generate_docx_handles_subspecies(self, mock_csv, _, __, mock_doc):
        """Test that subspecies are handled correctly."""
        mock_csv.return_value = [
            {
                "speciesCode": "gockin",
                "order": "Passeriformes",
                "familyComName": "Kinglets",
                "comName": "Golden-crowned Kinglet",
                "sciName": "Regulus satrapa",
                "State Status": "Common",
                "subspecies": "True"
            }
        ]

        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance

        generate_docx("test.csv")

        mock_doc_instance.save.assert_called_once()


class TestMain:
    """Tests for main function."""

    @patch('update_state_list.generate_docx.generate_docx')
    @patch('builtins.open', new_callable=mock_open, read_data=b'[tool.poetry]\nversion = "1.0.0"\n')
    @patch('sys.argv', ['prog', '--official_list_csv', 'test.csv'])
    def test_main_with_required_args(self, _, mock_generate):
        """Test main function with required arguments."""
        main()
        mock_generate.assert_called_once_with('test.csv')

    @patch('builtins.open', new_callable=mock_open, read_data=b'[tool.poetry]\nversion = "1.0.0"\n')
    @patch('sys.argv', ['prog', '--version'])
    def test_main_with_version(self, _):
        """Test main function with version flag."""
        with pytest.raises(SystemExit):
            main()

    @patch('update_state_list.generate_docx.generate_docx')
    @patch('builtins.open', new_callable=mock_open, read_data=b'[tool.poetry]\nversion = "1.0.0"\n')
    @patch('sys.argv', ['prog', '--official_list_csv', 'test.csv', '--verbose'])
    def test_main_with_verbose(self, _, mock_generate):
        """Test main function with verbose flag."""
        main()
        mock_generate.assert_called_once_with('test.csv')
