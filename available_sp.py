import gspread
import yaml
import pandas as pd
import numpy as np
import sys
from oauth2client.service_account import ServiceAccountCredentials
from make_selection import groupmeeting_time
import datetime
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('group_meeting.json',scope)
clients = gspread.authorize(creds)

sheet = clients.open('Attendee list').sheet1
absentee_list = sheet.get_all_records()

try:
	date = sys.argv[1]
except:
	date = groupmeeting_time().strftime("%d-%m-%y")


with open('selected_presenters.yaml', 'r') as fd:
	presenters = yaml.load(fd)
pre_selected_date = sorted(presenters.keys())[-1]

date = datetime.datetime.strptime(pre_selected_date,'%m/%d/%y')+datetime.timedelta(7)
date = date.strftime("%d-%m-%Y")

with open('members.yaml', 'r') as fd:
	members = yaml.load(fd)

abs_names = []

for ll in absentee_list:
	if ll[date] == 'No':
		abs_names.append(ll['Name'])
member_names = list(members.keys())
for nn in member_names:
	if nn in abs_names:
		members[nn]['available'] = 0
	else:
		members[nn]['available'] = 1

with open('members.yaml', 'w') as fd:
	yaml.safe_dump(members, fd)