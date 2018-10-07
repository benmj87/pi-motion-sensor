import RPi.GPIO as GPIO
import time
import ssl
import calendar
import http.client
import smtplib
import os
from email.mime.text import MIMEText

sendingThreshold = 1*60 # 1 minutes

def cleanup():
  global lastsent
  global movements

  now = calendar.timegm(time.gmtime())
  threshold = now - 30 # remove any movements older than 30 seconds
  for m in movements:
    if m < threshold:
      movements.remove(m)
    else:
      if lastsent + sendingThreshold < now:
        sendmail()
        getimage()
        lastsent = now

      print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(m)))

def getimage():
  host = os.environ['CAMERA_HOST']
  path = '/cgi-bin/currentpic.cgi'
  conn = http.client.HTTPSConnection(host, timeout=5, context=ssl._create_unverified_context())
  headers = { 'Authorization': 'Basic ' + os.environ['CAMERA_AUTH_KEY'] }
  conn.request('GET', path, None, headers)
  resp = conn.getresponse() 
  f = open(str(calendar.timegm(time.gmtime())) + '.jpg', 'wb')
  f.write(resp.read())
  f.close()
  print(resp.status)

def sendmail():
  msg = MIMEText('Sample message')
  msg['Subject'] = 'Movement alert'
  msg['To'] = os.environ['MAIL_TO']
  msg['From'] = os.environ['MAIL_FROM']

  s = smtplib.SMTP_SSL('in-v3.mailjet.com', 465)
  s.ehlo()
  s.login(os.environ['SMTP_USERNAME'], os.environ['SMTP_PASSWORD'])
  s.sendmail(os.environ['MAIL_FROM'], os.environ['MAIL_TO'], msg.as_string())
  s.close()

  print("Notification mail sent")


print("Starting")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(12, GPIO.IN)

movements = []
lastsent = 0

cleanup()
while True:
  i = GPIO.input(12)
  y = GPIO.input(11)
  if i == 1 and y == 1:
    movements.append(calendar.timegm(time.gmtime())) # add epoch time
    cleanup()

  time.sleep(1)

