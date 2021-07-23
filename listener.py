#! /usr/bin/env python
import pyaudio
import sys
import aubio
from numpy import fromstring, float32
from pyautogui import keyDown, keyUp, mouseDown, mouseUp, typewrite, hotkey
from pynput.keyboard import Controller
from pynput.mouse import Controller as mouseControl
from pynput.mouse import Button
from collections import deque
from controlTypes import controlTypes
import Xlib.threaded
from traceback import print_exc

def listener(controls, pval, sensitivity = 5):
	keyboard = Controller()
	mouse = mouseControl()
	# initialise pyaudio
	p = pyaudio.PyAudio()
	

	# open stream
	stream = p.open(format=pyaudio.paFloat32,
					channels=1,
					rate=44100,
					input=True,
					frames_per_buffer=1024)

	# setup pitch
	pitch_o = aubio.pitch("default", 4096, 1024, 44100)
	pitch_o.set_unit("midi")
	pitch_o.set_tolerance(0.8)
	
	pval = pval
	controls = controls

	debounceLog = deque(maxlen=sensitivity)
	pressed = None # TODO: Make this temp on for all buttons and pass out
	keys = None
	mouseLock = False
	while True:
		try:
			audiobuffer = stream.read(1024)
			signal = fromstring(audiobuffer, dtype=float32)
			if pval.value == -1:
				break
			pval.value = pitch_o(signal)[0]
			pitch = int(pval.value)
			debounceLog.append(pitch)
			if not pressed is None:
				if not pressed in debounceLog:
					[keyUp(key) for key in keys]
					pressed = None
			elif pitch in controls and isFull(debounceLog):
				if controls[pitch]["type"] == controlTypes.hold: # Hold
					key = controls[pitch]["option"]
					keyDown(key)
					keys = [key]
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.press: # Press once
					key = controls[pitch]["option"]
					keyDown(key)
					keyUp(key)
					keys = []
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.typewrite: # Type something out
					text = controls[pitch]["option"]
					typewrite(text)
					keys = []
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.mash: # Mash
					key = controls[pitch]["option"]
					keyboard.press(key)
					keyboard.release(key)
				elif controls[pitch]["type"] == controlTypes.pressMulti: # Press multiple buttons once
					hotkey(*controls[pitch]["option"])
					keys = []
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.holdMulti: # Hold down multiple buttons
					for key in controls[pitch]["option"]:
						keyDown(key)
					keys = controls[pitch]["key"]
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.mashMulti: # Mash multiple buttons
					for key in controls[pitch]["option"]:
						keyboard.press(key)
						keyboard.release(key)
				elif controls[pitch]["type"] == controlTypes.click: # Click once
					if mouseLock:
						continue
					mouse.click(Button.left)
					keys = []
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.doubleClick: # doubleclick
					if mouseLock:
						continue
					mouse.click(Button.left, 2)
					keys = []
					pressed = pitch
				elif controls[pitch]["type"] == controlTypes.mashClick: # Mash click
					if mouseLock:
						continue
					mouse.click(Button.left)
				elif controls[pitch]["type"] == controlTypes.clickHold: # Hold down the mouse button
					if not mouseLock:
						mouseDown()
						mouseLock = True
				elif controls[pitch]["type"] == controlTypes.clickRelease: # Release mouse button
					if mouseLock:
						mouseUp()
						mouseLock = False
				elif controls[pitch]["type"] == controlTypes.moveMouse: # Move the mouse around
					mouse.move(*controls[pitch]["option"])
				elif controls[pitch]["type"] == controlTypes.jumpMouse: # Move the mouse to a specific location
					mouse.position = controls[pitch]["option"]
					keys = []
					pressed = pitch
			#time.sleep(0.02)
			#stream.stop_stream()
		except KeyboardInterrupt:
			break
		except KeyError:
			print_exc()

	stream.stop_stream()
	stream.close()
	p.terminate()

def isFull(deq):
	return deq.count(deq[-1]) == deq.maxlen
