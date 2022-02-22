'''
This script has been created so the SQL generation step of
the upload_and_set_off_workflows.py script can be run independently 

Currently, samplesheet information needs to be seperated by line breaks in a txt file 
Ensure there is not an empty liine at the end of your txt file please : ) 

INPUT: Command line arguments given as displayed in --help. 
OUTPUT: SQL query returned to a txt file

'''

import argparse 
from datetime import datetime

# To enable SQL generation for different types of runs ===========================================
def arg_parse():
    """
    Parses arguments supplied by the command line.
        :return: (Namespace object) parsed command line attributes

    Creates argument parser, defines command line arguments, then parses supplied command line arguments using the
    created argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.description = '''For custom runs please provide: runtype, file, pipelineversion, runID. \n For all ONC (inc TSO, SWIFT, Archer) 
    runs please provide, runtype, file, pipelineversion, runID, NGSpanelID'''
    parser.add_argument('-r', '--runtype', help="Use: custompanels, ONC (includes ONC/Swift, ADX and TSO500), WES or SNP")
    parser.add_argument('-f', '--file',  help="path to the txt file with samples in")
    parser.add_argument('-p', '--pipelineversion', help="In number format e.g 4854")
    parser.add_argument('-i', '--runid',help="e.g 220218_NB551068_0449_AHGML5AFX3 ")       
    parser.add_argument('-n', '--ngspanelid',help="e.g 4396")                            
    return parser.parse_args()

args = arg_parse()

custom_query_list = [] # empty list to store each patients query

#=========================== ## Custom panels & Oncology runs (including Archer, Swift/ONC and TSO500) ## ==================
# open the file passed via the command line 
with open(args.file) as file: 
    for sample in file:
        if args.runtype == "custompanels" or args.runtype == "SNP": # Populate correct query
            DNAnumber = sample.split("_")[2] # split each sample (on each line by the second underscore), only one needed for custompanels
            query = ("insert into NGSCustomRuns(DNAnumber,PipelineVersion, RunID) values ('{DNANumber_placeholder}',"
                                                            "'{PipelineVersion_placeholder}','{RunID_placeholder}')"
                    ).format(
                DNANumber_placeholder=DNAnumber,
                PipelineVersion_placeholder=args.pipelineversion,
                RunID_placeholder=args.runid
            )
            custom_query_list.append(query) # add to the list
        if args.runtype == "ONC": # ONC covers ONC/SWIFT, Archer & TSO
            DNAnumber_one = sample.split("_")[2] # Two dnanumbers for onc samples
            DNAnumber_two = sample.split("_")[3] 
            #if "NTCcon" in sample:
            #    id2 = "NULL"
            query = ("insert into NGSOncologyAudit(SampleID1,SampleID2,RunID,PipelineVersion,ngspanelid) values"
                "('{DNANumberone_placeholder}',' {DNANumbertwo_placeholder}', '{RunID_placeholder}', '{PipelineVersion_placeholder}','{NGSPanelID_placeholder}')"
                    ).format(
                DNANumberone_placeholder=DNAnumber_one, 
                DNANumbertwo_placeholder=DNAnumber_two, 
                PipelineVersion_placeholder=args.pipelineversion,
                RunID_placeholder=args.runid,
                NGSPanelID_placeholder=args.ngspanelid
            )
            custom_query_list.append(query)

query_list = "\n".join(custom_query_list) # remove list brackets

#=========================== ## WES runs ## ==================

dna_id =[] # Create an empty list to append all the DNAnumbers for the run in 

with open(args.file) as file: # open the file passed via the command line 
    for sample in file:
        if args.runtype == "WES": 
            DNAnumber = sample.split("_")[2] # Get all the DNAnumbers from the samples in the file
            dna_id.append(DNAnumber) # Add them into the list 
            dna_id_list_unlisted = ", ".join(dna_id) # remove list brackets
# Generate query with list of DNANumbers 
            query_list = ("update NGSTest set PipelineVersion = {PipelineVersion_placeholder} , StatusID = 1202218805 where dna in ('{DNAlist_placeholder} ') and StatusID = 1202218804"
                ).format(
                    PipelineVersion_placeholder=args.pipelineversion,
                    DNAlist_placeholder=dna_id_list_unlisted 
                            )
                
# ========================== ### Check for None in the query list ### ================
#added to highlight when required command line arguments (e.g. runID) not given
for item in query_list: 
    if isinstance(item, type(None)) == True:
        print("Some elements of your query are none, did you provide all the required arguments for you run type?")
    else: 
        print("No empty fields found, all arguments given")

#=========================== ### Save output to a txt file for audit trail ### ==================
# Make the file name the runid and todays date
filename = args.runid + "_" + datetime.today().strftime('%Y-%m-%d')
#print(query_list)
new_file = open(filename+".txt", "a")
new_file.write(query_list) 
new_file.close()
print("File saved as: " + filename)
