#!/usr/bin/env python

"""
Usage: python jsonl2bio.py [input file location] [output file name without extension] [user id to BIO tag file]

Script that converts JSONL output from Doccano (https://github.com/chakki-works/doccano) to the BIO format
This script assumes content has been tokenised before uploading to Doccano (i.e., it uses spaces to split sentences into words)
Will produce multiple files if annotations from multiple users are present
Needs a file containing translations of Docanno user IDs to required BIO tag, separated by spaces, 1 tag per line. Example:

7 PER
8 LOC

"""

import jsonlines
import sys
import re

inputFileLocation = sys.argv[1]
outputFileLocation = sys.argv[2]
tagTableFileLocation = sys.argv[3]

# get annotation ID to BIO tag table
tagTable = {}
tagTableTemp = open(tagTableFileLocation).read().split('\n')
for tag in tagTableTemp:
    if len(tag):
        tag = tag.split(' ')
        tagTable[tag[0]] = tag[1]

# see how many users we've got
jsonAsText = open(inputFileLocation).read()
regex = r"\"user\": (\d+)}"
matches = re.finditer(regex, jsonAsText, re.MULTILINE)
userIds = []
for matchNum, match in enumerate(matches, start=1):
    userId = match.group(1)
    if userId not in userIds:
        userIds.append(userId)

# for each user, go through document and make BIO output
annotationId = 0
for userId in userIds:
    bioOutput = ''
    with jsonlines.open(inputFileLocation) as reader:
        for obj in reader:
            if len(obj['annotations']):
                # first, make list of annotated characters
                annotatedCharacters = {} 
                for ann in obj['annotations']: 
                    if ann['user'] is int(userId): # but only for current user
                        annotationId += 1
                        annRange = range(ann['start_offset'], ann['end_offset']+1) # make range, plus 1 at the end as we want to include the space after the word
                        for number in annRange:
                            annotatedCharacters[number] = {'label' : tagTable[str(ann['label'])], 'id' : annotationId} # add all numbers in range to annchars, so we can check each space against it later
                
                # now we'll check each space in string for a match against annotatedCharacters
                outputParagraph = ""
                i = 0
                previousAnnId = 0
                for char in obj['text']+' ': # add space at end so we can annotate last word
                    if char == " ":
                        if i in annotatedCharacters and (i-1) in annotatedCharacters: # this space is at the end of an annotated word
                            tag = annotatedCharacters[i]['label']
                            if previousAnnId is annotatedCharacters[i]['id']:
                                BorI = "I-"
                            else:
                                BorI = "B-"
                            outputParagraph += ' '+BorI+tag+'\n'
                            previousAnnId = annotatedCharacters[i]['id']
                        else:
                            outputParagraph += ' O\n'
                            
                    else:
                        outputParagraph += char # not a space, just add to output as is
                    i += 1
                outputParagraph += '\n\n'        
            else:
                outputParagraph = obj['text'].replace(' ',' O\n') + ' O\n\n'
            bioOutput += outputParagraph
        
    #print(bioOutput)
    with open(outputFileLocation+'-user'+userId+'.bio', "w") as text_file:
        text_file.write(bioOutput.encode('utf-8', errors='ignore'))
