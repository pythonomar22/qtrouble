from termcolor import colored
import sys
import random



def colorPrint(input, equalRed, equalBlue, equalGreen, equalYellow, toPrint):
    #can use this to look at first (ex. "R1") or modify however
    input = str(input)
    equalRed = str(equalRed)
    equalGreen = str(equalGreen)
    equalBlue = str(equalBlue)
    equalYellow = str(equalYellow)


    if input[0] == equalRed:
            toPrint = colors.RED + toPrint
    elif input[0] == equalGreen:
        toPrint = colors.GREEN + toPrint
    elif input[0] == equalBlue:
        toPrint = colors.BLUE + toPrint
    elif input[0] == equalYellow:
        toPrint = colors.YELLOW + toPrint
    return toPrint

class colors: # You may need to change color settings
    #add this before to inverse: "\033[;7m"
    RED = "\033[1;31m"  
    ENDC = '\033[m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'

def print_game_board(array):
    # Check if the array has enough elements for a square with 7 on each side
    if len(array) != 28:
        print("Invalid array length.")
        return

    # Print top row
    top_row = array[:7]
    right_side = array[7:14]
    left_side = array[21:28][::-1]
    bot_row = array[14:21][::-1]
    #print("["+ "]   [".join(map(str, top_row)) + "]")
    for index in range(len(top_row)):
        toPrint = "[" + str(top_row[index]) + "]   " + colors.ENDC
        toPrint = colorPrint(top_row[index], "R", "B", "G", "Y", toPrint)
       
        print(toPrint, end = "")
        
    print("\n")

    for index in range(len(left_side)):
        output1 = "[" + str(left_side[index]) + "]" + colors.ENDC
        
        output1 = colorPrint(left_side[index], "R", "B", "G", "Y", output1)
        print(output1, end = "")
        print("".ljust(38), end = "")
        output2 = "[" + str(right_side[index]) + "]" + colors.ENDC + "\n"
        output2 = colorPrint(right_side[index], "R", "B", "G", "Y", output2)
        print(output2)
    
    for index in range(len(bot_row)):
        toPrint = "[" + str(bot_row[index]) + "]   " + colors.ENDC

        toPrint = colorPrint(bot_row[index], "R", "B", "G", "Y", toPrint)
        print(toPrint, end = "")
        
    print("\n")


# Example usage with an array of length 28
my_array = [random.choice(["RR", "BB", "YY", "GG"]) for i in range(28)]
print_game_board(my_array)
