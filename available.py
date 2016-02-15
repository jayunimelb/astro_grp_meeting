import yaml
import pandas as pd
import numpy as np
from scrape_doodle import scrape_doodle
from make_selection import next_simslunch

def available():

    left = ['Camila', 'Paul A']

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)
    
    doodle_poll = scrape_doodle("http://doodle.com/poll/umri2w7pxqnged37")
    next_thursday = next_simslunch().strftime("%-m/%-d/%y")

    unavailable = list(doodle_poll.columns[doodle_poll.loc[next_thursday, 'unavailable']])
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
