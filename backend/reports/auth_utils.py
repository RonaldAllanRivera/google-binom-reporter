import requests
import urllib.parse
import logging
from django.conf import settings


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
