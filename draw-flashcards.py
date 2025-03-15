#!/usr/bin/env python3

import json
import sys
import os
import argparse
import subprocess
import glob
import copy

from textwrap import wrap

parser = argparse.ArgumentParser()
parser.add_argument('infile',type=argparse.FileType('r', encoding='latin-1'))

args = parser.parse_args()
infile = args.infile.name

ROWSPERPAGE = 3
COLSPERPAGE = 2
CARDSPERPAGE = ROWSPERPAGE * COLSPERPAGE
FONTS = ['Georgia, Times New Roman, serif', 'Calibri, Arial, Helvetica, sans-serif']
COLORS = ['darkred', 'darkblue']
FONTSIZE="250"
FRONT=0
BACK=1

#####################

def cardcenter(row,col,side):
  if side == FRONT:
    return ( int(100 * col / COLSPERPAGE) + int(100/(COLSPERPAGE*2)),
             int(100 * row / ROWSPERPAGE) + int(100/(ROWSPERPAGE*2)) )
  else:
    return ( int(100 * col / COLSPERPAGE) + int(100/(COLSPERPAGE*2)),
             100 - (int(100 * row / ROWSPERPAGE) + int(100/(ROWSPERPAGE*2))) )

#####################

def writepage(cardcontents,pagenum,startingcardnum,side):
  with open(f"page{pagenum:04}-side{side}.svg","w",encoding='utf-8') as f:
     print(f"""
<svg width="816px" height="1104px" viewBox="0 0 816 1104"> <g dominant-baseline="middle" fill="COLORS[side]" font-size="{FONTSIZE}%" text-anchor="middle" font-family="{FONTS[side]}">
""",file=f)

    whichcard = 0
    for row in range(ROWSPERPAGE):
      for col in range(COLSPERPAGE):
        thisx, thisy = cardcenter(row,col,side)
        for chunk,offset in enumerate([-6,0,+8]):
          print(f"""
<text x="{thisx}%" y="{thisy+offset}%">{cardcontents[whichcard][chunk]}</text>    
""",file=f)
        whichcard += 1

    print(f"""
  </g>
</svg>
""",file=f)

  os.system(f"inkscape --export-filename=page{pagenum:04}-side{side}.eps page{pagenum:04}-side{side}.svg")

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

oldwd = os.getcwd()
newbasename = infile.replace('.json','')
scratchdirname = newbasename + str(os.getpid())
os.mkdir(scratchdirname, mode=0o755)
os.chdir(scratchdirname)

pagenum = 0
firstcardonpage = 1

while(len(cardlist) > 0):

################################################################
# 
# now we write a questions side
# 
################################################################

  pagecontents = []
  for card in range(CARDSPERPAGE):
    pagecontents.append(wrap(cardlist[card][FRONT],width=20))
    if len(pagecontents[card]) == 1:
      pagecontents[card].append(pagecontents[card][0])
      pagecontents[card].append('')
      pagecontents[card][0] = ''
    elif len(pagecontents[card]) == 2:
      pagecontents[card].append('')
    else:
      pass # we just ignore lines in excess of 3 for now
    
  writepage(pagecontents,pagenum,firstcardonpage,FRONT)

################################################################
# 
# now we write an answers side
# 
################################################################

  pagecontents = []
  for card in range(CARDSPERPAGE):
    pagecontents.append(wrap(cardlist[card][BACK],width=20))
    if len(pagecontents[card]) == 1:
      pagecontents[card].append(pagecontents[card][0])
      pagecontents[card].append('')
      pagecontents[card][0] = ''
    elif len(pagecontents[card]) == 2:
      pagecontents[card].append('')
    else:
      pass # we just ignore lines in excess of 3 for now
    
  writepage(pagecontents,pagenum,firstcardonpage,BACK)

  print(f"wrote the sides of page {pagenum}")
  pagenum += 1
  firstcardonpage += CARDSPERPAGE
  del cardlist[:CARDSPERPAGE]

################################################################
# 
# finally we let ghostscript make a PDF
# 
################################################################

epsfiles = glob.glob("*.eps")
n = len(epsfiles)
print(f"I found {n} sides")
if n>0:
  ghostscript_result = subprocess.run(["gs", 
                                     "-sDEVICE=pdfwrite", 
                                     "-dNOPAUSE", 
                                     "-dBATCH", 
                                     "-dSAFER", 
                                     "-dCenterPages=true", 
                                     f"-sOutputFile={scratchdirname}.pdf", 
                                     *epsfiles], 
                                    stdout=subprocess.DEVNULL,check=True)

  print("done")
else:
  print("giving up")
os.chdir(oldwd)
# os.rename(oldwd + f'/{newbasename}.pdf', f'/{newbasename}.pdf')
# os.unlink(scratchdirname)
