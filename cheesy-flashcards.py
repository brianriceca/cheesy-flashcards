#!/usr/bin/env python3

import PySimpleGUI as sg                        
import os
import sys
import json
import random
import argparse

sg.theme('LightBlue2')

colorfg = 'pink'
colorbg = 'blue'

ALL = -1

def check_event(s,l):
  if l is None:
    return False
  for a in l:
    if a is None:
      if s is None:
        return True
    elif ':' in a:
      if s[:a.index(':')] == a[:a.index(':')]:
        return True
    elif s == a:
      return True
  return False

def compare_text(a,b):
  print(f'a is {a}, b is {b}')
  if b.find('/') == -1:
    return a == b
  else:
    correctlist = b.split('/')
    return (a in correctlist)

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiz', type=int, choices=[0, 3, 4, 5], default=argparse.SUPPRESS)
parser.add_argument('-n', '--number', type=int, default=ALL)
parser.add_argument('-i', '--invert', action='store_true')
parser.add_argument('infile',type=argparse.FileType('r', encoding='latin-1'))

args = parser.parse_args()
infile = args.infile.name

mytitle = infile + ' ' 

nchoices = None
quizevents = None
if hasattr(args,'quiz'):
  nchoices = int(args.quiz)
  if nchoices > 0:
    mytitle += 'quiz '
    quizevents = [chr(x) for x in range(ord('1'), ord(chr(ord('1')+nchoices)))]
  else:
    mytitle += 'test '
else:
  mytitle += 'flashcards '
 
with open(infile,encoding='utf-8') as f:
  flashcards = json.load(f)

if args.invert:
  if len(list(flashcards.values())) != len(set(flashcards.values())):
    raise ValueError('to invert, values must be unique')
  inverted = {v: k for k, v in flashcards.items()}
  flashcards = inverted
  mytitle += '(inverted) '

if args.number == ALL:
  frontsides = list(flashcards.keys())
  nquestions = len(frontsides)
  random.shuffle(frontsides)
else:
  nquestions = args.number # thanks to random.sample,
                           #  even works if number > nquestions
  frontsides = random.sample(list(flashcards.keys()),nquestions)

backsides = list(flashcards.values()) # not every distracter will be the 
                                      # correct answer to something else 
                                      # in the chosen quiz items

mytitle += f'{nquestions} Qs / {len(flashcards)} entries '


layout = [  [sg.Text(mytitle, key='-TITLE-')],
            [sg.Text('', size=(80,1), justification='right', key='-FEEDBACK-')],
            [sg.Text(f"{frontsides[0]}", size=(15,1), key='-CARDTEXT-',
                   font=('fixed',24),background_color = colorbg,text_color = colorfg)],
            [sg.Text('', size=(80,1), key='-FEEDBACK2-')] ]

next_events = [ 'Next', 'Right:' ]
prev_events = [ 'Prev', 'Left:']
flip_events = [ 'Flip', ' ', 'Space:' ]
quit_events = [ 'Quit', 'Escape:', sg.WIN_CLOSED ]
keyboard_events = False
fill_in_the_blank = False
multiple_choice = False
if nchoices is not None:
  if nchoices == 0:
    fill_in_the_blank = True
  else:
    multiple_choice = True

if fill_in_the_blank:
  layout.append( [ sg.InputText('',key='-INPUTTEXT-'), sg.Button('Check') ] )
  layout.append( [sg.Text('', size=(80,1), key='-FEEDBACK3-')] )
elif multiple_choice:
  choiceline = [ sg.Text("", size=(12,1), 
                                key=f"-CHOICE{i}-", 
                                background_color=sg.theme_input_background_color())
                              for i in range(nchoices) ]
  choiceline.insert(0, sg.Text(" ",size=(1,1),key="-CHECKED-"))
  next_events.append('n')
  prev_events.append('p')
  flip_events.append('f')
  quit_events.append('q')
  keyboard_events = True
  layout.append(choiceline)

layout.append( [sg.Button('Prev'),sg.Button('Flip'),sg.Button('Next'),sg.Button('Quit')] )

window = sg.Window(mytitle, layout, resizable=False,
             margins=(50, 50), return_keyboard_events=keyboard_events, finalize=True)

distracters = ""
rightanswer = -1
attempted = [ False for x in frontsides ]
gotthemright = [ False for x in frontsides ] 

