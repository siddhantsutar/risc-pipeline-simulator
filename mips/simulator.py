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

""" MEMORY """
pc = 0
instruction_memory = []
register_file = ["0000000000000000", "0000000000000001", "0000000000000010", "0000000000000011", "0000000000000100", "0000000000000101", "0000000000000000", None]
data_memory = [] * 64 

machine_code_file = open("test.mips", "r")

# Read machine code into instruction memory
for each in machine_code_file:
    i = re.sub('\s+', '', each)
    instruction_memory.append(i[0:8])
    instruction_memory.append(i[8:16])

# List of control signals passed to pipeline registers
control_signals = ('RegDst', 'ALUSrc', 'ALUOp2', 'ALUOp1', 'ALUOp0', 'MemRead', 'MemWrite', 'MemToReg', 'RegWrite') 

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
    buffer_write['ID/EX']['ALUOp1'] = ALUOp2
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
        init_signals(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
    else:
        opcode = buffer_read['IF/ID']['Instruction'][0:4]
        if opcode == "0000": #R-format
            init_signals(1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1)
        elif opcode == "0111": #lw
            init_signals(0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1)
        elif opcode == "1010": #sw
            init_signals("X", 1, 0, 0, 0, 0, 0, 0, 0, 1, "X", 0)
        elif opcode == "0011": #beq
            init_signals("X", 0, 0, 0, 1, 0, 1, 0, 0, 0, "X", 0)

        elif opcode == "0001": #addi
            init_signals(0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1)

""" ARITHMETIC LOGIC UNIT and CONTROL """
def ALU_control():

    #F[2-0] will be F[0:3] in Python

    Funct = buffer_read['ID/EX']['SEImm'][13:16]
    ALUOp1 = int(buffer_read['ID/EX']['ALUOp1'])
    ALUOp0 = int(buffer_read['ID/EX']['ALUOp0'])
    ALUOp1_NOT = int(not ALUOp1)
    ALUOp0_NOT = int(not ALUOp0)
    operation = ""

    operation += str((ALUOp1_NOT * ALUOp0) + (ALUOp1 * ALUOp0_NOT * int(Funct[0])))
    operation += str(ALUOp1_NOT + (ALUOp1 * ALUOp0_NOT * int(Funct[1])))
    operation += str(ALUOp1 * ALUOp0_NOT * int(Funct[2]))

    print(ALUOp1, ALUOp0, Funct)
    return operation

def ALU(a, b):
    if ALU_control() == "010":
        buffer_write['EX/MEM']['ALU Result'] = dec_to_bin(int(a, 2) + int(b, 2))

"""
HAZARD DETECTION UNIT - Handles load-use data hazard and data hazards on branches
"""
def hazard_detection_unit():    
    if buffer_read['ID/EX']['MemRead'] == 1:
        if buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][7:10]: # Load use data hazard
            control_unit(0)
            hdu_signals['PCWrite'] = 0
            hdu_signals['IF/IDWrite'] = 0

    # Stalling for data hazard on branches
    elif branch_signals['Branch'] == 1 or branch_signals['Branch_NE'] == 1:
        if buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rd'] == buffer_read['IF/ID']['Instruction'][7:10]:
            if buffer_read['ID/EX']['RegWrite'] == 1:
                control_unit(0)
                hdu_signals['PCWrite'] = 0
                hdu_signals['IF/IDWrite'] = 0

        if buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][7:10]:
            if buffer_read['ID/EX']['MemRead'] == 1:
                control_unit(0)
                hdu_signals['PCWrite'] = 0
                hdu_signals['IF/IDWrite'] = 0

            if buffer_read['EX/MEM']['MemRead'] == 1:
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
        buffer_write['EX/MEM']['Read data 2'] = buffer_read['ID/EX']['Read data 2']

        if buffer_read['ID/EX']['RegDst'] == 0:
            buffer_write['EX/MEM']['Rd'] = buffer_read['ID/EX']['Rt']
        elif buffer_read['ID/EX']['RegDst'] == 1:
            buffer_write['EX/MEM']['Rd'] = buffer_read['ID/EX']['Rd']

        forwardA, forwardB = forwarding_unit()

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
        buffer_write['ID/EX']['SEImm'] = buffer_read['IF/ID']['Instruction'][10:16].zfill(16)
        print(buffer_read['IF/ID']['Instruction'])

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
            pc = buffer_write['IF/ID']['PC+2'] + int(buffer_write['ID/EX']['SEImm'], 2)
        elif global_signals['PCSrc'] == 2:
            pc = int(buffer_read['IF/ID']['Instruction'][4:16], 2) * 2

""" HELPER MODULES """
# Convert integer to 16-bit sign-extended binary string
def dec_to_bin(x):
    return str(bin(x)[2:]).zfill(16)

# If returned true, insert stall cycle in the stage called from
def nop(b):
    return all(buffer_read[b][signal] == 0 for signal in control_signals if signal in buffer_read[b])

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

# Internal handler to check for simulation termination
def termination_check():
    return all(v2 == None for k1, v1 in buffer_read.items() for k2, v2 in buffer_read[k1].items())

# Simulator function
def simulate():
    global buffer_read
    print(len(instruction_memory))
    i = 1
    while 1:
        print("--- Cycle " + str(i) + "---")
        print(register_file)
        print(pc)
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
        i += 1
    print("--- End of simulation ---")
    print(register_file)

# Start simulation
simulate()
