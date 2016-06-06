import warnings
import sys
import random
import yaml
import pandas as pd
import datetime
from scrape_doodle import scrape_doodle
from termcolor import colored
import numpy as np
import pickle
from make_selection import groupmeeting_time

def replace(reselect_contribution):
    print(colored('%s is to be replaced.'%reselect_contribution,'red'))

    half_talk_list = ['master', 'phd_junior']                       
    exception_list = {'chairs':{'',} ,'speakers':{'Stuart Wyithe',}}

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'
    emails = members.email
    
    this_monday = groupmeeting_time(week=0).strftime("%m/%d/%y")  
    next_monday = groupmeeting_time(week=1).strftime("%m/%d/%y")  
    next4_monday = groupmeeting_time(week=4).strftime("%m/%d/%y") 

    # cut down the members to just those who are available this coming week 
    print(colored("Unavailable list: %s"%members[members.available==0].index.tolist(),'red'))
    members = members[members.available==1]                                           
    # read in the selected selected_presenters                  
    with open('selected_presenters.yaml', 'r') as fd: 
        selected_presenters = yaml.load(fd)                    

    # choose the paper selected_presenters randomly from those who have presented the
    # minimum number of times.
    offset = 0
    count_min = members[reselect_contribution+'s'].min()
    count_max = members[reselect_contribution+'s'].max()
    diff = count_max - count_min
    while offset<=diff:
        mi = count_min+offset
        pool = list(set(members.query(reselect_contribution + 's == @mi').index) - exception_list[reselect_contribution+'s'] - set(selected_presenters[next4_monday][reselect_contribution]))
        if len(pool)<1:
            offset +=1
        else:
            reselected_name = random.sample(pool,1)[0] 
            if members['type'][reselected_name] not in half_talk_list:
                selected_presenters[next4_monday][reselect_contribution] = '%s'%reselected_name
                break

    with open("selected_presenters_tba.yaml", "w") as fd:  
        yaml.safe_dump(selected_presenters, fd)            

    print(colored('%s'%selected_presenters[next4_monday]+'4 weeks later',"red"))
    femail4 = open('email4.txt', 'w') 
    femail4.write('Hi there,\n\nYou are selected to be the chair and speaker(s) for the group meeting to be held 4 weeks later (http://qyx268.github.io/astromeeting_site/)\n\nHere are the details:\n') 
    femail4.write('date: %s\n'%groupmeeting_time(week=4).strftime("%d. %B %Y"))
    femail4.write('chair:\t%s (%s)\nspeaker:\t%s (%s)\n'%(selected_presenters[next4_monday]['chair'],members['email'][selected_presenters[next4_monday]['chair']],selected_presenters[next4_monday]['speaker'],members['email'][selected_presenters[next4_monday]['speaker']])) 
    femail4.write("\nPlease note that it will be the speaker's duty to prepare a talk (less than 30 minutes) on the astro-group meeting.\n")  
    femail4.write("\nAnd it will be the chair's responsibility to\n\t1) supervise the speaker on preparing the talk, \n\t2) remind the astro group that you are the chair and collect agendas from them on Monday, \n\t3) send an announcement to the astro-people about 15 minutes before the group meeting, \n\t4) update the group meeting minutes on AstroWiki,\n\t5) prepare a cake (usually) on Wednesday afternoon. \n")   
    femail4.write('\nPlease confirm it by replying me or let me know as soon as possible if you cannot make it :)\n')                                    
    femail4.write('\nIf you become unable to attend the meeting after this Friday, unfortunately, you will need to find an alternative by yourself.\n')  
    femail4.write('If you only need to give a 15-minute talk but you are the only speaker selected, let me know and I will arrange one more speaker.\n') 
    femail4.write('\nCheers,\nYuxiang') 
    femail4.close()  

    email4 = members['email'][reselected_name]
    print('mail -s "Speaker and chair on the astro-group meeting" %s'%email4)

if __name__ == "__main__":
    if len(sys.argv)<2:
        print(colored("Who do you want to replace?",'red'))
    else:
        replace(sys.argv[1])
