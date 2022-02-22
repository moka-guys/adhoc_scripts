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
'-r', '--runtype', help="Use: custompanels, ONC (includes ONC/Swift, ADX and TSO500), WES or SNP"
'-f', '--file',  help="path to the txt file with samples in"
'-p', '--pipelineversion', help="In number format e.g 4854"
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
