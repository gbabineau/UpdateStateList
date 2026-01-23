"""
Tests for create_links module.
"""

from update_state_list.create_links import (
    ebird_chart_link,
    ebird_map_link,
    ebird_species_information,
)


class TestEbirdSpeciesInformation:
    """Tests for ebird_species_information function."""

    def test_ebird_species_information_basic(self):
        """Test creating a basic species information link."""
        result = ebird_species_information("amerob")
        assert result == "https://ebird.org/species/amerob/US-VA"

    def test_ebird_species_information_different_species(self):
        """Test species information link with different species code."""
        result = ebird_species_information("carwre")
        assert result == "https://ebird.org/species/carwre/US-VA"

    def test_ebird_species_information_contains_virginia(self):
        """Test that species information link contains Virginia state code."""
        result = ebird_species_information("bkcchi")
        assert "US-VA" in result

    def test_ebird_species_information_contains_ebird_domain(self):
        """Test that species information link contains eBird domain."""
        result = ebird_species_information("tuftin")
        assert "ebird.org" in result


class TestEbirdMapLink:
    """Tests for ebird_map_link function."""

    def test_ebird_map_link_basic(self):
        """Test creating a basic map link."""
        result = ebird_map_link("amerob")
        assert "https://ebird.org/ebird/map/amerob" in result

    def test_ebird_map_link_contains_species_code(self):
        """Test that map link contains the species code."""
        result = ebird_map_link("carwre")
        assert "carwre" in result

    def test_ebird_map_link_contains_virginia_coordinates(self):
        """Test that map link contains Virginia geographic coordinates."""
        result = ebird_map_link("amerob")
        assert "-84.70" in result
        assert "36.20" in result
        assert "-70.95" in result
        assert "37.22" in result

    def test_ebird_map_link_contains_parameters(self):
        """Test that map link contains required parameters."""
        result = ebird_map_link("amerob")
        assert "neg=true" in result
        assert "zh=true" in result
        assert "gp=true" in result


class TestEbirdChartLink:
    """Tests for ebird_chart_link function."""

    def test_ebird_chart_link_basic(self):
        """Test creating a basic chart link."""
        result = ebird_chart_link("amerob")
        assert "https://ebird.org/ebird/GuideMe" in result

    def test_ebird_chart_link_contains_species_code(self):
        """Test that chart link contains the species code."""
        result = ebird_chart_link("carwre")
        assert "carwre" in result

    def test_ebird_chart_link_contains_virginia_state(self):
        """Test that chart link contains Virginia state code."""
        result = ebird_chart_link("amerob")
        assert "US-VA" in result

    def test_ebird_chart_link_contains_date_range(self):
        """Test that chart link contains full year date range."""
        result = ebird_chart_link("amerob")
        assert "bMonth=1" in result
        assert "eMonth=12" in result

    def test_ebird_chart_link_contains_all_years(self):
        """Test that chart link contains all years parameters."""
        result = ebird_chart_link("amerob")
        assert "bYear=1900&eYear=Cur" in result
