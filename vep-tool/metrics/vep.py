'''
Metrics table class for VEP 
'''
from metrics.mixins import CustomToolMd5TypeMixin
from metrics.base_metrics import CWLMetricsMd5Tool

from cdis_pipe_utils import postgres
from sqlalchemy import Column, Integer, String

class VEPMetricsTable(CustomToolMd5TypeMixin, postgres.Base):
    hostname       = Column(String)
    total_variants = Column(Integer)
    novel_variants = Column(Integer)

    __tablename__  = 'vep_metrics'

class VEPMetricsTool(CWLMetricsMd5Tool):
    def __init__(self, time_file, normal_id, tumor_id, input_uuid, output_uuid, case_id, engine, input_file, stats_file, hostname):
        super(VEPMetricsTool,self).__init__(time_file, normal_id, tumor_id, input_uuid, output_uuid, 
                                            case_id, engine, input_file)
        self.tool       = 'vep'
        self.files      = [normal_id, tumor_id]
        self.stats_file = stats_file
        self.hostname   = hostname 

    def add_metrics(self):
        time_metrics = self.get_time_metrics()
        md5          = self.get_gz_md5()
        nvar, nnovel = self.get_variant_counts()
        metrics      = VEPMetricsTable(case_id           = self.case_id,
                                       vcf_id            = self.output_uuid,
                                       src_vcf_id        = self.input_uuid,
                                       tool              = self.tool,
                                       files             = self.files,
                                       systime           = time_metrics['system_time'],
                                       usertime          = time_metrics['user_time'],
                                       elapsed           = time_metrics['wall_clock'],
                                       cpu               = time_metrics['percent_of_cpu'],
                                       max_resident_time = time_metrics['maximum_resident_set_size'],
                                       md5               = md5,
                                       hostname          = self.hostname,
                                       total_variants    = nvar,
                                       novel_variants    = nnovel)
        postgres.create_table(self.engine, metrics)
        postgres.add_metrics(self.engine, metrics)

    def get_variant_counts(self):
        ''' Parse the variant counts and novel counts from vep stats file '''
        n_variants = 0
        n_novel    = 0
        section    = None
        data       = []
        with open(self.stats_file, 'rU') as fh:
            for line in fh: 
                if not line.rstrip(): continue
                elif line.startswith('[') and not section:
                    section = line.rstrip()
                elif line.startswith('[') and section:
                    if section == '[General statistics]':
                        for row in data:
                            if row[0] == 'Variants remaining after filtering': 
                                try: n_variants = int(row[1])
                                except: print('Unable to parse n_variants: {0}'.format(row[1])) 
                            elif row[0] == 'Novel / existing variants':
                                try: n_novel = int(row[1].split(' ')[0])
                                except: print('Unable to parse n_novel: {0}'.format(row[1])) 
                    section = line.rstrip()
                    data = []
                else:
                    data.append(line.rstrip().split('\t'))

        return n_variants, n_novel
