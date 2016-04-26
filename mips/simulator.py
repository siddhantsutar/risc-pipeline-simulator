"""
ECE 4713 - Computer Architecture
Team: Architecture Dawgs
Authors: Siddhant Sutar, Veera Karri, Mabry Wilkinson
Description: Simulator for a 16-bit pipelined classic RISC processor.
"""

# Regex for interpretting machine code if formatted with spaces
import re

# For deep copying write buffer to read buffer
import copy

import os

""" MEMORY """
pc = 0
instruction_memory = []
register_file = [None] * 8
data_memory = [None] * 64 

# List of control signals passed to pipeline registers
control_signals = ('RegDst', 'ALUSrc', 'ALUOp2', 'ALUOp1', 'ALUOp0', 'MemRead', 'MemWrite', 'MemToReg', 'RegWrite')

# Keeps track of the number of clock cycles that have passed
clock_cycle = 0

"""
PIPELINE REGISTERS
IF/ID: stores 16-bit instruction, PC+2
ID/EX: stores EX, MEM, WB control signals + Read data 1, Read data 2, Rs (for forwarding), Rt, Rd, SEImm
EX/MEM: stores MEM, WB control signals + Zero, ALU Result, Read data 2, Rd
MEM/WB: stores WB control signals + ALU Result, Read data, Rd
"""

