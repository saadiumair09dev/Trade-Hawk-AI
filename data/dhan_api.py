import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.dhan.co/v2/charts/intraday"

def get_data(security_id, interval="5"):
    try:
        token = st.secrets["dhan"]["token"]
        client_id = st.secrets["dhan"]["client_id"]

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }

        payload = {
            "securityId": security_id,
            "exchangeSegment": "IDX_I",
            "interval": interval
        }

        res = requests.post(BASE_URL, json=payload
