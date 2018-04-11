"""
Author: Srini Raghunathan
Date: March / April 2017
Execute as: python get_papers_citations.py fname-lname
example: python get_papers_citations.py Albert-Einstein

Output: pickle file containing python dictionary
key is the bibcode of each article
value of each key contains (yearval, citations, citation_years, citations_bib, articletitle, authorlist, latex_style)
where 
yearval = publication year
citations = total citations
citation_years = number of citations in each year (for histogram)
citations_bib = bibcode of all citations
articletitle = title of the article
authorlist = authorlist
latex_style = formatted authorlist, articlename, journal details, etc. - you will see when you execute it.
"""


import requests, sys, pickle, numpy as np
import argparse
from HTMLParser import HTMLParser; h = HTMLParser()

if len(sys.argv)==1:
	print 'execute as python get_papers_citations.py [fname-lname]'
	sys.exit()
args = sys.argv[1:]
args = ' '.join(args)
fname, lname = args.split('-')

print '\n\tQuerying ADS for "%s %s". The following are the list publications to include in latex document.\n\n' %(fname, lname)
ads_search_str = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&author=%s,+%s' %(lname, fname)
op_pkl = 1 #1 - Pickle; 0 - text file output

page = requests.get(ads_search_str)
data = page.text.encode('utf8').split('\n')

if op_pkl:
	citation_dic = {}
else:
	citation_dic = []
for lines in data:
	
	if lines.find('input type="checkbox"  name="bibcode"')>-1:
		searchstr_1 = 'name="bibcode" value="'
		searchstr_2 = '">&nbsp;'
		pos_1 = lines.find(searchstr_1)
		pos_2 = lines.find(searchstr_2)
		extract = lines[pos_1:pos_2].replace(searchstr_1,'').strip()
		article_url = 'http://adsabs.harvard.edu/abs/%s' %(extract)
		article = requests.get(article_url).text.encode('utf8').split('\n')
		
		sys.exit(0)
		#article = requests.get(article_url).text.encode('ascii').split('\n')
		#print extract
		yearval = int(extract[0:4])
		for tmp in article:
			if tmp.find('Refereed')>-1: continue
			citations_search = 'Citations to the Article'
			pos = tmp.find(citations_search)
			if pos>-1:
				citations = int(tmp[pos:tmp.find('</strong></a>')].replace(citations_search,'').strip().replace('(','').replace(')',''))
				#loop over citations and get their entries:
				citations_hreflink = tmp[tmp.find('a href=')+8:pos].strip('>"').replace('&#38','&amp')
				citations_page = requests.get(citations_hreflink).text.encode('utf8').split('\n')
				#citations_page = requests.get(citations_hreflink).text.encode('ascii').split('\n')
				citations_bib = []
				citation_years = []
				for citation_page_lines in citations_page:
					if citation_page_lines.find('input type="checkbox"  name="bibcode"')>-1:
						pos_1 = citation_page_lines.find(searchstr_1)
						pos_2 = citation_page_lines.find(searchstr_2)
						citations_extract = citation_page_lines[pos_1:pos_2].replace(searchstr_1,'').strip()
						citations_bib.append(citations_extract)
						citation_years.append(int(citations_extract[0:4]))
				break
			else:
				citations = 0
				citations_bib = []
				citation_years = []

		#get the article title
		for tmp in article:
			if tmp.find('Title:')>-1:
				tmpsplit = tmp.split('>');
				tmpsplit = np.asarray([val if val.find('<')>0 else 'None' for val in tmpsplit])
				articletitle = tmpsplit[tmpsplit<>'None'][1].replace('</td','')
				break

		#get author list
		for tmp in article:
			if tmp.find('Authors:')>-1:
				tmpsplit = tmp.split('>');
				tmpsplit = np.asarray([val if val.find('<')>0 else 'None' for val in tmpsplit])
				authorlist = tmpsplit[tmpsplit<>'None']
				authorrecinds = np.arange(1,len(authorlist),2); authorlist = authorlist[authorrecinds].tolist()
				authorlist = '; '.join(authorlist).replace('&#160;',' ').replace('</a','') #replace html spaces
				authorlist=h.unescape(authorlist) #replace html characters
				break
			
		#get journal name/volume/etc.
		for tmp in article:
			if tmp.find('Publication:')>-1:
				tmpsplit = tmp.split('>');
				tmpsplit = np.asarray([val if val.find('<')>0 else 'None' for val in tmpsplit])
				journaldetails = tmpsplit[tmpsplit<>'None'][1]
				pos = journaldetails.find('(<'); journaldetails = journaldetails[:pos].strip()
				journaldetails=h.unescape(journaldetails) #replace html characters
				break

		#make latex style formatting - choose whatever you want here
		#format authorlist to fname and lname
		authorlist_mod = authorlist.split(';')
		authorlist_mod = [' '.join(val.strip().split(', ')[::-1]) for val in authorlist_mod]
		authorlist_mod = ', '.join(authorlist_mod)
		
		latex_style = '%s, \\emph{\"%s\"}, %s (%s)' %(authorlist, articletitle, journaldetails, yearval)

		if op_pkl:
			citation_dic[extract] = [yearval, citations, citation_years, citations_bib, articletitle, authorlist, latex_style]
		else:
			citation_dic.append([extract, yearval, citations, citation_years, citations_bib, articletitle, authorlist, latex_style])

		print '%s. %s\n' %(len(citation_dic), latex_style)

if op_pkl:
	pickle.dump(citation_dic, open('citations_dic_%s_%s.pkl' %(fname, lname), 'wb'), protocol = 2)
else:
	np.savetxt('citations_dic_%s_%s.txt' %(fname, lname), citation_dic, fmt = '%s')
