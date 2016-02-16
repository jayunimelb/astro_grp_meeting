import yaml
import pandas as pd
import toyplot
import toyplot.html
import toyplot.color
import pickle
from jinja2 import Environment, FileSystemLoader
from make_selection import groupmeeting_time
import numpy as np

def generate():

    exception_list = {'chairs':{} ,'speakers':{'Stuart Wyithe',}}   

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'

    # read in the pickled doodle poll
    with open("doodle_poll.pkl", "rb") as fd:
        doodle_poll = pickle.load(fd)

    # count the number of volunteer contributions
    for t in ('chair', 'speaker'):
        members['vcount_'+t] = doodle_poll.query('type == @t').sum()

    members = members.fillna(0)

    # generate speakers of the current standings and render them to html files
    for contribution in ["Chairs", "Speakers"]:
        pool = members.drop(exception_list[contribution.lower()])   
        data = np.column_stack((pool[contribution.lower()],
                                pool["vcount_"+contribution.lower()[:-1]]))
        canvas = toyplot.Canvas(1200, 500)
        axes = canvas.axes(bounds=(80, -200, 50, -120))
        mark = axes.bars(data, baseline="stacked")
        axes.x.ticks.locator = toyplot.locator.Explicit(labels=pool.index)
        axes.label.text = contribution
        axes.x.ticks.labels.angle = 30
        axes.x.ticks.show = True
        axes.x.ticks.labels.style = {"baseline-shift":0, "text-anchor":"end", "-toyplot-anchor-shift":"-6px"}
        axes.x.ticks.labels.offset = 8
        axes.y.label.text = "Times presented"
        axes.y.ticks.locator = toyplot.locator.Integer()
        axes.coordinates.show = False
        palette = toyplot.color.Palette()
        canvas.legend([
            ("Finished (past)", "rect", {"fill":palette.css(0),}),
            ("Volunteered (future)", "rect", {"fill":palette.css(1),}),
        ], corner=("right", 80, 80, 50),)
        toyplot.html.render(canvas, fobj="templates/"+contribution.lower()+"_history.html")

    # read in this week's presenters
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
