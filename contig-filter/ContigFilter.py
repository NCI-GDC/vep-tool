'''
Removes unwanted contigs from VCF and adds in GDC-specific
headers to VCF file.
'''
import argparse
import os
import gzip
import logging
import datetime
import time
import sys

__version__='0.1'
__author__='Kyle Hernandez'
__email__='kmhernan@uchicago.edu'

def load_contigs_from_fai(fai_file, assembly):
    '''
    Loads the data from the FAI file. A set of contigs to keep and a list of
    VCF formatted contig names.
    '''
    contigs = []
    fmt = []
    for line in open(fai_file, 'r'):
        chrm, length = line.rstrip().split('\t')[:2]
        contigs.append(chrm)
        fmt.append('##contig=<ID={0},length={1},assembly={2}>'.format(chrm, length, assembly)) 
    return fmt, contigs

def load_contigs(args):
    '''
    Loads the contig data.
    '''
    # Contigs
    fai_file = args.fai if args.fai else \
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'GRCh38.d1.vd1.contig_filtered.fai')
    contig_format, contig_list = load_contigs_from_fai(fai_file, args.assembly)
    return contig_format, set(contig_list)

def write_custom_header(o, args):
    '''
    Writes the fileDate, reference, center, indivdual, and sample VCF header columns.
    '''
    fmt_str = '''##fileDate={fdate}
##reference={ref}
##center="NCI Genomic Data Commons (GDC)"
##source={vcf_source}
##INDIVIDUAL=<NAME={patient_barcode},ID={case_id}>
##SAMPLE=<ID=NORMAL,NAME={normal_barcode},ALIQUOT_ID={normal_aliquot_uuid},BAM_ID={normal_bam_uuid}>
##SAMPLE=<ID=TUMOR,NAME={tumor_barcode},ALIQUOT_ID={tumor_aliquot_uuid},BAM_ID={tumor_bam_uuid}>
'''.format(fdate=datetime.date.today(), ref=args.reference, vcf_source=args.vcf_source,
           patient_barcode=args.patient_barcode, case_id=args.case_id, 
           normal_barcode=args.normal_barcode, normal_aliquot_uuid=args.normal_aliquot_uuid, normal_bam_uuid=args.normal_bam_uuid,
           tumor_barcode=args.tumor_barcode, tumor_aliquot_uuid=args.tumor_aliquot_uuid, tumor_bam_uuid=args.tumor_bam_uuid)
    o.write(fmt_str)

if __name__ == '__main__':
    start = time.time()

    # Setup logger
    logger = logging.getLogger('ContigFilter')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Print header
    logger.info('-'*75)
    logger.info('ContigFilter v{0}'.format(__version__))
    logger.info('Author: {0}'.format(__author__))
    logger.info('Program Args: ContigFilter.py {0}'.format(" ".join(sys.argv[1::])))
    logger.info('Date/time: {0}'.format(datetime.datetime.now()))
    logger.info('-'*75)
    logger.info('-'*75)

    # Setup parser
    parser = argparse.ArgumentParser('Filter extra contigs and format VCF header for GDC specifications')

    parser.add_argument('--input_vcf', required=True, help='Input VCF file')
    parser.add_argument('--output_vcf', required=True, help='Output VCF file')
    parser.add_argument('--patient_barcode', required=True, help='Patient barcode')
    parser.add_argument('--case_id', required=True, help='Case ID')
    parser.add_argument('--tumor_barcode', required=True, help='Tumor barcode')
    parser.add_argument('--tumor_aliquot_uuid', required=True, help='Tumor aliquot uuid')
    parser.add_argument('--tumor_bam_uuid', required=True, help='Tumor BAM uuid')
    parser.add_argument('--normal_barcode', required=True, help='Normal barcode')
    parser.add_argument('--normal_aliquot_uuid', required=True, help='Normal aliquot uuid')
    parser.add_argument('--normal_bam_uuid', required=True, help='Normal BAM uuid')
    parser.add_argument('--vcf_source', required=True, choices=['MuTect2', 'VarScan2', 'MuSE', 'SomaticSniper'], 
        help='sets the ##source=<choice>')
    parser.add_argument('--fai', required=False, 
        help='The FAI file containing the contigs you want to keep. Default the fai file in the repository.') 
    parser.add_argument('--assembly', required=False, default='GRCh38.d1.vd1', 
        help='The assembly name to use in VCF header. [GRCh38.d1.vd1]') 
    parser.add_argument('--reference', required=False, default='GRCh38.d1.vd1.fa', 
        help='The reference fasta name to use in VCF header. [GRCh38.d1.vd1.fa]') 
    args = parser.parse_args()

    # Custom header 
    contig_str, contigs = load_contigs(args)

    # Reader 
    reader = gzip.open(args.input_vcf, 'rb') if args.input_vcf.endswith('.gz') else open(args.input_vcf, 'r')
   
    # Parse VCF 
    total   = 0
    kept    = 0
    with open(args.output_vcf, 'wb') as o:
        for line in reader:
            # Header
            if line.startswith('#'): 
                if line.startswith('##fileformat'):
                    o.write(line)
                    write_custom_header(o, args)
                elif line.startswith('##FILTER') or \
                   line.startswith('##FORMAT') or \
                   line.startswith('##INFO'):
                    o.write(line)
                # Write new data
                elif line.startswith('#CHROM'):
                    # Write contigs
                    o.write('\n'.join(contig_str) + '\n') 
                    # Write header
                    o.write(line)
            # Filter
            else:
                # Count
                total += 1
                # Get chromosome
                chrm = line.rstrip().split('\t')[0]
                # Only write if in contig header
                if chrm in contigs: 
                    kept += 1
                    o.write(line) 
    reader.close()

    # Done
    logger.info("Variants Analyzed={0}".format(total))
    logger.info("Variants Output={0}".format(kept))
    logger.info("Finished, took {0} seconds.".format(time.time() - start)) 