buffer_read = {'IF/ID': {'PC+2': None, 'Instruction': None}, \
           'ID/EX': {'RegDst': None, 'ALUSrc': None, 'ALUOp2': None, 'ALUOp1': None, 'ALUOp0': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'Read data 1': None, 'Read data 2': None, 'Rs': None, 'Rt': None, 'Rd': None, 'SEImm': None}, \
           'EX/MEM': {'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'Zero': None, 'ALU Result': None, 'Read data 2': None, 'Rd': None}, \
           'MEM/WB': {'MemToReg': None, 'RegWrite': None, 'ALU Result': None, 'Read data': None, 'Rd': None}}

buffer_write = {'IF/ID': {'PC+2': None, 'Instruction': None}, \
           'ID/EX': {'RegDst': None, 'ALUSrc': None, 'ALUOp2': None, 'ALUOp1': None, 'ALUOp0': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'Read data 1': None, 'Read data 2': None, 'Rs': None, 'Rt': None, 'Rd': None, 'SEImm': None}, \
           'EX/MEM': {'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'Zero': None, 'ALU Result': None, 'Read data 2': None, 'Rd': None}, \
           'MEM/WB': {'MemToReg': None, 'RegWrite': None, 'ALU Result': None, 'Read data': None, 'Rd': None}}

""" SIGNALS NOT STORED IN BUFFER """
hdu_signals = {'PCWrite': None, 'IF/IDWrite': None}
global_signals = {'PCSrc': None, 'IF.Flush': None}
branch_signals = {'Jump': None, 'Branch': None, 'Branch_NE': None}

""" CONTROL UNIT """
def init_signals(RegDst, ALUSrc, ALUOp2, ALUOp1, ALUOp0, Jump, Branch, Branch_NE, MemRead, MemWrite, MemToReg, RegWrite):
    buffer_write['ID/EX']['RegDst'] = RegDst
    buffer_write['ID/EX']['ALUSrc'] = ALUSrc
    buffer_write['ID/EX']['ALUOp2'] = ALUOp2
    buffer_write['ID/EX']['ALUOp1'] = ALUOp1
    buffer_write['ID/EX']['ALUOp0'] = ALUOp0
    buffer_write['ID/EX']['MemRead'] = MemRead
    buffer_write['ID/EX']['MemWrite'] = MemWrite
    buffer_write['ID/EX']['MemToReg'] = MemToReg
    buffer_write['ID/EX']['RegWrite'] = RegWrite

    branch_signals['Jump'] = Jump
    branch_signals['Branch'] = Branch
    branch_signals['Branch_NE'] = Branch_NE

def control_unit(i):
    if i == 0:
        init_signals(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
    else:
        opcode = buffer_read['IF/ID']['Instruction'][0:4]
        if opcode == "0000": #R-format
            init_signals(1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1)
        elif opcode == "0111": #lw
            init_signals(0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1)
        elif opcode == "1010": #sw
            init_signals("X", 1, 0, 0, 0, 0, 0, 0, 0, 1, "X", 0)

        # Branches - since all the control signals other than Branch/Branch_NE/Jump are 0, the subsequent stages will automatically insert NOPs (see nop() module)
        elif opcode == "0011": #beq
            init_signals("X", "X", "X", "X", "X", 0, 1, 0, "X", "X", "X", "X")
        elif opcode == "0100": #bne
            init_signals("X", "X", "X", "X", "X", 0, 0, 1, "X", "X", "X", "X")
        elif opcode == "0101": #j
            init_signals("X", "X", "X", "X", "X", 1, 0, 0, "X", "X", "X", "X")

        elif opcode == "0001": #addi
            init_signals(0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        elif opcode == "0010": #andi
            init_signals(0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
        elif opcode == "1000": #ori
            init_signals(0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1)
        elif opcode == "1001": #slti
            init_signals(0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1)

""" ARITHMETIC LOGIC UNIT and CONTROL """
def ALU_control():

    #F[2-0] will be F[0:3] in Python

    Funct = buffer_read['ID/EX']['SEImm'][13:16]
    F2 = int(Funct[0])
    F1 = int(Funct[1])
    F0 = int(Funct[2])
    not_F2 = int(not F2)
    not_F1 = int(not F1)
    not_F0 = int(not F0)

    ALUOp2 = int(buffer_read['ID/EX']['ALUOp2'])
    ALUOp1 = int(buffer_read['ID/EX']['ALUOp1'])
    ALUOp0 = int(buffer_read['ID/EX']['ALUOp0'])
    not_ALUOp2 = int(not ALUOp2)
    not_ALUOp1 = int(not ALUOp1)
    not_ALUOp0 = int(not ALUOp0)

    operation = ""

    operation += "0" if ALUOp2 + (not_ALUOp1 * not_ALUOp0) + (F2 * not_ALUOp0) == 0 else "1"
    operation += "0" if (ALUOp2 * ALUOp1) + (F1 * ALUOp1 * not_ALUOp0) == 0 else "1"
    operation += "0" if (ALUOp2 * ALUOp0) + (F0 * not_ALUOp2 * ALUOp1 * not_ALUOp0) == 0 else "1"

    return operation

def ALU(a, b):
    result = 0
    x = int(a, 2)
    if a[0] == "1":
        x = x - (1 << 16)
    y = int(b, 2)
    if b[0] == "1":
        y = y - (1 << 16)
    operation = ALU_control()
    if operation == "100":
        #print("add")
        result = x + y
    elif operation == "101":
        #print("and")
        result = x & y
    elif operation == "110":
        #print("or")
        result = x | y
    elif operation == "111":
        #print("slt")
        if x < y:
            result = 1
        else:
            result = 0
    elif operation == "000":
        #print("xor")
        result = x ^ y
    elif operation == "001":
        #print("sll")
        result = x << int(buffer_read['ID/EX']['Rt'], 2) #shift constant
    elif operation == "010":
        #print("srl")
        result = x >> int(buffer_read['ID/EX']['Rt'], 2) #shift constant
    elif operation == "011":
        #print("sub")
        result = x - y

    buffer_write['EX/MEM']['ALU Result'] = dec_to_bin(result)

"""
HAZARD DETECTION UNIT - Handles load-use data hazard and data hazards on branches
"""
def hazard_detection_unit():
    if buffer_read['ID/EX']['MemRead'] == 1 and (buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][7:10]): # Load use data hazard
        control_unit(0)
        hdu_signals['PCWrite'] = 0
        hdu_signals['IF/IDWrite'] = 0

    # Stalling for data hazard on branches
    elif (branch_signals['Branch'] == 1 or branch_signals['Branch_NE'] == 1) and (buffer_read['ID/EX']['RegWrite'] == 1) and (buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][7:10]):
        control_unit(0)
        hdu_signals['PCWrite'] = 0
        hdu_signals['IF/IDWrite'] = 0

    elif (branch_signals['Branch'] == 1 or branch_signals['Branch_NE'] == 1) and (buffer_read['ID/EX']['MemRead'] == 1) and (buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][7:10]):
        control_unit(0)
        hdu_signals['PCWrite'] = 0
        hdu_signals['IF/IDWrite'] = 0

    elif (branch_signals['Branch'] == 1 or branch_signals['Branch_NE'] == 1) and (buffer_read['EX/MEM']['MemRead'] == 1) and (buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][7:10]):
        control_unit(0)
        hdu_signals['PCWrite'] = 0
        hdu_signals['IF/IDWrite'] = 0

    else:
        control_unit(1)
        hdu_signals['PCWrite'] = 1
        hdu_signals['IF/IDWrite'] = 1
            
""" FORWARDING UNITS - Handle forwarding paths during regular data hazards (EX unit) and control hazards (ID unit) """
def forwarding_unit():

    # Initialize values in case forwarding is not required
    forwardA = buffer_read['ID/EX']['Read data 1']
    forwardB = buffer_read['ID/EX']['Read data 2']

    double_data = 0
    hazard = 0

    if buffer_read['MEM/WB']['Rd'] == buffer_read['EX/MEM']['Rd']:
        double_data = 1

    # EXE hazard
    if buffer_read['EX/MEM']['RegWrite'] == 1 and buffer_read['EX/MEM']['Rd'] == buffer_read['ID/EX']['Rs']:
        print("EXE hazard detected")
        hazard = 1
        forwardA = buffer_read['EX/MEM']['ALU Result']

    if buffer_read['EX/MEM']['RegWrite'] == 1 and buffer_read['EX/MEM']['Rd'] == buffer_read['ID/EX']['Rt']:
        print("EXE hazard detected")
        hazard = 1
        forwardB = buffer_read['EX/MEM']['ALU Result']

    # MEM hazard
    if not double_data and not hazard:
        if buffer_read['MEM/WB']['RegWrite'] == 1 and buffer_read['MEM/WB']['Rd'] == buffer_read['ID/EX']['Rs']:
            print("MEM hazard detected")
            if buffer_read['MEM/WB']['MemToReg'] == 0:
                forwardA = buffer_read['MEM/WB']['ALU Result']
            elif buffer_read['MEM/WB']['MemToReg'] == 1:
                forwardA = buffer_read['MEM/WB']['Read data']

        if buffer_read['MEM/WB']['RegWrite'] == 1 and buffer_read['MEM/WB']['Rd'] == buffer_read['ID/EX']['Rt']:
            print("MEM hazard detected")
            if buffer_read['MEM/WB']['MemToReg'] == 0:
                forwardB = buffer_read['MEM/WB']['ALU Result']
            elif buffer_read['MEM/WB']['MemToReg'] == 1:
                forwardB = buffer_read['MEM/WB']['Read data']

    return forwardA, forwardB

def ID_forwarding_unit():

    forwardA = buffer_write['ID/EX']['Read data 1']
    forwardB = buffer_write['ID/EX']['Read data 2']

    if branch_signals['Branch'] == 1 or branch_signals['Branch_NE'] == 1:
        double_data = 0
        hazard = 0

        if buffer_write['MEM/WB']['Rd'] == buffer_write['EX/MEM']['Rd']:
            double_data = 1

        # EXE hazard
        if buffer_write['EX/MEM']['RegWrite'] == 1 and buffer_write['EX/MEM']['Rd'] == buffer_write['ID/EX']['Rs']:
            print("EXE hazard detected")
            hazard = 1
            forwardA = buffer_write['EX/MEM']['ALU Result']

        if buffer_write['EX/MEM']['RegWrite'] == 1 and buffer_write['EX/MEM']['Rd'] == buffer_write['ID/EX']['Rt']:
            print("EXE hazard detected")
            hazard = 1
            forwardB = buffer_write['EX/MEM']['ALU Result']

        # MEM hazard
        if not double_data and not hazard:
            if buffer_write['MEM/WB']['RegWrite'] == 1 and buffer_write['MEM/WB']['Rd'] == buffer_write['ID/EX']['Rs']:
                print("MEM hazard detected")
                if buffer_write['MEM/WB']['MemToReg'] == 0:
                    forwardA = buffer_write['MEM/WB']['ALU Result']
                elif buffer_write['MEM/WB']['MemToReg'] == 1:
                    forwardA = buffer_write['MEM/WB']['Read data']

            if buffer_write['MEM/WB']['RegWrite'] == 1 and buffer_write['MEM/WB']['Rd'] == buffer_write['ID/EX']['Rt']:
                print("MEM hazard detected")
                if buffer_write['MEM/WB']['MemToReg'] == 0:
                    forwardB = buffer_write['MEM/WB']['ALU Result']
                elif buffer_write['MEM/WB']['MemToReg'] == 1:
                    forwardB = buffer_write['MEM/WB']['Read data']

    return forwardA, forwardB

""" WB STAGE """
def wb_stage():
    if not nop('MEM/WB'):
        if buffer_read['MEM/WB']['RegWrite'] == 1:
            if buffer_read['MEM/WB']['MemToReg'] == 0:
                register_file[int(buffer_read['MEM/WB']['Rd'], 2)] = buffer_read['MEM/WB']['ALU Result']
            elif buffer_read['MEM/WB']['MemToReg'] == 1:
                register_file[int(buffer_read['MEM/WB']['Rd'], 2)] = buffer_read['MEM/WB']['Read data']

    else:
        print("NOP in WB stage")

""" MEM STAGE """
def mem_stage():
    buffer_write['MEM/WB']['MemToReg'] = buffer_read['EX/MEM']['MemToReg']
    buffer_write['MEM/WB']['RegWrite'] = buffer_read['EX/MEM']['RegWrite']

    if not nop('EX/MEM'):
        global pc
        buffer_write['MEM/WB']['Rd'] = buffer_read['EX/MEM']['Rd']
        mem_addr = int(buffer_read['EX/MEM']['ALU Result'], 2)

        if buffer_read['EX/MEM']['MemRead'] == 1:
            buffer_write['MEM/WB']['Read data'] = data_memory[mem_addr] + data_memory[mem_addr+1]
        elif buffer_read['EX/MEM']['MemRead'] == 0:
            buffer_write['MEM/WB']['ALU Result'] = buffer_read['EX/MEM']['ALU Result']
            
        if buffer_read['EX/MEM']['MemWrite'] == 1:
            data_memory[mem_addr] = buffer_read['EX/MEM']['Read data 2'][0:8]
            data_memory[mem_addr+1] = buffer_read['EX/MEM']['Read data 2'][8:16]

    else:
        print("NOP in MEM stage")

""" EX STAGE """
def ex_stage():
    buffer_write['EX/MEM']['MemRead'] = buffer_read['ID/EX']['MemRead']
    buffer_write['EX/MEM']['MemWrite'] = buffer_read['ID/EX']['MemWrite']
    buffer_write['EX/MEM']['MemToReg'] = buffer_read['ID/EX']['MemToReg']
    buffer_write['EX/MEM']['RegWrite'] = buffer_read['ID/EX']['RegWrite']

    if not nop('ID/EX'):
        forwardA, forwardB = forwarding_unit()

        buffer_write['EX/MEM']['Read data 2'] = forwardB

        if buffer_read['ID/EX']['RegDst'] == 0:
            buffer_write['EX/MEM']['Rd'] = buffer_read['ID/EX']['Rt']
        elif buffer_read['ID/EX']['RegDst'] == 1:
            buffer_write['EX/MEM']['Rd'] = buffer_read['ID/EX']['Rd']


        if buffer_read['ID/EX']['ALUSrc'] == 0: #R-format instruction
            ALU(forwardA, forwardB)
        elif buffer_read['ID/EX']['ALUSrc'] == 1: 
            ALU(forwardA, buffer_read['ID/EX']['SEImm'])

    else:
        print("NOP in EX stage")

""" ID STAGE """         
def id_stage():
    if buffer_read['IF/ID']['Instruction'] == dec_to_bin(0):
        print("NOP in ID stage")
        control_unit(0) #do NOP

    else:
        hazard_detection_unit()
        buffer_write['ID/EX']['PC+2'] = buffer_read['IF/ID']['PC+2']
        buffer_write['ID/EX']['Read data 1'] = register_file[int(buffer_read['IF/ID']['Instruction'][4:7], 2)]
        buffer_write['ID/EX']['Read data 2'] = register_file[int(buffer_read['IF/ID']['Instruction'][7:10], 2)]
        buffer_write['ID/EX']['Rs'] = buffer_read['IF/ID']['Instruction'][4:7]
        buffer_write['ID/EX']['Rt'] = buffer_read['IF/ID']['Instruction'][7:10]
        buffer_write['ID/EX']['Rd'] = buffer_read['IF/ID']['Instruction'][10:13]
        buffer_write['ID/EX']['SEImm'] = sign_extend(buffer_read['IF/ID']['Instruction'][10:16])

        forwardA, forwardB = ID_forwarding_unit()

        if branch_signals['Jump'] == 1:
            global_signals['PCSrc'] = 2
            global_signals['IF.Flush'] = 1

        elif branch_signals['Branch'] == 1:
            if forwardA == forwardB:
                global_signals['PCSrc'] = 1
                global_signals['IF.Flush'] = 1

        elif branch_signals['Branch_NE'] == 1:
            if forwardA != forwardB:
                print("Branch taken")
                global_signals['PCSrc'] = 1
                global_signals['IF.Flush'] = 1

""" IF STAGE """
def if_stage():
    global pc

    if hdu_signals['IF/IDWrite']:    
        buffer_write['IF/ID']['PC+2'] = pc + 2
        buffer_write['IF/ID']['Instruction'] = instruction_memory[pc] + instruction_memory[pc+1]

    if global_signals['IF.Flush']:
        buffer_write['IF/ID']['Instruction'] = dec_to_bin(0)

    if hdu_signals['PCWrite']:
        if global_signals['PCSrc'] == 0:
            pc = buffer_write['IF/ID']['PC+2']
        elif global_signals['PCSrc'] == 1:
            pc = buffer_write['IF/ID']['PC+2'] + (int(buffer_write['ID/EX']['SEImm'], 2) * 2)
        elif global_signals['PCSrc'] == 2:
            pc = int(buffer_read['IF/ID']['Instruction'][4:16], 2) * 2

""" HELPER MODULES """

# Convert integer to 16-bit zero-extended binary string
def dec_to_bin(x):
    return str(bin(x)[2:]).zfill(16)

# Sign-extend binary string to 16-bit
def sign_extend(x):
    return str(x).rjust(16, x[0])

# Initialize memory
def init_memory():
    global instruction_memory, register_file, data_memory

    machine_code_file = open("machine_code.mips", "r")

    # Read machine code into instruction memory
    for each in machine_code_file:
        i = re.sub('\s+', '', each)
        instruction_memory.append(i[0:8])
        instruction_memory.append(i[8:16])
    
    register_file[0] = "0000000000000000"
    register_file[1] = "0000000000000101"
    register_file[2] = "0000000000010000"
    register_file[3] = "0000000000000000"
    register_file[4] = "0000000001000000"
    register_file[5] = "0001000000010000"
    register_file[6] = "0000000000001111"
    register_file[7] = "0000000011110000"

    data_memory[int(register_file[2], 2)+0] = "00000001" #01
    data_memory[int(register_file[2], 2)+1] = "00000001" #01

    data_memory[int(register_file[2], 2)+2] = "00000001" #01
    data_memory[int(register_file[2], 2)+3] = "00010000" #10

    data_memory[int(register_file[2], 2)+4] = "00000000" #00
    data_memory[int(register_file[2], 2)+5] = "00010001" #11

    data_memory[int(register_file[2], 2)+6] = "00000000" #00
    data_memory[int(register_file[2], 2)+7] = "11110000" #F0

    data_memory[int(register_file[2], 2)+8] = "00000000" #00
    data_memory[int(register_file[2], 2)+9] = "11111111" #FF

# Initialize signals at the beginning of clock cycle
def init_clock_cycle():
    hdu_signals['PCWrite'] = 1
    hdu_signals['IF/IDWrite'] = 1

    global_signals['PCSrc'] = 0
    global_signals['IF.Flush'] = 0

    branch_signals['Jump'] = None
    branch_signals['Branch'] = None
    branch_signals['Branch_NE'] = None

# Initialize write buffers at the beginning of clock cycle            
def init_buffer_write():
    k1 = buffer_write.keys()
    for i in k1:
        k2 = buffer_write[i].keys()
        for j in k2:
            buffer_write[i][j] = None

# Check if argument read buffer empty; if yes, the corresponding stage has no active instruction
def buffer_read_empty(b):
    return all(value == None for key, value in buffer_read[b].items())

# If returned true, insert stall cycle in the stage called from
def nop(b):
    return all(buffer_read[b][signal] == 0 or buffer_read[b][signal] == "X" for signal in control_signals if signal in buffer_read[b])

# Internal handler to check for simulation termination
def termination_check():
    return all(v2 == None for k1, v1 in buffer_read.items() for k2, v2 in buffer_read[k1].items())

# Generate output files
def generate_output(pre=""):

    directory = "output"
    if not os.path.exists(directory):
        os.makedirs(directory)

    rf_f = open("output/" + pre + str(clock_cycle) + "_register_file.txt", "w")
    dm_f = open("output/" + pre + str(clock_cycle) + "_data_memory.txt", "w")

    # If simulation not started, output the contents of instruction memory
    if not clock_cycle:
        im_f = open("output/" + str(clock_cycle) + "_instruction_memory.txt", "w")

        im_f.write("Address".ljust(15) + "Hex Value".ljust(15) + "Binary Value\n")
        for i in range(int(len(instruction_memory)/2)):
            j = instruction_memory[i*2] + instruction_memory[(i*2)+1]
            a = "{0:#0{1}x}".format((i*2)+4096, 6)
            h = "{0:#0{1}x}".format(int(j, 2), 6)
            b = j[:4] + " " + j[4:8] + " " + j[8:12] + " " + j[12:]
            im_f.write(a.ljust(15) + h.ljust(15) + b + "\n")

    rf_f.write("Register #".ljust(15) + "Hex Value".ljust(15) + "Binary Value\n")
    for i in range(len(register_file)):
        j = register_file[i]
        r = str("$" + str(i))
        h = "{0:#0{1}x}".format(int(j, 2), 6)
        b = j[:4] + " " + j[4:8] + " " + j[8:12] + " " + j[12:]
        rf_f.write(r.ljust(15) + h.ljust(15) + b + "\n")

    dm_f.write("Address".ljust(15) + "Hex Value".ljust(15) + "Binary Value\n")
    for i in range(int(len(data_memory)/2)):
        a = "{0:#0{1}x}".format(i*2, 6)
        if data_memory[i*2]:
            j = data_memory[i*2] + data_memory[(i*2)+1]
            h = "{0:#0{1}x}".format(int(j, 2), 6)
            b = j[:4] + " " + j[4:8] + " " + j[8:12] + " " + j[12:]

        else:
            h = "NaN"
            b = "NaN"

        dm_f.write(a.ljust(15) + h.ljust(15) + b + "\n")

# Simulator function
def simulate():
    global buffer_read, clock_cycle, pc
    init_memory()
    generate_output()
    while 1:
        if pc == 70:
            generate_output("loop") #Generate output at the end of the loop
        clock_cycle += 1
        print("--- Cycle " + str(clock_cycle) + "---")
        print(pc)
        generate_output()
        init_clock_cycle()
        init_buffer_write()
        if not buffer_read_empty("MEM/WB"):
            print("WB stage")
            wb_stage()
        if not buffer_read_empty("EX/MEM"):
            print("MEM stage")
            mem_stage()
        if not buffer_read_empty("ID/EX"):
            print("EX stage")
            ex_stage()
        if not buffer_read_empty("IF/ID"):
            print("ID stage")
            id_stage()
        if pc < len(instruction_memory):
            print("IF stage")
            if_stage()
        buffer_read = copy.deepcopy(buffer_write)
        if termination_check():
            break
    print("--- End of simulation ---")

# Start simulation
simulate()
