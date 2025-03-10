#!/usr/bin/env python3

import json
import sys
import os
import argparse
import subprocess
import glob
from textwrap import wrap

parser = argparse.ArgumentParser()
parser.add_argument('infile',type=argparse.FileType('r', encoding='latin-1'))

args = parser.parse_args()
infile = args.infile.name

oldwd = os.getcwd()

ROWSPERPAGE = 3
COLSPERPAGE = 2
CARDSPERPAGE = ROWSPERPAGE * COLSPERPAGE
QUESTIONFONTS1 = 'Georgia, Times New Roman, serif'
ANSWERFONTS1 = 'Calibri, Arial, Helvetica, sans-serif'
FONTSIZE="250"

#####################

def cardcenter(row,col):
  return ( int(100 * col / COLSPERPAGE) + int(100/(COLSPERPAGE*2)),
           int(100 * row / ROWSPERPAGE) + int(100/(ROWSPERPAGE*2)) )

#####################

def writepage(pagenum,cardcontents):
  with open(f"page{pagenum:04}-0.svg","w",encoding='utf-8') as f:
    print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104"> <g dominant-baseline="middle" fill="darkred" font-size="{FONTSIZE}%" text-anchor="middle" font-family="{ANSWERFONTS1}">
""",file=f)

  for row in range(ROWSPERPAGE):
    for col in range(COLSPERPAGE):
      thisx, thisy = cardcenter(row,col)
      print(f"""
### TODO start refactoring here. Need to address the cards on a page as 
###      cardcontents[row][col][chunk]

    <text x="{thisx}%" y="{thisy-UPINCREMENT}%" {cardcontents[0][0]}</text>    
    <text x="25%" y="19%">{wrapped[0][1]}</text>    
    <text x="25%" y="21%">{wrapped[0][2]}</text>    

    <text x="75%" y="12%">{wrapped[1][0]}</text>    
    <text x="75%" y="19%">{wrapped[1][1]}</text>    
    <text x="75%" y="21%">{wrapped[1][2]}</text>    

    <text x="25%" y="46%">{wrapped[2][0]}</text>    
    <text x="25%" y="50%">{wrapped[2][1]}</text>    
    <text x="25%" y="56%">{wrapped[2][2]}</text>    

    <text x="75%" y="46%">{wrapped[3][0]}</text>    
    <text x="75%" y="50%">{wrapped[3][1]}</text>    
    <text x="75%" y="56%">{wrapped[3][2]}</text>    

    <text x="25%" y="80%">{wrapped[4][0]}</text>    
    <text x="25%" y="84%">{wrapped[4][1]}</text>    
    <text x="25%" y="90%">{wrapped[4][2]}</text>    

    <text x="75%" y="80%">{wrapped[5][0]}</text>    
    <text x="75%" y="84%">{wrapped[5][1]}</text>    
    <text x="75%" y="90%">{wrapped[5][2]}</text>    

  </g>
