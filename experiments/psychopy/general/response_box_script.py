from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue
from pypixxlib._libdpx import DPxSetDinLog, DPxStartDinLog, DPxGetDinStatus, DPxReadDinLog, DPxEnableDinDebounce
from psychopy import core
#
# function[resp, time] = getButton()
#
# while true
#     Datapixx('RegWrRd');
#     kbcheck = dec2bin(Datapixx('GetDinValues'));
#     if kbcheck(end) == '1' | | kbcheck(end - 1) == '1' | | kbcheck(end - 2) == '1' | | kbcheck(
#             end - 3) == '1' | | kbcheck(end - 5) == '1' | | kbcheck(end - 6) == '1' | | kbcheck(
#             end - 7) == '1' | | kbcheck(end - 8) == '1'
#         for i_but = 1:9
#         buttonBox(i_but) = str2num(kbcheck(end - 9 + i_but));
#     end
#
#     resp = find(buttonBox);
#     time = GetSecs;
#     if length(resp) == 1
#         break;
#     end
# end
# end

def decimal_to_binary(decimal_number):
    """
    Converts a decimal number to its binary representation.

    Parameters:
        decimal_number (int): The decimal number to convert.

    Returns:
        str: A string representing the binary equivalent of the decimal number.
    """
    if decimal_number < 0:
        raise ValueError("The number should be non-negative.")
    return bin(decimal_number)[2:]


#Connect to VPixx device
DPxOpen()

condition = True

value = DPxGetDinValue()


# Updated table 21-11-2024 tested
# RIGHT BOX
# 9  RED
# 7  GREEN
# 6 BLUE
# 8 Yellow

# Left Box
# 4 RED
# 2 Green
# 1 Blue
# 3 Yellow


# +-----------+--------------+-------------------+--------------------+-----------+
# |   Box     | Button Color |   Button States   | Response Number    | Offset Bit|
# +-----------+--------------+-------------------+--------------------+-----------+
# | Left Box  | Red          | 111111111111111000000001 | 9          | 0         |
# | Left Box  | Yellow       | 111111111111111000000010 | 8          | 1         |
# | Left Box  | Green        | 111111111111111000000100 | 7          | 2         |
# | Left Box  | Blue         | 111111111111111000001000 | 6          | 3         |
# | Right Box | Red          | 111111111111110000010000 | 4          | 5         |
# | Right Box | Yellow       | 111111111111110000100000 | 3          | 6         |
# | Right Box | Green        | 111111111111110001000000 | 2          | 7         |
# | Right Box | Blue         | 111111111111110010000000 | 1          | 8         |
# +-----------+--------------+-------------------+--------------------+-----------+


def getbutton():

    while True:
        DPxUpdateRegCache()
        value = DPxGetDinValue()
        #print(decimal_to_binary(value))
        value = decimal_to_binary(value)
        # The final 8 values should correspond to the button presses

        # Check if any relevant button is pressed
        if (value[-1] == '1' or value[-2] == '1' or value[-3] == '1' or
                value[-4] == '1' or value[-6] == '1' or value[-7] == '1' or
                value[-8] == '1' or value[-9] == '1'):

            # Extract button box states
            button_box = [
                int(value[-9 + i_but]) for i_but in range(9)
            ]

            # Find which button was pressed
            resp = [i + 1 for i, state in enumerate(button_box) if state == 1]


            # If only one button is pressed, return the result
            if len(resp) == 1:
                return resp[0]


response = getbutton()




while True:
    response = getbutton()
    print(' Button press', response)


DPxClose()
