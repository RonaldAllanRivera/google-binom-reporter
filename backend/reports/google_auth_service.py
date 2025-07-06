# backend/reports/google_auth_service.py
import requests
from django.conf import settings
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import urllib.parse
import logging


def build_auth_url(request=None):
    """
    Returns the Google OAuth URL with the correct redirect_uri.
    If ?redirect=frontend is in the query params, use the frontend callback;
    otherwise, use the backend callback.
    """

    logger = logging.getLogger(__name__)
    use_frontend = False
    if request and hasattr(request, "GET"):
        use_frontend = request.GET.get("redirect") == "frontend"
    redirect_uri = settings.FRONTEND_OAUTH_REDIRECT_URI if use_frontend else settings.BACKEND_OAUTH_REDIRECT_URI
    logger.info(f"Google OAuth redirect_uri used: {redirect_uri}")

    # If used as a Django view, request will be passed; otherwise default to backend
    use_frontend = False
    if request and hasattr(request, "GET"):
        use_frontend = request.GET.get("redirect") == "frontend"

    redirect_uri = settings.FRONTEND_OAUTH_REDIRECT_URI if use_frontend else settings.BACKEND_OAUTH_REDIRECT_URI

    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/adwords",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "consent"
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params, safe=":/ ")
    return url


def exchange_code_for_tokens(code, redirect="backend"):
    from django.conf import settings
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    if redirect == "frontend":
        redirect_uri = settings.FRONTEND_OAUTH_REDIRECT_URI
    else:
        redirect_uri = settings.BACKEND_OAUTH_REDIRECT_URI

    url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    tokens_data = response.json()

    access_token = tokens_data.get("access_token")
    if not access_token:
        raise ValueError("Access token not found in Google's token response.")

    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo_response.raise_for_status()
    userinfo = userinfo_response.json()
    user_email = userinfo.get("email")
    if not user_email:
        raise ValueError("Email not found in Google userinfo response.")
    tokens_data["user_email"] = user_email
    return tokens_data

def load_google_ads_client(refresh_token, login_customer_id=None):
    credentials_dict = {
        "developer_token": settings.GOOGLE_DEVELOPER_TOKEN,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "use_proto_plus": True,
    }
    login_cid = login_customer_id or getattr(settings, 'GOOGLE_LOGIN_CUSTOMER_ID', None)
    if login_cid and str(login_cid).isdigit():
        credentials_dict["login_customer_id"] = str(login_cid)
    client = GoogleAdsClient.load_from_dict(credentials_dict, version="v18")
    return client



def fetch_all_client_campaign_costs(refresh_token, start_date, end_date):
    # The hierarchy function now returns all necessary details, including the 'is_manager' flag.
    all_accounts = get_all_accounts_in_hierarchy(refresh_token)


    
    all_costs = []
    # Sequentially process each client to avoid overwhelming the API
    for account_info in all_accounts:
        # The crucial fix: Only request metrics for accounts that are NOT managers.
        if not account_info.get("is_manager"):
            customer_id = account_info["customer_id"]
            parent_id = account_info["parent_id"]
            
            costs = fetch_campaign_costs(refresh_token=refresh_token, 
                                         customer_id=customer_id, 
                                         parent_id=parent_id,
                                         start_date=start_date, 
                                         end_date=end_date)
            
            if costs:
                all_costs.extend(costs)
    
    # Filter out campaigns with zero cost (already handled in fetch_campaign_costs, but good for safety)
    filtered_costs = [cost for cost in all_costs if cost['Cost'] > 0]
    # Sort the results by Account and then by Campaign name
    filtered_costs.sort(key=lambda x: (x['Account'], x['Campaign']))
    return filtered_costs


