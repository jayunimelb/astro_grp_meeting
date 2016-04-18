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
        days_ahead += week*7
    return today + datetime.timedelta(days_ahead)

def make_selection():

    now = datetime.datetime.now()
    tick_end = datetime.datetime(now.year, now.month, now.day-datetime.date.today().weekday(), 17,0,0,0)
    if now < tick_end:
        print(colored("THIS IS NOT THE TIME!!!",'red'))
        #return

    femail1 = open('email1.txt', 'w')
    femail4 = open('email4.txt', 'w')
    femail1.write('Hi there,\n\nLet me remind you that you are the chair and speaker(s) for next week. (http://qyx268.github.io/astromeeting_site/)\n\nHere are the details:\n')
    femail4.write('Hi there,\n\nYou are selected to be the chair and speaker(s) for the group meeting to be held 4 weeks later (http://qyx268.github.io/astromeeting_site/)\n\nHere are the details:\n')
    femail1.write('date: %s\n'%groupmeeting_time(week=1).strftime("%d. %B %Y"))
    femail4.write('date: %s\n'%groupmeeting_time(week=4).strftime("%d. %B %Y"))

    half_talk_list = ['master', 'phd_junior']
    exception_list = {'chairs':{'',} ,'speakers':{'Stuart Wyithe',}} 

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'

    # Temporarily increment the contribution counts to include future volunteers
    doodle_poll = scrape_doodle("http://doodle.com/poll/psdh3untd9dqedzi")
    next4_monday = groupmeeting_time().strftime("%m/%d/%y")
    volunteers = {}
    for t in ('chair', 'speaker'):
        volunteers[t] = list(doodle_poll.columns[doodle_poll.loc[next4_monday, t]])
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
            femail4.write(v+" volunteered for "+k+'\n')

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
            print(colored(presenters['speaker']+'volunteered to do both','red'))
            break

    # masters or 1-st year phds are required to give 15 mins talk, so add an other one
    flag = 0
    if members['type'][presenters['speaker']] in half_talk_list:
        half_talk_members = members[members['type'].isin(half_talk_list)].drop(presenters['speaker'])
        mi = half_talk_members['speakers'].min()
        pool = list(half_talk_members.query('speakers == @mi').index)
        presenters['speaker']+=', '+random.sample(pool, 1)[0]
        flag = 1

    # upate the selected_presenters file
    with open('selected_presenters.yaml', 'r') as fd:
        selected_presenters = yaml.load(fd)
    
    next_monday = groupmeeting_time(week=1).strftime("%m/%d/%y")
    try:
        femail1.write('chair:\t%s (%s)\nspeaker:\t%s (%s)\n'%(selected_presenters[next_monday]['chair'],members['email'][selected_presenters[next_monday]['chair']],selected_presenters[next_monday]['speaker'],members['email'][selected_presenters[next_monday]['speaker']]))
    except KeyError:
        femail1.write('chair:\t%s (%s)\nspeaker:\t%s (%s)\n'%(selected_presenters[next_monday]['chair'],members['email'][selected_presenters[next_monday]['chair']],selected_presenters[next_monday]['speaker'],members['email'][selected_presenters[next_monday]['speaker'].split(', ')].values))


    selected_presenters.pop(groupmeeting_time(week=0).strftime("%m/%d/%y")) 
    selected_presenters[next4_monday]= presenters

    print(colored('%s'%presenters+'4 weeks later',"red"))
    print(colored('%s'%selected_presenters[next_monday]+'next week','red'))
    if flag:
        femail4.write('chair:\t%s (%s)\nspeaker:\t%s (%s)\n'%(presenters['chair'],members['email'][presenters['chair']],presenters['speaker'],members['email'][presenters['speaker'].split(', ')].values))
    else:
        femail4.write('chair:\t%s (%s)\nspeaker:\t%s (%s)\n'%(presenters['chair'],members['email'][presenters['chair']],presenters['speaker'],members['email'][presenters['speaker']]))
    with open("selected_presenters_tba.yaml", "w") as fd:
        yaml.safe_dump(selected_presenters, fd)

    femail1.write("\nPlease note that it will be the speaker's duty to prepare a talk (less than 30 minutes) on the astro-group meeting.\n")
    femail1.write("\nAnd it will be the chair's responsibility to\n\t1) supervise the speaker on preparing the talk, \n\t2) remind the astro group that you are the chair and collect agendas from them on Monday, \n\t3) send an announcement to the astro-people about 15 minutes before the group meeting, \n\t4) update the group meeting minutes on AstroWiki,\n\t5) prepare a cake (usually) on Wednesday afternoon. \n")
    femail1.write('\nIf you have swapped with other people, please forward this email :)\n')

    femail4.write("\nPlease note that it will be the speaker's duty to prepare a talk (less than 30 minutes) on the astro-group meeting.\n")
    femail4.write("\nAnd it will be the chair's responsibility to\n\t1) supervise the speaker on preparing the talk, \n\t2) remind the astro group that you are the chair and collect agendas from them on Monday, \n\t3) send an announcement to the astro-people about 15 minutes before the group meeting, \n\t4) update the group meeting minutes on AstroWiki,\n\t5) prepare a cake (usually) on Wednesday afternoon. \n")
    femail4.write('\nPlease confirm it by replying me or let me know as soon as possible if you cannot make it :)\n')
    femail4.write('If you only need to give a 15-minute talk but you are the only speaker selected, let me know and I will arrange one more speaker.\n')

    femail1.write('\nCheers,\nYuxiang')
    femail4.write('\nCheers,\nYuxiang')
    femail1.close()
    femail4.close()

    #double speaker:
    tmp = list(selected_presenters[next4_monday].values())
    email4 = members['email'][tmp[1].split(', ')+tmp[0].split(', ')]

    tmp = list(selected_presenters[next_monday].values())
    email1 = members['email'][tmp[1].split(', ')+tmp[0].split(', ')]
    print('mail -s "Speaker and chair on the astro-group meeting" "'+', '.join([people for people in email4])+'" <email4.txt')
    print('mail -s "Speaker and chair on the astro-group meeting" "'+', '.join([people for people in email1])+'" <email1.txt')

if __name__ == "__main__":
    make_selection()
