#!/usr/bin/env python
'''
Main entry point for adding the variant-annotation pipeline tools. 
'''
import argparse
import tools.contigfilter
import tools.vcfreheader

def pg_metrics(args):
    '''Main wrapper for adding metrics to PG db'''
    from cdis_pipe_utils import postgres
    from metrics.vep import VEPMetricsTool
    # Only if you want to add these tables
    #from metrics.contigfilter import ContigFilterMetricsTool
    #from metrics.vcfreheader import VcfReheaderMetricsTool

    # postgres
    s = open(args.postgres_config, 'r').read()
    postgres_config = eval(s)

    DATABASE = {
        'drivername': 'postgres',
        'host' : args.host,
        'port' : '5432',
        'username': postgres_config['username'],
        'password' : postgres_config['password'],
        'database' : args.database
    }

    engine = postgres.db_connect(DATABASE)

    ## Load tool
    tool = None
    if args.tool == 'vep':
        assert args.input_file, 'VEP Requires --input_file'
        assert args.stats_file, 'VEP Requires --stats_file'
        tool = VEPMetricsTool(args.time_file, args.normal_id, args.tumor_id, 
                              args.input_uuid, args.output_uuid, args.case_id,
                              engine, args.input_file, args.stats_file)

    # Only if you want to add these tables
    #elif args.tool == 'contigfilter':
    #    tool = ContigFilterMetricsTool(args.time_file, args.normal_id, args.tumor_id, 
    #                          args.input_uuid, args.output_uuid, args.case_id,
    #                          engine)

    #elif args.tool == 'vcfreheader':
    #    tool = VcfReheaderMetricsTool(args.time_file, args.normal_id, args.tumor_id, 
    #                          args.input_uuid, args.output_uuid, args.case_id,
    #                          engine)

    tool.add_metrics()

def main():
    ## Set up parser
    parser = argparse.ArgumentParser(description='Variant-Annotation-Pipeline Tools')

    ## Sub parser
    sp     = parser.add_subparsers(help='Choose the tool you want to run', dest='choice')

    ## Postgres
    p_pg   = sp.add_parser('postgres', help='Adding run metrics to GDC postgres for VEP workflow')
    # For now, only recording vep stats
    #p_pg.add_argument('--tool', required=True, choices=['vep', 'contigfilter', 'vcfreheader'], help='Which CWL tool used')
    p_pg.add_argument('--tool', required=True, choices=['vep'], help='Which CWL tool used')
    p_pg.add_argument('--time_file', required=True, help='path to the output of time for this tool')
    p_pg.add_argument('--normal_id', default="unknown", help='normal sample unique identifier')
    p_pg.add_argument('--tumor_id', default="unknown", help='tumor sample unique identifier')
    p_pg.add_argument('--input_uuid', default="unknown", help='input file UUID')
    p_pg.add_argument('--output_uuid', default="unknown", help='output file UUID')
    p_pg.add_argument('--case_id', default="unknown", help='case ID')
    p_pg.add_argument('--input_file', help='path to file for md5. required for vep')
    p_pg.add_argument('--stats_file', help='path to file for vep stats. required for vep')

    # database parameters
    p_pg_db = p_pg.add_argument_group("Database parameters")
    p_pg_db.add_argument("--host", default='172.17.65.79', help='hostname for db')
    p_pg_db.add_argument("--database", default='prod_bioinfo', help='name of the database')
    p_pg_db.add_argument("--postgres_config", default=None, help="postgres config file", required=True)

    ## Contig Filter
    p_cf    = sp.add_parser('contigfilter', help='Filter extra contigs')
    p_cf.add_argument('--input_vcf', required=True, help='Input VCF file')
    p_cf.add_argument('--output_vcf', required=True, help='Output VCF file. Automatically gzip if ends with ".gz"')
    p_cf.add_argument('--fai', required=False,
        help='The FAI file containing the contigs you want to keep. Default the fai file in the repository.')
    p_cf.add_argument('--assembly', required=False, default='GRCh38.d1.vd1',
        help='The assembly name to use in VCF header. [GRCh38.d1.vd1]')
    p_cf.add_argument('--reference', required=False, default='GRCh38.d1.vd1.fa',
        help='The reference fasta name to use in VCF header. [GRCh38.d1.vd1.fa]')

    ## VCF Reheader 
    p_cf    = sp.add_parser('vcfreheader', help='Format VCF header to GDC specs')
    p_cf.add_argument('--input_vcf', required=True, help='Input VCF file')
    p_cf.add_argument('--output_vcf', required=True, help='Output VCF file. Automatically gzip if ends with ".gz"')
    p_cf.add_argument('--patient_barcode', required=True, help='Patient barcode')
    p_cf.add_argument('--case_id', required=True, help='Case ID')
    p_cf.add_argument('--tumor_barcode', required=True, help='Tumor barcode')
    p_cf.add_argument('--tumor_aliquot_uuid', required=True, help='Tumor aliquot uuid')
    p_cf.add_argument('--tumor_bam_uuid', required=True, help='Tumor BAM uuid')
    p_cf.add_argument('--normal_barcode', required=True, help='Normal barcode')
    p_cf.add_argument('--normal_aliquot_uuid', required=True, help='Normal aliquot uuid')
    p_cf.add_argument('--normal_bam_uuid', required=True, help='Normal BAM uuid')
    p_cf.add_argument('--caller_workflow_id', required=True, help='sets "ID" in gdcWorkflow header') 
    p_cf.add_argument('--caller_workflow_name', required=True, help='sets "Name" in gdcWorkflow header') 
    p_cf.add_argument('--caller_workflow_description', help='sets "Description" in gdcWorkflow header')
    p_cf.add_argument('--caller_workflow_version', default='1.0', help='sets "Version" in gdcWorkflow header')
    p_cf.add_argument('--annotation_workflow_id', required=True, help='sets "ID" in gdcWorkflow header') 
    p_cf.add_argument('--annotation_workflow_name', required=True, help='sets "Name" in gdcWorkflow header') 
    p_cf.add_argument('--annotation_workflow_description', help='sets "Description" in gdcWorkflow header')
    p_cf.add_argument('--annotation_workflow_version', default='1.0', help='sets "Version" in gdcWorkflow header')

    ## Parse args
    args = parser.parse_args()

    ## Run tools
    if args.choice == 'postgres': pg_metrics(args)
    elif args.choice == 'contigfilter': tools.contigfilter.run(args)
    elif args.choice == 'vcfreheader': tools.vcfreheader.run(args)

if __name__ == '__main__':
    main() 
