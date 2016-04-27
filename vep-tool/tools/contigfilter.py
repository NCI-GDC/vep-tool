'''
Removes unwanted contigs from VCF. 
'''
import logging
import utils.log
import gzip
import os

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
        os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'etc/GRCh38.d1.vd1.contig_filtered.fai')
    contig_format, contig_list = load_contigs_from_fai(fai_file, args.assembly)
    return contig_format, set(contig_list)

def run(args):
    '''
    Main entrypoint for contigfilter
    '''
    # Set up logging
    logger = utils.log.setup_logging(logging.INFO, 'contigfilter', None)

    # Print info
    logger.info('Contig Filter')
    
    # Load contigs
    logger.info('Loading contigs...')
    contig_str, contigs = load_contigs(args)

    # Reference line
    refline = '##reference={0}'.format(args.reference)

    # Reader
    reader = gzip.open(args.input_vcf, 'rt') if args.input_vcf.endswith('.gz') else open(args.input_vcf, 'r')

    # Writer
    writer = gzip.open(args.output_vcf, 'wt') if args.output_vcf.endswith('.gz') else open(args.output_vcf, 'w') 
    
    # Parse VCF
    logger.info('Parsing contigs...')
    total = 0
    kept  = 0
    try:
        for line in reader:
            # Header
            if line.startswith('##'):
                if line.startswith('##contig'): continue
                elif line.startswith('##reference'): continue
                else: writer.write(line)
            # CHROM line 
            elif line.startswith('#CHROM'):
                # Write reference line
                writer.write(refline + '\n')
                # write contigs
                writer.write('\n'.join(contig_str) + '\n')
                # write chromline
                writer.write(line)
            # Records
            else:
                # Count
                total += 1
                # Get chromosome
                chrm = line.rstrip().split('\t')[0]
                # Only write if in contig header
                if chrm in contigs:
                    kept += 1
                    writer.write(line) 
    finally:
        reader.close()
        writer.close()

    # Done
    logger.info("Variants Analyzed={0}".format(total))
    logger.info("Variants Output={0}".format(kept))
