"""
usage 
-t path to truth vcf
-q path to truth vcf
-s37 path to b37 snp positions
-s38 path to b38 snp positions
-qb build of query sample (choice of 37 or 38)
-tb build of truth sample (choice of 37 or 38)
"""
import sys
import os
import argparse
import gzip

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--truth_filepath")
    parser.add_argument("-q","--query_filepath")
    parser.add_argument("-tb","--truth_build", choices=["37","38"])
    parser.add_argument("-qb","--query_build", choices=["37","38"])
    parser.add_argument("-s37","--snp_pos_filepath_b37")
    parser.add_argument("-s38","--snp_pos_filepath_b38")
    return parser.parse_args()
    

def set_SNP_list(SNP37_file_path,SNP38_file_path):
    """
    Set up the SNP dictionary, with the position for each build for each snp
    """
    snp_set={}
    with open(SNP37_file_path) as snp_file:
        # loop throught list of SNPs to SNP info
        for line in snp_file.readlines():
            Chromosome,Start,Stop,rsID,Gene,REF=line.rstrip().split("\t")
            snp_set[rsID] = {"chr37":Chromosome,"pos37":Stop,"ref37":REF,"samples":{}}
    with open(SNP38_file_path) as snp_file:
        for line in snp_file.readlines():
            Chromosome,Start,Stop,rsID,Gene,REF=line.rstrip().split("\t")
            snp_set[rsID]["chr38"] = Chromosome
            snp_set[rsID]["pos38"] = Stop
            snp_set[rsID]["ref38"]= REF

    return snp_set

def parse_vcf(filepath, build, snp_dict):
    """
    Parse a VCF, given a build and populate the snp_dict with the genotype for each sample
    """
    if os.path.exists(filepath) and filepath.endswith(".gz"):
        with gzip.open(filepath,'rb') as vcf_in:
            vcf_list=vcf_in.readlines()
    elif os.path.exists(filepath) and filepath.endswith(".vcf"):
        with open(filepath,'r') as vcf_in:
            vcf_list=vcf_in.readlines()
    else:
        print "no filepath or can't determine if gzipped or not"
    
    for SNP in snp_dict:                  
        DP=None
        GT=None
        obs_REF=None
        obs_ALT=None
        genotype=None
        
        if build == "37":
            snp_chr = str(snp_dict[SNP]["chr37"].replace("chr",""))
            snp_pos = int(snp_dict[SNP]["pos37"])
        elif build == "38":
            snp_chr = str(snp_dict[SNP]["chr38"].replace("chr",""))
            snp_pos = int(snp_dict[SNP]["pos38"])
        for line in vcf_list:
            if line.startswith("#C"):
                sample_name = line.rstrip().split("\t")[-1]
                snp_dict[SNP]["samples"][sample_name] = {"genotype":genotype,"obs_ref":obs_REF,"obs_alt":obs_ALT,"obs_GT":GT,"obs_DP":DP}
            elif not line.startswith("#"):
                # set fields
                vcf_CHROM,vcf_POS,ID,vcf_REF,vcf_ALT,QUAL,FILTER,INFO,vcf_FORMAT,vcf_sample = line.rstrip().split("\t")
                # if same chrom and pos expect this is the correct variant
                if str(vcf_CHROM.replace("chr","")) == snp_chr and int(vcf_POS) == snp_pos:
                    # loop through format field and determine where GT and DP values are in the list - extract these values from
                    for count,i in enumerate(vcf_FORMAT.split(":")):
                        if i == "GT":
                            GT=vcf_sample.split(":")[count]
                        if i == "DP":
                            DP=vcf_sample.split(":")[count]
                    # as we have decomposed the VCF we want to ignore any genotypes with a full stop as this isn't the ALT allele predicted to be the correct genotype
                    if "." in GT:
                        DP=None
                        GT=None
                    # capture the REF,ALT
                    else:
                        obs_ALT=vcf_ALT
                        obs_REF=vcf_REF
                        # if the genotype is homozygous ref set the alt as the ref base
                        # record the genotype in base form (eg AA)
                        if GT == "0/0":
                            obs_ALT = vcf_REF
                            genotype="%s%s" %(vcf_REF,vcf_REF)
                        elif GT == "0/1":
                            genotype="%s%s" %(vcf_REF,vcf_ALT)
                        elif GT == "1/1":
                            genotype="%s%s" %(vcf_ALT,vcf_ALT)
                        else:
                            genotype="%s%s" %("?","?")
                        snp_dict[SNP]["samples"][sample_name] = {"genotype":genotype,"obs_ref":vcf_REF,"obs_alt":vcf_ALT,"obs_GT":GT,"obs_DP":DP}
    return snp_dict
                            
                            
def summarise_results(snp_dict):
    """
    Go through the dictionary of SNPs and print
    SNPID, sample1 genotype, sample2 genotype, match (yes/no)
    Followed by a count of matching SNPs.
    """
    example_SNP=snp_dict.keys()[0]
    sample_names=snp_dict[example_SNP]["samples"].keys()
    
    print "\t".join(["SNP",sample_names[0],sample_names[1],"Match?"])
    match_count=0
    for SNP in snp_dict:
        match_str="No"
        if snp_dict[SNP]["samples"][sample_names[0]]["genotype"]==snp_dict[SNP]["samples"][sample_names[1]]["genotype"] and snp_dict[SNP]["samples"][sample_names[1]]["genotype"]:
            match_count+=1
            match_str="Yes"
        print "\t".join([SNP,str(snp_dict[SNP]["samples"][sample_names[0]]["genotype"]),str(snp_dict[SNP]["samples"][sample_names[1]]["genotype"]),match_str])
    print "%s out of %s SNPs match" % (match_count,len(snp_dict.keys()))


args = parse_args()
SNP37_file_path=args.snp_pos_filepath_b37
SNP38_file_path=args.snp_pos_filepath_b38
snp_dict=set_SNP_list(SNP37_file_path,SNP38_file_path)
snp_dict = parse_vcf(args.truth_filepath,args.truth_build,snp_dict)
snp_dict =parse_vcf(args.query_filepath,args.query_build,snp_dict)
summarise_results(snp_dict)