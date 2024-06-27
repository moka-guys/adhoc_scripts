"""
DNAnexus FastQC and MultiQC Command Generator

Created: 22/05/2024
Author: Bioinformatics @ Synnovis (Guy's & St. Thomas' NHS Foundation Trust)

This script automates the generation of DNAnexus MultiQC/FastQC commands for any runfolder

Usage:
    python3 qc_command_generation.py -p {dnanexus_project_id} -f {illumina_runfolder_name}

Arguments:
    -p, --project_id        The DNAnexus project ID for the run.
    -r, --runfolder_name    The name of the run folder (e.g., 240521_A01229_0331_AHWGJGDRX3)
    -a, --auth_token        Authentication token string
Output:
    Generates a shell script with commands to run FastQC and MultiQC on OKD fastq files.
"""

import argparse
import subprocess


def execute_subprocess_command(command: str):
    """
    Execute a subprocess
        :param command(str):            Input command
        :return (stdout(str),
        stderr(str)) (tuple):           Outputs from the command
    """
    proc = subprocess.Popen(
        [command],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
        executable="/bin/bash",
    )
    out, err = proc.communicate()
    out = out.decode("utf-8").strip()
    err = err.decode("utf-8").strip()
    return out, err


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate a shell script for running FastQC and MultiQC on OKD fastq files."
    )
    parser.add_argument(
        "-p",
        "--project_id",
        required=True,
        type=str,
        help="The DNAnexus project ID for the run",
    )
    parser.add_argument(
        "-r",
        "--runfolder_name",
        required=True,
        type=str,
        help="The name of the run folder (e.g., 240521_A01229_0331_AHWGJGDRX3)",
    )
    parser.add_argument(
        "-a",
        "--auth_token",
        required=True,
        type=str,
        help="Authentication token string",
    )
    return parser.parse_args()


