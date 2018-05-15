import numpy as np
import warnings, random, yaml, datetime, pickle, os, gspread, sys, argparse
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('group_meeting.json',scope)
clients = gspread.authorize(creds)
no_of_speakers_meeting = 2
no_of_organisers_meeting = 1 

def groupmeeting_time(week=4):
    """http://stackoverflow.com/a/6558571"""
    today = datetime.date.today()
    weekday = 0  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += week*7
    return today + datetime.timedelta(days_ahead)

def read_poll(list_name, date, response = 'Yes'):
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
	date = date.strftime("%d-%m-%Y")
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


with open('presenters_log.yaml', 'r') as fd:
	presenters_log = yaml.load(fd)
pre_selected_date = sorted(presenters_log.keys())[-1]
date = datetime.datetime.strptime(pre_selected_date,'%m/%d/%y')+datetime.timedelta(7)

# members.yaml is updated manually so for all the selected members above the current week +1 has to be added
this_monday = groupmeeting_time(week=0).strftime("%m/%d/%y")
this_friday = groupmeeting_time(week=0) + datetime.timedelta(4)


for k, l in iter(presenters_log.items()):
	if k>this_monday:
		for contribution in ('chairs', 'speakers'):
			names = l[contribution[:-1]]
			for name in names:
				members.loc[name][contribution] += 1

# Get list of volunteers if any
speakers_volunteer_list= read_poll('Speakers volunteers list',date)
organisers_volunteer_list = read_poll('Organisers volunteer List',date)
# Get lis to of absentees for that particular group meeting
absntees_list = read_poll('Attendee list', date, response = 'No')

# to make sure that volunteered speakers, organisers, and absntees are not randomly selected again 
members_not_to_consider = speakers_volunteer_list +organisers_volunteer_list + absntees_list
for nn in members_not_to_consider:
	members.loc[nn]['available'] = 0

pool_members = members[members.available==1] 

number_of_speakers_volunteered = len(speakers_volunteer_list)
number_of_organisers_volunteered = len(organisers_volunteer_list)


number_of_speakers_needed = no_of_speakers_meeting - number_of_speakers_volunteered  
number_of_orgnaisers_needed = no_of_organisers_meeting - number_of_organisers_volunteered
# Select speakers
pool_speakers = [];pool_organisers = []
cnt = 0
while len(pool_speakers) < number_of_speakers_needed:
	if cnt == 0:
		# select members with lowest contribution
		pool_speakers=list(set(pool_members.query('speakers' + ' == @cnt').index))
	else:	
		# if the list selected doesn't sufficient members update it.
		pool_speakers= pool_speakers + list(set(pool_members.query('speakers' + ' == @cnt').index)) 
	cnt = cnt+1
speakers = random.sample(pool_speakers,number_of_speakers_needed)

# select organisers

cnt= 0
while len(pool_organisers)  < number_of_orgnaisers_needed:
	if cnt == 0:
		# select members with lowest contribution
		pool_organisers = list(set(pool_members.query('chairs' + ' == @cnt').index))
	else:
		# if the list selected doesn't sufficient members update it.
		pool_organisers = pool_organisers + list(set(pool_members.query('chairs' + ' == @cnt').index))  
	cnt = cnt +1
organisers = random.sample(pool_organisers,number_of_orgnaisers_needed)

if len(speakers_volunteer_list)>0:
	for ii in speakers_volunteer_list:
		speakers.append(ii)

if len(organisers_volunteer_list)>0:
	for ii in organisers_volunteer_list:
		organisers.append(ii)

# convert the date to format compatible for updating webpage
date_str = date.strftime("%m/%d/%y")
presenters_log[date_str] = {}
presenters_log[date_str]['chair']  = organisers
presenters_log[date_str]['speaker'] = speakers

with open('presenters_log.yaml', 'w') as fd:
	yaml.safe_dump(presenters_log, fd)

ff = open('email.txt','w')
#ff.write('emails of organiser and speakers \n%s %s %s\n'%(members.loc[organisers[0]]['email'], members.loc[speakers[0]]['email'], members.loc[speakers[1]]['email']))
ff.write('Subject: Group meeting on %s \n'%(date.strftime("%A %d. %B %Y")))
ff.write('This email is to inform that you are selected either as an organiser or as a speaker for the group meeting to be held on %s and below are the details \n'%(date.strftime("%A %d. %B %Y")))
ff.write('Orgnaiser: %s \n'%(organisers[0]))
ff.write('Speakers: %s and %s\n'%(speakers[0],speakers[1]))
ff.write("Please note that each speaker needs to give a talk (around 10 minutes) during the astro-group meeting.") 
ff.write("Organiser's responsibility is to update the group meeting minutes on AstroWiki, serve a cake after the meeting and to clean up the refrigerator on Monday of the corresponding week which includes getting rid of unclaimed items.")
ff.write("If you can't make it to the meeting, please let me know before this friday i.e, %s\n"%(this_friday.strftime("%A %d. %B %Y")))
ff.write('cheers, \n')
ff.write('Sanjay')
ff.close()
print 'emails of organiser and speakers for %s\n%s %s %s\n'%(date.strftime("%A %d. %B %Y"),members.loc[organisers[0]]['email'], members.loc[speakers[0]]['email'], members.loc[speakers[1]]['email'])
