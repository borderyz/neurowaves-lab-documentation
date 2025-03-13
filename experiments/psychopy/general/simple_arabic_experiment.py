from psychopy import visual, core, event
import arabic_reshaper
# Create a window
win = visual.Window(size=(1919, 1079), units='pix', color='white', fullscr = False)

# Define text parameters
stimuliFont = 'Open Sans'  # Change to 'Noto Sans Arabic' or another font if Sahel has issues

stimuliUnits = 'pix'  # or 'height' depending on your preference
stimuliSize = 40  # Change the font size as needed
stimuliColor = 'black'  # Set text color

# Test Arabic text with diacritics
test_text =  'لمُدرسة'
#test_text = arabic_reshaper.reshape('لمُدرسة')
# Create the TextStim object

#stim = visual.TextStim(win, text=test_text, font=stimuliFont, units=stimuliUnits, height=stimuliSize, color=stimuliColor, languageStyle='Arabic')

stim = visual.TextBox2(win, text=test_text, font=stimuliFont, units=stimuliUnits, color=stimuliColor, languageStyle='RTL')


# Draw and display the text
stim.draw()
win.flip()

# Wait for a key press before closing
event.waitKeys()

# Close the window
win.close()
core.quit()
