# backend/reports/views.py
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import logging
from .google_auth_service import build_auth_url, exchange_code_for_tokens, fetch_all_client_campaign_costs
from .models import GoogleAccount
from .report_service import fetch_binom_data


logger = logging.getLogger(__name__)

@api_view(['GET'])
def google_auth_url(request):
    url = build_auth_url(request)
    return Response({'auth_url': url})

@api_view(['GET'])
def google_auth_callback(request):
    """
    API endpoint for Google OAuth2 authorization callback.

    This endpoint is called automatically by Google after a user authenticates via the OAuth consent screen.
    It exchanges the received `code` for OAuth tokens, retrieves the user's email, and stores or updates the user's GoogleAccount credentials in the database.

    - Accepts:
        - code (OAuth2 authorization code, from Google)
    - On success: Registers or updates the user's refresh token for future API access, and returns the email.
    - On failure: Returns a detailed error message for UI or backend debugging.

    This endpoint is for internal use only, and is never called directly by users.
    It is only used as the callback URL for Google's OAuth2 flow, triggered by `/api/auth/google/`.

    Example flow:
        1. Frontend redirects user to /api/auth/google/
        2. User authenticates with Google and is redirected back to /api/auth/google/callback/?code=...
        3. This endpoint stores/updates the refresh token and user email for future use.

    Only employees of LogicMedia BV should ever authorize via this flow.
    """    
    code = request.GET.get("code")
    redirect_param = request.GET.get("redirect") or "backend"

    if not code:
        return Response({"error": "Authorization code not found in callback."}, status=400)

    try:
        tokens = exchange_code_for_tokens(code, redirect=redirect_param)
    except requests.exceptions.HTTPError as e:
        error_detail = "Unknown error from Google."
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        return Response({"error": "Failed to exchange code for tokens with Google.", "details": error_detail}, status=e.response.status_code if e.response else 400)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Token exchange error: {e}", exc_info=True)
        return Response({"error": "An unexpected error occurred during token exchange.", "details": str(e)}, status=500)
    
    user_email = tokens.get("user_email")
    if not user_email:
        return Response({"error": "Could not retrieve user email from Google's token response."}, status=400)

    new_refresh_token = tokens.get("refresh_token")
    try:
        with transaction.atomic():
            account = GoogleAccount.objects.filter(user_email=user_email).first()
            if account:
                if new_refresh_token:
                    account.refresh_token = new_refresh_token
                    account.save()
                message = "Google account re-authorized successfully."
            else:
                if new_refresh_token:
                    GoogleAccount.objects.create(user_email=user_email, refresh_token=new_refresh_token)
                    message = "Google account authorized and created successfully."
                else:
                    return Response({
                        "error": "Authorization succeeded, but no refresh token was provided by Google."
                    }, status=400)
    except Exception as e:
        logger.error(f"Database error while processing Google account for {user_email}: {e}", exc_info=True)
        return Response({"error": "A database error occurred while processing the Google account.", "details": str(e)}, status=500)

    return Response({
        "message": message,
        "email": user_email
    })

@api_view(['GET'])
def generate_report(request):
    """
    API endpoint for internal use only.

    Returns a raw Binom campaign report for a given date range and filter criteria.
    The output is an exact pass-through of the Binom API response (same as Binom admin/Postman).
    No additional filtering, merging, or transformation is performed.

    - Accepts:
        - start_date / dateFrom (YYYY-MM-DD)
        - end_date / dateTo (YYYY-MM-DD)
        - timezone (IANA TZ, e.g. America/Atikokan; default)
        - trafficSourceIds (comma-separated, e.g. "1,6")
        - dateType (default: "custom-time")
    - Response: JSON object of Binom API report data (campaigns, leads, revenue, etc).
    - Used for verifying connectivity/parity with Binom, or for building custom reporting pipelines.

    Example:
      GET /api/report/generate/?start_date=2025-05-01&end_date=2025-05-31&trafficSourceIds=1,6&dateType=custom-time&timezone=America/Atikokan

    This endpoint is intended for backend/reporting automation within LogicMedia BV only.
    """
    start_date = request.GET.get("start_date") or request.GET.get("dateFrom")
    end_date = request.GET.get("end_date") or request.GET.get("dateTo")
    timezone_value = request.GET.get("timezone") or request.GET.get("dateTimeZone") or "America/Atikokan"
    traffic_source_ids = request.GET.get("trafficSourceIds", "1,6")
    date_type = request.GET.get("dateType", "custom-time")

    binom_data = fetch_binom_data(
        start_date,
        end_date,
        timezone_value,
        traffic_source_ids,
        date_type
    )
    return Response(binom_data)

@api_view(['GET'])
def google_ads_test_view(request):
    """
    Returns Google Ads cost/campaign data for all enabled accounts (or one customer_id if provided).
    Always uses the immediate parent as login_customer_id to avoid MCC permission errors.
    """
    email = request.query_params.get('email')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not email or not start_date or not end_date:
        return Response({"error": "Missing required query parameters: email, start_date, end_date"}, status=400)

    try:
        account = GoogleAccount.objects.get(user_email=email)
    except GoogleAccount.DoesNotExist:
        return Response({"error": "Google account not found for this email."}, status=404)

    if not account.refresh_token:
        return Response({"error": "No refresh token found for this account. Please re-authenticate."}, status=400)

    # The main service function now handles the entire process of fetching and aggregating costs.
    all_costs = fetch_all_client_campaign_costs(account.refresh_token, start_date, end_date)
    
    return Response(all_costs)

@api_view(['GET'])
def google_ads_manager_check(request):
    """
    Lists all accounts in the hierarchy, including their name, ID, parent, and manager status.
    This is a diagnostic endpoint to verify account discovery.
    Usage: /api/google-ads/manager-check/?email=allan@logicmedia.be
    """
    email = request.GET.get("email")
    if not email:
        return Response({"error": "Email parameter is required."}, status=400)
    try:
        account = GoogleAccount.objects.get(user_email=email)
    except Exception as e:
        return Response({"error": f"GoogleAccount not found for email: {email}. {str(e)}"}, status=404)

    # Use the enhanced function that gets all accounts and their details.
    from .google_auth_service import get_all_accounts_in_hierarchy
    all_accounts = get_all_accounts_in_hierarchy(account.refresh_token, max_accounts=9999)
    
    # The function already returns a list of dicts with all the needed info.
    # We can just return it directly.
    return Response(all_accounts)
