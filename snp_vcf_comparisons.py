'''
This script compares two gVCFS when tested by different SNP genotyping assays, an 'observed' - in this case from a SNP genotyping assay and an 'expected' "truth" set.

gVCFs should be created, applying BED file to limit calls to the desired SNPs
The VCFs should then be decomposed by vt

This script matches gVCFs using a common identified, here the third item when split on underscore and compares the ALT and Genotype at each position.
The read depth at each location is also retreived and reported for each sample (in observed/test sample - not the expected as this is a irrelevant methodology.)

The script performs analysis seperately for GIAB samples (with na) in filename.
'''

import os

# create two dictionaries to hold results - one for GIAB and one for non-GIAB
dict={"variant":{},"samples":{}}
dict2={"variant":{},"samples":{}}
# create two lists for dna numbers
samples=[]
samples2=[]
# define output files
output_file1='/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/non_giab_results.txt'
output_file2='/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/giab_results.txt'
output_file3='/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/non_giab_coverage.txt'
output_file4='/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/giab_coverage.txt'
# loop throught list of SNPs to SNP info
with open ('/home/mokaguys/Desktop/snp_genotyping_NP/SNP_POS.txt','r') as variant_list:
    for line in variant_list.readlines():
        Chromosome,Start,Stop,rsID,Gene,REF=line.rstrip().split("\t")
        dict["variant"][Gene] = {"chr":Chromosome,"pos":Stop,"ref":REF,"RS":rsID,"samples":{}}
        dict2["variant"][Gene] = {"chr":Chromosome,"pos":Stop,"ref":REF,"RS":rsID,"samples":{}}

