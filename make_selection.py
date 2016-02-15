import warnings
import random
import yaml
import pandas as pd
import datetime
from scrape_doodle import scrape_doodle
import numpy as np
import pickle

def next_simslunch():
    """http://stackoverflow.com/a/6558571"""
    today = datetime.date.today()
    weekday = 3  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = 3 - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return today + datetime.timedelta(days_ahead)


def make_selection():
    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'

    # Temporarily increment the contribution counts to include future volunteers
    doodle_poll = scrape_doodle("http://doodle.com/poll/g3idnd5gfg8ck2ze")
    next_thursday = next_simslunch().strftime("%-m/%-d/%y")
    volunteers = {}
    for t in ('paper', 'plot'):
        volunteers[t] = list(doodle_poll.columns[doodle_poll.loc[next_thursday, t]])
    for name in doodle_poll.columns:
        for contribution in ('papers', 'plots'):
            members.loc[name][contribution] += np.count_nonzero(doodle_poll[name].loc[:, contribution[:-1]])

    # pickle the doodle poll for later use
    with open("doodle_poll.pkl", "wb") as fd:
        pickle.dump(doodle_poll, fd)

    # cut down the members to just those who are available this coming week and
    # split by type
    members = members[members.available==1] 

    # Set up the dicts for storing the selection information
    postdocs = members.query('type == "postdoc"')
    postdocs.name = "postdocs"
    postdocs.presenters = dict(
        paper = "",
        plot = ""
    )
    postdocs.volunteered = dict(
        paper = False,
        plot = False,
    )
    students = members.query('type == "student"')
    students.name = "students"
    students.presenters = postdocs.presenters.copy()
    students.volunteered = postdocs.volunteered.copy()

    # select volunteers if there are any
    for k, l in iter(volunteers.items()):
        for v in l:
            vgroup = None
            for group in (postdocs, students):
                if v in group.index and group.volunteered[k] is False:
                    vgroup = group
                    group.presenters[k] = v
                    group.volunteered[k] = True
                    break
            #if vgroup is None:
            #    for group in (postdocs, students):
            #        if not group.volunteered[k]:
            #            vgroup = group
            #            break
            #group.presenters[k] = v
            #group.volunteered[k] = True

    # choose the paper presenters randomly from those who have presented the
    # minimum number of times.
    for contribution in ('papers', 'plots'):
        for group in (students, postdocs):
            if not group.volunteered[contribution[:-1]]:
                mi = group[contribution].min()
                pool = list(group.query(contribution + ' == @mi').index)
                group.presenters[contribution[:-1]] = random.sample(pool, 1)[0]

                # if we have someone who is meant to be presenting both types of
                # contributions then keep randomizing until we get
                # a valid combination (if possible)
                max_tries = 100
                n_tries = 0
                while len(set(group.presenters.values())) < 2:
                    try:
                        group.presenters[contribution[:-1]] = random.sample(pool, 1)[0]
                    except ValueError:
                        n_tries = max_tries
                    n_tries+=1
                    if n_tries >= max_tries:
                        mi += 1
                        pool = list(group.query(contribution + ' == @mi').index)
                        n_tries = 0

    # write the presenters to a file
    presenters = dict(postdocs = postdocs.presenters,
                      students = students.presenters)
    with open("selected_presenters.yaml", "w") as fd:
        yaml.safe_dump(presenters, fd)


if __name__ == "__main__":
    make_selection()
