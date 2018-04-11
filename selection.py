import numpy as np
import warnings, random, yaml, datetime, pickle, os, gspread, sys
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('group_meeting.json',scope)
clients = gspread.authorize(creds)


def groupmeeting_time(week=4):
    """http://stackoverflow.com/a/6558571"""
    today = datetime.date.today()
    weekday = 0  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += week*7
    return today + datetime.timedelta(days_ahead)

def read_poll(list_name, response = 'Yes'):
	'''
	This function reads the poll and returns the the list of names as output
	Input: 
		list_name is the poll name
	         	response is the key word to check
	output:
		list of names
	'''

	names_list = []
	sheet = clients.open(list_name).sheet1
	mems_list = sheet.get_all_records()
	for ll in mems_list:
		ll[date] = ll[date].strip()
		if ll[date] == response:
			names_list.append(ll['Name'])
	return names_list

# read members list
with open('members.yaml', 'r') as fd:
	members = yaml.load(fd)
members = pd.DataFrame.from_dict(members).T
# get the date for which we need group meeting speakers
try:
	date = sys.argv[1]
	date = datetime.datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
	print('Pleas make sure that date format is "%d-%m-%Y"')
except:
	with open('selected_presenters.yaml', 'r') as fd:
		presenters = yaml.load(fd)
	pre_selected_date = sorted(presenters.keys())[-1]
	date = datetime.datetime.strptime(pre_selected_date,'%m/%d/%y')+datetime.timedelta(7)
	date = date.strftime("%d-%m-%Y")

# members.yaml is updated manually so for all the selected members above the current week +1 has to be added
with open('selected_presenters.yaml', 'r') as fd:
	selected_presenters = yaml.load(fd)
this_monday = groupmeeting_time(week=0).strftime("%m/%d/%y")
for k, l in iter(selected_presenters.items()):
	if k!=this_monday:
		for contribution in ('chairs', 'speakers'):
			names = l[contribution[:-1]]
			for name in names:
				members.loc[name][contribution] += 1

# Get list of volunteers if any
speakers_volunteer_list= read_poll('Speakers volunteers list')
organisers_volunteer_list = read_poll('Organisers volunteer List')
# Get lis to of absentees for that particular group meeting
absntees_list = read_poll('Attendee list', response = 'No')

# to make sure that volunteered speakers, organisers, and absntees are not randomly selected again 
members_not_to_consider = speakers_volunteer_list +organisers_volunteer_list + absntees_list

for nn in members_not_to_consider:
	members.loc[nn]['available'] = 0

members = members[members.available==1] 

number_of_speakers_volunteered = len(speakers_volunteer_list)
number_of_organisers_volunteered = len(organisers_volunteer_list)


number_of_speakers_needed = 2 - number_of_speakers_volunteered
number_of_orgnaisers_needed = 1 - number_of_speakers_volunteered
# Select speakers
pool_speakers = [];pool_organisers = []
cnt = 0
while len(pool_speakers) < number_of_speakers_needed:
	if cnt == 0:
		pool_speakers=list(set(members.query('speakers' + ' == @cnt').index))
	else:
		pool_speakers= pool_speakers + list(set(members.query('speakers' + ' == @cnt').index)) 
	cnt = cnt+1
speakers = random.sample(pool_speakers,number_of_speakers_needed)


cnt= 0
while len(pool_organisers)  < number_of_orgnaisers_needed:
	if cnt == 0:
		pool_organisers = list(set(members.query('chairs' + ' == @cnt').index))
	else:
		pool_organisers = pool_organisers + list(set(members.query('chairs' + ' == @cnt').index))
	cnt = cnt +1
organisers = random.sample(pool_organisers,number_of_orgnaisers_needed)
from IPython import embed;embed()
print organisers, speakers