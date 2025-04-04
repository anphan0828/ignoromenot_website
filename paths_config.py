from pathlib import Path

# Base paths
DATA_DIR = Path("/home/ahphan/RotationData/Friedberg/ign_exp_0628/protein-annotation-bias/0_data")
OUTPUT_DIR = Path("/home/ahphan/RotationData/Friedberg/ign_exp_0628/protein-annotation-bias/output")

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input files
# GAF_FILE = DATA_DIR / "03Nov24goa_human.gaf"
GAF_FILE = ""
DAT_FILE = DATA_DIR / "ext_data/uniprot_sprot_human.dat"
IDMAPPING_FILE = DATA_DIR / "ext_data/HUMAN_9606_idmapping.dat"

# Output files
ND_PROTEINS_OUTPUT = OUTPUT_DIR / "ND_proteins.tsv"
IGNORED_PROTEINS_OUTPUT = OUTPUT_DIR / "ignored_proteins.tsv"
PUBTATOR_PICKLE = OUTPUT_DIR / "pubtator_pubs.pkl"
OUTPUT_PUBS = OUTPUT_DIR / "potential_pubs.tsv"

# API Configuration
UNIPROT_API_BASE = "https://rest.uniprot.org/uniprotkb/"
API_RATE_LIMIT = 0.3  # seconds between requests

# # Updating path configs
# import os
# from pathlib import Path

# # Get base paths from environment variables or use defaults
# data_dir = os.environ.get("PROTEIN_DATA_DIR")
# output_dir = os.environ.get("PROTEIN_OUTPUT_DIR")

# # Base paths
# DATA_DIR = Path(data_dir) if data_dir else Path("data")
# OUTPUT_DIR = Path(output_dir) if output_dir else Path("output")

# # Ensure directories exist
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# # Input files - use environment variables if provided
# GAF_FILE = Path(os.environ.get("GAF_FILE")) if os.environ.get("GAF_FILE") else DATA_DIR / "goa_human.gaf"
# DAT_FILE = Path(os.environ.get("DAT_FILE")) if os.environ.get("DAT_FILE") else DATA_DIR / "uniprot_sprot_human.dat"
# IDMAPPING_FILE = Path(os.environ.get("IDMAPPING_FILE")) if os.environ.get("IDMAPPING_FILE") else DATA_DIR / "human_idmapping.txt"

# # Output files
# ND_PROTEINS_OUTPUT = OUTPUT_DIR / "ND_proteins_{date}.tsv"
# IGNORED_PROTEINS_OUTPUT = OUTPUT_DIR / "ignored_proteins_{date}.tsv"
# PUBTATOR_PICKLE = OUTPUT_DIR / "pubtator_pubs.pkl"

# # API Configuration
# UNIPROT_API_BASE = "https://rest.uniprot.org/uniprotkb/"
# API_RATE_LIMIT = float(os.environ.get("API_RATE_LIMIT", "0.3"))  # seconds between requests

# review the python files in 7_website, ignore the R scripts. i want to extract nd proteins (then write out a file), then for each protein in the previous step, fetch the pubtato information on it (then store in a pickle file). FInally, the streamlit app reads the pickle file and display the data. What is the most optimal way to do the preprocessing (knowing that 2 files will be provided as raw input), and deploying the website, if i were to (1) give this code to someone else to run on their local machine and host website locally and (2) host this website on another server (like AWS)