class GenerateQCCmds:
    """
    Class to generate all QC commands for any given runfolder

    Attributes
        runfolder_name (str):   Name of runfolder
        project_id (str):       DNAnexus project ID
        auth_token (str):       DNAnexus auth token
        fastq_id_cmd (str):     Command for identifying fastqs within the project 
        fastqs_dict (dict):     Dictionary to hold fastq names and IDs
        script_filename (str):  Name of output bash script
        project_name (str):     Name of DNAnexus project
        dx_cmds (list):         List to hold generated commands

    Methods
        get_fastq_files()
            Create list of all fastq file IDs, excluding Undetermined
        generate_fastqc_cmds()
            Generate per sample fastq commands and dependency strings
        generate_multiqc_cmds()
            Generate commands for MultiQC job and dependency string
        generate_upload_multiqc_cmd()
            Generate command for MultiQC upload job
        write_cmds()
            Generate the shell script
    """

    def __init__(self, runfolder_name: str, project_id: str, auth_token: str):
        """
        Constructor for GenerateQCCmds class
            :param runfolder_name (str):    Name of runfolder
            :param project_id (str):        ID of project in DNAnexus
            :param auth_token (str):        DNAnexus authentication token
        """
        self.runfolder_name = runfolder_name
        self.project_id = project_id
        self.auth_token = auth_token
        self.fastq_id_cmd = (
            f"dx find data --path={self.project_id}:{self.runfolder_name} --brief --name "
            f"'*.fastq.gz' --tag as_upload --auth {self.auth_token}"
        )
        self.fastqs_dict = self.get_fastq_files()
        self.script_filename = f"{self.runfolder_name}_qc.sh"
        self.project_name, _ = execute_subprocess_command(
            f"dx describe {self.project_id} --auth {self.auth_token} --json | jq -r .name"
        )
        self.dx_cmds = ["depends_list=''\n\n"]
        self.dx_cmds.extend(self.generate_fastqc_cmds())
        self.dx_cmds.extend(self.generate_multiqc_cmds())
        self.dx_cmds.append(self.generate_upload_multiqc_cmd())
        self.write_cmds()

    def get_fastq_files(self) -> dict:
        """
        Create list of all fastq file IDs, excluding Undetermined
            :return dict:   Dictionary with file names as keys and IDs as items
        """
        fastqs_dict = {}
        # Use startswith to exclude undetermined fastqs
        file_ids, _ = execute_subprocess_command(self.fastq_id_cmd)
        # Exclude undetermined
        for file_id in file_ids.split("\n"):
            name, _ = execute_subprocess_command(f"dx describe {file_id} --json | jq -r .name | grep -v Undetermined")
            if name:
                fastqs_dict[name] = file_id     
        return dict(sorted(fastqs_dict.items()))

    def generate_fastqc_cmds(self) -> list:
        """
        Generate per sample fastq commands and dependency strings
            :return list:   List of commands
        """
        fastqc_cmds = []
        fastqs_dict_temp = self.fastqs_dict
        for fastq_name, fastq_id in fastqs_dict_temp.items():
            if "_R1_" in fastq_name:
                r1_name = fastq_name
                r2_name = fastq_name.replace("_R1_", "_R2_")
                r1_id = fastq_id
                r2_id = fastqs_dict_temp[r2_name]

                sample_name = "_".join(fastq_name.split("_")[:-3])

                # Write the FastQC command for each pair of fastq files
                fastqc_cmds.append(
                    "jobid=$(dx run project-ByfFPz00jy1fk6PjpZ95F27J:/Apps/fastqc_v1.4.0 --priority high -y "
                    f"--name {sample_name} -ireads={r1_id} -ireads={r2_id} "
                    f"--dest={self.project_id}:/ --brief --auth-token {self.auth_token})\n"
                )
                fastqc_cmds.append('depends_list="${depends_list} -d ${jobid} "\n')
        return fastqc_cmds

    def generate_multiqc_cmds(self) -> list:
        """
        Generate commands for MultiQC job and dependency string
            :return list:   List containing MultiQC command and dependency string
        """
        multiqc_cmds = []
        # Write the MultiQC command
        multiqc_cmds.append(
            "jobid=$(dx run project-ByfFPz00jy1fk6PjpZ95F27J:/Apps/multiqc_v1.18.0 --priority high -y "
            f"--instance-type mem1_ssd1_v2_x4 -iproject_for_multiqc={self.project_name} "
            f"-icoverage_level=100 $depends_list --dest={self.project_id} --brief --auth-token {self.auth_token})\n"
        )
        multiqc_cmds.append('depends_list="${depends_list} -d ${jobid} "\n')
        return multiqc_cmds

    def generate_upload_multiqc_cmd(self) -> str:
        """
        Generate command for MultiQC upload job
            :return str:    MultiQC upload job command string
        """
        return (
            "jobid=$(dx run project-ByfFPz00jy1fk6PjpZ95F27J:/Apps/upload_multiqc_v1.4.0 --priority high -y "
            "--instance-type mem1_ssd1_v2_x2 -imultiqc_html=$jobid:multiqc_report -imultiqc_data_input=$jobid:multiqc "
            f"-imultiqc_data_input={self.project_name}:/{self.runfolder_name}/{self.runfolder_name}.illumina_lane_metrics "
            f"$depends_list --dest={self.project_id} --brief --auth-token {self.auth_token})\n"
        )

    def write_cmds(self) -> None:
        """
        Generate the shell script
            :return None:
        """
        with open(self.script_filename, "w") as script_file:
            for command in self.dx_cmds:
                # Create and open the output shell script file
                script_file.write(command)
        print(f"Shell script generated successfully: {self.script_filename}")


def main():
    # Parse command line arguments
    args = parse_arguments()

    # Generate the shell script with FastQC and MultiQC commands
    GenerateQCCmds(args.runfolder_name, args.project_id, args.auth_token)


if __name__ == "__main__":
    main()
