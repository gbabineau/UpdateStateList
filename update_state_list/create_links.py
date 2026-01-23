"""Module to generate strings for referencing information in eBird"""


def ebird_species_information(species_code: str) -> str:
    """Create link to species information."""
    return f"https://ebird.org/species/{species_code}/US-VA"


def ebird_map_link(species_code: str) -> str:
    """Create link to map of species observation in VA"""
    return f"https://ebird.org/ebird/map/{species_code}?neg=true&env.minX=-84.70&env.minY=36.20&env.maxX=-70.95&env.maxY=37.22&zh=true&gp=true&ev=Z&mr=1-12&bmo=1&emo=12&yr=all"


def ebird_chart_link(species_code: str) -> str:
    """Create link to chart of species observation occurrence in VA"""
    return f"https://ebird.org/ebird/GuideMe?cmd=decisionPage&speciesCodes={species_code}&getLocations=states&states=US-VA&bYear=1900&eYear=Cur&bMonth=1&eMonth=12&reportType=species&parentState=US-VA"