# loop through all 'observed' decmposed gVCFs 
for obs_file in os.listdir("/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/vcfs_decomposed"):
    if obs_file.endswith(".vcf"):
        dna_num = obs_file.split("_")[3]
        # take DNA number and ensure not a GIAB sample
        if "na" not in dna_num:
            # add dna number to list to help create outputs later
            samples.append(dna_num)
            # loop through expected vcfs - finding the vcf which corresponds to the test sample
            for exp_file in os.listdir("/media/MokaNAS2/projects/190619_Nimegen_SNP_part2/expected/vcf_decomposed"):
                if exp_file.endswith(".vcf") and dna_num in exp_file:
                    # set up dict entry
                    dict["samples"][dna_num]={"obs_file":obs_file,"exp_file":exp_file,"observed_var":{},"expected_var":{}}
                    # for each gene (SNP)
                    for gene in dict["variant"]:
                        # set up more dictionary entries
                        dict["variant"][gene]["samples"][dna_num]={"obs_var":{},"exp_var":{}}
                        # set flag to determine if this SNP was found
                        found=False
                        # loop through observed gVCF
                        with open("/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/vcfs_decomposed/" + obs_file,'r') as obs_vcf:
                            for line in obs_vcf.readlines():
                                if not line.startswith("#"):
                                    # set fields
                                    CHROM,POS,ID,REF,ALT,QUAL,FILTER,INFO,FORMAT,sample = line.rstrip().split("\t")
                                    # if same chrom and pos expect this is the correct variant
                                    if CHROM==dict["variant"][gene]["chr"] and POS==dict["variant"][gene]["pos"]:
                                        # set empty values for DP and GT
                                        DP="?"
                                        GT="?"
                                        # loop through format field and determine where GT and DP values are in the list - extract these values from
                                        for count,i in enumerate(FORMAT.split(":")):
                                            if i == "GT":
                                                GT=sample.split(":")[count]
                                            if i == "DP":
                                                DP=sample.split(":")[count]
                                        # as we have decomposed the VCF we want to ignore any genotypies with a full stop as this isn't the ALT allele predicted to be the correct genotype
                                        if "." in GT:
                                            DP="?"
                                            GT="?"
                                        # capture the REF,ALT GT and DP
                                        else:
                                            found=True
                                            obs_ref=REF
                                            obs_alt=ALT
                                            obs_GT=GT
                                            obs_DP=DP
                                            # if the genotype is homozygous ref set the alt as the ref base
                                            if obs_GT == "0/0":
                                                obs_alt = obs_ref
                                            # add all this to dict
                                            dict["variant"][gene]["samples"][dna_num]["obs_var"]={"REF":obs_ref,"ALT":obs_alt,"GT":obs_GT,"DP":obs_DP}
                        # if the variant was not found in the VCF add empty values to the dictionary
                        if not found:
                            dict["variant"][gene]["samples"][dna_num]["obs_var"]={"REF":"","ALT":"","GT":"","DP":""}
                                        
                        # Now need to extract expected alt allele and genotype
                        # set flag to denote SNP genotpye identified
                        found=False
                        # open expected vcf
                        with open("/home/mokaguys/Desktop/snp_genotyping_NP/expected_vcfs/vcf_decomposed/" + exp_file,'r') as exp_vcf:
                            for line in exp_vcf.readlines():
                                if not line.startswith("#"):
                                    # capture the columns
                                    CHROM,POS,ID,REF,ALT,QUAL,FILTER,INFO,FORMAT,sample = line.rstrip().split("\t")
                                    # if chr and pos match
                                    if CHROM==dict["variant"][gene]["chr"] and POS==dict["variant"][gene]["pos"]:
                                        DP="?"
                                        GT="?"
                                        # loop through format to define what order the values are in 
                                        for count,i in enumerate(FORMAT.split(":")):
                                            # extract the GT and DP from sample column
                                            if i == "GT":
                                                GT=sample.split(":")[count]
                                            if i == "DP":
                                                DP=sample.split(":")[count]
                                        # as we have decomposed the VCF we want to ignore any genotypies with a full stop as this isn't the ALT allele predicted to be the correct genotype
                                        if "." in GT:
                                            pass
                                        else:
                                            # capture required fields
                                            found=True
                                            exp_ref=REF
                                            exp_alt=ALT
                                            exp_GT=GT
                                            exp_DP=DP
                                            # if the genotype is homozygous ref set the alt as the ref base
                                            if exp_GT == "0/0":
                                                exp_alt = exp_ref
                                            dict["variant"][gene]["samples"][dna_num]["exp_var"]={"REF":exp_ref,"ALT":exp_alt,"GT":exp_GT,"DP":exp_DP}
                        if not found:
                            dict["variant"][gene]["samples"][dna_num]["exp_var"]={"REF":"","ALT":"","GT":"","DP":""}
        # repeat for na12878 samples 
        else:
            # add to list of samples to help create report
            samples2.append(dna_num)
            # loop through expected vcfs - looking for file with dna number in
            for exp_file in os.listdir("/home/mokaguys/Desktop/snp_genotyping_NP/expected_vcfs/vcf_decomposed"):
                if exp_file.endswith(".vcf") and dna_num in exp_file:
                    # create entry to dictionary 2
                    dict2["samples"][dna_num]={"obs_file":obs_file,"exp_file":exp_file,"observed_var":{},"expected_var":{}}
                    # loop through each SNP
                    for gene in dict2["variant"]:
                        # create dict entry for each sample in each SNP
                        dict2["variant"][gene]["samples"][dna_num]={"obs_var":{},"exp_var":{}}
                        #open the obsereved vcf
                        found=False
                        with open("/home/mokaguys/Desktop/snp_genotyping_NP/observed_kmer13/vcfs_decomposed/" + obs_file,'r') as obs_vcf:
                            for line in obs_vcf.readlines():
                                if not line.startswith("#"):
                                    # split the line
                                    CHROM,POS,ID,REF,ALT,QUAL,FILTER,INFO,FORMAT,sample = line.rstrip().split("\t")
                                    # if the chr and pos match
                                    if CHROM==dict2["variant"][gene]["chr"] and POS==dict2["variant"][gene]["pos"]:
                                        DP="?"
                                        GT="?"
                                        # extract the order of items in format and sample cols + capture GT and DP
                                        for count,i in enumerate(FORMAT.split(":")):
                                            if i == "GT":
                                                GT=sample.split(":")[count]
                                            if i == "DP":
                                                DP=sample.split(":")[count]
                                        # as we have decomposed the VCF we want to ignore any genotypies with a full stop as this isn't the ALT allele predicted to be the correct genotype
                                        if "." in GT:
                                            pass
                                        else:
                                            # capture required fields
                                            found=True
                                            exp_ref=REF
                                            exp_alt=ALT
                                            exp_GT=GT
                                            exp_DP=DP
                                            # if the genotype is homozygous ref set the alt as the ref base
                                            if exp_GT == "0/0":
                                                exp_alt = exp_ref
                                            dict2["variant"][gene]["samples"][dna_num]["obs_var"]={"REF":obs_ref,"ALT":obs_alt,"GT":obs_GT,"DP":obs_DP}
                        if not found:
                            dict2["variant"][gene]["samples"][dna_num]["obs_var"]={"REF":"","ALT":"","GT":"","DP":""}
                                        
                        # repeat for expected VCF
                        found=False
                        with open("/home/mokaguys/Desktop/snp_genotyping_NP/expected_vcfs/vcf_decomposed/" + exp_file,'r') as exp_vcf:
                            for line in exp_vcf.readlines():
                                if not line.startswith("#"):
                                    # split the line
                                    CHROM,POS,ID,REF,ALT,QUAL,FILTER,INFO,FORMAT,sample = line.rstrip().split("\t")
                                    if CHROM==dict2["variant"][gene]["chr"] and POS==dict2["variant"][gene]["pos"]:
                                        # extract the order of items in format and sample cols + capture GT and DP
                                        DP="?"
                                        GT="?"
                                        for count,i in enumerate(FORMAT.split(":")):
                                            if i == "GT":
                                                GT=sample.split(":")[count]
                                            if i == "DP":
                                                DP=sample.split(":")[count]
                                        # as we have decomposed the VCF we want to ignore any genotypies with a full stop as this isn't the ALT allele predicted to be the correct genotype
                                        if "." in GT:
                                            pass
                                        else:
                                            found=True
                                            exp_ref=REF
                                            exp_alt=ALT
                                            exp_GT=GT
                                            exp_DP=DP
                                            # if the genotype is homozygous ref set the alt as the ref base
                                            if exp_GT == "0/0":
                                                exp_alt = exp_ref
                                            
                                            dict2["variant"][gene]["samples"][dna_num]["exp_var"]={"REF":exp_ref,"ALT":exp_alt,"GT":exp_GT,"DP":exp_DP}
                            if not found:
                                #print gene,dna_num,exp_vcf.readlines()
                                dict2["variant"][gene]["samples"][dna_num]["exp_var"]={"REF":"","ALT":"","GT":"","DP":""}

