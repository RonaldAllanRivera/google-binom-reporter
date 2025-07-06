# backend/reports/report_service.py
from .binom_service import fetch_binom_data as fetch_binom_data_from_binom_module

def fetch_binom_data(
    start_date,
    end_date,
    timezone="America/Atikokan",
    traffic_source_ids="1,6",
    date_type="custom-time"
):
    return fetch_binom_data_from_binom_module(
        start_date,
        end_date,
        timezone,
        traffic_source_ids,
        date_type
    )
