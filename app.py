import certstream
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from fuzzer.fuzzer import fuzz_string
from requests.auth import HTTPBasicAuth

monitor_strings = ['google', 'paypal', 'office']
monitor_whitelis =['domain.com', 'site']
sender = ''
receivers = ['', '']
username = ''
password = ''
server_address = ''

def send_mail(sender, receivers, subject, body, username, password, server_address):
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ",".join(receivers)
    message["Subject"] = subject
    message.attach(MIMEText(body))

    try:
        server = smtplib.SMTP(server_address, 587)
        server.starttls()
        server.login(username, password)
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
    except Exception as e:
        print('Failed to send a mail: {}'.format(e))


def fuzz_strings(monitor_strings):
    domains = []

    for string in monitor_strings:
        fuzzer = fuzz_string(string)
        fuzzer.fuzz()
        for fdomain in (fuzzer.domains):
            domains.append(fdomain['domain-name'].strip())

    return domains


def callback(message, context):
    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']
        for domain in all_domains:
            for search_string in search_strings:
                if search_string in domain and search_string not in monitor_whitelis:
                    print('Suspicious domain: {}'.format(domain))
                    subject = 'SSL-Monitor: Suspicious domain found {}'.format(domain)
                    body = 'While monitoring newly registerd SSL certificates as domain was detected that matches your search criteria:\n\n{}'.format(domain)
                    send_mail(sender, receivers, subject, body, username, password, server_address)
                    return

search_strings = fuzz_strings(monitor_strings)
print('A total of {} strings will be monitored'.format(len(search_strings)))
certstream.listen_for_events(callback)