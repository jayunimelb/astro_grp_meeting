After every group meeting:

* Update the contribution of speakers and organiser's in members.yaml manually. (if there is any change in speakers or chair, please update it on presenters_log.yaml)

* Run selection.py, it will select 2 speakers and an orgnaiser. In addition to updating presenters_log.yaml file, it also prints out the emails of the people who have been selected for that particular week.

* email.txt will contain the body and subject of email that is supposed to be sent to the organiser and speakers (you can edit it the way you want and it is pretty straight forward if you look into selection.py)

* Manually edit the selected_presenters.yaml file (currently the template needs 6 entries, if you want to change look into "templates/index.html" file)

* run "make update_webpage" to upadate astro group meeting webpage (https://jayunimelb.github.io/astro_grp_meeting/)

* If the person selected for a particual group meeting is not able to attend for any reasons, then run "re_selection.py" script. 
