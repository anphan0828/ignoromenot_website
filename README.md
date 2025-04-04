# Potential Publications for Unannotated Human Proteins

## Overview

This file (`potential_pubs.tsv`) contains potential publications about human proteins that currently lack GO (Gene Ontology) annotations in the UniProt SwissProt database (version 2025-02-05). It provides a list of scientific literature that mentions these unannotated proteins, which could be valuable for annotating their functions and properties.

## File Description

The file is a tab-separated values (TSV) file containing 874 publications associated with 235 human proteins that currently have no GO annotations. Each row represents a publication mentioning a specific protein, with various metrics about the publication and how relevant it might be for annotation purposes.

Data were collected from SwissProt dat file (version 2025-02-05), PubTator API, and NCBI Gene API. Publications listed in the file are not included in the "References" field of SwissProt dat file for that protein, so they are assumed as not reviewed by UniProt biocurators.

## Column Descriptions

| Column Name | Description |
|-------------|-------------|
| `uniprot_id` | UniProt accession number for the protein |
| `ncbi_gene` | NCBI Gene ID for the protein (from SwissProt dat file)|
| `gene_name` | Official gene symbol, sometimes with evidence codes |
| `gene_description` | Functional description of the gene/protein (from NCBI Gene Summary)|
| `gene_aliases` | Alternative names/symbols for the gene, comma-separated (from NCBI Gene Summary). These aliases are used in PubTator, so false positives might stem from gene aliases|
| `pmid` | PubMed ID of the publication |
| `year` | Publication year |
| `in_title` | Boolean (True/False) indicating if gene/protein is mentioned in the title |
| `fraction_mentions` | Fraction of gene mentions in the paper that refer to this gene (0-1), calculated as the number of times mentioning the query gene/protein divided by the number of times mentioning any gene/protein as recognized by PubTator |
| `total_genes` | Total number of genes mentioned in the publication |
| `journal` | Name of the journal |
| `full_text` | Boolean (True/False) indicating if the full text was analyzed by PubTator (vs. just abstract) |
| `title` | Title of the publication |

## Usage

Publications with high `fraction_mentions` values, low `total_genes`, and `in_title = True` are generally more focused on the protein of interest and may be the best candidates for curation.

This dataset can be used to:
- Identify relevant literature for previously unannotated proteins
- Prioritize papers for manual curation and GO annotation
- Find publications with strong focus on specific proteins (high fraction_mentions)

