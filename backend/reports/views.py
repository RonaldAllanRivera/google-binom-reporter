# backend/reports/views.py
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
import logging
from .google_auth_service import build_auth_url, exchange_code_for_tokens, fetch_all_client_campaign_costs
from .models import GoogleAccount
from .report_service import fetch_binom_data
from .permissions import IsGoogleOrSuperuser


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
                    frontend_callback_url = f'{settings.FRONTEND_URL}/auth/google/callback?email={user_email}'
                    return redirect(frontend_callback_url)
    except Exception as e:
        logger.error(f"Database error while processing Google account for {user_email}: {e}", exc_info=True)
        return Response({"error": "A database error occurred while processing the Google account.", "details": str(e)}, status=500)

    # Log the user in to create a session
    try:
        user, created = User.objects.get_or_create(
            username=user_email,
            defaults={'email': user_email}
        )
        if created:
            user.set_unusable_password()
            user.save()
        
        login(request, user)
        logger.info(f"Successfully logged in and created session for user: {user_email}")

    except Exception as e:
        logger.error(f"Failed to create session for user {user_email}: {e}", exc_info=True)
        # Don't block the process if session creation fails, but log it as a critical issue.

    # Redirect back to the frontend callback page with the user's email
    frontend_callback_url = f'{settings.FRONTEND_URL}/auth/google/callback?email={user_email}'
    return redirect(frontend_callback_url)

@api_view(['GET'])
@permission_classes([IsGoogleOrSuperuser])
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
    
    # Filter, transform, and sort the data
    if isinstance(binom_data, list):
        # First filter and transform the data
        filtered_data = [
            {
                'id': item.get('id'),
                'name': item.get('name'),
                'leads': item.get('leads', '0'),
                'revenue': item.get('revenue', '0')
            }
            for item in binom_data 
            if item.get('revenue') != "0" or item.get('leads') != "0"
        ]
        # Then sort by name (case-insensitive)
        filtered_data.sort(key=lambda x: str(x.get('name', '')).lower())
        return Response(filtered_data)
    
    return Response(binom_data)

@api_view(['GET'])
@permission_classes([IsGoogleOrSuperuser])
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

from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import redirect
import os

