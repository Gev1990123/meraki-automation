import re

site_info = {
    "Birmingham":{
        "site_code": "BRM",
        "description": "Birmingham Site",
    },

    "Newcastle":{
        "site_code": "NWC",
        "description": "Newcastle Site"
    },

    "Shak Dev":{
        "site_code": "SW-EXE",
        "description": "Shak Development Site"
    },

    "Belfast":{
        "site_code": "BEL",
        "description": "Belfast Site"
    },

    "Cardiff":{
        "site_code": "CAR",
        "description": "Cardiff Site"
    },

        "Exeter":{
        "site_code": "EXE",
        "description": "Exeter Site"
    },

        "Glasgow":{
        "site_code": "GLA",
        "description": "Glasgow Site"
    },

    "Leeds":{
        "site_code": "LDS",
        "description": "Leeds Site"
    },

        "London":{
        "site_code": "LON",
        "description": "London Site"
    },

        "Newtown":{
        "site_code": "NWT",
        "description": "Newtown Site"
    },

}

site_codes = {
    "BRM": "Birmingham",
    "NWC": "Newcastle",
    "EXE-MER01": "Shak Dev",
    "BEL": "Belfast",
    "CAR": "Cardiff",
    "EXE": "Exeter",
    "GLA": "Glasgow",
    "LDS": "Leeds",
    "LON": "London",
    "NWT": "Newtown",
    "Matt": "Birmingham",
}


def get_site_info_from_network(network_name: str):
    for pattern, site_key in site_codes.items():
        if re.search(pattern, network_name, re.IGNORECASE):
            return site_info.get(site_key)
    return None