## Create output files for coverage and genotypes for GIAB and truth sets.
# create header line for non GIAB samples
header=["chr","pos","ref","gene","RS"]
for sample in samples:
    header.append(sample+"_expected_GT")
    header.append(sample+"_observed_GT")
    header.append(sample+"_match")

# create genotyping file
with open(output_file1,'w') as non_giab_results:
    # write the header
    non_giab_results.write("\t".join(header)+"\n")
    # one line per gene and one column for observed and expected and if it matches per sample
    for gene in dict["variant"]:
        # create a list of elements that will become the line with the SNP descriptors
        line=[dict["variant"][gene]["chr"],dict["variant"][gene]["pos"],dict["variant"][gene]["ref"],gene,dict["variant"][gene]["RS"]]
        # append result of samples to this list
        for sample in samples:
            if dict["variant"][gene]["samples"][sample]["exp_var"]["GT"] =="0/0":
                line.append(dict["variant"][gene]["samples"][sample]["exp_var"]["REF"] + "/" + dict["variant"][gene]["samples"][sample]["exp_var"]["REF"])
            elif dict["variant"][gene]["samples"][sample]["exp_var"]["GT"] =="0/1":
                line.append(dict["variant"][gene]["samples"][sample]["exp_var"]["REF"] + "/" + dict["variant"][gene]["samples"][sample]["exp_var"]["ALT"])
            elif dict["variant"][gene]["samples"][sample]["exp_var"]["GT"] =="1/1":
                line.append(dict["variant"][gene]["samples"][sample]["exp_var"]["ALT"] + "/" + dict["variant"][gene]["samples"][sample]["exp_var"]["ALT"])
            else:
                line.append("unable to determine genotype")
            
            if dict["variant"][gene]["samples"][sample]["obs_var"]["GT"] =="0/0":
                line.append(dict["variant"][gene]["samples"][sample]["obs_var"]["REF"] + "/" + dict["variant"][gene]["samples"][sample]["obs_var"]["REF"])
            elif dict["variant"][gene]["samples"][sample]["obs_var"]["GT"] =="0/1":
                line.append(dict["variant"][gene]["samples"][sample]["obs_var"]["REF"] + "/" + dict["variant"][gene]["samples"][sample]["obs_var"]["ALT"])
            elif dict["variant"][gene]["samples"][sample]["obs_var"]["GT"] =="1/1":
                line.append(dict["variant"][gene]["samples"][sample]["obs_var"]["ALT"] + "/" + dict["variant"][gene]["samples"][sample]["obs_var"]["ALT"])
            else:
                line.append("unable to determine genotype")
            # add the expected ALT allele and the genotype
            #line.append(dict["variant"][gene]["samples"][sample]["exp_var"]["REF"]+","+dict["variant"][gene]["samples"][sample]["exp_var"]["ALT"]+","+dict["variant"][gene]["samples"][sample]["exp_var"]["GT"])
            # add the observed ALT allele and the genotype
            #line.append(dict["variant"][gene]["samples"][sample]["obs_var"]["ALT"]+","+dict["variant"][gene]["samples"][sample]["obs_var"]["GT"])
            # assess if the ALT allele and the genotype matches and record match or not
            if dict["variant"][gene]["samples"][sample]["obs_var"]["ALT"] == dict["variant"][gene]["samples"][sample]["exp_var"]["ALT"] and dict["variant"][gene]["samples"][sample]["exp_var"]["GT"] == dict["variant"][gene]["samples"][sample]["obs_var"]["GT"]:
                line.append("match")
            else:
                line.append("UhOh")

        # write list to file
        non_giab_results.write("\t".join(line)+"\n")
        
