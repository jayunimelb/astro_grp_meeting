import yaml
import pandas as pd
import numpy as np
from scrape_doodle import scrape_doodle
from make_selection import groupmeeting_time

def available():

    left = []

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)
    
    doodle_poll = scrape_doodle("http://doodle.com/poll/pd7rn7esk4q5vuft")
    next_monday = groupmeeting_time().strftime("%m/%d/%y")
    doodle_poll[doodle_poll=='q']=False
    doodle_poll = doodle_poll.astype(np.bool)

    unavailable = list(doodle_poll.columns[doodle_poll.loc[next_monday, 'unavailable']])
    for name in members.keys():   
        if name in unavailable or name in left:
            members[name]['available'] = 0
        else:
            members[name]['available'] = 1

    # write out the updated members list
    with open('members.yaml', 'w') as fd:
        yaml.safe_dump(members, fd)

if __name__ == "__main__":
    available()
