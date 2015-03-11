import argparse
import datetime
import boto
import boto.glacier.layer2
import sqlite3
import sys
import os

SQLITE_DB = 'glacier_archive.sqlite3'
ACCESS_KEY = ''
SECRET_KEY = ''
ACCOUNT_ID = ''


def record_successful_upload(run_name=None, filename=None, archive_id=None,
                             **kwargs):
  '''record info in glacier_archive.sqlite3'''
  dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  try:
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.execute("INSERT INTO archives VALUES('%s', '%s', '%s', '%s')" % \
        (dt, run_name, filename, archive_id))
    conn.commit()
    conn.close()
  except Exception as e:
    print >>sys.stderr, \
        "ERROR: unable to update sqlite3 with:\n%s\n%s\n%s\ninfo: %s" % \
        (run_name, filename, archive_id, str(e))
    raise
  print >>sys.stderr, ("COMPLETE: %s" % archive_id)


def upload_file(infile=None, vault=None, description=None, **kwargs):
  archive_id = ''
  try:
    l2 = boto.glacier.layer2.Layer2(aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY, account_id=ACCOUNT_ID)
    v = l2.get_vault(vault)
    # attend to unicode bug in returned name
    v.name = str(v.name)
    archive_id = v.concurrent_create_archive_from_file(infile, description)
  except Exception as e:
    print >>sys.stderr, "ERROR: Unable to upload to glacier: %s" % infile
    print >>sys.stderr, "Info: " + str(e)
    raise

  record_successful_upload(run_name=description, filename=infile, 
      archive_id=archive_id)


def confirm_db():
  if not os.path.isfile(SQLITE_DB):
    sys.exit("ERROR: %s is missing" % SQLITE_DB)


def main():
  parser = argparse.ArgumentParser(description='''Upload single archive file 
to the provided Glacier vault.  Requires sqlite db: %s  
[sqlite> create table archives (date text, run_name text, filename text, 
 archive_id text);]''' % SQLITE_DB)

  parser.add_argument('-f', '--file', dest='infile', action='store',
      required=True, help='File to be archived.')
  parser.add_argument('-d', '--description', dest='description',
      action='store')
  parser.add_argument('-V', '--vault', dest='vault', action='store',
      required=True, help='Glacier vault.')
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

  sys.stderr.write("file: %s ... " % args.infile)
  confirm_db()
  upload_file(infile=args.infile, vault=args.vault, 
      description=args.description)
  

if __name__ == '__main__':
  main()
