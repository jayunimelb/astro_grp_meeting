import numpy as np
import warnings
import random
import yaml
import pandas as pd
import datetime
from scrape_doodle import scrape_doodle
from termcolor import colored
import numpy as np
import pickle
import os

def groupmeeting_time(week=4):
    """http://stackoverflow.com/a/6558571"""
    today = datetime.date.today()
    weekday = 0  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += week*7
    return today + datetime.timedelta(days_ahead)

def make_selection():
    #now = datetime.datetime.now()
    #tick_end = datetime.datetime(now.year, now.month, now.day-datetime.date.today().weekday(), 17,0,0,0)
    #if now < tick_end:
    #    print(colored("THIS IS NOT THE TIME!!!",'red'))
    #    return
    print('!! Warning!!!! \n Please make sure that you update the members.yaml file by looking at the doodle polls https://doodle.com/poll/psdh3untd9dqedzi and https://doodle.com/poll/pd7rn7esk4q5vuft  !!!')
    this_monday = groupmeeting_time(week=0).strftime("%m/%d/%y")
    
    
    # get date
    with open('members.yaml', 'r') as fd:
    	members = yaml.load(fd)
    with open('selected_presenters.yaml', 'r') as fd:
    	selected_presenters = yaml.load(fd)
    pre_selected_date = sorted(selected_presenters.keys())[-1]
    date = datetime.datetime.strptime(pre_selected_date,'%m/%d/%y')+datetime.timedelta(7)
    date = date.strftime("%d-%m-%Y")
    

    for k, l in iter(selected_presenters.items()):
    	if k>this_monday:
    		for contribution in ('chairs', 'speakers'):
    			names = l[contribution[:-1]]
    			for name in names:
    				members.loc[name][contribution] += 1
    from IPython import embed;embed()
    members = members[members.available==1] 
    if len(members)<2:
    	print(colored("not enough people","red"))

    	
    # write some heads
    femail1 = open('email1.txt', 'w')
    femail4 = open('email4.txt', 'w')
    femail1.write("Dear Organiser and Speakers,\nThis email is just a reminder that you are either organiser or speaker for the next week's (i,e on %s) group meeting\nHere are the details:\n"%(groupmeeting_time(week=1).strftime("%A %d. %B %Y")))
    femail4.write("Dear all,\nThis email is to inform that you are selected either as an organiser or as a speaker for the group meeting to be held 4 weeks later (i.e on %s)\nHere are the details:\n"%(groupmeeting_time(week=4).strftime("%A %d. %B %Y")))
    femail1.write('Date: %s\n'%groupmeeting_time(week=1).strftime("%d. %B %Y"))
    femail4.write('Date: %s\n'%groupmeeting_time(week=4).strftime("%d. %B %Y"))
    
    # this is the exception list, people here do not present or host and currently hard coded for Stu!
    exception_list = {'chairs':{'',} ,'speakers':{'Stuart Wyithe',}}     
    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)
    
    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'
    
    # Temporarily increment the contribution counts to include future volunteers

    '''
    doodle_poll = scrape_doodle("http://doodle.com/poll/psdh3untd9dqedzi")
    doodle_poll = doodle_poll.replace('q',False) 
    doodle_poll = doodle_poll.astype(np.bool)
    volunteers = {}
    for t in ('chair', 'speaker'):
        volunteers[t] = list(doodle_poll.columns[doodle_poll.loc[next4_monday, t]])
    for name in doodle_poll.columns:
        for contribution in ('chairs', 'speakers'):
            members.loc[name][contribution] += np.count_nonzero(doodle_poll[name].loc[:, contribution[:-1]])
    print(colored("Volunteers %s"%volunteers,'red'))
    '''
    # Temporarily increment the contribution counts to include the selected peopl
make_selection()