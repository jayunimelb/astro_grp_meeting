 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('group_meeting.json',scope)
client = gspread.authorize(creds)
sheet = client.open('Volunteers list') .sheet1
vs = sheet.get_all_records()
from IPython import embed;embed()
print(vs)