from django.conf import settings
from google.ads.googleads.client import GoogleAdsClient

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
