"""
Tests  update_state_list/get_taxonomy.py
"""

import json
import unittest
from unittest import mock

import update_state_list.get_taxonomy


class TestGetTaxonomy(unittest.TestCase):
    def test_ebird_taxonomy(self):
        """tests the function with that name"""
        test_json = {"comName": "value"}
        # Test case for when does not exist
        with (
            mock.patch(
                "update_state_list.get_taxonomy.os.path.isfile"
            ) as mock_isfile,
            mock.patch(
                "builtins.open",
                mock.mock_open(read_data=json.dumps(test_json)),
            ) as mock_file,
            mock.patch(
                "update_state_list.get_taxonomy.get_taxonomy"
            ) as mock_get_taxonomy,
        ):
            mock_isfile.return_value = True
            mock_get_taxonomy.return_value = test_json
            taxonomy = update_state_list.get_taxonomy.ebird_taxonomy("key")
            mock_file.assert_called_with(
                ".cache/taxonomy.json", encoding="utf-8", mode="rt"
            )
            self.assertEqual(taxonomy, test_json)
        # Cache does not exist
        with (
            mock.patch(
                "update_state_list.get_taxonomy.os.path.isfile"
            ) as mock_isfile,
            mock.patch(
                "builtins.open",
                mock.mock_open(read_data=json.dumps(test_json)),
            ) as mock_file,
            mock.patch(
                "update_state_list.get_taxonomy.get_taxonomy"
            ) as mock_get_taxonomy,
        ):
            mock_isfile.return_value = False
            mock_get_taxonomy.return_value = test_json
            taxonomy = update_state_list.get_taxonomy.ebird_taxonomy("key")
            mock_file.assert_called_with(
                ".cache/taxonomy.json", encoding="utf-8", mode="wt"
            )
            self.assertEqual(taxonomy, test_json)
