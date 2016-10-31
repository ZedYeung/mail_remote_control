import poplib
import smtplib
import re
import time
import subprocess
import shelve
from collections import OrderedDict
from email.mime.text import MIMEText
from email.header import Header
from email.header import decode_header
from email.utils import parseaddr

# have fun
cc = "******@****"
password = "***********"
master = "******@***"
message = "At your service"


def decode_header_value(header_value):
	header_value, charset = decode_header(header_value)[0]
	if charset:
		header_value = header_value.decode(charset)
	return header_value


def guess_charset(msg):
	charset = msg.get_charset()
	if charset is None:
		content_type = msg.get('Content-Type', '').lower()
		pos = content_type.find('charset=')
		# can find charset, else pos = -1
		if pos >= 0:
			charset = content_type[pos + 8:].strip()
	return charset


def parse_header(msg):
	mail_header = OrderedDict()
	for header in ['From', 'To', 'Subject']:
		header_value = msg.get(header, '')
		if header_value:
			if header == 'Subject':
				header_value = decode_header_value(header_value)
			else:
				# name <address>
				name, address = parseaddr(header_value)
				name = decode_header_value(name)
				header_value = u'%s <%s>' % (name, address)
		mail_header[header] = header_value
	return mail_header


def login_mail():
	pop_client = poplib.POP3('pop3.sina.com')
	# pop_client.set_debuglevel(1)
	pop_client.user(cc)
	pop_client.pass_(password)
	return pop_client


def accept_mail(pop_client):
	# list() return ['response', ['mesg_num octets', ...], octets]
	mails = pop_client.list()[1]
	# index start from 1
	newest_index = len(mails)
	# retr() return ['response', ['line', ...], octets]
	newest_mail = pop_client.retr(newest_index)[1]
	mail_header = parse_header(newest_mail)
	return mail_header


def send_mail(message):
	smtp_client = smtplib.SMTP('smtp.sina.com', 25)
	smtp_client.starttls()
	smtp_client.login(cc, password)
	msg = MIMEText(message, 'plain', 'utf-8')
	msg['Subject'] = Header(message, 'utf-8').encode()
	msg['From'] = 'Your_Highness <%s>' % cc
	msg['To'] = 'Yedthon <%s>' % master
	smtp_client.sendmail(cc, [master], msg.as_string())
	smtp_client.close()


def yes_my_lord(mail_header):
	"""execute local script"""
	# use[-1] to avoid address like <master> <hacker>
	if re.findall('<(.*?)>', mail_header['From'])[-1] != master:
		pass
	else:
		subprocess.Popen(mail_header['Subject'], shell=True)


def main():
	print('Working...')
	pop_client = login_mail()
	while True:
		# time interval
		time.sleep(60)
		with shelve.open('local_mail_info') as local_mail_info:
			newest_mail_header = accept_mail(pop_client)
			# when there is a new email, update the local's and print relevant info
			if local_mail_info['info'] != newest_mail_header:
				# stat() return tuple of 2 ints (message count, mailbox size):
				print('messages count: %s & mailbox size: %s' % pop_client.stat())
				print(local_mail_info['info'])
				print(newest_mail_header)
				local_mail_info['info'] = newest_mail_header
				yes_my_lord(newest_mail_header)
				send_mail(message)

if __name__ == '__main__':
	main()

