import numpy as np
import warnings, random, yaml, datetime, pickle, os, gspread, sys
from IPython import embed;embed()
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('group_meeting.json',scope)
from IPython import embed;embed()
clients = gspread.authorize(creds)
from IPython import embed;embed()
#from scrape_doodle import scrape_doodle
#from termcolor import colored


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
		if ll[date] == response:
			names_list.append(ll['Name'])


# read members list
with open('members.yaml', 'r') as fd:
	members = yaml.load(fd)
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
# Get list of volunteers if any
speakers_volunteer_list = read_poll('Speakers volunteers list')
organisers_volunteer_list = read_poll('Organisers volunteer List')
# Get lis to of absentees for that particular group meeting
absntees_list = read_poll('Attendee list', response = 'No')
# to make sure that volunteered speakers, organisers, and absntees are not randomly selected again 
members_not_to_consider = speakers_volunteer_list +organisers_volunteer_list + absntees_list

for nn in members_not_to_consider:
	members[nn]['available'] = 0

number_of_speakers_volunteered = len(speakers_volunteer_list)
number_of_organisers_volunteered = len(organisers_volunteer_list)


number_of_speakers_needed = 2 - number_of_speakers_volunteered
number_of_orgnaisers_volunteered = 1 - number_of_speakers_volunteered
from IPython import embed;embed()
# members.yaml is updated manually so for all the selected members above the current week +1 has to be added

with open('selected_presenters.yaml', 'r') as fd:
	selected_presenters = yaml.load(fd)

