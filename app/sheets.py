import pandas as pd
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_service():
    creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON"))
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

PILOT_SHEET_ID = "1LpW2Ff2OGDRceSzg5Hwc0mSfI_CZMQOAaDr0bzaQM10"
DRONE_SHEET_ID = "1yYQ_WaK0H5NPMHPX0QH5NvMv02Dbqk0LtoMv_DQiZSE"
MISSION_SHEET_ID = "1eDwqUpzJtuXH9536-ND-J5rx-3nyGqQ9sUyGTNyaB-g"

def read_sheet(service, sheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()
    return result.get("values", [])

def to_dataframe(rows):
    """
    Convert Google Sheets rows to pandas DataFrame.
    First row = header.
    """
    if not rows:
        return pd.DataFrame()

    headers = rows[0]
    data = rows[1:]

    return pd.DataFrame(data, columns=headers)

def load_all_data():
    service = get_service()

    pilots_raw = read_sheet(service, PILOT_SHEET_ID, "Pilot_roster!A1:H")
    drones_raw = read_sheet(service, DRONE_SHEET_ID, "Drone_fleet!A1:G")
    missions_raw = read_sheet(service, MISSION_SHEET_ID, "Missions!A1:H")

    pilots_df = to_dataframe(pilots_raw)
    drones_df = to_dataframe(drones_raw)
    missions_df = to_dataframe(missions_raw)

    return {
        "pilots": pilots_df,
        "drones": drones_df,
        "missions": missions_df
    }
