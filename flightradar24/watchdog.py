#!/usr/bin/env python

from os.path import exists
import datetime
import smtplib
from email.mime.text import MIMEText

filename = datetime.date.today().strftime('/home/michael/flightradar_scraper/filtered/%Y-%m-%d.tsv')
if not exists(filename):
	me = 'scraper@flightradar24.com'
	you = 'sven@popmodernism.org'
	msg = MIMEText('help me!')
	msg['Subject'] = 'i\'m down!'
	msg['From'] = me
	msg['To'] = you
	s = smtplib.SMTP('localhost')
	s.sendmail(me, [you], msg.as_string())
	s.quit()