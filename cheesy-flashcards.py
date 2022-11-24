#!/usr/bin/env python3

import PySimpleGUI as sg                        
import os
import sys
import re
import json
import random
import argparse

sg.theme('LightBlue2')

colorfg = 'pink'
colorbg = 'blue'

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiz', type=int, choices=range(1, 5), default=argparse.SUPPRESS)
parser.add_argument('-i', '--invert', action='store_true')
parser.add_argument('infile',type=argparse.FileType('r', encoding='latin-1'))

args = parser.parse_args()
infile = args.infile.name



nquizitems = None
if hasattr(args,'quiz'):
  nquizitems = int(args.quiz)
  if nquizitems < 2:
    raise ValueError("gotta have at least 2 choices")
  quizevents = [chr(x) for x in range(ord('1'), ord(chr(ord('1')+nquizitems)))]
 
with open(infile,encoding='utf-8') as f:
  flashcards = json.load(f)

if args.invert:
  if len(list(flashcards.values())) != len(set(flashcards.values())):
    raise ValueError('to invert, values must be unique')
  inverted = {v: k for k, v in flashcards.items()}
  flashcards = inverted
  print(flashcards)

prompts = list(flashcards.keys())
population = list(flashcards.values())
random.shuffle(prompts)
layout = [  [sg.Text(f"flashcards {infile}", key='-TITLE-')],
            [sg.Text('', size=(80,1), justification='right', key='-FEEDBACK-')],
            [sg.Text(f"{prompts[0]}", size=(15,1), key='-CARDTEXT-',
                   font=('fixed',24),background_color = colorbg,text_color = colorfg)],
            [sg.Text('', size=(80,1), key='-FEEDBACK2-')] ]

if nquizitems is not None:
  choiceline = [ sg.Text("", size=(12,1), 
                                key=f"-CHOICE{i}-", 
                                background_color=sg.theme_input_background_color())
                            for i in range(nquizitems) ]
  choiceline.insert(0, sg.Text(" ",size=(1,1),key="-CHECKED-"))
  layout.append(choiceline)
  layout.append( [sg.Text('', size=(80,1), key='-FEEDBACK3-')] )

layout.append( [sg.Button('Prev'),sg.Button('Flip'),sg.Button('Next'),sg.Button('Quit')] )

window = sg.Window('Cheesy flashcards', layout, resizable=True,
             margins=(50, 50), return_keyboard_events=True, use_default_focus=False,
             finalize=True)

distracters = ""
rightanswer = -1
attempted = [ False for x in prompts ]
gotthemright = [ False for x in prompts ] 

def update_score():
  if (nAttempted := attempted.count(True)) == 0:
    window['-FEEDBACK-'].update(f'Score n/a; completed 0/{len(prompts)} (0%)')
  else:
    score = gotthemright.count(True) / nAttempted
    completion = nAttempted / len(prompts)
    window['-FEEDBACK-'].update(f'Score {(score*100):.0f}%; completed {nAttempted}/{len(prompts)} ({(completion*100):.0f}%)')

def refresh_quiz_row(n):
  distracters = population.copy()
  distracters.remove(therightresponse := flashcards[prompts[n]])
  samples = random.sample(distracters, nquizitems-1)
  samples.append(therightresponse)
  distracters = samples
  random.shuffle(distracters)
  for i in range(nquizitems):
    window[f"-CHOICE{i}-"].update(f"{i+1}:{distracters[i]}",background_color=sg.theme_input_background_color())
  update_score()
  if gotthemright[n]:
    window['-CHECKED-'].update("x")
  else:
    window['-CHECKED-'].update(" ")
  return distracters.index(flashcards[prompts[n]])

if nquizitems is not None:
  rightanswer = refresh_quiz_row(0)

pointer = 0
current_side = 0

while True:
  event, values = window.Read()
#  window['-FEEDBACK2-'].update(f"event was {event}, ord = {ord(event[0])}")

#---------- quit

  if (event == sg.WIN_CLOSED or event is None or
    event == 'Quit' or event.lower().startswith('q')):
    sys.exit(0)

#---------- flip

  if (event == 'Flip' or event == ' ' or 
      event.lower().startswith('space') or event.lower().startswith('f')):
    if current_side == 1:
      window['-CARDTEXT-'].update(f"{prompts[pointer]}",background_color = colorbg,text_color = colorfg)
      current_side = 0
    else:
      window['-CARDTEXT-'].update(f"{flashcards[prompts[pointer]]}",background_color = colorfg,text_color = colorbg)
      current_side = 1

#---------- prev

  if event == 'Prev' or event.lower().startswith('p'):
    current_side = 0
    if pointer == 0:
      pointer = len(prompts)-1
    else:
      pointer -= 1
    window['-CARDTEXT-'].update(f"{prompts[pointer]}",background_color = colorbg,text_color = colorfg)
    if nquizitems is not None:
      rightanswer = refresh_quiz_row(pointer)

#---------- next

  if event == 'Next' or event[0].lower().startswith('n') or event.lower().startswith('return'):
    current_side = 0
    if pointer == len(prompts)-1:
      pointer = 0
    else:
      pointer += 1
    window['-CARDTEXT-'].update(f"{prompts[pointer]}",background_color = colorbg,text_color = colorfg)
    if nquizitems is not None:
      rightanswer = refresh_quiz_row(pointer)

#---------- number key
  if nquizitems is not None and event[0] in quizevents:
    responsenumber = ord(event[0]) - ord("1")
#    window['-FEEDBACK2-'].update(f"I got event {event}, rightanswer = {rightanswer}")
    if responsenumber == rightanswer:
      if not attempted[pointer]:
        gotthemright[pointer] = True
      window[f"-CHOICE{responsenumber}-"].update(background_color='green')
    else:
      window[f"-CHOICE{responsenumber}-"].update(background_color='red')
    attempted[pointer] = True
    update_score()
  
