from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import DragBehavior
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from keyTable import keyTable
from selectableGrid import SelectableGrid
from copy import deepcopy
from listener import listener
from multiprocessing import Value
from threading import Thread

from controlTypes import controlTypes

class UI(BoxLayout): # TODO: Add color options
	def __init__(self, data, **kwargs): #TODO: Add saving button positions
		super(UI, self).__init__(**kwargs)
		self.lastOrder = []
		self.update_data(data["buttons"])
		self.data = data["buttons"]
		self.buttonPos = data["positions"]
		Window.size = data["window"]
		self.size = data["window"]
		self.pval = Value('d', 0)
		self.sensitivity = 5 # TODO: add slider
		self.p1 = Thread(target=listener, args=(self.data, self.pval, self.sensitivity))
		self.p1.start()
		self.displayItems = {}
		self.lastHighlight = None
		Clock.schedule_interval(self.update_notes, 0.2)
		for key in self.data:
			row = self.data[key]
			self.add_control(row)
		Window.bind(on_resize=self.on_resize)

	def create_button(self, text, buttonType):
		if not text in self.buttonPos:
			self.buttonPos[text] = [300,300]

		if buttonType == "key":
			return buttonDisplay(text, pos = self.buttonPos[text])
		elif buttonType == "mouse":
			return mouseDisplay(text, pos = self.buttonPos[text])
		else:
			return None

	def on_resize(self, win, x, y):
		self.size = (x, y)

	def update_data(self, data): # TODO: add sort modes
		self.lastOrder = [data[key] for key in data]
		self.ids["bindings"].fill_data(self.lastOrder)

	def update_notes(self, dt):
		pitch = self.pval.value
		note = int(pitch)
		self.ids["pitch"].text = str(round(pitch, 5))
		self.ids["note"].text = str(note)
		if self.lastHighlight is None:
			if note in self.data:
				self.lastHighlight = note
				for button in self.data[note]["button"]:
					button.activate()
		else:
			if note != self.lastHighlight:
				for button in self.data[self.lastHighlight]["button"]:
					button.deactivate()
				self.lastHighlight = None

	def get_selected(self):
		return self.ids["bindings"].ids["dat"].layout_manager.selected_nodes

	def restart_listener(self):
		self.p1.kill()
		self.p1 = Process(target=listener, args=(self.data, self.pval))
		self.p1.start()

	def delete_control(self, pitch):
		toDelete = self.data[pitch]
		for button in toDelete["button"]:
			button.ref.remove(toDelete)
			if len(button.ref) == 0:
				self.ids["display"].remove_widget(button)
		self.data.pop(self.lastOrder[self.get_selected()[0]]["notes"])
		pass

	def add_control(self, row):
		row.update({"button":[]})
		if row["option"] == "mouse":
			if "mouse" in self.displayItems:
				self.displayItems["mouse"].ref.append(row)
			else:
				temp = self.create_button("mouse", "mouse")
				temp.ref = [row]
				self.displayItems["mouse"] = temp
				self.ids["display"].add_widget(temp)
			row["button"].append(self.displayItems["mouse"])
		elif isinstance(row["option"], str):
			if row["option"] in self.displayItems:
				self.displayItems[row["option"]].ref.append(row)
			else:
				temp = self.create_button(row["option"], "key")
				temp.ref = [row]
				self.displayItems[row["option"]] = temp
				self.ids["display"].add_widget(temp)
			row["button"].append(self.displayItems[row["option"]])
		elif isinstance(row["option"][0], int):
			if "mouse" in self.displayItems:
				self.displayItems["mouse"].ref.append(row)
			else:
				temp = self.create_button("mouse", "mouse")
				temp.ref = [row]
				self.displayItems["mouse"] = temp
				self.ids["display"].add_widget(temp)
			row["button"].append(self.displayItems["mouse"])
		else:
			for opt in row["option"]:
				if opt in self.displayItems:
					self.displayItems[opt].ref.append(row)
				else:
					temp = self.create_button(str(opt), "key")
					temp.ref = [row]
					self.displayItems[opt] = temp
					self.ids["display"].add_widget(temp)
				row["button"].append(self.displayItems[opt])

	def button_add(self):
		popup = addDialog(self, title="add", size_hint=(None, None), size = self.ids["control"].size, pos_hint = {'x': 0, 'y':0}, overlay_color= (0,0,0,0))
		popup.open()

	def button_edit(self):
		pass

	def button_remove(self):
		try: # Skip if nothing selected
			self.delete_control(self.lastOrder[self.get_selected()[0]]["notes"])
		except:
			return
		self.update_data(self.data)

	def __exit__(self):
		self.pval.value = -1

