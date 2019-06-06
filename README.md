# jsonl2bio

Usage: python jsonl2bio.py [input file location] [output file name without extension] [user id to BIO tag file]

Script that converts JSONL output from Doccano (https://github.com/chakki-works/doccano) to the BIO format

This script assumes content has been tokenised before uploading to Doccano (i.e., it uses spaces to split sentences into words)

Will produce multiple files if annotations from multiple users are present

Needs a file containing translations of Docanno user IDs to required BIO tag, separated by spaces, 1 tag per line. Example:

7 PER
8 LOC
