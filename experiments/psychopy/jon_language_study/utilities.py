from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue


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


def getbutton():

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