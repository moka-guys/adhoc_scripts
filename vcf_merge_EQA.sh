# find vcf output files
samplename="NGS644_52"
vcfs=$(find . -name "${samplename}*.vcf")

# modify vcf header and filter column so that bcftools can parse, zip and index
for vcf in $vcfs; do
    sed -i -e 's/Evidence level (Lee and Wagenmakers, 2013)/Evidence level Lee and Wagenmakers 2013/g' $vcf
	sed -i -e 's/cnvCopyRatio,outOfScope/cnvCopyRatio\/outOfScope/g' $vcf
    awk '/^#CHROM/ { printf("##FILTER=<ID=cnvCopyRatio/outOfScope,Description=“CNV with copy ratio within +/- 0.25 of 1.0/ CNV out of scope”>\n");} \
{print;}' $vcf > "${vcf%.vcf}"_reheader.vcf
	bgzip -c "${vcf%.vcf}"_reheader.vcf > "${vcf%.*}".vcf.gz
    tabix -p vcf "${vcf%.*}".vcf.gz
done

