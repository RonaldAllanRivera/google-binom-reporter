import re

def extract_campaign_id(name):
    """
    Extracts the campaign ID pattern like 250417_02 from campaign names.
    """
    match = re.search(r'(\d{6}_\d{2})', name)
    return match.group(1) if match else None
