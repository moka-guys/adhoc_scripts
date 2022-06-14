from checksumdir import dirhash
import argparse 

## What this script does ##
# This script will determine the md5 check sum of two run folders for the same sequencing run 
# It will check the "InterOp","Thumbnail_Images" and  "Data" directories.

## How to use it ##
# Two inputs are given as paths via the command line 
# please specify the output file when running the script as follows 
# python manual_md5_checksum.py -p /path/to/folder1/ -c /path/to/folder2/ > run_id_output.txt

# arg_parser ===========================================
def arg_parse():
    """
    Parses arguments supplied by the command line.
        :return: (Namespace object) parsed command line attributes
    Creates argument parser, defines command line arguments, then parses supplied command line arguments using the
    created argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.description = '''Use this script to compare two compies of the same sequencing run via an md5 checksum. Script will check Interop, Thumbnail_Images and Data directories'''
    parser.add_argument('-p1', '--path1', help="Full path to runfolder 1")
    parser.add_argument('-p2', '--path2',  help="Full path to runfolder 2")                  
    return parser.parse_args()

# Script ===========================================
args = arg_parse()

# List of directories for loop
directories_to_check = ["InterOp","Thumbnail_Images","Data"]

# For each directory in the loop
for directory in directories_to_check:
    
    print("Working on the " + directory + " directory.")
      
    # Run dirshash in md5 mode
    check_runfolder_1_directory_hash = dirhash(args.path1+directory, "md5")
    check_runfolder_2_directory_hash = dirhash(args.path2+directory, "md5")

    print("Runfolder 1 " + args.path1 + " md5 checksum for the directory " + directory + " = " + check_runfolder_1_directory_hash)
    print("Runfolder 2 " + args.path2 +  " md5 checksum for the directory " + directory + " = " + check_runfolder_2_directory_hash)    

    # Compare hashes     
    if check_runfolder_1_directory_hash == check_runfolder_2_directory_hash:
        print ("MD5 checksums match for "+ directory + " directory")
    else: 
        print ("MD5 checksums do not match for "+ directory + " directory")


 # Make the path to directory 1
    #path_to_runfolder_1 = args.path1+directory
    # Make the path to directory 2
    #path_to_runfolder_2 = args.path2+directory
