# backend/reports/google_auth_service.py
# Refactored: This file now imports and exposes functions from auth_utils, google_ads_client, and google_ads_reports modules.
from .auth_utils import build_auth_url, exchange_code_for_tokens
from .google_ads_client import load_google_ads_client
from .google_ads_reports import (
    fetch_all_client_campaign_costs,
    fetch_campaign_costs,
    get_all_accounts_in_hierarchy
)

# The implementations are now in their respective modules for clarity and maintainability.    return unique_accounts
