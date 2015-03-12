import argparse
import boto
import boto.glacier.layer2
import datetime
import json
import os
import sqlite3
import sys

SQLITE_DB = 'glacier_archive.sqlite3'
ACCESS_KEY = ''
SECRET_KEY = ''
ACCOUNT_ID = ''
#SNS_TOPIC = 'arn:aws:glacier:us-east-1:203237044369:vaults/'

def check_jobs_status(vault=None, **kwargs):
  l = list()
  try:
    l2 = boto.glacier.layer2.Layer2(aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY, account_id=ACCOUNT_ID)
    v = l2.get_vault(vault)
    # attend to unicode bug in returned name
    v.name = str(v.name)
    for job in v.list_jobs():
      j = {'JobID': job.id,
           'Action': job.action,
           'ArchiveID': job.archive_id,
           'StatusCode': job.status_code,
           }
      l.append(j)
  except Exception as e:
    print >>sys.stderr, "ERROR: Unable to query glacier job"
    print >>sys.stderr, "Info: " + str(e)
    raise
  return l


def main():
  parser = argparse.ArgumentParser(description='Check glacier download ' \
      + 'request status')

  parser.add_argument('-V', '--vault', dest='vault', action='store',
      required=True, help='Glacier vault.')
  #parser.add_argument('-s', '--sns-topic', dest='sns', action='store',
  #    required=True, help='SNS topic for notifications (append to default '
  #    + 'header: arn:aws:glacier:us-east-1:203237044369:vaults/)')
  parser.add_argument('-a', '--aws-access-key-id', dest='access_key',
      action='store', required=True)
  parser.add_argument('-s', '--aws-secret-access-key', dest='secret_key',
      action='store', required=True)
  parser.add_argument('-c', '--aws-account-id', dest='account_id',
      action='store', required=True)
  args = parser.parse_args()

  global ACCESS_KEY
  ACCESS_KEY = args.access_key
  global SECRET_KEY
  SECRET_KEY = args.secret_key
  global ACCOUNT_ID
  ACCOUNT_ID = args.account_id

  status = check_jobs_status(vault=args.vault) 
  print json.dumps(status, indent=2)
  

if __name__ == '__main__':
  main()
