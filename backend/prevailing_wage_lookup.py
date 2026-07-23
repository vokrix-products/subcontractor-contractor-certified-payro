# Hardcoded prevailing wage dataset for demo purposes.
# In production this would integrate with a state/federal wage determination database.
PREVAILING_WAGES = {
    # County -> classification -> {base_rate, fringe_rate}
    "cook county": {
        "carpenter": {"base_rate": 42.00, "fringe_rate": 9.50},
        "electrician": {"base_rate": 50.00, "fringe_rate": 11.00},
        "laborer": {"base_rate": 35.00, "fringe_rate": 7.25},
    },
    "dupage county": {
        "carpenter": {"base_rate": 44.00, "fringe_rate": 10.00},
        "electrician": {"base_rate": 52.00, "fringe_rate": 12.00},
    },
}

def get_prevailing_wage(county, classification):
    """
    Returns prevailing wage dict for given county and classification, or None if not found.
    Case‑insensitive matching.
    """
    county_key = county.strip().lower()
    class_key = classification.strip().lower()
    county_data = PREVAILING_WAGES.get(county_key)
    if county_data:
        return county_data.get(class_key)
    return None
