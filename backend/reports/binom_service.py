# backend/reports/binom_service.py
import requests
from django.conf import settings
from urllib.parse import urlencode

BINOM_API_URL = settings.BINOM_API_URL
BINOM_API_KEY = settings.BINOM_API_KEY

def fetch_binom_data(
    start_date,
    end_date,
    timezone_value="America/Atikokan",
    traffic_source_ids="1,6",
    date_type="custom-time"
):
    date_from = f"{start_date} 00:00:00"
    date_to = f"{end_date} 23:59:59"
    params = [
        ('datePreset', 'custom_time'),
        ('dateType', date_type),
        ('dateFrom', date_from),
        ('dateTo', date_to),
        ('timezone', timezone_value)
    ]
    if ',' in str(traffic_source_ids):
        ids = [x.strip() for x in str(traffic_source_ids).split(',') if x.strip()]
        for tid in ids:
            params.append(('trafficSourceIds[]', tid))
    else:
        params.append(('trafficSourceIds[]', str(traffic_source_ids).strip()))

    headers = {
        "Api-Key": BINOM_API_KEY,
        "cache-control": "no-cache"
    }
    url = f"{BINOM_API_URL}?{urlencode(params, doseq=True)}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
