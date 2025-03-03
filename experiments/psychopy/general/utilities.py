from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue


trigger_channels_dictionary = {
    224: 4,
    225: 16,
    226: 64,
    227: 256,
    228: 1024,
    229: 4096,
    230: 16384,
    231: 65536
}

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


def getbutton(buttons=None):
    # buttons is an array or None
    # if buttons is an array it contains the code number of the button we want
    # Updated table 13-01-2025 tested

    # RIGHT BOX

        # Red button:
            # return response = 9   (this is the value returned by the getbutton or listenbutton function)
            # buttons array set to = 1     (add this number to the buttons array in order to listen to it)

        # Green button:
            # return response = 7
            # listen to = 3

        # Blue button:
            # return response = 6
            # listen to = 4

        # Yellow button:
            # return response = 8
            # listen to = 2


    # Left Box

        # Red button:
            # return response = 4
            # listen to = 6

        # Green button:
            # return response = 2
            # listen to = 8

        # Blue button:
            # return response = 1
            # listen to = 9

        # Yellow button:
            # return response = 3
            # listen to = 7

    if buttons == None:

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
    else:

        neg_buttons = [-x for x in buttons]
        print(neg_buttons)
        while True:

            DPxUpdateRegCache()
            value = DPxGetDinValue()
            # print(decimal_to_binary(value))
            value = decimal_to_binary(value)
            # The final 8 values should correspond to the button presses
            #print(value)
            if any(value[x] == '1' for x in neg_buttons):

                # Extract button box states
                button_box = [
                    int(value[-9 + i_but]) for i_but in range(9)
                ]

                # Find which button was pressed
                resp = [i + 1 for i, state in enumerate(button_box) if state == 1]

                # If only one button is pressed, return the result
                if len(resp) == 1:
                    return resp[0]



def listenbutton(keycode):

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

    # Keycode is one of the above numbers that correspond to the button we want to listen to

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
            if len(resp) == 1 and resp[0]==keycode:
                return resp[0]

