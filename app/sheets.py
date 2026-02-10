import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_service():
    creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON"))
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

# TODO: replace with your real spreadsheet IDs
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

def load_all_data():
    service = get_service()

    pilots = read_sheet(service, PILOT_SHEET_ID, "Pilot_roster!A1:H")
    drones = read_sheet(service, DRONE_SHEET_ID, "Drone_fleet!A1:G")
    missions = read_sheet(service, MISSION_SHEET_ID, "Missions!A1:H")

    return {
        "pilots": pilots,
        "drones": drones,
        "missions": missions
    }
