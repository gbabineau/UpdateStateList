"""
Tests for generate_html module.
"""

from io import StringIO
from unittest.mock import patch

import pytest
from update_state_list.generate_html import (
    main,
    write_taxonomy_header,
    write_family_header,
    write_order_header,
    write_taxon,
    generate_html,
)



@pytest.fixture
def mock_file_pointer():
    """Create a mock file pointer."""
    return StringIO()


class TestWriteTaxonomyHeader:
    """Tests for write_taxonomy_header function."""

    def test_write_taxonomy_header_basic(self, mock_file_pointer):
        """Test writing a basic taxonomy header."""
        write_taxonomy_header(
            mock_file_pointer, "#D9D9D9", "4", "Order", "Passeriformes"
        )
        output = mock_file_pointer.getvalue()
        assert "#D9D9D9" in output
        assert "Order Passeriformes" in output
        assert "<tr>\n  <td colspan=6 bgcolor=" in output

    def test_write_taxonomy_header_different_colors(self, mock_file_pointer):
        """Test taxonomy header with different background colors."""
        write_taxonomy_header(
            mock_file_pointer, "#B8CCE4", "3", "Family", "Corvidae"
        )
        output = mock_file_pointer.getvalue()
        assert "#B8CCE4" in output
        assert "Family Corvidae" in output


class TestWriteOrderHeader:
    """Tests for write_order_header function."""

    def test_write_order_header(self, mock_file_pointer):
        """Test writing an order header."""
        write_order_header(mock_file_pointer, "Passeriformes")
        output = mock_file_pointer.getvalue()
        assert "Order Passeriformes" in output
        assert "#D9D9D9" in output


class TestWriteFamilyHeader:
    """Tests for write_family_header function."""

    def test_write_family_header(self, mock_file_pointer):
        """Test writing a family header."""
        write_family_header(mock_file_pointer, "Corvidae")
        output = mock_file_pointer.getvalue()
        assert "Family Corvidae" in output
        assert "#B8CCE4" in output


class TestWriteTaxon:
    """Tests for write_taxon function."""

    def test_write_taxon_basic(self, mock_file_pointer):
        """Test writing a taxon row."""
        write_taxon(
            mock_file_pointer,
            "amerob",
            "1",
            "American Robin",
            "Turdus migratorius",
            "Resident",
        )
        output = mock_file_pointer.getvalue()
        assert "American Robin" in output
        assert "Turdus migratorius" in output
        assert "Resident" in output
        assert "amerob" in output
        assert "<tr>" in output

    def test_write_taxon_with_ebird_links(self, mock_file_pointer):
        """Test that taxon row includes eBird links."""
        write_taxon(
            mock_file_pointer,
            "amerob",
            "1",
            "American Robin",
            "Turdus migratorius",
            "Resident",
        )
        output = mock_file_pointer.getvalue()
        assert "ebird.org/species/amerob/US-VA" in output
        assert "Map" in output
        assert "Chart" in output

    def test_write_taxon_empty_index(self, mock_file_pointer):
        """Test writing a taxon with empty index text."""
        write_taxon(
            mock_file_pointer,
            "amerob",
            "",
            "American Robin",
            "Turdus migratorius",
            "Resident",
        )
        output = mock_file_pointer.getvalue()
        assert '<td align="center">' in output
        assert 'Resident' in output


class TestGenerateHtml:
    """Tests for generate_html function."""

    def test_generate_html_creates_file(self, tmp_path):
        """Test that generate_html creates an output HTML file."""
        csv_file = tmp_path / "test_birds.csv"
        csv_content = "order,familyComName,speciesCode,comName,sciName,State Status,subspecies\nPasseriformes,Corvidae,amerob,American Robin,Turdus migratorius,,False"
        csv_file.write_text(csv_content)

        with patch("update_state_list.generate_html.logging.info"):
            generate_html(str(csv_file))

        html_file = tmp_path / "test_birds.html"
        assert html_file.exists()

    def test_generate_html_contains_table(self, tmp_path):
        """Test that generated HTML contains a table."""
        csv_file = tmp_path / "test_birds.csv"
        csv_content = "order,familyComName,speciesCode,comName,sciName,State Status,subspecies\nPasseriformes,Corvidae,amerob,American Robin,Turdus migratorius,,False"
        csv_file.write_text(csv_content)

        with patch("update_state_list.generate_html.logging.info"):
            generate_html(str(csv_file))

        html_file = tmp_path / "test_birds.html"
        html_content = html_file.read_text()
        assert "<table" in html_content
        assert "Species" in html_content

    def test_generate_html_historical_species_section(self, tmp_path):
        """Test that historical species section is added."""
        csv_file = tmp_path / "test_birds.csv"
        csv_content = "order,familyComName,speciesCode,comName,sciName,State Status,subspecies\nPasseriformes,Corvidae,amerob,American Robin,Turdus migratorius,(4),False"
        csv_file.write_text(csv_content)

        with patch("update_state_list.generate_html.logging.info"):
            generate_html(str(csv_file))

        html_file = tmp_path / "test_birds.html"
        html_content = html_file.read_text()
        assert "Species Believed to Have Occurred Historically" in html_content


class TestMain:
    """Tests for main function."""

    def test_main_without_csv_argument_fails(self):
        """Test main function fails without required CSV argument."""
        with patch("sys.argv", ["generate-html"]):
            with pytest.raises(SystemExit):
                main()
