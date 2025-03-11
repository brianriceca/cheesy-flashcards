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

def writepage(cardcontents,pagenum,startingcardnum,side):
  with open(f"page{pagenum:04}-0.svg","w",encoding='utf-8') as f:
    print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104"> <g dominant-baseline="middle" fill="darkred" font-size="{FONTSIZE}%" text-anchor="middle" font-family="{ANSWERFONTS1}">
""",file=f)

    for row in range(ROWSPERPAGE):
      for col in range(COLSPERPAGE):
        thisx, thisy = cardcenter(row,col)
        for chunk,offset in enumerate([-6,0,+8]):
          print(f"""
<text x="{thisx}%" y="{thisy+offset}%" {cardcontents[row][col][chunk]}</text>    
""",file=f)

    print(f"""
  </g>
</svg>
""",file=f)

  os.system(f"inkscape --export-filename=page{pagenum:04}-0.eps page{pagenum:04}-0.svg")

#####################

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

newbasename = infile.replace('.json','')
os.mkdir(newbasename, mode=0o755)
os.chdir(newbasename)

pagenum = 0
firstcardonpage = 1

while(len(cardlist) > 0):
  for side in range(1):

################################################################
# 
# now we write a questions side
# 
################################################################

# let's wrap all the text on the page

# TODO change this so that it populates pagecontents with a data structure
# suitable for passing to writepage()

  pagecontents = []
  for card in range(CARDSPERPAGE):
    wrapped.append(wrap(frontsides[card],width=20))
    if len(wrapped[card]) == 1:
      wrapped[card].append(wrapped[card][0])
      wrapped[card].append('')
      wrapped[card][0] = ''
    elif len(wrapped[card]) == 2:
      wrapped[card].append('')
    
  writepage(pagecontents,pagenum,startingcardnum,0)

################################################################
# 
# now we write an answers side
# 
################################################################

# TODO reverse each row of pagecontents

  writepage(flippedpagecontents,pagenum,startingcardnum)
  writepage(pagecontents,pagenum,startingcardnum,1)

  print(f"wrote the sides of page {pagenum}")
  pagenum += 1
  startingcardnum += CARDSPERPAGE
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
