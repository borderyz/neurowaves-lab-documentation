from psychopy import visual, core, event

# Set up the window
#win = visual.Window(size=(1920, 1080), fullscr=False, color=(1, 1, 1), units="pix")
#win = visual.Window(size=(800, 600), fullscr=False, color=(1, 1, 1), units="pix")
win = visual.Window(size=(1910, 1070), fullscr=False, color=(1, 1, 1), units="pix")

# Define the stimuli
instructions = visual.TextStim(win, text="Press any key to begin.", color=(-1, -1, -1))
stimulus = visual.TextStim(win, text="Look at this!", color=(-1, -1, -1))
response_screen = visual.TextStim(win, text="Press 'y' if you saw the text, 'n' if not.", color=(-1, -1, -1))

# Display the instructions
instructions.draw()
win.flip()
event.waitKeys()  # Wait for any key to begin

# Display the main stimulus
stimulus.draw()
win.flip()
core.wait(1.5)  # Display for 1.5 seconds

# Display the response screen
response_screen.draw()
win.flip()

# Get a response
keys = event.waitKeys(keyList=['y', 'n'])

# End the experiment
win.close()

# Print the result
if 'y' in keys:
    print("Participant saw the text.")
else:
    print("Participant did not see the text.")
