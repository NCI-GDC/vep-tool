'''
Formats the vcf header to the GDC specs
'''
import logging
import utils.log
import gzip
import datetime

def write_custom_header(o, args):
    '''
    Writes the GDC formatted rows
    '''
    fmt_str = '''##fileDate={fdate}
##center="NCI Genomic Data Commons (GDC)"
##gdcWorkflow=<ID={caller_workflow_id},Name={caller_workflow_name},Description="{caller_workflow_description}",Version={caller_workflow_version}>
##gdcWorkflow=<ID={annotation_workflow_id},Name={annotation_workflow_name},Description="{annotation_workflow_description}",Version={annotation_workflow_version}>
##INDIVIDUAL=<NAME={patient_barcode},ID={case_id}>
##SAMPLE=<ID=NORMAL,NAME={normal_barcode},ALIQUOT_ID={normal_aliquot_uuid},BAM_ID={normal_bam_uuid}>
##SAMPLE=<ID=TUMOR,NAME={tumor_barcode},ALIQUOT_ID={tumor_aliquot_uuid},BAM_ID={tumor_bam_uuid}>
'''.format(fdate=datetime.date.today().strftime('%Y%m%d'),
           caller_workflow_id=args.caller_workflow_id.lower().replace(' ', '_'),
           caller_workflow_name=args.caller_workflow_name.lower().replace(' ', '_'),
           caller_workflow_description=args.caller_workflow_description if args.caller_workflow_description else '',
           caller_workflow_version=args.caller_workflow_version,
           annotation_workflow_id=args.annotation_workflow_id.lower().replace(' ', '_'),
           annotation_workflow_name=args.annotation_workflow_name.lower().replace(' ', '_'),
           annotation_workflow_description=args.annotation_workflow_description if args.annotation_workflow_description else '',
           annotation_workflow_version=args.annotation_workflow_version,
           patient_barcode=args.patient_barcode,
           case_id=args.case_id,
           normal_barcode=args.normal_barcode,
           normal_aliquot_uuid=args.normal_aliquot_uuid,
           normal_bam_uuid=args.normal_bam_uuid,
           tumor_barcode=args.tumor_barcode,
           tumor_aliquot_uuid=args.tumor_aliquot_uuid,
           tumor_bam_uuid=args.tumor_bam_uuid)
    o.write(fmt_str)

def run(args):
    ''' Wrapper for formatting VCF header '''
    # Set up logging
    logger = utils.log.setup_logging(logging.INFO, 'vcfreheader', None)

    # Print info
    logger.info('VCF Reheader')

    # Reader
    reader = gzip.open(args.input_vcf, 'rt') if args.input_vcf.endswith('.gz') else open(args.input_vcf, 'r')

    ## Writer
    writer = gzip.open(args.output_vcf, 'wt') if args.output_vcf.endswith('.gz') else open(args.output_vcf, 'w')

    ## Parse VCF
    logger.info('Parsing VCF...')
    header_flag = False
    try:
        for line in reader:
            # Header
            if line.startswith('#'):
                if line.startswith('##fileformat'): 
                    writer.write(line)
                    # Custom header
                    write_custom_header(writer, args)
                elif line.startswith('##reference') or \
                   line.startswith('##contig') or \
                   line.startswith('##INFO') or \
                   line.startswith('##FORMAT') or \
                   line.startswith('##FILTER') or \
                   line.startswith('##ALT') or \
                   line.startswith('##VEP') or \
                   line.startswith('#CHROM'):
                    writer.write(line)
            else:
                writer.write(line)

    finally:
        reader.close()
        writer.close() 

    # Finished
    logger.info('Finished...')
