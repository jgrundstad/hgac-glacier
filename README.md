# hgac-glacier
scripts for backing up HGAC run directories to glacier

1. Create a compressed tape archive of the Illumina run directory:

    `tar czvf run_directory.tar.gz run_directory`

2. Split the archive into 4GB chunks:

    `split -a 4 -b 4294967296 run_directory.tar.gz`

3. upload chunks:

    `ls run_directory[a-z]* | xargs -IFILE python upload.py ......`



```bash
usage: upload.py [-h] -f INFILE [-d DESCRIPTION] -V VAULT -a ACCESS_KEY -s
                 SECRET_KEY -c ACCOUNT_ID

Upload single archive file to the provided Glacier vault. 
Requires sqlite db: glacier_archive.sqlite3 

sqlite> create table archives (date text, run_name text, filename text, 
        archive_id text);

optional arguments:
  -h, --help            show this help message and exit
  -f INFILE, --file INFILE
                        File to be archived.
  -d DESCRIPTION, --description DESCRIPTION
  -V VAULT, --vault VAULT
                        Glacier vault.
  -a ACCESS_KEY, --aws-access-key-id ACCESS_KEY
  -s SECRET_KEY, --aws-secret-access-key SECRET_KEY
  -c ACCOUNT_ID, --aws-account-id ACCOUNT_ID
```
