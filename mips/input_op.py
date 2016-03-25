"""
Architecture Dawgs
Author(s): Mabry Wilkinson, Veera Karri
input_op.py
Description: Input operations for the simulator.
"""


# instruction memory is an ever growing list that will store the
# instructions we will be performing throughout our program

instruction_memory = []


# Machine_code_file is the file that contains the machine code for that
# our program will read from and execute

machine_code_file = open("machine_code.mips", "r")

# here we are ensuring that our machine code instructions are at least 16 bits
# once we determine that they are then we append them to instruction_memory

for each in machine_code_file:
    if len(each) != 16:
        print("exit")

    else:
        instruction_memory.append(each)

# here we are initializing a list of size 8 that stores None or null
# we will update this as the program executes

memory = [None]** 8

# here we clear our memory list so that we do not have things loaded into
# memory before the program begins execution

for i in range (len(memory)):
    memory[i] = ["","","",""]

# our register_file is a list that currently is of size 8
# since we have 8 registers we decided that we could access them
# through indexing the list

register_file = ["","","","","","","",""]

# pc is the program counter

pc = 0

