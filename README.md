# adhoc_scripts
Scripts for adhoc changes. See below for details of each script

## make_SQL_statements.py
Script to generate the SQL query to update Moka.
This is normally performed by the [automated scripts](https://github.com/moka-guys/automate_demultiplex)
If the SQL query is not generated (e.g. when an error has occured), this script can be used to generate the query.

#### Required inputs:
- A text file with the samples list taken from the samplesheet
- For custom runs please provide: runtype, file, pipelineversion, runID. 
- For all ONC (inc TSO, SWIFT, Archer) runs please provide, runtype, file, pipelineversion, runID, NGSpanelID
pipelineversion and NGSpanelID can be found in the [automated scripts config file](https://github.com/moka-guys/automate_demultiplex/blob/master/automate_demultiplex_config.py)

#### make_SQL_statements.py --help:
'-r', '--runtype', help="Use: custompanels, ONC (includes ONC/Swift, ADX and TSO500), WES or SNP" <br>
'-f', '--file',  help="path to the txt file with samples in" <br>
'-p', '--pipelineversion', help="In number format e.g 4854" <br>
'-i', '--runid', help="e.g 220218_NB551068_0449_AHGML5AFX3 "       
'-n', '--ngspanelid', help="e.g 4396" 

## upload_runfolders.py
Script to generate commands to upload runfolders and samplesheets to DNA Nexus
This is normally performed by the [automated scripts](https://github.com/moka-guys/automate_demultiplex)
If errors with the automated scripts mean runfolders have not been uploaded to DNA Nexus, this script can be used to backup the runfolder. It uses the [backup_runfolder.py](https://github.com/moka-guys/workstation_housekeeping/blob/master/backup_runfolder.py) script.

#### Required inputs:
A text file (tab separated) with a list of runfolder names and DNA Nexus project names

#### Outputs:
- Text file with list of commands to run the backup_runfolder.py script 
- Text file with list of commands to run the DNA Nexus upload agent to upload the samplesheet to the workstation. Note: "/usr/local/src/mokaguys/.dnanexus_auth_token" will need to be replaced with the authentication token prior to running.

## manual_md5_checksum.py
Script to be run on the workstation to check the md5 check sum of three folders, across two copies of the same sequencing run 
This  is normally performed by the automated intergirty scripts on the sequencer (https://github.com/moka-guys/integrity_checking)
This adhoc script can be used if permissions errors on the sequencer mean python cannot be run and this cannot be resolved via the fix in KB article 'Failing Integrity checks on sequencers' (KB0010053)

To be run "python manual_md5_checksum.py -p /path/to/folder1/ -c /path/to/folder2/ > run_id_output.txt"

### Required inputs: 
- Full path to two folders 

### manual_md5_checksum.py --help:
'-p1', '--path1', help="Full path to runfolder 1" <br>
'-p2', '--path2',  help="Full path to runfolder 2" <br>                  

## bulk_url_downloader.html

This is a static webpage that can be used to automate the download of multiple URLs.  

- Save the HTML file locally and open it with the webrowser of your choice.
- Copy & paste the URLs into the text box pictured below and click 'Download Files'
- The files will be downloaded one by one.  If you are prompted for permission to download multiple files try adjusting the download delay in the HTML file which is currently set at 1 second.

![image](./bulkUploader.png)
