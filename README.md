VEP Tool
---

Contains VEP plugins and utility scripts for running the VEP pipeline.

## VEP Plugins

### Entrez

The `GDC_entrez.pm` plugin uses a pre-populated JSON file containing mappings from GENCODE to
Entrez identifiers. The JSON file can be created using the `vep-plugins/utils/make_ensembl_entrez_json.py`
script.

Usage: `--plugin GDC_entrez,<entrez_ensembl.json>`

### Evidence

The `GDC_evidence.pm` plugin uses the tabix-indexed VEP evidence VCF to add in the evidence values for dbSNP
annotations.

Usage: `--plugin GDC_evidence,<variation.vcf.gz>`
