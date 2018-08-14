'''
Metrics table class for contig filter 
'''
from metrics.mixins import CustomToolTypeMixin
from metrics.base_metrics import CWLMetricsTool

from cdis_pipe_utils import postgres

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
