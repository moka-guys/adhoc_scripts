"""
This script has been generated to handle uploading of runfolders to DNA Nexus
This action is normally performed by the automated scripts, but errors with these may result in runfolders not being uploaded

The script makes a python dictionary with runfolder name and DNANexus projectname
Use this to generate the commands to upload the runs to DNANexus using the backup_runfolder.py script (on the workstation)

INPUT: text file (tab separated) with a list of runfolders and DNA Nexus project names
OUTPUT: text file with the commands to run the backup_runfolder.py script 
"""

import datetime
import argparse 

def arg_parse():
    """
    Parses arguments supplied by the command line.
        :return: (Namespace object) parsed command line attributes

    Creates argument parser, defines command line arguments, then parses supplied command line arguments using the
    created argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.description = '''Provide a text file (tab separated) containing a list of runfolders and DNA Nexus project names to be backup up'''
    parser.add_argument('-f', '--file',  help="path to the txt file with list of runs")                          
    return parser.parse_args()

args = arg_parse()
now = str('{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now()))

# create a dictionary for the runs
runs = {}
with open(args.file) as runs_list:
	for run in runs_list:
		run_name, project_name = run.split("\t")
		runs[run_name] = project_name.strip("\n") # remove the \n character from the end of the lines

# ==================== ### create commands to upload runfolders ### =================================== 
# Create output file with commands to backup the runfolder
runfolders_outfile = "backup_runfolders_" + now + ".txt"

with open(runfolders_outfile, "a") as commands_file:
	for run_name, project_name in runs.items():
		backup_cmd = "/usr/local/src/mokaguys/apps/workstation_housekeeping/backup_runfolder.py -i /media/data3/share/%s -a /usr/local/src/mokaguys/.dnanexus_auth_token --ignore L00 -p %s --logpath /usr/local/src/mokaguys/automate_demultiplexing_logfiles/backup_runfolder_logfiles" % (run_name,project_name)
		commands_file.write(backup_cmd + "\n")

# ==================== ### create commands to upload samplesheet ### =================================== 
# Create output file with commands to upload the samplesheet
upload_agent_path = "/usr/local/src/mokaguys/apps/dnanexus-upload-agent-1.5.17-linux/ua"
Nexus_API_key = "/usr/local/src/mokaguys/.dnanexus_auth_token"
samplesheet_outfile = "backup_samplesheet_" + now + ".txt"

with open(samplesheet_outfile, "a") as commands_file:
	for run_name, project_name in runs.items():
		folder_name = "/" + project_name.replace("002_","")
		samplesheet_name = "/media/data3/share/samplesheets/" + run_name + "_SampleSheet.csv"
		backup_cmd = "%s -p %s -f %s --do-not-compress --auth-token %s %s" % (upload_agent_path, project_name, folder_name, Nexus_API_key, samplesheet_name)
		commands_file.write(backup_cmd + "\n")