# create non - GIAB coverage file
with open(output_file3,'w') as non_giab_coverage:
    # create new header row
    header=["chr","pos","ref","gene","RS"]
    # append one column for each observed sample with DP
    for sample in samples:
        header.append(sample+"_observed_DP")
    non_giab_coverage.write("\t".join(header)+"\n")
    for gene in dict["variant"]:
        line=[dict["variant"][gene]["chr"],dict["variant"][gene]["pos"],dict["variant"][gene]["ref"],gene,dict["variant"][gene]["RS"]]
        for sample in samples:
            line.append(dict["variant"][gene]["samples"][sample]["obs_var"]["DP"])
        non_giab_coverage.write("\t".join(line)+"\n")

# create genotype results for GIAB samples -one row per SNP, 3 cols per sample, expected ALT+GT, observed ALT+GT and if these match
header=["chr","pos","ref","gene","RS"]
for sample in samples2:
    header.append(sample+"_expected_GT")
    header.append(sample+"_observed_GT")
    header.append(sample+"_match")

with open(output_file2,'w') as giab_results:
    giab_results.write("\t".join(header)+"\n")
    for gene in dict2["variant"]:
        # the PDP1 gene isn't ijn the truth set VCF so skip
        if gene != "PDP1":
            # create list for this line
            line=[dict2["variant"][gene]["chr"],dict2["variant"][gene]["pos"],dict2["variant"][gene]["ref"],gene,dict2["variant"][gene]["RS"]]
            for sample in samples2:
                # add 3 cols for each sample ( expected, observed genotype and if these match)
                if dict2["variant"][gene]["samples"][sample]["exp_var"]["GT"] =="0/0":
                    line.append(dict2["variant"][gene]["samples"][sample]["exp_var"]["REF"] + "/" + dict2["variant"][gene]["samples"][sample]["exp_var"]["REF"])
                elif dict2["variant"][gene]["samples"][sample]["exp_var"]["GT"] =="0/1":
                    line.append(dict2["variant"][gene]["samples"][sample]["exp_var"]["REF"] + "/" + dict2["variant"][gene]["samples"][sample]["exp_var"]["ALT"])
                elif dict2["variant"][gene]["samples"][sample]["exp_var"]["GT"] =="1/1":
                    line.append(dict2["variant"][gene]["samples"][sample]["exp_var"]["ALT"] + "/" + dict2["variant"][gene]["samples"][sample]["exp_var"]["ALT"])
                else:
                    line.append("unable to determine genotype")
                
                if dict2["variant"][gene]["samples"][sample]["obs_var"]["GT"] =="0/0":
                    line.append(dict2["variant"][gene]["samples"][sample]["obs_var"]["REF"] + "/" + dict2["variant"][gene]["samples"][sample]["obs_var"]["REF"])
                elif dict2["variant"][gene]["samples"][sample]["obs_var"]["GT"] =="0/1":
                    line.append(dict2["variant"][gene]["samples"][sample]["obs_var"]["REF"] + "/" + dict2["variant"][gene]["samples"][sample]["obs_var"]["ALT"])
                elif dict2["variant"][gene]["samples"][sample]["obs_var"]["GT"] =="1/1":
                    line.append(dict2["variant"][gene]["samples"][sample]["obs_var"]["ALT"] + "/" + dict2["variant"][gene]["samples"][sample]["obs_var"]["ALT"])
                else:
                    line.append("unable to determine genotype")
                # assess if the ALT allele and the genotype matches and record match or not
                if dict2["variant"][gene]["samples"][sample]["obs_var"]["ALT"] == dict2["variant"][gene]["samples"][sample]["exp_var"]["ALT"] and dict2["variant"][gene]["samples"][sample]["exp_var"]["GT"] == dict2["variant"][gene]["samples"][sample]["obs_var"]["GT"]:
                    line.append("match")
                else:
                    line.append("UhOh")
            giab_results.write("\t".join(line)+"\n")

# create GIAB coverage             
with open(output_file4,'w') as giab_coverage:
    # chearet header line
    header=["chr","pos","ref","alt","gene","RS"]
    for sample in samples2:
        header.append(sample+"_observed_DP")
    giab_coverage.write("\t".join(header)+"\n")
    # for each SNP
    for gene in dict2["variant"]:
        # create a list of DP for each sample
        line=[dict2["variant"][gene]["chr"],dict2["variant"][gene]["pos"],dict2["variant"][gene]["ref"],gene,dict["variant"][gene]["RS"]]
        for sample in samples2:
            line.append(dict2["variant"][gene]["samples"][sample]["obs_var"]["DP"])
        giab_coverage.write("\t".join(line)+"\n")