def fetch_campaign_costs(refresh_token, customer_id, parent_id, start_date, end_date):
    logger = logging.getLogger(__name__)
    # Use the top-level manager ID from settings for login_customer_id
    client = load_google_ads_client(refresh_token, login_customer_id=str(settings.GOOGLE_LOGIN_CUSTOMER_ID))
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            customer.descriptive_name,
            campaign.name,
            metrics.cost_micros
        FROM
            campaign
        WHERE
            segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND metrics.cost_micros > 0
    """
    results = []
    try:
        stream = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in stream:
            for row in batch.results:
                results.append({
                    "Account": row.customer.descriptive_name,
                    "Campaign": row.campaign.name,
                    "Cost": round(row.metrics.cost_micros / 1_000_000, 2),
                })
    except GoogleAdsException as ex:
        # This is expected for manager accounts which don't have campaign data.
        logger.info(f"No campaign data for customer_id {customer_id} (likely a manager account).")
    except Exception as e:
        logger.error(f"An unexpected error occurred for customer_id {customer_id}: {e}", exc_info=True)
    return results


def get_all_accounts_in_hierarchy(refresh_token, root_cid=None, max_accounts=200):
    """
    Recursively retrieves ALL accounts under a manager account, including other managers.
    This is more robust because manager accounts can also have their own campaigns.
    """
    logger = logging.getLogger(__name__)
    client = load_google_ads_client(refresh_token)
    ga_service = client.get_service("GoogleAdsService")
    if not root_cid:
        root_cid = str(settings.GOOGLE_LOGIN_CUSTOMER_ID)
    query = """
        SELECT
            customer_client.client_customer,
            customer_client.manager,
            customer_client.descriptive_name
        FROM customer_client
        WHERE customer_client.level = 1 AND customer_client.status = 'ENABLED'
    """
    all_accounts = []
    visited_managers = set()

    def walk(parent_id):
        nonlocal all_accounts
        if len(all_accounts) >= max_accounts or parent_id in visited_managers:
            return
        visited_managers.add(parent_id)

        try:
            search_request = ga_service.search_stream(customer_id=parent_id, query=query)
            for batch in search_request:
                for row in batch.results:
                    if len(all_accounts) >= max_accounts:
                        return
                    
                    child_cid = row.customer_client.client_customer.split('/')[-1]
                    is_manager = row.customer_client.manager
                    desc_name = row.customer_client.descriptive_name
                    logger.debug(f"Discovered account: {child_cid} (desc: {desc_name}) under parent {parent_id} - is_manager: {is_manager}")

                    if child_cid == parent_id:
                        continue

                    # Add the discovered account to our list.
                    all_accounts.append({
                        "customer_id": child_cid,
                        "parent_id": parent_id,
                        "descriptive_name": desc_name,
                        "is_manager": is_manager
                    })

                    # If it's a manager, we also need to walk its children.
                    if is_manager:
                        walk(child_cid)
        except Exception as e:
            logger.error(f"Error discovering children for {parent_id}: {e}", exc_info=True)

    # Start the recursive walk from the root manager.
    walk(root_cid)
    
    # Finally, add the root manager account itself to the list, as it could also have campaigns.
    root_name = "Unknown Root Manager"
    try:
        # Query for the root manager's name
        root_details_query = f"SELECT customer.descriptive_name FROM customer WHERE customer.id = '{root_cid}'"
        stream = ga_service.search_stream(customer_id=root_cid, query=root_details_query)
        for batch in stream:
            for row in batch.results:
                root_name = row.customer.descriptive_name
                break
            break
    except Exception as e:
        logger.error(f"Could not fetch root manager name for {root_cid}: {e}", exc_info=True)

    all_accounts.append({
        "customer_id": root_cid,
        "parent_id": None,  # It has no parent in this context
        "descriptive_name": root_name,
        "is_manager": True # The root of the hierarchy is always a manager
    })
    
    logger.info(f"Discovered {len(all_accounts)} accounts in total (limit was {max_accounts})")
    # To avoid duplicates if the root is somehow also a child
    unique_accounts = list({v['customer_id']:v for v in all_accounts}.values())
    logger.info(f"Returning {len(unique_accounts)} unique accounts.")
    return unique_accounts