class buttonDisplay(DragBehavior, AnchorLayout): # TODO: Make type display
	def __init__(self, text = "", **kwargs): # TODO: Replace directions with arrows
		super(buttonDisplay, self).__init__(**kwargs)
		self.id = text
		self.change_text(text)

	def change_color(self, color):
		self.ids["image"].color = color

	def change_text(self, text):
		if text in ["left", "right", "up", "down"]:
			self.ids["icon"].color = (0.1,0.1,0.1,1)
			if text == "left":
				self.ids["icon"].source = "img/leftarrow.png"
			elif text == "down":
				self.ids["icon"].source = "img/downarrow.png"
			elif text == "up":
				self.ids["icon"].source = "img/uparrow.png"
			else:
				self.ids["icon"].source = "img/rightarrow.png"
		else:
			self.ids["text"].text = text

	def activate(self):
		self.change_color((0.1,0.1,0.9,1))

	def deactivate(self):
		self.change_color((0.1,0.1,0.1,1))

	def on_touch_up(self, button):
		super(buttonDisplay, self).on_touch_up(button)
		p = self.parent
		p.remove_widget(self)
		p.add_widget(self)
		p.parent.buttonPos[self.id] = list(self.pos)

class mouseDisplay(DragBehavior, AnchorLayout): # TODO: fold this and buttonDisplay into a class
	def __init__(self, text = "", **kwargs):	# TODO: Add arrows
		super(mouseDisplay, self).__init__(**kwargs)

	def change_color(self, color):
		self.ids["image"].color = color

	def activate(self):
		self.change_color((0.1,0.1,0.9,1))

	def deactivate(self):
		self.change_color((0.1,0.1,0.1,1))

class addDialog(Popup):
	def __init__(self, parentWidget, data = None, **kwargs):
		super(addDialog, self).__init__(**kwargs)
		self.parentWidget = parentWidget
		for i in controlTypes:
			temp = Button(text=str(i))
			temp.enum = i
			self.ids["mode"].add_widget(temp)
		if data is None:
			self.new = None
		else:
			self.new = data
			#Populate fields

	def submit(self): # TODO: Make option selection better
		temp = {"type":self.ids["mode"].selected_nodes[0].enum,
				"option":self.ids["options"].text,
				"notes":int(self.ids["pitch"].text)}
		self.parentWidget.data[temp["notes"]] = temp
		self.parentWidget.add_control(temp)
		self.parentWidget.update_data(self.parentWidget.data)
		self.dismiss()

	def cancel(self):
		if not self.new is None:
			self.parentWidget.data[self.new["notes"]] = self.new
			self.parentWidget.add_control(self.new)
			self.parentWidget.update_data(self.parentWidget.data)
			pass # Repopulate
		self.dismiss()

class OffkeyApp(App):
	def __init__(self, data, **kwargs):
		super(OffkeyApp, self).__init__(**kwargs)
		self.data = data

	def build(self):
		self.ui = UI(self.data)
		return self.ui
		#return UI([{"option":str(x), "notes":str(x+1), "type":"Click and Hold"} for x in range(100)])

	def on_stop(self, *args):
		self.ui.__exit__()
		return True