</svg>
""",file=f)

  os.system(f"inkscape --export-filename=page{pagenum:04}-0.eps page{pagenum:04}-0.svg")

with open(infile,encoding='utf-8') as f:
  flashcards = json.load(f)

if not infile.endswith('.json'):
  raise RuntimeError("gotta end in .json")

# we get the text for the cards as a dict, let's change that to a 
# stoopid list of strings to put on cards

cardlist = list(flashcards.items())
if (leftovers := len(cardlist) % CARDSPERPAGE):
  for i in range(CARDSPERPAGE-leftovers):
    cardlist.append( (f"bogus{i}", str(i) ) )
textlist = []

newbasename = infile.replace('.json','')
os.mkdir(newbasename, mode=0o755)
os.chdir(newbasename)

pagenum = 0

while(len(cardlist) > 0):
  for side in range(1):

################################################################
# 
# now we write a questions side
# 
################################################################

# let's wrap all the text on the page

  wrapped = []
  for card in range(CARDSPERPAGE):
    wrapped.append(wrap(frontsides[card],width=20))
    if len(wrapped[card]) == 1:
      wrapped[card].append(wrapped[card][0])
      wrapped[card].append('')
      wrapped[card][0] = ''
    elif len(wrapped[card]) == 2:
      wrapped[card].append('')
    
  with open(f"page{pagenum:04}-0.svg","w",encoding='utf-8') as f:
    print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104"> <g dominant-baseline="middle" fill="darkred" font-size="250%" text-anchor="middle" font-family="{ANSWERFONTS1}">

    <text x="25%" y="12%">{wrapped[0][0]}</text>    
    <text x="25%" y="19%">{wrapped[0][1]}</text>    
    <text x="25%" y="21%">{wrapped[0][2]}</text>    

    <text x="75%" y="12%">{wrapped[1][0]}</text>    
    <text x="75%" y="19%">{wrapped[1][1]}</text>    
    <text x="75%" y="21%">{wrapped[1][2]}</text>    

    <text x="25%" y="46%">{wrapped[2][0]}</text>    
    <text x="25%" y="50%">{wrapped[2][1]}</text>    
    <text x="25%" y="56%">{wrapped[2][2]}</text>    

    <text x="75%" y="46%">{wrapped[3][0]}</text>    
    <text x="75%" y="50%">{wrapped[3][1]}</text>    
    <text x="75%" y="56%">{wrapped[3][2]}</text>    

    <text x="25%" y="80%">{wrapped[4][0]}</text>    
    <text x="25%" y="84%">{wrapped[4][1]}</text>    
    <text x="25%" y="90%">{wrapped[4][2]}</text>    

    <text x="75%" y="80%">{wrapped[5][0]}</text>    
    <text x="75%" y="84%">{wrapped[5][1]}</text>    
    <text x="75%" y="90%">{wrapped[5][2]}</text>    

  </g>
</svg>
""",file=f)

  os.system(f"inkscape --export-filename=page{pagenum:04}-0.eps page{pagenum:04}-0.svg")

################################################################
# 
# now we write an answers side
# 
################################################################

  with open(f"page{pagenum:04}-0.svg","w",encoding='utf-8') as f:
    print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104">
  <g dominant-baseline="middle" fill="darkblue" font-size="300%" text-anchor="middle" font-family="{QUESTIONFONTS1}">
    <text x="25%" y="16%">{flashcards[frontsides[1]]}</text>    
    <text x="75%" y="16%">{flashcards[frontsides[0]]}</text>    
    <text x="25%" y="50%">{flashcards[frontsides[3]]}</text>    
    <text x="75%" y="50%">{flashcards[frontsides[2]]}</text>    
    <text x="25%" y="84%">{flashcards[frontsides[5]]}</text>    
    <text x="75%" y="84%">{flashcards[frontsides[4]]}</text>    
  </g>
</svg>
""",file=f)
  inkscape_result = subprocess.run(["inkscape", 
                                    f"--export-filename=page{pagenum:04}-1.eps", 
                                    f"page{pagenum:04}-1.svg"], stdout=subprocess.DEVNULL,check=True)


  print(f"wrote the sides of page {pagenum}")
  pagenum += 1
  del frontsides[:CARDSPERPAGE]

################################################################
# 
# finally we let ghostscript make a PDF
# 
################################################################

svgfiles = glob.glob("*.eps")
n = len(svgfiles)
print(f"I found {n} sides")
if n>0:
  ghostscript_result = subprocess.run(["gs", 
                                     "-sDEVICE=pdfwrite", 
                                     "-dNOPAUSE", 
                                     "-dBATCH", 
                                     "-dSAFER", 
                                     "-dCenterPages=true", 
                                     f"-sOutputFile={newbasename}.pdf", 
                                     *svgfiles], 
                                    stdout=subprocess.DEVNULL,check=True)

  print("done")
else:
  print("giving up")
os.chdir(oldwd)
