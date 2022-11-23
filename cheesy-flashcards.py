#!/usr/bin/env python3

import PySimpleGUI as sg                        
import os
import sys
import re
import json
import random

colorfg = 'pink'
colorbg = 'blue'

def main():
  if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} items.json")
    sys.exit(1)
  infile = str(sys.argv[1])
  with open(infile,encoding='utf-8') as f:
    flashcards = json.load(f)
  prompts = list(flashcards.keys())
  random.shuffle(prompts)
  
  layout = [  [sg.Text(f"flashcards {infile}", key='-TITLE-')],
              [sg.Text('', size=(80,1), key='-FEEDBACK-')],
              [sg.Text(f"{prompts[0]}", size=(15,1), key='-CARDTEXT-',font=('fixed',24),background_color = colorbg,text_color = colorfg)],
              [sg.Text('', size=(80,1), key='-FEEDBACK2-')],
              [sg.Button('Prev'),sg.Button('Flip'),sg.Button('Next'),sg.Button('Quit')] ]
  window = sg.Window('Cheesy flashcards', layout, resizable=True,
               margins=(50, 50), return_keyboard_events=True, use_default_focus=False)
  
  pointer = 0
  current_side = 0

  while True:
    event, values = window.Read()
    window['-FEEDBACK2-'].update(f"event was {event}, ord = {ord(event[0])}")
    if (event == sg.WIN_CLOSED or event is None or
      event == 'Quit' or event.lower().startswith('q')):
      sys.exit(0)
    if event == 'Flip' or event == ' ' or event.lower().startswith('space'):
      if current_side == 1:
        window['-CARDTEXT-'].update(f"{prompts[pointer]}",background_color = colorbg,text_color = colorfg)
        current_side = 0
      else:
        window['-CARDTEXT-'].update(f"{flashcards[prompts[pointer]]}",background_color = colorfg,text_color = colorbg)
        current_side = 1
    if event == 'Prev' or event.lower().startswith('p'):
      current_side = 0
      if pointer == 0:
        pointer = len(prompts)-1
      else:
        pointer -= 1
      window['-CARDTEXT-'].update(f"{prompts[pointer]}",background_color = colorbg,text_color = colorfg)
    if event == 'Next' or event[0].lower().startswith('n') or event.lower().startswith('return'):
      current_side = 0
      if pointer == len(prompts)-1:
        pointer = 0
      else:
        pointer += 1
      window['-CARDTEXT-'].update(f"{prompts[pointer]}",background_color = colorbg,text_color = colorfg)

if __name__ == '__main__':
  main()
