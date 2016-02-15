import yaml

def increment():
    # read in this week's presenters
    with open('selected_presenters.yaml', 'r') as fd:
        presenters = yaml.load(fd)

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # increment the presenter counters
    for member_type in iter(presenters.values()):
        for presentation, name in iter(member_type.items()):
            members[name][presentation+'s'] += 1

    # write out the updated members list
    with open('members.yaml', 'w') as fd:
        yaml.safe_dump(members, fd)


if __name__ == "__main__":
    increment()
