#!/usr/bin/env python3

import json
import copy
import sys
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('infile',type=argparse.FileType('r', encoding='latin-1'))

args = parser.parse_args()
infile = args.infile.name

oldwd = os.getcwd()

CARDSPERPAGE = 6

with open(infile,encoding='utf-8') as f:
  flashcards = json.load(f)

if not infile.endswith('.json'):
  raise RuntimeError("gotta end in .json")

newbasename = infile.replace('.json','')
os.mkdir(newbasename, mode=0o755)
os.chdir(newbasename)

if (leftovers := len(list(flashcards.keys())) % CARDSPERPAGE):
  for i in range(CARDSPERPAGE-leftovers):
    flashcards[f"bogus{i}"] = str(i)
  
frontsides = list(flashcards.keys())
backsides = list(flashcards.values()) 

pagenum = 0

while(len(frontsides) > 0):
  with open(f"page{pagenum:04}-0.svg","w",encoding='utf-8') as f:
    print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104">
  <g dominant-baseline="middle" fill="darkred" font-size="300%" text-anchor="middle" font-family="Georgia, Times New Roman, serif">
    <text x="25%" y="16%">{frontsides[0]}</text>    
    <text x="75%" y="16%">{frontsides[1]}</text>    
    <text x="25%" y="50%">{frontsides[2]}</text>    
    <text x="75%" y="50%">{frontsides[3]}</text>    
    <text x="25%" y="84%">{frontsides[4]}</text>    
    <text x="75%" y="84%">{frontsides[5]}</text>    
  </g>
</svg>
""",file=f)
  os.system(f"inkscape --export-filename=page{pagenum:04}-0.eps page{pagenum:04}-0.svg")

  with open(f"page{pagenum:04}-1.svg","w",encoding='utf-8') as f:
    print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104">
  <g dominant-baseline="middle" fill="darkblue" font-size="300%" text-anchor="middle" font-family="Calibri, Arial, Helvetica, sans-serif">
    <text x="25%" y="16%">{flashcards[frontsides[1]]}</text>    
    <text x="75%" y="16%">{flashcards[frontsides[0]]}</text>    
    <text x="25%" y="50%">{flashcards[frontsides[3]]}</text>    
    <text x="75%" y="50%">{flashcards[frontsides[2]]}</text>    
    <text x="25%" y="84%">{flashcards[frontsides[5]]}</text>    
    <text x="75%" y="84%">{flashcards[frontsides[4]]}</text>    
  </g>
</svg>
  """,file=f)
  os.system(f"inkscape --export-filename=page{pagenum:04}-1.eps page{pagenum:04}-1.svg")

  pagenum += 1
  del frontsides[:CARDSPERPAGE]

os.system(f"gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -dCenterPages=true -sOutputFile={newbasename}.pdf *.eps")
os.chdir(oldwd)
