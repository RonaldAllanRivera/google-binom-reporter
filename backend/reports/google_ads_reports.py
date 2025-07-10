import logging
from django.conf import settings
from google.ads.googleads.errors import GoogleAdsException
from .google_ads_client import load_google_ads_client

def fetch_all_client_campaign_costs(refresh_token, start_date, end_date):
    all_accounts = get_all_accounts_in_hierarchy(refresh_token)
    all_costs = []
    for account_info in all_accounts:
        if not account_info.get("is_manager"):
            customer_id = account_info["customer_id"]
            parent_id = account_info["parent_id"]
            costs = fetch_campaign_costs(
                refresh_token=refresh_token,
                customer_id=customer_id,
                parent_id=parent_id,
                start_date=start_date,
                end_date=end_date
            )
            if costs:
                all_costs.extend(costs)
    filtered_costs = [cost for cost in all_costs if cost['Cost'] > 0]
    filtered_costs.sort(key=lambda x: (x['Account'], x['Campaign']))
    return filtered_costs


def fetch_campaign_costs(refresh_token, customer_id, parent_id, start_date, end_date):
    logger = logging.getLogger(__name__)
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
        logger.info(f"No campaign data for customer_id {customer_id} (likely a manager account).")
    except Exception as e:
        logger.error(f"An unexpected error occurred for customer_id {customer_id}: {e}", exc_info=True)
    return results


def get_all_accounts_in_hierarchy(refresh_token, root_cid=None, max_accounts=200):
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

    def _walk_account_tree(parent_id):
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
                    all_accounts.append({
                        "customer_id": child_cid,
                        "parent_id": parent_id,
                        "descriptive_name": desc_name,
                        "is_manager": is_manager
                    })
                    if is_manager:
                        _walk_account_tree(child_cid)
        except Exception as e:
            logger.error(f"Error discovering children for {parent_id}: {e}", exc_info=True)

    _walk_account_tree(root_cid)
    root_name = "Unknown Root Manager"
    try:
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
        "parent_id": None,
        "descriptive_name": root_name,
        "is_manager": True
    })
    logger.info(f"Discovered {len(all_accounts)} accounts in total (limit was {max_accounts})")
    unique_accounts = list({v['customer_id']: v for v in all_accounts}.values())
    logger.info(f"Returning {len(unique_accounts)} unique accounts.")
    return unique_accounts
