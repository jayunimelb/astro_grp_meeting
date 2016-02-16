import warnings
import random
import yaml
import pandas as pd
import datetime
from scrape_doodle import scrape_doodle
from termcolor import colored
import numpy as np
import pickle

def groupmeeting_time(week=4):
    """http://stackoverflow.com/a/6558571"""
    today = datetime.date.today()
    weekday = 0  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += (week+1)*7
    return today + datetime.timedelta(days_ahead)

def make_selection():

    half_talk_list = ['master', 'phd_junior']
    exception_list = {'chairs':{'',} ,'speakers':{'Sanjay Patil',}} 

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'

    # Temporarily increment the contribution counts to include future volunteers
    doodle_poll = scrape_doodle("http://doodle.com/poll/psdh3untd9dqedzi")
    next_monday = groupmeeting_time().strftime("%m/%d/%y")
    volunteers = {}
    for t in ('chair', 'speaker'):
        volunteers[t] = list(doodle_poll.columns[doodle_poll.loc[next_monday, t]])
    for name in doodle_poll.columns:
        for contribution in ('chairs', 'speakers'):
            members.loc[name][contribution] += np.count_nonzero(doodle_poll[name].loc[:, contribution[:-1]])

    # pickle the doodle poll for later use
    with open("doodle_poll.pkl", "wb") as fd:
        pickle.dump(doodle_poll, fd)

    # cut down the members to just those who are available this coming week and
    # split by type
    print(colored("Unavailable list: %s"%members[members.available==0].index,'red'))
    members = members[members.available==1] 

    if len(members)<2:
        print(colored("not enough people","red"))
        return

    presenters = dict(chair = "", speaker = "")
    volunteered = dict(chair = "", speaker = "")

    # select volunteers if there are any
    for k, l in iter(volunteers.items()):
        for v in l:
            presenters[k] = v
            volunteered[k] = True
            print(colored("Volunteer for "+k+" by "+v,'red'))

    # choose the chair presenters randomly from those who have presented the
    # minimum number of times.
    for contribution in ('chairs', 'speakers'):
        if not volunteered[contribution[:-1]]:
            mi = members[contribution].min()
            pool = list(members.query(contribution + ' == @mi').index)
            # some people are exception
            pool = set(pool) - exception_list[contribution]
            presenters[contribution[:-1]] = random.sample(pool, 1)[0]
    
    # try to avoid same person holding and speaking at the same time
    while presenters['chair'] == presenters['speaker']:
        if not volunteered['chair']:
            mi = members['chair'].min()
            pool = list(members.query('chair == @mi').index)
            presenters['chair'] = random.sample(pool, 1)[0]
        elif not volunteered['speaker']:
            mi = members['speaker'].min()
            pool = list(members.query('speaker == @mi').index)     
            presenters['speaker'] = random.sample(pool, 1)[0]
        else:
            # well unless this guy volunteered to do both
            print(colored(presenters['speaker']+'volunteered to do both',red))
            break

    # masters or 1-st year phds are required to give 15 mins talk, so add an other one
    if members['type'][presenters['speaker']] in half_talk_list:
        half_talk_members = members[members['type'].isin(half_talk_list)].drop(presenters['speaker'])
        mi = half_talk_members['speakers'].min()
        pool = list(half_talk_members.query('speakers == @mi').index)
        presenters['speaker']+=', '+random.sample(pool, 1)[0]

    # upate the selected_presenters file
    with open('selected_presenters.yaml', 'r') as fd:
        selected_presenters = yaml.load(fd)

    selected_presenters.pop(groupmeeting_time(week=-1).strftime("%m/%d/%y")) 
    selected_presenters[next_monday]= presenters

    print(colored(presenters,"red"))
    with open("selected_presenters_tba.yaml", "w") as fd:
        yaml.safe_dump(selected_presenters, fd)

if __name__ == "__main__":
    make_selection()
