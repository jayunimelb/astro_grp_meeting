"""
This piece of code is used to reselect organisers of speakers for a meeting on particular date

Input:
date: provide the date on which you need to reselect speakers/organisers
# of speakers/organisers to be selcted

Output:
Names of organisers or speakers

Example command: python re_selection.py -no_of_speakers 1 -no_of_organisers 1 -date Apr 09 2018
"""





import numpy as np
import warnings, random, yaml, datetime, pickle, os, gspread, sys, argparse
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from termcolor import colored
scope = ['https://spreadsheets.google.com/feeds']
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

def read_poll(list_name,date,response = 'Yes'):
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


parser = argparse.ArgumentParser(description='')

parser.add_argument('-no_of_speakers', dest='no_of_speakers', action='store', help='no_of_speakers', type=int, required=True)
parser.add_argument('-no_of_organisers', dest='no_of_organisers', action='store', help='no_of_speakers', type=int, required=True)
parser.add_argument('-date', dest = 'date', action='store', help='date', type=str, required=True)

args = parser.parse_args()
args_keys = args.__dict__
for kargs in args_keys:
        param_value = args_keys[kargs]
        if isinstance(param_value, str):
                cmd = '%s = "%s"' %(kargs, param_value)
        else:
                cmd = '%s = %s' %(kargs, param_value)
        exec(cmd)


try:
	date = datetime.datetime.strptime('%s'%(date),'%b %d %Y')
except:
	print  colored("date should be provide in 'Month day year' for example 'Sep 01 2018' \n exiting now",'red')
	sys.exit()



# read members list
with open('members.yaml', 'r') as fd:
	members = yaml.load(fd)
members = pd.DataFrame.from_dict(members).T
# get the date for which we need group meeting speakers


print date.strftime("%m/%d/%y")
from IPython import embed;embed()


# members.yaml is updated manually so for all the selected members above the current week +1 has to be added
with open('presenters_log.yaml', 'r') as fd:
	selected_presenters = yaml.load(fd)
this_monday = groupmeeting_time(week=0).strftime("%m/%d/%y") # Below this monday the contribuation is taken into account in members.yaml
for k, l in iter(selected_presenters.items()):
	if k>this_monday:
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
from IPython import embed; embed()
number_of_speakers_volunteered = len(speakers_volunteer_list)
number_of_organisers_volunteered = len(organisers_volunteer_list)


number_of_speakers_needed = no_of_speaker - number_of_speakers_volunteered
number_of_orgnaisers_needed = no_of_organisers - number_of_speakers_volunteered
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
