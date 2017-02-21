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

    now = datetime.datetime.now()
    tick_end = datetime.datetime(now.year, now.month, now.day-datetime.date.today().weekday(), 17,0,0,0)
    if now < tick_end:
        print(colored("THIS IS NOT THE TIME!!!",'red'))
        #return

    # calculate the timings
    this_monday = groupmeeting_time(week=0).strftime("%m/%d/%y")
    next_monday = groupmeeting_time(week=1).strftime("%m/%d/%y")
    next2_monday = groupmeeting_time(week=2).strftime("%m/%d/%y")
    next3_monday = groupmeeting_time(week=3).strftime("%m/%d/%y")
    next4_monday = groupmeeting_time(week=4).strftime("%m/%d/%y")

    # write some heads
    femail1 = open('email1.txt', 'w')
    femail4 = open('email4.txt', 'w')
    femail1.write('Dear all,\n\nPlease allow me to remind you that you are the chair and speakers for next week. (http://qyx268.github.io/astromeeting_site/)\n\nHere are the details:\n')
    femail4.write('Dear all,\n\nYou are selected to be the chair and speakers for the group meeting to be held 4 weeks later (http://qyx268.github.io/astromeeting_site/)\n\nHere are the details:\n')
    femail1.write('date: %s\n'%groupmeeting_time(week=1).strftime("%d. %B %Y"))
    femail4.write('date: %s\n'%groupmeeting_time(week=4).strftime("%d. %B %Y"))

    # this is the exception list, people here do not present or host
    exception_list = {'chairs':{'',} ,'speakers':{'Stuart Wyithe',}} 

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'

    # Temporarily increment the contribution counts to include future volunteers
    doodle_poll = scrape_doodle("http://doodle.com/poll/psdh3untd9dqedzi")
    doodle_poll[doodle_poll=='q']=False
    doodle_poll = doodle_poll.astype(np.bool)
    volunteers = {}
    for t in ('chair', 'speaker'):
        volunteers[t] = list(doodle_poll.columns[doodle_poll.loc[next4_monday, t]])
    for name in doodle_poll.columns:
        for contribution in ('chairs', 'speakers'):
            members.loc[name][contribution] += np.count_nonzero(doodle_poll[name].loc[:, contribution[:-1]])

    # Temporarily increment the contribution counts to include the selected people
    with open('selected_presenters.yaml', 'r') as fd:
        presenters = yaml.load(fd)
    for k, l in iter(presenters.items()):
        if k!=this_monday:
            for contribution in ('chairs', 'speakers'):
                name = l[contribution[:-1]]
                members.loc[name][contribution] += 1
        
    # pickle the doodle poll for later use
    with open("doodle_poll.pkl", "wb") as fd:
        pickle.dump(doodle_poll, fd)

    # cut down the members to just those who are available this coming week and
    # split by type
    print(colored("Unavailable list: %s"%list(members[members.available==0].index),'red'))
    members = members[members.available==1] 

    if len(members)<2:
        print(colored("not enough people","red"))
        return

    presenters = dict(chair = [], speaker = [])
    volunteered = dict(chair = "", speaker = "")

    # select volunteers if there are any
    for k, l in iter(volunteers.items()):
        for v in l:
            presenters[k] = v
            volunteered[k] = True
            print(colored("Volunteer for "+k+" by "+v,'red'))
            femail4.write(v+" volunteered for "+k+'\n')

    # the selected_presenters file
    with open('selected_presenters.yaml', 'r') as fd:
        selected_presenters = yaml.load(fd)
    
    # choose the chair presenters randomly from those who have presented the
    # minimum number of times.
    for contribution, number_contribution in zip(('chairs', 'speakers'),(1,2)):
        offset = 0
        count_min = members[contribution].min()
        count_max = members[contribution].max()
        diff = count_max - count_min           
        while (len(presenters[contribution[:-1]])<2) and (offset<=diff):
            mi = count_min+offset
            # you don't want people contribute continuously
            pool = list(set(members.query(contribution + ' == @mi').index) - set(presenters['chair']) - set(presenters['speaker']) - set(selected_presenters[next_monday][contribution[:-1]]) - set(selected_presenters[next2_monday][contribution[:-1]]) - set(selected_presenters[next3_monday][contribution[:-1]]))
            # some people are exception
            pool = set(pool) - exception_list[contribution]
            presenters[contribution[:-1]] += random.sample(pool, min(len(pool),number_contribution-len(presenters[contribution[:-1]])))
            offset +=1
    
    # save the selection result
    selected_presenters.pop(this_monday) 
    selected_presenters[next4_monday]= presenters
    with open("selected_presenters_tba.yaml", "w") as fd:
        yaml.safe_dump(selected_presenters, fd)

    # print the result so you can check
    os.system('cat selected_presenters_tba.yaml')

    # finish the email
    femail1.write('chair:\t%s (%s)\n'%(selected_presenters[next_monday]['chair'][0],members['email'][selected_presenters[next_monday]['chair'][0]]))
    femail1.write('speaker1:\t%s (%s)\n'%(selected_presenters[next_monday]['speaker'][0],members['email'][selected_presenters[next_monday]['speaker'][0]]))
    femail1.write('speaker2:\t%s (%s)\n'%(selected_presenters[next_monday]['speaker'][1],members['email'][selected_presenters[next_monday]['speaker'][1]]))
    femail1.write("\nPlease note that each speaker needs to give a talk (around 10 minutes) on the astro-group meeting.\n")
    femail1.write("\nAnd it will be the chair's responsibility to\n\t1) supervise the speakers on preparing the talks, \n\t2) remind the astro group that you are the chair and collect agendas from them on Monday, \n\t3) send an announcement to the astro-people about 15 minutes before the group meeting, \n\t4) update the group meeting minutes on AstroWiki,\n\t5) serve a cake after the meeting \n")
    femail1.write('\nIf you will be unable to attend the meeting, please find an alternative.\n')
    femail1.write('If you have swapped with other people, please forward this email :)\n')
    femail1.write('\nCheers,\nYuxiang')
    femail1.close()

    femail4.write('chair:\t%s (%s)\n'%(selected_presenters[next4_monday]['chair'][0],members['email'][selected_presenters[next4_monday]['chair'][0]]))
    femail4.write('speaker1:\t%s (%s)\n'%(selected_presenters[next4_monday]['speaker'][0],members['email'][selected_presenters[next4_monday]['speaker'][0]]))
    femail4.write('speaker2:\t%s (%s)\n'%(selected_presenters[next4_monday]['speaker'][1],members['email'][selected_presenters[next4_monday]['speaker'][1]]))
    femail4.write("\nPlease note that each speaker needs to give a talk (around 10 minutes) on the astro-group meeting.\n")
    femail4.write("If possible, please finish your slice 8 days before your due date, just in case the previous meeting needs your backup :)\n")
    femail4.write("\nAnd it will be the chair's responsibility to\n\t1) supervise the speakers on preparing the talks, \n\t2) remind the astro group that you are the chair and collect agendas from them on Monday, \n\t3) send an announcement to the astro-people about 15 minutes before the group meeting, \n\t4) update the group meeting minutes on AstroWiki,\n\t5) serve a cake after the meeting \n")
    femail4.write('\nPlease let me know as soon as possible if you cannot make it :)\n')
    femail4.write('\nAfter this Friday, you will need to find an alternative by yourself.\n')
    femail4.write('\nCheers,\nYuxiang')
    femail4.close()

    # print out the email commands
    email4 = "%s, %s, %s"%(members['email'][selected_presenters[next4_monday]['chair'][0]],members['email'][selected_presenters[next4_monday]['speaker'][0]],members['email'][selected_presenters[next4_monday]['speaker'][1]])
    email1 = "%s, %s, %s"%(members['email'][selected_presenters[next_monday]['chair'][0]],members['email'][selected_presenters[next_monday]['speaker'][0]],members['email'][selected_presenters[next_monday]['speaker'][1]])
    print('mail -s "Speaker and chair on the astro-group meeting" "'+email4+'" <email4.txt')
    print('mail -s "Speaker and chair on the astro-group meeting" "'+email1+'" <email1.txt')

if __name__ == "__main__":
    make_selection()
