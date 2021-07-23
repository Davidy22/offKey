from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
								 RecycleBoxLayout):
	''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, GridLayout):
	''' Add selection support to the Label '''
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		''' Catch and handle the view changes '''
		self.index = index
		self.ids["option"].text = str(data["option"])
		self.ids["type"].text = str(data["type"])
		self.ids["notes"].text = str(data["notes"])
		return super(SelectableLabel, self).refresh_view_attrs(
			rv, index, data)

	def on_touch_down(self, touch):
		''' Add selection on touch down '''
		if super(SelectableLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		''' Respond to the selection of items in the view. '''
		self.selected = is_selected


class RV(RecycleView):
	def __init__(self, data = [], **kwargs):
		super(RV, self).__init__(**kwargs)
		#self.data = [{"keys":str(x), "notes":str(x+1)} for x in range(100)]
		self.data = data
	
	def fill_data(self, data):
		self.data = data

class keyTable(BoxLayout):
	def __init__(self, **kwargs):
		super(keyTable, self).__init__(**kwargs)
	
	def fill_data(self, data = []):
		self.ids["dat"].fill_data(data)
