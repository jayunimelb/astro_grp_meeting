import yaml
from make_selection import groupmeeting_time

def increment():
    # read in this week's presenters
    with open('selected_presenters.yaml', 'r') as fd:
        presenters = yaml.load(fd)

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # increment the presenter counters
    finished_presenters = presenters[groupmeeting_time(week=-1).strftime("%m/%d/%y")]
    for t in ('chair', 'speaker'):
        members[finished_presenters[t]][t+'s']+=1

    # write out the updated members list
    with open('members.yaml', 'w') as fd:
        yaml.safe_dump(members, fd)


if __name__ == "__main__":
    increment()
