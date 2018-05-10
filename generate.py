import yaml
import pandas as pd
import toyplot
import toyplot.html
import toyplot.color
import pickle
from jinja2 import Environment, FileSystemLoader
import numpy as np

def generate():
    print "Make sure you have update selected_presenters.yaml file!"
    with open('selected_presenters.yaml', 'r') as fd:
        presenters = yaml.load(fd)
    presenters = pd.DataFrame.from_dict(presenters).T
    presenters.index.name = 'name'

    # render the page
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')
    with open('build/index.html', 'w') as fd:
        fd.write(template.render(dates = [pd.to_datetime(item).to_pydatetime().strftime("%d. %B %Y") for item in presenters.index] , presenters=presenters))

if __name__ == "__main__":
    generate()
