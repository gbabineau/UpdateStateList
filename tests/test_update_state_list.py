"""Unit tests for update_state_list module."""

import csv
import logging
from unittest.mock import patch

import pytest

from update_state_list.update_state_list import (
    create_output_file,
    get_matching_taxon,
    get_taxonomy_of_interest,
    main,
    read_input_file,
    update_state_list,
)


class TestCreateOutputFile:
    """Tests for create_output_file function."""

    def test_create_output_file_with_data(self, tmp_path):
        """Test creating output file with valid bird data."""
        input_file = tmp_path / "test.csv"
        updated_data = [
            {
                "comName": "American Robin",
                "sciName": "Turdus migratorius",
                "State Status": "Common",
                "speciesCode": "amerob",
                "order": "Passeriformes",
                "familyComName": "Thrushes",
                "taxonOrder": "100",
                "subspecies": False,
            }
        ]

        create_output_file(updated_data, str(input_file))

        output_file = tmp_path / "test_updated.csv"
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["comName"] == "American Robin"

    def test_create_output_file_sorts_by_taxon_order(self, tmp_path):
        """Test that output file is sorted by taxonOrder."""
        input_file = tmp_path / "test.csv"
        updated_data = [
            {
                "comName": "Bird B",
                "taxonOrder": "200",
                "sciName": "Sci B",
                "State Status": "Rare",
                "speciesCode": "birdb",
                "order": "Order1",
                "familyComName": "Family1",
                "subspecies": False,
            },
            {
                "comName": "Bird A",
                "taxonOrder": "100",
                "sciName": "Sci A",
                "State Status": "Common",
                "speciesCode": "birda",
                "order": "Order2",
                "familyComName": "Family2",
                "subspecies": False,
            },
        ]

        create_output_file(updated_data, str(input_file))

        output_file = tmp_path / "test_updated.csv"
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]["comName"] == "Bird A"
            assert rows[1]["comName"] == "Bird B"


class TestGetTaxonomyOfInterest:
    """Tests for get_taxonomy_of_interest function."""

    @patch("update_state_list.update_state_list.get_taxonomy")
    def test_filters_hybrids(self, mock_get_taxonomy):
        """Test that hybrid birds are filtered out."""
        mock_get_taxonomy.ebird_taxonomy.return_value = [
            {"comName": "Regular Bird", "category": "species"},
            {"comName": "Hybrid Bird", "category": "hybrid"},
        ]

        result = get_taxonomy_of_interest("fake_api_key")

        assert len(result) == 1
        assert result[0]["comName"] == "Regular Bird"

    @patch("update_state_list.update_state_list.get_taxonomy")
    def test_filters_domestic(self, mock_get_taxonomy):
        """Test that domestic birds are filtered out."""
        mock_get_taxonomy.ebird_taxonomy.return_value = [
            {"comName": "Wild Bird", "category": "species"},
            {"comName": "Domestic Bird", "category": "domestic"},
        ]

        result = get_taxonomy_of_interest("fake_api_key")

        assert len(result) == 1
        assert result[0]["comName"] == "Wild Bird"


