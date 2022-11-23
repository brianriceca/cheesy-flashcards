#!/usr/bin/env python3

import PySimpleGUI as sg                        
import os
import sys
import re
import json
import random

def main():
  """create a crossword puzzle bracket interactively"""
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
              [sg.Text(f"{prompts[0]}", size=(15,1), key='-CARDTEXT-',font=('fixed',24))],
              [sg.Text('', size=(80,1), key='-FEEDBACK2-')],
              [sg.Button('Prev'),sg.Button('Flip'),sg.Button('Next'),sg.Button('Quit')] ]
  window = sg.Window('Cheesy flashcards', layout, resizable=True,
               margins=(50, 50), return_keyboard_events=True, use_default_focus=False)
  
  pointer = 0
  current_side = 0

  while True:
    event, values = window.Read()
    if (event == sg.WIN_CLOSED or event is None or
      event == 'Quit' or event.startswith('q')):
      sys.exit(0)
    if event == 'Flip' or event == ' ':
      if current_side == 1:
        window['-CARDTEXT-'].update(f"{prompts[pointer]}")
        current_side = 0
      else:
        window['-CARDTEXT-'].update(f"{flashcards[prompts[pointer]]}")
        current_side = 1
    if event == 'Prev' or event[0].startswith('p'):
      current_side = 0
      if pointer == 0:
        pointer = len(prompts)-1
      else:
        pointer -= 1
      window['-CARDTEXT-'].update(f"{prompts[pointer]}")
    if event == 'Next' or event[0].startswith('n'):
      current_side = 0
      if pointer == len(prompts)-1:
        pointer = 0
      else:
        pointer += 1
      window['-CARDTEXT-'].update(f"{prompts[pointer]}")

if __name__ == '__main__':
  main()
