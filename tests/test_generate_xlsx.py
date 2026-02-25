"""
Unit tests for generate_xlsx.py
"""

from pathlib import Path
import tempfile
from unittest.mock import Mock

import csv
import pytest

from update_state_list.generate_xlsx import (
    write_taxonomy_header,
    write_taxon,
    generate_xlsx,
    headers,
    STATE_STATUS,
)

# pylint: disable=W0621
@pytest.fixture
def mock_worksheet():
    """Create a mock worksheet object."""
    return Mock()


@pytest.fixture
def mock_format():
    """Create a mock format object."""
    return Mock()


class TestWriteTaxonomyHeader:
    """Tests for write_taxonomy_header function."""

    def test_write_taxonomy_header_basic(self, mock_worksheet, mock_format):
        """Test writing a taxonomy header with level and text."""
        write_taxonomy_header(
            mock_worksheet, 1, "Order", "Passeriformes", mock_format
        )

        mock_worksheet.write.assert_any_call(1, headers.index("Level"), "Order")
        mock_worksheet.write.assert_any_call(
            1, headers.index("Species"), "Passeriformes"
        )
        mock_worksheet.set_row.assert_called_once_with(1, None, mock_format)

    def test_write_taxonomy_header_family(self, mock_worksheet, mock_format):
        """Test writing a family taxonomy header."""
        write_taxonomy_header(
            mock_worksheet, 5, "Family", "Corvidae", mock_format
        )

        mock_worksheet.write.assert_any_call(
            5, headers.index("Level"), "Family"
        )
        mock_worksheet.write.assert_any_call(
            5, headers.index("Species"), "Corvidae"
        )


class TestWriteTaxon:
    """Tests for write_taxon function."""

    def test_write_taxon_species(self, mock_worksheet):
        """Test writing a species row without subspecies."""
        write_taxon(
            mock_worksheet,
            2,
            "amecro",
            "1",
            "American Crow",
            "Corvus brachyrhynchos",
            "1",
            "",
            "https://some_url",
        )

        assert mock_worksheet.write.call_count >= 6
        mock_worksheet.write.assert_any_call(
            2, headers.index("Level"), "Species"
        )
        mock_worksheet.write.assert_any_call(2, headers.index("Count"), "1")

    def test_write_taxon_subspecies(self, mock_worksheet):
        """Test writing a subspecies row."""
        write_taxon(
            mock_worksheet,
            3,
            "amecro",
            "1.1",
            "American Crow",
            "Corvus brachyrhynchos",
            "1",
            "",
            "https://some_url",
        )

        mock_worksheet.write.assert_any_call(
            3, headers.index("Level"), "Subspecies"
        )
        mock_worksheet.write.assert_any_call(3, headers.index("Count"), "1.1")

    def test_write_taxon_category_extraction(self, mock_worksheet):
        """Test category extraction from state status."""
        write_taxon(
            mock_worksheet,
            4,
            "amecro",
            "2",
            "American Crow",
            "Corvus brachyrhynchos",
            "1",
            "Accidental",
            "https://some_url",
        )

        mock_worksheet.write.assert_any_call(
            4, headers.index("State Status"), "1"
        )
        mock_worksheet.write.assert_any_call(
            4, headers.index("Abundance"), "Accidental"
        )


    def test_write_taxon_urls_created(self, mock_worksheet):
        """Test that URL links are created."""
        write_taxon(
            mock_worksheet,
            6,
            "amecro",
            "4",
            "American Crow",
            "Corvus brachyrhynchos",
            "2",
            "",
            "https://some_url",
        )

        assert mock_worksheet.write_url.call_count == 4


class TestGenerateXlsx:
    """Tests for generate_xlsx function."""

    @pytest.fixture
    def sample_csv_file(self):
        """Create a temporary CSV file with sample data."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "order",
                    "familyComName",
                    "comName",
                    "sciName",
                    "speciesCode",
                    "subspecies",
                    STATE_STATUS,
                    "atlasUrl"
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "order": "Passeriformes",
                    "familyComName": "Corvidae",
                    "comName": "American Crow",
                    "sciName": "Corvus brachyrhynchos",
                    "speciesCode": "amecro",
                    "subspecies": "False",
                    STATE_STATUS: "(1)",
                    "atlasUrl": "https://some_url",
                }
            )
            writer.writerow(
                {
                    "order": "Passeriformes",
                    "familyComName": "Corvidae",
                    "comName": "American Crow",
                    "sciName": "Corvus brachyrhynchos",
                    "speciesCode": "amecro",
                    "subspecies": "False",
                    STATE_STATUS: "(1)",
                    "atlasUrl": "",
                }
            )
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()
        Path(temp_path.replace(".csv", ".xlsx")).unlink(missing_ok=True)

    def test_generate_xlsx_creates_file(self, sample_csv_file):
        """Test that generate_xlsx creates an xlsx file."""
        generate_xlsx(sample_csv_file)

        xlsx_file = sample_csv_file.replace(".csv", ".xlsx")
        assert Path(xlsx_file).exists()

    def test_generate_xlsx_with_multiple_rows(self):
        """Test generate_xlsx with multiple species and families."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "order",
                    "familyComName",
                    "comName",
                    "sciName",
                    "speciesCode",
                    "subspecies",
                    STATE_STATUS,
                    "atlasUrl",
                ],
            )
            writer.writeheader()
            for i in range(3):
                writer.writerow(
                    {
                        "order": "Passeriformes",
                        "familyComName": "Corvidae",
                        "comName": f"Species {i}",
                        "sciName": f"Genus species{i}",
                        "speciesCode": f"code{i}",
                        "subspecies": "False",
                        STATE_STATUS: "(1)",
                        "atlasUrl": "https://some_url"
                    }
                )
            temp_path = f.name

        try:
            generate_xlsx(temp_path)
            xlsx_file = temp_path.replace(".csv", ".xlsx")
            assert Path(xlsx_file).exists()
        finally:
            Path(temp_path).unlink()
            Path(temp_path.replace(".csv", ".xlsx")).unlink(missing_ok=True)

    def test_generate_xlsx_historically_occurring(self):
        """Test generate_xlsx with historically occurring species."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "order",
                    "familyComName",
                    "comName",
                    "sciName",
                    "speciesCode",
                    "subspecies",
                    STATE_STATUS,
                    "atlasUrl",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "order": "Passeriformes",
                    "familyComName": "Corvidae",
                    "comName": "Current Species",
                    "sciName": "Corvus current",
                    "speciesCode": "curcur",
                    "subspecies": "False",
                    STATE_STATUS: "(1)",
                    "atlasUrl": "https://some_url",
                }
            )
            writer.writerow(
                {
                    "order": "Passeriformes",
                    "familyComName": "Corvidae",
                    "comName": "Historical Species",
                    "sciName": "Corvus historical",
                    "speciesCode": "hishis",
                    "subspecies": "False",
                    STATE_STATUS: "(4)",
                    "atlasUrl": "",
                }
            )
            temp_path = f.name

        try:
            generate_xlsx(temp_path)
            xlsx_file = temp_path.replace(".csv", ".xlsx")
            assert Path(xlsx_file).exists()
        finally:
            Path(temp_path).unlink()
            Path(temp_path.replace(".csv", ".xlsx")).unlink(missing_ok=True)