class TestReadInputFile:
    """Tests for read_input_file function."""

    def test_read_valid_csv(self, tmp_path):
        """Test reading a valid CSV file."""
        test_file = tmp_path / "birds.csv"
        with open(test_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["comName", "State Status"])
            writer.writeheader()
            writer.writerow(
                {"comName": "American Robin", "State Status": "Common"}
            )

        result = read_input_file(str(test_file))

        assert len(result) == 1
        assert result[0]["comName"] == "American Robin"

    def test_read_nonexistent_file(self):
        """Test that FileNotFoundError is raised for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_input_file("nonexistent.csv")


class TestGetMatchingTaxon:
    """Tests for get_matching_taxon function."""

    def test_exact_match(self):
        """Test finding an exact match for common name."""
        taxonomy = [
            {"comName": "American Robin", "sciName": "Turdus migratorius"}
        ]

        result, is_subspecies = get_matching_taxon("American Robin", taxonomy)

        assert result["comName"] == "American Robin"
        assert is_subspecies is False

    def test_base_name_match(self):
        """Test matching using base name for subspecies."""
        taxonomy = [
            {
                "comName": "Yellow-rumped Warbler",
                "sciName": "Setophaga coronata",
            }
        ]

        result, is_subspecies = get_matching_taxon(
            "Yellow-rumped Warbler (Myrtle)", taxonomy
        )

        assert result["comName"] == "Yellow-rumped Warbler"
        assert is_subspecies is True

    def test_no_match_found(self):
        """Test when no match is found."""
        taxonomy = [
            {"comName": "American Robin", "sciName": "Turdus migratorius"}
        ]

        result, is_subspecies = get_matching_taxon("Nonexistent Bird", taxonomy)

        assert result is None
        assert is_subspecies is True


    """Tests for update_state_list function."""

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_basic(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test basic update_state_list functionality."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "American Robin",
                "sciName": "Turdus migratorius",
                "speciesCode": "amerob",
                "order": "Passeriformes",
                "familyComName": "Thrushes",
                "taxonOrder": "100",
                "category": "species",
            }
        ]
        mock_read.return_value = [
            {"comName": "American Robin", "State Status": "Common"}
        ]

        update_state_list("test.csv")

        mock_create.assert_called_once()
        updated_data = mock_create.call_args[0][0]
        assert len(updated_data) == 1
        assert updated_data[0]["sciName"] == "Turdus migratorius"
        assert updated_data[0]["subspecies"] is False

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_with_issf(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test handling ISSF subspecies."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "Yellow-rumped Warbler",
                "sciName": "Setophaga coronata",
                "speciesCode": "yerwar",
                "order": "Passeriformes",
                "familyComName": "Wood-Warblers",
                "taxonOrder": "200",
                "category": "issf",
            }
        ]
        mock_read.return_value = [
            {"comName": "Yellow-rumped Warbler", "State Status": "Common"}
        ]

        update_state_list("test.csv")

        updated_data = mock_create.call_args[0][0]
        assert updated_data[0]["subspecies"] is True
class TestMain:
    """Tests for main function."""

    @patch("update_state_list.update_state_list.update_state_list")
    @patch("sys.argv", ["update-state-list", "--common_names_file", "test.csv"])
    def test_main_basic_execution(self, mock_update):
        """Test main function with basic arguments."""

        main()

        mock_update.assert_called_once_with("test.csv")

    @patch("update_state_list.update_state_list.update_state_list")
    @patch("logging.basicConfig")
    @patch("sys.argv", ["update-state-list", "--common_names_file", "test.csv", "--verbose"])
    def test_main_with_verbose(self, mock_logging, mock_update):
        """Test main function with verbose flag."""

        main()

        mock_logging.assert_called_once_with(level=logging.INFO)
        mock_update.assert_called_once_with("test.csv")

    @patch("sys.argv", ["update-state-list", "--version"])
    @patch("builtins.open", create=True)
    def test_main_version(self, mock_open):
        """Test main function with version argument."""

        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = b"""
