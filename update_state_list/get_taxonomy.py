
"""
This module provides functionality to retrieve and cache the eBird taxonomy using the eBird API.
"""
import json


import os

from ebird.api import get_taxonomy

def ebird_taxonomy(ebird_api_key) -> list:
    """
    Retrieves the ebird taxonomy.
    Args:
        ebird_api_key (str): The ebird API key.

    Returns:
        list: The ebird taxonomy.
    """
    taxonomy = []
    cache_file = ".cache/taxonomy.json"
    directory = os.path.dirname(cache_file)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.isfile(cache_file):
        taxonomy = get_taxonomy(ebird_api_key)
        with open(cache_file, encoding="utf-8", mode="wt") as f:
            json.dump(taxonomy, indent=4, fp=f)
    else:
        with open(cache_file, encoding="utf-8", mode="rt") as f:
            taxonomy = json.load(f)
    return taxonomy
