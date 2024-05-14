#!/usr/bin/env python3
#coding: UTF-8

#
# Author: Sergii Kulyk
#
# Input - you can provide necessary data as arguments or environment variable
# -n | --name  | SYMPHONY_BOT_NAME | bot name (usually in form of email)
# -u | --url   | SYMPHONY_API_URL  | url to your symphony chat
# -r | --room  | SYMPHONY_ROOM_ID  | room_id to send messages
# -t | --token | SYMPHONY_TOKEN    | generated jwt token (if you didn't provide RSA private key)
# -k | --key   | SYMPHONY_KEY_FILE | path to RSA private key file (if you didn't provide JWT token)
#	if you have provided key, script will generate token file in the same directory and
#       renew it from time to time


from jose import jwt
import datetime as dt
import requests
import json
import sys
import argparse
import os

# disable ssl warnings
requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser(prog='symphony-handler.py', usage='\n\t %(prog)s -r room_id', description='Script to send text to symphony room')
parser.add_argument('-r', '--room', action='store', help="rooom_id", required=False)
parser.add_argument('-k', '--key',  action='store', help="ssh key", required=False)
parser.add_argument('-n', '--name', action='store', help="bot name", required=False)
parser.add_argument('-u', '--url',  action='store', help="symphony api url", required=False)
parser.add_argument('-t', '--token',action='store', help="symphony api token", required=False)
args = parser.parse_args()

room    = args.room if args.room else os.environ.get('SYMPHONY_ROOM_ID', '')
name    = args.name if args.name else os.environ.get('SYMPHONY_BOT_NAME', '')
keyfile = args.key  if args.key else os.environ.get('SYMPHONY_KEY_FILE', '')
url     = args.url  if args.url else os.environ.get('SYMPHONY_API_URL', '')
token   = args.token if args.token else os.environ.get('SYMPHONY_TOKEN', '')
tempfile=keyfile+'.cache.tmp'

# in case of generate GWT token set expiration to 24 hours
expiration = 24 * 60 * 60

timestamp_now = int(dt.datetime.now(dt.timezone.utc).timestamp())

# Token was not provided. Checking for cache
if token == "":
  if os.path.isfile(tempfile):
    tempfileH = open(tempfile,'r')
    templine=tempfileH.read().strip()
    tempfileH.close()
    if templine:
      values=templine.split(" ")
      if int(values[0]) > timestamp_now:
        token = values[1]

# token was not provided and not found in cache, Generate new JWT token
if token == "":
  keyfile = open(keyfile, 'r')
  keyLines = keyfile.readlines()
  key=''

  for line in keyLines:
    if "BEGIN RSA PRIVATE KEY" in line:
      key = key + line.strip() + "\n"
    elif "END RSA PRIVATE KEY" in line:
      key = key + "\n" + line
    else:
      key = key + line.strip()
  keyfile.close()

  expiration_date = int(timestamp_now + expiration)
  payload = {
    'sub': name,
    'iat': timestamp_now,
    'exp': expiration_date
  }
  token = jwt.encode(payload, key, algorithm='RS512')

  # store token to cache
  tokenfile=open(tempfile,'w')
  tokenfile.write(str(expiration_date) + ' ' + token)
  tokenfile.close()


event = json.load(sys.stdin)
if (event["check"]["status"] == 0):
    status = "OK"
elif (event["check"]["status"] == 1):
    status = "WARNING"
elif (event["check"]["status"] == 2):
    status = "CRITICAL"
else:
    status = "unknown"

checkname=event["check"]["metadata"]["name"]
namespace=event["check"]["metadata"]["namespace"]
entity=event["entity"]["metadata"]["name"]
message= "[%s] status is %s for check [%s] (agent: %s)" % (namespace,status,checkname,entity)

# DEBUG
# print("curl -k -v -XPOST \"" + url + "/cvsym/v1/bot/room/" + room + "/message\" -H 'accept: */*' -H \"Authorization: Bearer " + token + "\" -H 'Content-Type: multipart/form-data' -F 'attachment=' -F \"message='"+message+"'\"")

# send to room
resp = requests.post(url+'/cvsym/v1/bot/room/'+room+'/message',data={'message':message}, headers={'Authorization': 'Bearer ' + token, 'accept':'*/*'}, verify=False)
