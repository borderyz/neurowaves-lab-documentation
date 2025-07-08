import pyglet
display = pyglet.canvas.Display()
screens = display.get_screens()
print(len(screens))  # Number of screens