from controlTypes import controlTypes
from kivy.core.window import Window
from ui import OffkeyApp
import pickle

try:
	with open("config", "rb") as f:
		controls = pickle.load(f)
except FileNotFoundError:
	controls = {}
try:
	app = OffkeyApp(controls)
	app.run()
except KeyboardInterrupt:
	app.on_stop()

with open("config", "wb") as f:
	controls["window"] = Window.size
	for i in controls["buttons"]:
		controls["buttons"][i].pop("button")

	print(controls)
	pickle.dump(controls, f)