@api_view(['GET'])
@permission_classes([IsGoogleOrSuperuser])
def combined_report_view(request):
    """
    Combined report: merges Binom and Google Ads data, stores result, pushes to Google Sheets, returns local table and sheet URLs.
    Accepts: start_date, end_date (YYYY-MM-DD)
    """
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    # Constants from .env or settings
    EMAIL = getattr(settings, 'GOOGLE_ACCOUNT_EMAIL', os.environ.get('GOOGLE_ACCOUNT_EMAIL'))
    TRAFFIC_SOURCE_IDS = getattr(settings, 'TRAFFIC_SOURCE_IDS', os.environ.get('TRAFFIC_SOURCE_IDS', '1,6'))
    TIMEZONE = getattr(settings, 'DEFAULT_TIMEZONE', os.environ.get('DEFAULT_TIMEZONE', 'America/Atikokan'))
    DATE_TYPE = getattr(settings, 'DEFAULT_DATE_TYPE', os.environ.get('DEFAULT_DATE_TYPE', 'custom-time'))

    # 1. Fetch Binom data
    binom_data = fetch_binom_data(
        start_date,
        end_date,
        TIMEZONE,
        TRAFFIC_SOURCE_IDS,
        DATE_TYPE
    )
    # 2. Fetch Google Ads data
    account = GoogleAccount.objects.filter(user_email=EMAIL).first()
    if not account or not account.refresh_token:
        return Response({"error": "."}, status=400)
    google_ads_data = fetch_all_client_campaign_costs(account.refresh_token, start_date, end_date)

    # 3. Merge/align data by campaign ID and name
    import re
    
    def normalize_campaign_name(name):
        """Normalize campaign name by removing the domain part and extra spaces"""
        if not name:
            return ''
        # Remove anything in parentheses (domain part)
        name = re.sub(r'\([^)]*\)', '', str(name))
        # Remove extra spaces and trim
        return ' '.join(name.split()).strip()
    
    def extract_campaign_id(s):
        if not s:
            return None
        # Look for patterns like 250417_02
        match = re.search(r'(\d{6}_\d{2})', str(s))
        return match.group(1) if match else None
    
    def get_campaign_key(campaign_name):
        """Create a consistent key for matching campaigns"""
        if not campaign_name:
            return None
        # Extract the campaign ID if exists
        cid = extract_campaign_id(campaign_name)
        if cid:
            return cid
        # If no ID, use the normalized campaign name
        return normalize_campaign_name(campaign_name)

    # Prepare Binom dict: {campaign_key: row}
    binom_rows = binom_data['data'] if isinstance(binom_data, dict) and 'data' in binom_data else binom_data
    binom_lookup = {}
    for row in binom_rows or []:
        campaign_name = row.get('name', '')
        key = get_campaign_key(campaign_name)
        if key:
            binom_lookup[key] = row

    # Prepare Google Ads dict: {campaign_key: row}
    google_rows = google_ads_data['data'] if isinstance(google_ads_data, dict) and 'data' in google_ads_data else google_ads_data
    google_lookup = {}
    for row in google_rows or []:
        campaign_name = row.get('Campaign', '')
        key = get_campaign_key(campaign_name)
        if key:
            google_lookup[key] = row

    # Merge by campaign key (ID or normalized name)
    combined_rows = []
    matched_keys = set()
    
    # First, process all campaigns that exist in both Binom and Google Ads
    common_keys = set(binom_lookup.keys()) & set(google_lookup.keys())
    for key in common_keys:
        binom_row = binom_lookup[key]
        google_row = google_lookup[key]
        
        # Get account name from Google or extract from campaign name
        account_name = google_row.get('Account', '')
        if not account_name and ' - ' in str(binom_row.get('name', '')):
            account_name = str(binom_row.get('name', '')).split(' - ')[0].strip()
            
        campaign_name = binom_row.get('name', '')
        # Remove domain part if exists
        campaign_name = campaign_name.split(' (')[0].strip()
        
        total_spend = float(google_row.get('Cost', 0))
        revenue = float(binom_row.get('revenue', 0))
        sales = binom_row.get('leads', '0')
        
        # Calculate P/L and ROI
        pl_value = revenue - total_spend
        roi_value = ((revenue / total_spend) - 1) if total_spend else 0
        
        combined_rows.append({
            'ACCOUNT NAME': account_name,
            'CAMPAIGN NAME': campaign_name,
            'TOTAL SPEND': total_spend,
            'REVENUE': revenue,
            'P/L': pl_value,
            'P/L_FORMULA': f'=D{len(combined_rows) + 2}-C{len(combined_rows) + 2}',
            'ROI': f'{roi_value:.2%}' if total_spend else '',
            'ROI_VALUE': roi_value if total_spend else 0,
            'ROI_FORMULA': f'=(D{len(combined_rows) + 2}/C{len(combined_rows) + 2})-1' if total_spend else '',
            'SALES': sales
        })
        matched_keys.add(key)
    
    # Add Binom-only campaigns (present in Binom but not in Google Ads)
    binom_only_keys = set(binom_lookup.keys()) - matched_keys
    for key in binom_only_keys:
        binom_row = binom_lookup[key]
        campaign_name = binom_row.get('name', '')
        
        # Extract account name from campaign name if it follows the pattern
        account_name = ''
        if ' - ' in str(campaign_name):
            account_name = str(campaign_name).split(' - ')[0].strip()
        
        # Remove domain part if exists
        campaign_name = campaign_name.split(' (')[0].strip()
        
        total_spend = 0
        revenue = float(binom_row.get('revenue', 0))
        sales = binom_row.get('leads', '0')
        
        combined_rows.append({
            'ACCOUNT NAME': account_name,
            'CAMPAIGN NAME': campaign_name,
            'TOTAL SPEND': total_spend,
            'REVENUE': revenue,
            'P/L': revenue,  # P/L is same as revenue when spend is 0
            'P/L_FORMULA': f'=D{len(combined_rows) + 2}-C{len(combined_rows) + 2}',
            'ROI': '',  # No ROI when there's no spend
            'ROI_VALUE': 0,
            'ROI_FORMULA': '',
            'SALES': sales
        })
    
    # Add Google Ads-only campaigns (present in Google but not in Binom)
    google_only_keys = set(google_lookup.keys()) - matched_keys
    for key in google_only_keys:
        google_row = google_lookup[key]
        campaign_name = google_row.get('Campaign', '')
        
        # Extract account name from Google data or campaign name
        account_name = google_row.get('Account', '')
        if not account_name and ' - ' in str(campaign_name):
            account_name = str(campaign_name).split(' - ')[0].strip()
        
        # Remove domain part if exists
        campaign_name = campaign_name.split(' (')[0].strip()
        
        total_spend = float(google_row.get('Cost', 0))
        revenue = 0  # No revenue data from Google Ads
        
        combined_rows.append({
            'ACCOUNT NAME': account_name,
            'CAMPAIGN NAME': campaign_name,
            'TOTAL SPEND': total_spend,
            'REVENUE': revenue,
            'P/L': -total_spend,  # Negative P/L when there's no revenue
            'P/L_FORMULA': f'=D{len(combined_rows) + 2}-C{len(combined_rows) + 2}',
            'ROI': '-100.00%',  # -100% ROI when there's no revenue
            'ROI_VALUE': -1,
            'ROI_FORMULA': f'=(D{len(combined_rows) + 2}/C{len(combined_rows) + 2})-1',
            'SALES': '0'  # No sales data from Google Ads
        })
    # Columns for frontend DataGrid
    columns = [
        {"field": "ACCOUNT NAME", "headerName": "ACCOUNT NAME", "width": 180},
        {"field": "CAMPAIGN NAME", "headerName": "CAMPAIGN NAME", "width": 300},
        {"field": "TOTAL SPEND", "headerName": "TOTAL SPEND", "width": 130},
        {"field": "REVENUE", "headerName": "REVENUE", "width": 130},
        {"field": "P/L", "headerName": "P/L", "width": 120},
        {"field": "ROI", "headerName": "ROI", "width": 120},
        {"field": "SALES", "headerName": "SALES", "width": 100}
    ]
    # Sort by ACCOUNT NAME, then by CAMPAIGN NAME (both case-insensitive)
    combined_rows.sort(key=lambda x: (str(x.get('ACCOUNT NAME', '')).lower(), str(x.get('CAMPAIGN NAME', '')).lower()))
    # Add id for DataGrid
    for i, row in enumerate(combined_rows):
        row['id'] = i

    # 4. Store in DB (stub)
    # TODO: Implement DB storage for historical/ROI

    # 5. Push to Google Sheets (stub)
    sheet_url = None
    sheet_preview_url = None
    # TODO: Implement Google Sheets API integration

    # 6. Return data
    # Clean and filter combined_rows before returning
    cleaned_rows = []
    for row in combined_rows:
        # Exclude if both ACCOUNT NAME and CAMPAIGN NAME are empty
        if not str(row.get("ACCOUNT NAME", "")).strip() and not str(row.get("CAMPAIGN NAME", "")).strip():
            continue
        # Exclude if both TOTAL SPEND and REVENUE are zero
        try:
            spend = float(row.get("TOTAL SPEND", 0))
            revenue = float(row.get("REVENUE", 0))
        except (TypeError, ValueError):
            spend = revenue = 0
        if spend == 0 and revenue == 0:
            continue
        # Remove formula fields and ROI_VALUE
        cleaned_row = {k: v for k, v in row.items() 
                     if k not in ['P/L_FORMULA', 'ROI_FORMULA', 'ROI_VALUE', 'id']}
        cleaned_rows.append(cleaned_row)
    
    # 4. Sort the cleaned rows by Account and Campaign name
    cleaned_rows.sort(key=lambda x: (
        str(x.get('ACCOUNT NAME', '')).lower(),
        str(x.get('CAMPAIGN NAME', '')).lower()
    ))
    
    # 5. Format the final output as specified
    final_output = []
    for row in cleaned_rows:
        final_output.append({
            'Account': row.get('ACCOUNT NAME', ''),
            'Campaign': row.get('CAMPAIGN NAME', '').split(' (')[0],  # Remove domain part if exists
            'Total Spend': row.get('TOTAL SPEND', 0),
            'Revenue': row.get('REVENUE', 0),
            'Sales': row.get('SALES', 0)
        })
    
    return Response({
        'data': final_output,
        'start_date': start_date,
        'end_date': end_date,
        'total_rows': len(final_output)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_status_view(request):
    return Response({'email': request.user.email})

@api_view(['GET'])
@permission_classes([IsGoogleOrSuperuser])
def google_ads_manager_check(request):
    """
    Lists all accounts in the hierarchy, including their name, ID, parent, and manager status.
    This is a diagnostic endpoint to verify account discovery.
    Usage: /api/google-ads/manager-check/?email=your-email@example.com
    """
    email = request.GET.get("email")
    if not email:
        return Response({"error": "Email parameter is required."}, status=400)
    try:
        account = GoogleAccount.objects.get(user_email=email)
    except GoogleAccount.DoesNotExist:
        return Response({"error": f"GoogleAccount not found for email: {email}."}, status=404)

    # Use the enhanced function that gets all accounts and their details.
    from .google_auth_service import get_all_accounts_in_hierarchy
    all_accounts = get_all_accounts_in_hierarchy(account.refresh_token)
    
    return Response(all_accounts)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Log out the current user by ending their session.
    This will invalidate the session cookie on the client side.
    """
    logout(request)
    response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
    # Clear the session cookie
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path=settings.SESSION_COOKIE_PATH,
        domain=settings.SESSION_COOKIE_DOMAIN,
    )
    
    # Clear CSRF token cookie
    response.delete_cookie(
        key='csrftoken',
        path='/',
        domain=settings.SESSION_COOKIE_DOMAIN,
    )
    
    return response
