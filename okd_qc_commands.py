"""
DNAnexus FastQC and MultiQC Command Generator

Created: 22/05/2024
Author: Bioinformatics @ Synnovis (Guy's & St. Thomas' NHS Foundation Trust)

This script automates the generation of DNAnexus MultiQC/FastQC commands for a given OncoDeep runfolder.
Must be ran on workstation where authkey file is present.

Usage:
    python3 qcgen.py -p {dnanexus_project_id} -f {illumina_runfolder_name}

Arguments:
    -p, --project    The DNAnexus project ID for the run.
    -f, --fastq_dir  The name of the run folder (i.e., 240521_A01229_0331_AHWGJGDRX3).

Output:
    Generates a shell script with commands to run FastQC and MultiQC on OKD fastq files.
"""

import os
import argparse
import re

def parse_arguments():
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser(description="Generate a shell script for running FastQC and MultiQC on OKD fastq files.")
    parser.add_argument("-p", "--project", required=True, help="The DNAnexus project ID for the run.")
    parser.add_argument("-f", "--fastq_dir", required=True, help="The name of the run folder (i.e., 240521_A01229_0331_AHWGJGDRX3).")
    return parser.parse_args()

def get_fastq_dir(fastq_dir):
    '''Construct the directory path containing fastq files'''
    return os.path.join("/media/data3/share", fastq_dir, "Data/Intensities/BaseCalls")

def get_okd_id(fastq_dir):
    '''Extract the OKD ID'''
    fastq_files = os.listdir(fastq_dir)
    for file in fastq_files:
        # Regex to extract OKD_XXXXX ID
        match = re.search(r'OKD\d{5}', file)
        if match:
            return match.group()
    raise ValueError("No OKD ID found in fastq files.")

def get_fastq_files(fastq_dir):
    '''Create list of all OKD fastq files'''
    # Use startswith to exclude undetermined fastqs
    return [f for f in os.listdir(fastq_dir) if f.startswith("OKD") and f.endswith(".fastq.gz")]

def sort_fastq_files(fastq_files):
    '''Sort the fastq files based on sample number'''
    def sort_key(filename):
        # Get the RX sample ID from the end of the fastq name
        sample_name = "_".join(filename.split("_")[:-2]) 
        # Remove letter to leave int for sorting
        sample_number = int(re.search(r'S(\d+)', sample_name).group(1))
        return sample_number
    return sorted(fastq_files, key=sort_key)

def read_auth_token(token_path):
    '''Read DNAnexus auth token from file'''
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def generate_script(fastq_folder_name, okd_id, provided_fastq_folder_name, fastq_files, project_id, auth_token):
    '''Generate the shell script'''
    script_filename = "{}_multiqc_fastqc.sh".format(fastq_folder_name)
    with open(script_filename, "w") as script_file:
        # Create and open the output shell script file
        script_file.write("depends_list=''\n\n")
        for r1_file in fastq_files:
            if "_R1_" in r1_file:
                r2_file = r1_file.replace("_R1_", "_R2_")
                sample_name = "_".join(r1_file.split("_")[:-3])

                # Write the FastQC command for each pair of fastq files
                script_file.write(
                    "jobid=$(dx run project-ByfFPz00jy1fk6PjpZ95F27J:/Apps/fastqc_v1.4.0 --priority high -y "
                    "--name {sample_name} -ireads={provided_fastq_folder_name}:/{fastq_folder_name}_{okd_id}/Data/Intensities/BaseCalls/{r1_file} "
                    "-ireads={provided_fastq_folder_name}:/{fastq_folder_name}_{okd_id}/Data/Intensities/BaseCalls/{r2_file} "
                    "--dest={provided_fastq_folder_name}:/ --brief --auth-token {auth_token})\n".format(
                        sample_name=sample_name, provided_fastq_folder_name=provided_fastq_folder_name, fastq_folder_name=fastq_folder_name, r1_file=r1_file, r2_file=r2_file, okd_id=okd_id, auth_token=auth_token
                    )
                )
                script_file.write("depends_list=\"${depends_list} -d ${jobid} \"\n")
        
        # Write the MultiQC command
        script_file.write(
            "jobid=$(dx run project-ByfFPz00jy1fk6PjpZ95F27J:/Apps/multiqc_v1.18.0 --priority high -y "
            "--instance-type mem1_ssd1_v2_x4 -iproject_for_multiqc={provided_fastq_folder_name} "
            "-icoverage_level=100 --project={project_id} $depends_list --brief --auth-token {auth_token})\n".format(
                provided_fastq_folder_name=provided_fastq_folder_name, project_id=project_id, auth_token=auth_token
            )
        )
        script_file.write("depends_list=\"${depends_list} -d ${jobid} \"\n")
        
        # Write the upload_multiqc command
        script_file.write(
            "jobid=$(dx run project-ByfFPz00jy1fk6PjpZ95F27J:/Apps/upload_multiqc_v1.4.0 --priority high -y "
            "--instance-type mem1_ssd1_v2_x2 -imultiqc_html=$jobid:multiqc_report -imultiqc_data_input=$jobid:multiqc "
            "-imultiqc_data_input={provided_fastq_folder_name}:/{fastq_folder_name}_{okd_id}/{fastq_folder_name}.illumina_lane_metrics "
            "--project={project_id} $depends_list --brief --auth-token {auth_token})\n".format(
                provided_fastq_folder_name=provided_fastq_folder_name, fastq_folder_name=fastq_folder_name, okd_id=okd_id, project_id=project_id, auth_token=auth_token
            )
        )

    print("Shell script generated successfully: {}".format(script_filename))

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Construct the directory path for fastq files
    fastq_dir = get_fastq_dir(args.fastq_dir)
    
    # Extract the OKD ID from fastq files
    okd_id = get_okd_id(fastq_dir)
    
    # Get the fastq folder name
    fastq_folder_name = os.path.basename(os.path.normpath(os.path.join(fastq_dir, "..", "..", "..")))
    
    # Create the provided fastq folder name
    provided_fastq_folder_name = "003_{}_{}".format(fastq_folder_name, okd_id)
    
    # Get the list of fastq files
    fastq_files = get_fastq_files(fastq_dir)
    
    # Sort the fastq files
    sorted_fastq_files = sort_fastq_files(fastq_files)
    
    # Read the DNAnexus auth token from file
    auth_token = read_auth_token("/usr/local/src/mokaguys/.dnanexus_auth_token")
    
    # Generate the shell script with FastQC and MultiQC commands
    generate_script(fastq_folder_name, okd_id, provided_fastq_folder_name, sorted_fastq_files, args.project, auth_token)

if __name__ == "__main__":
    main()