def update_score():
  if (nAttempted := attempted.count(True)) == 0:
    window['-FEEDBACK-'].update(f'Score n/a; completed 0/{nquestions} (0%)')
  else:
    score = gotthemright.count(True) / nAttempted
    completion = nAttempted / nquestions
    window['-FEEDBACK-'].update(f'Score {(score*100):.0f}%; completed {nAttempted}/{nquestions} ({(completion*100):.0f}%)')

def refresh_quiz_row(n):
  distracters = backsides.copy()
  distracters.remove(therightresponse := flashcards[frontsides[n]])
  samples = random.sample(distracters, nchoices-1)
  samples.append(therightresponse)
  distracters = samples.copy()
  random.shuffle(distracters)
  for i in range(nchoices):
    window[f"-CHOICE{i}-"].update(f"{i+1}:{distracters[i]}",background_color=sg.theme_input_background_color())
  update_score()
  if gotthemright[n]:
    window['-CHECKED-'].update("x")
  else:
    window['-CHECKED-'].update(" ")
  return distracters.index(flashcards[frontsides[n]])

if nchoices is not None and nchoices > 0:
  rightanswer = refresh_quiz_row(0)

itemnumber = 0
current_side = 0

while True:
  event, values = window.Read()
  window['-FEEDBACK2-'].update(f"event was {event}, ord = {ord(event[0])}")

#---------- quit

  if check_event(event, quit_events):
    sys.exit(0)

#---------- flip

  if check_event(event, flip_events):
    if current_side == 1:
      window['-CARDTEXT-'].update(f"{frontsides[itemnumber]}",background_color = colorbg,text_color = colorfg)
      current_side = 0
    else:
      window['-CARDTEXT-'].update(f"{flashcards[frontsides[itemnumber]]}",background_color = colorfg,text_color = colorbg)
      current_side = 1

#---------- prev

  if check_event(event, prev_events):
    current_side = 0
    if itemnumber == 0:
      itemnumber = len(frontsides)-1
    else:
      itemnumber -= 1
    if '-INPUTTEXT-' in window.AllKeysDict:
      window['-INPUTTEXT-'].update('')
    window['-CARDTEXT-'].update(f"{frontsides[itemnumber]}",background_color = colorbg,text_color = colorfg)
    if nchoices is not None:
      rightanswer = refresh_quiz_row(itemnumber)

#---------- next

  if check_event(event, next_events):
    current_side = 0
    if itemnumber == len(frontsides)-1:
      itemnumber = 0
    else:
      itemnumber += 1
    if '-INPUTTEXT-' in window.AllKeysDict:
      window['-INPUTTEXT-'].update('')
    window['-CARDTEXT-'].update(f"{frontsides[itemnumber]}",background_color = colorbg,text_color = colorfg)
    if nchoices is not None:
      rightanswer = refresh_quiz_row(itemnumber)

  if fill_in_the_blank:

#---------- text box

    response = values['-INPUTTEXT-'].strip().lower()
    if compare_text(response,flashcards[frontsides[itemnumber]]):
      window['-FEEDBACK3-'].update(f"{response} is correct")
      if not attempted[itemnumber]:
        gotthemright[itemnumber] = True
    else:
      window['-FEEDBACK3-'].update(f"{response} is not correct")
    attempted[itemnumber] = True
    if gotthemright[itemnumber]:
      window['-INPUTTEXT-'].update('')
      current_side = 0
      if itemnumber == len(frontsides)-1:
        itemnumber = 0
      else:
        itemnumber += 1
    update_score()
    window['-CARDTEXT-'].update(f"{frontsides[itemnumber]}",background_color = colorbg,text_color = colorfg)

  elif multiple_choice and check_event(event, quizevents):

#---------- number key

    responsenumber = ord(event[0]) - ord("1")
    window['-FEEDBACK2-'].update(f"I got event {event}, rightanswer = {rightanswer}")
    if responsenumber == rightanswer:
      if not attempted[itemnumber]:
        gotthemright[itemnumber] = True
      window[f"-CHOICE{responsenumber}-"].update(background_color='green')
    else:
      window[f"-CHOICE{responsenumber}-"].update(background_color='red')
    attempted[itemnumber] = True
    update_score()

   
window.close()
