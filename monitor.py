import RPi.GPIO as GPIO
import time
import ssl
import calendar
import http.client
import smtplib
import os
from pathlib import Path
from email.mime.text import MIMEText

sendingThreshold = 5*60 # 5 minutes
imageThreshold = 1*60 # 1 minute

def trigger():
  global lastsent
  global lastimage

  image = None
  now = calendar.timegm(time.gmtime())
  if (lastimage + imageThreshold < now):
    image = getimage()
    lastimage = now

  emailfile = Path('email-flag')
  if (lastsent + sendingThreshold < now) and (emailfile.is_file()):
    sendmail(image)
    lastsent = now

  print('Triggered ' + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(now)))

def getimage():
  host = os.environ['CAMERA_HOST']
  path = '/cgi-bin/currentpic.cgi'
  conn = http.client.HTTPSConnection(host, timeout=5, context=ssl._create_unverified_context())
  headers = { 'Authorization': 'Basic ' + os.environ['CAMERA_AUTH_KEY'] }
  conn.request('GET', path, None, headers)
  resp = conn.getresponse() 
  image = 'captured_images/' + str(calendar.timegm(time.gmtime())) + '.jpg'
  f = open(image, 'wb')
  f.write(resp.read())
  f.close()
  print('Image captured with http response' + str(resp.status) + ' to image ' + image)
  return image

def sendmail(image):
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

lastsent = 0
lastimage = 0

while True:
  i = GPIO.input(12)
  y = GPIO.input(11)
  if i == 1 and y == 1:
    trigger()

  time.sleep(1)

