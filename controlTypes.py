from enum import Enum, auto
strings = ["Press","Hold", "Mash", "Push Multiple",
		"Hold Multiple", "Mash Multiple", "Type", "Click",
		"Double Click", "Mash Click", "Click and Hold", "Release Mouse",
		"Move Mouse", "Jump Mouse"]
class controlTypes(Enum):
	press = 0
	hold = 1
	mash = 2
	pressMulti = 3
	holdMulti = 4
	mashMulti = 5
	typewrite = 6
	click = 7
	doubleClick = 8
	mashClick = 9
	clickHold = 10
	clickRelease = 11
	moveMouse = 12
	jumpMouse = 13
	
	def __str__(self):
		return strings[self.value]