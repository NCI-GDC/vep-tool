GDC VEP Tool
---

Contains VEP plugins, utility scripts, and a dockerfile for running the VEP pipeline.

## VEP Plugins

We have only tested these plugins on the software dependencies listed in the
Dockerfile:

* BioPerl 1.6.924
* VEP v84

All of these plugins require tabix to be installed and in your `PATH` which is often
installed automatically (via htslib) during the VEP installation process.

### Entrez

The `GDC_entrez.pm` plugin uses a pre-populated JSON file containing mappings from GENCODE to
Entrez identifiers. The JSON file can be created using the `vep-plugins/utils/make_ensembl_entrez_json.py`
script.

VEP Usage: `--plugin GDC_entrez,<entrez_ensembl.json>`

### Evidence

The `GDC_evidence.pm` plugin uses the tabix-indexed VEP evidence VCF to add in the evidence values for dbSNP
annotations.

VEP Usage: `--plugin GDC_evidence,<variation.vcf.gz>`