[tool.poetry]
version = "1.2.3"
"""

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch("sys.argv", ["update-state-list"])
    def test_main_missing_required_arg(self):
        """Test main function fails when required argument is missing."""

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code != 0
class TestUpdateStateList:
    """Tests for update_state_list function."""

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_with_sort_as_field(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test that 'Sort as' field is used for taxonomy matching when present."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "Canada Goose",
                "sciName": "Branta canadensis",
                "speciesCode": "cangoo",
                "order": "Anseriformes",
                "familyComName": "Ducks, Geese, and Waterfowl",
                "taxonOrder": "50",
                "category": "species",
            }
        ]
        mock_read.return_value = [
            {
                "comName": "Cackling Goose",
                "Sort as": "Canada Goose",
                "State Status": "Rare",
            }
        ]

        update_state_list("test.csv")

        updated_data = mock_create.call_args[0][0]
        assert len(updated_data) == 1
        assert updated_data[0]["sciName"] == "Branta canadensis"

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_with_non_issf_subspecies(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test handling non-ISSF subspecies with taxon order adjustment."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "Yellow-rumped Warbler",
                "sciName": "Setophaga coronata",
                "speciesCode": "yerwar",
                "order": "Passeriformes",
                "familyComName": "Wood-Warblers",
                "taxonOrder": 200,
                "category": "species",
            }
        ]
        mock_read.return_value = [
            {
                "comName": "Yellow-rumped Warbler (Myrtle)",
                "State Status": "Common",
            }
        ]

        update_state_list("test.csv")

        updated_data = mock_create.call_args[0][0]
        assert updated_data[0]["subspecies"] is True
        assert updated_data[0]["taxonOrder"] == 200.01

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_multiple_subspecies(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test multiple consecutive subspecies get incremental order offsets."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "Yellow-rumped Warbler",
                "sciName": "Setophaga coronata",
                "speciesCode": "yerwar",
                "order": "Passeriformes",
                "familyComName": "Wood-Warblers",
                "taxonOrder": 200,
                "category": "species",
            }
        ]
        mock_read.return_value = [
            {
                "comName": "Yellow-rumped Warbler (Myrtle)",
                "State Status": "Common",
            },
            {
                "comName": "Yellow-rumped Warbler (Audubon's)",
                "State Status": "Rare",
            },
        ]

        update_state_list("test.csv")

        updated_data = mock_create.call_args[0][0]
        assert updated_data[0]["taxonOrder"] == 200.01
        assert updated_data[1]["taxonOrder"] == 200.02

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_resets_counter_after_species(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test that subspecies counter resets after regular species."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "Yellow-rumped Warbler",
                "sciName": "Setophaga coronata",
                "speciesCode": "yerwar",
                "order": "Passeriformes",
                "familyComName": "Wood-Warblers",
                "taxonOrder": 200,
                "category": "species",
            },
            {
                "comName": "American Robin",
                "sciName": "Turdus migratorius",
                "speciesCode": "amerob",
                "order": "Passeriformes",
                "familyComName": "Thrushes",
                "taxonOrder": 300,
                "category": "species",
            },
        ]
        mock_read.return_value = [
            {
                "comName": "Yellow-rumped Warbler (Myrtle)",
                "State Status": "Common",
            },
            {"comName": "American Robin", "State Status": "Common"},
            {
                "comName": "Yellow-rumped Warbler (Audubon's)",
                "State Status": "Rare",
            },
        ]

        update_state_list("test.csv")

        updated_data = mock_create.call_args[0][0]
        assert updated_data[0]["taxonOrder"] == 200.01
        assert updated_data[1]["taxonOrder"] == 300
        assert updated_data[2]["taxonOrder"] == 200.01

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_no_matching_taxon(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create, caplog
    ):
        """Test logging when no matching taxon is found."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = []
        mock_read.return_value = [
            {"comName": "Nonexistent Bird", "State Status": "Common"}
        ]

        with caplog.at_level(logging.ERROR):
            update_state_list("test.csv")

        assert "No matching taxon for Nonexistent Bird" in caplog.text
        updated_data = mock_create.call_args[0][0]
        assert len(updated_data) == 0

    @patch("update_state_list.update_state_list.create_output_file")
    @patch("update_state_list.update_state_list.read_input_file")
    @patch("update_state_list.update_state_list.get_taxonomy_of_interest")
    @patch("update_state_list.update_state_list.get_ebird_api_key")
    def test_update_state_list_copies_all_fields(
        self, mock_api_key, mock_taxonomy, mock_read, mock_create
    ):
        """Test that all required taxonomy fields are copied."""
        mock_api_key.get_ebird_api_key.return_value = "fake_key"
        mock_taxonomy.return_value = [
            {
                "comName": "American Robin",
                "sciName": "Turdus migratorius",
                "speciesCode": "amerob",
                "order": "Passeriformes",
                "familyComName": "Thrushes",
                "taxonOrder": 100,
                "category": "species",
            }
        ]
        mock_read.return_value = [
            {"comName": "American Robin", "State Status": "Common"}
        ]

        update_state_list("test.csv")

        updated_data = mock_create.call_args[0][0]
        assert updated_data[0]["sciName"] == "Turdus migratorius"
        assert updated_data[0]["speciesCode"] == "amerob"
        assert updated_data[0]["order"] == "Passeriformes"
        assert updated_data[0]["familyComName"] == "Thrushes"
        assert updated_data[0]["taxonOrder"] == 100


