#!/usr/bin/env python
'''
Main entry point for adding the runtime metrics from the annotation pipeline
to the postgres db.
'''
import argparse
import logging

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY

from cdis_pipe_utils import time_util
from cdis_pipe_utils import postgres

class CustomToolTypeMixin(object):
    ''' Gather timing metrics with input/output uuids '''
    id = Column(Integer, primary_key=True)
    case_id = Column(String)
    vcf_id = Column(String)
    src_vcf_id = Column(String)
    tool = Column(String)
    files = Column(ARRAY(String))
    systime = Column(Float)
    usertime = Column(Float)
    elapsed = Column(String)
    cpu = Column(Float)
    max_resident_time = Column(Float)

    def __repr__(self):
        return "<CustomToolTypeMixin(systime='%d', usertime='%d', elapsed='%s', cpu='%d', max_resident_time='%d'>" %(self.systime,
                self.usertime, self.elapsed, self.cpu, self.max_resident_time)


class CWLMetricsTool(object):
    def __init__(self, time_file, normal_id, tumor_id, input_uuid, output_uuid, case_id, engine):
        self.time_file   = time_file
        self.normal_id   = normal_id
        self.tumor_id    = tumor_id
        self.input_uuid  = input_uuid
        self.output_uuid = output_uuid
        self.case_id     = case_id 
        self.engine      = engine

    def get_time_metrics(self):
        time_str = None
        with open(self.time_file, 'rb') as fh:
            time_str = fh.read()
        return time_util.parse_time(time_str)
 
    def add_metrics(self):
        pass 

## Contig Filter 
class ContigFilterMetricsTable(CustomToolTypeMixin, postgres.Base):

    __tablename__ = 'contig_filter_metrics'

class ContigFilterMetricsTool(CWLMetricsTool):
    def __init__(self, time_file, normal_id, tumor_id, input_uuid, output_uuid, case_id, engine):
        super(ContigFilterMetricsTool,self).__init__(time_file, normal_id, tumor_id, input_uuid, output_uuid, case_id, engine)
        self.tool  = 'contig_filter'
        self.files = [normal_id, tumor_id]

    def add_metrics(self):
        time_metrics = self.get_time_metrics()
        metrics      = ContigFilterMetricsTable(case_id  = self.case_id,
                                       vcf_id            = self.output_uuid,
                                       src_vcf_id        = self.input_uuid,
                                       tool              = self.tool,
                                       files             = self.files,
                                       systime           = time_metrics['system_time'],
                                       usertime          = time_metrics['user_time'],
                                       elapsed           = time_metrics['wall_clock'],
                                       cpu               = time_metrics['percent_of_cpu'],
                                       max_resident_time = time_metrics['maximum_resident_set_size']) 
        postgres.create_table(self.engine, metrics)
        postgres.add_metrics(self.engine, metrics)

## VEP
class VEPMetricsTable(CustomToolTypeMixin, postgres.Base):

    __tablename__ = 'variant_effect_predictor_metrics'

class VEPMetricsTool(CWLMetricsTool):
    def __init__(self, time_file, normal_id, tumor_id, input_uuid, output_uuid, case_id, engine):
        super(VEPMetricsTool,self).__init__(time_file, normal_id, tumor_id, input_uuid, output_uuid, case_id, engine)
        self.tool  = 'variant_effect_predictor'
        self.files = [normal_id, tumor_id]

    def add_metrics(self):
        time_metrics = self.get_time_metrics()
        metrics      = VEPMetricsTable(case_id           = self.case_id,
                                       vcf_id            = self.output_uuid,
                                       src_vcf_id        = self.input_uuid,
                                       tool              = self.tool,
                                       files             = self.files,
                                       systime           = time_metrics['system_time'],
                                       usertime          = time_metrics['user_time'],
                                       elapsed           = time_metrics['wall_clock'],
                                       cpu               = time_metrics['percent_of_cpu'],
                                       max_resident_time = time_metrics['maximum_resident_set_size']) 
        postgres.create_table(self.engine, metrics)
        postgres.add_metrics(self.engine, metrics)
 
def main():
    ## Set up parser
    parser = argparse.ArgumentParser(description='Adding run metrics to GDC postgres for VEP workflow')
    parser.add_argument('--tool', required=True, choices=['vep', 'contigfilter'], help='Which CWL tool used')
    parser.add_argument('--time_file', required=True, help='path to the output of time for this tool')
    parser.add_argument('--normal_id', default="unknown", help='normal sample unique identifier')
    parser.add_argument('--tumor_id', default="unknown", help='tumor sample unique identifier')
    parser.add_argument('--input_uuid', default="unknown", help='input file UUID')
    parser.add_argument('--output_uuid', default="unknown", help='output file UUID')
    parser.add_argument('--case_id', default="unknown", help='case ID')

    # database parameters
    db = parser.add_argument_group("Database parameters")
    db.add_argument("--host", default='172.17.65.79', help='hostname for db')
    db.add_argument("--database", default='prod_bioinfo', help='name of the database')
    db.add_argument("--postgres_config", default=None, help="postgres config file", required=True)

    args = parser.parse_args()

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
        tool = VEPMetricsTool(args.time_file, args.normal_id, args.tumor_id, 
                              args.input_uuid, args.output_uuid, args.case_id,
                              engine)

    elif args.tool == 'contigfilter':
        tool = ContigFilterMetricsTool(args.time_file, args.normal_id, args.tumor_id, 
                              args.input_uuid, args.output_uuid, args.case_id,
                              engine)

    tool.add_metrics()

if __name__ == '__main__':
    main() 
