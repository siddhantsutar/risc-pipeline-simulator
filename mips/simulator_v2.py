import re
import csv
import copy

machine_code_file = open("test.mips", "r")

pc = 0
PCWrite = 1
instruction_memory = []

# Registers $6 and $7 will be reserved as base addresses for referencing data memory
register_file = ["0000000000000000", "0000000000000001", "0000000000000010", "0000000000000011", "0000000000000100", "0000000000000101", "0000000000000000", None]

"""
In our implementation, each word is 16 bits (2 bytes) long. MIPS is Big Endian, so we will store the most and least significant bytes
at indices i and i+1 respectively. Typically, our addresses would be range from 0 to 65535 (2**16 - 1), but we do not need to include
these many since we are supposed to output the data memory.
"""
data_memory = [] * 64 

for each in machine_code_file:
    i = re.sub('\s+', '', each)
    instruction_memory.append(i[0:8])
    instruction_memory.append(i[8:16])

"""
PIPELINE REGISTERS (MEM signals also include Jump and Branch_NE)
IF/ID: stores 16-bit instruction, PC+2
ID/EX: stores EX, MEM, WB control signals + JumpAddr, PC+2, Read data 1, Read data 2, Rs (for forwarding), Rt, Rd, SEImm
EX/MEM: stores MEM, WB control signals + JumpAddr, BranchAdder, Zero, ALU Result, Read data 2, Rd
MEM/WB: stores WB control signals + ALU Result, Read data, Rd
"""

control_signals = ('RegDst', 'ALUSrc', 'ALUOp1', 'ALUOp0', 'Jump', 'Branch', 'Branch_NE', 'MemRead', 'MemWrite', 'MemToReg', 'RegWrite')

buffer_read = {'IF/ID': {'PC+2': None, 'Instruction': None}, \
           'ID/EX': {'RegDst': None, 'ALUSrc': None, 'ALUOp1': None, 'ALUOp0': None, 'Jump': None, 'Branch': None, 'Branch_NE': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None,  'JumpAddr': None, 'PC+2': None, 'Read data 1': None, 'Read data 2': None, 'Rs': None, 'Rt': None, 'Rd': None, 'SEImm': None}, \
           'EX/MEM': {'Jump': None, 'Branch': None, 'Branch_NE': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'JumpAddr': None, 'BranchAdder': None, 'Zero': None, 'ALU Result': None, 'Read data 2': None, 'Rd': None}, \
           'MEM/WB': {'MemToReg': None, 'RegWrite': None, 'ALU Result': None, 'Read data': None, 'Rd': None}}

buffer_write = {'IF/ID': {'PC+2': None, 'Instruction': None}, \
           'ID/EX': {'RegDst': None, 'ALUSrc': None, 'ALUOp1': None, 'ALUOp0': None, 'Jump': None, 'Branch': None, 'Branch_NE': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None,  'JumpAddr': None, 'PC+2': None, 'Read data 1': None, 'Read data 2': None, 'Rs': None, 'Rt': None, 'Rd': None, 'SEImm': None}, \
           'EX/MEM': {'Jump': None, 'Branch': None, 'Branch_NE': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'JumpAddr': None, 'BranchAdder': None, 'Zero': None, 'ALU Result': None, 'Read data 2': None, 'Rd': None}, \
           'MEM/WB': {'MemToReg': None, 'RegWrite': None, 'ALU Result': None, 'Read data': None, 'Rd': None}}

def init_signals(RegDst, ALUSrc, ALUOp1, ALUOp0, Jump, Branch, Branch_NE, MemRead, MemWrite, MemToReg, RegWrite):
    buffer_write['ID/EX']['RegDst'] = RegDst
    buffer_write['ID/EX']['ALUSrc'] = ALUSrc
    buffer_write['ID/EX']['ALUOp1'] = ALUOp1
    buffer_write['ID/EX']['ALUOp0'] = ALUOp0
    buffer_write['ID/EX']['Jump'] = Jump
    buffer_write['ID/EX']['Branch'] = Branch
    buffer_write['ID/EX']['Branch_NE'] = Branch_NE
    buffer_write['ID/EX']['MemRead'] = MemRead
    buffer_write['ID/EX']['MemWrite'] = MemWrite
    buffer_write['ID/EX']['MemToReg'] = MemToReg
    buffer_write['ID/EX']['RegWrite'] = RegWrite

def nop(b):
    return all(buffer_read[b][signal] == 0 for signal in control_signals if signal in buffer_read[b])


def hazard_detection_unit():
    global PCWrite
    
    if buffer_read['ID/EX']['MemRead'] == 1:
        if buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][4:7] or buffer_read['ID/EX']['Rt'] == buffer_read['IF/ID']['Instruction'][7:10]: # Load use data hazard
            control_unit(0)
            PCWrite = 0

    else:
        control_unit(1)
        PCWrite = 1
            

def control_unit(i):
    if i == 0:
        init_signals(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
    else:
        opcode = buffer_read['IF/ID']['Instruction'][0:4]
        if opcode == "0000": #R-format
            init_signals(1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1)
        elif opcode == "0111" : #lw
            init_signals(0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1)
        elif opcode == "1010" : #sw
            init_signals("X", 1, 0, 0, 0, 0, 0, 0, 1, "X", 0)
        elif opcode == "0011" : #beq
            init_signals("X", 0, 0, 1, 0, 1, 0, 0, 0, "X", 0)      


def forwarding_unit():

    # Initialize values in case forwarding is not required
    forwardA = buffer_read['ID/EX']['Read data 1']
    forwardB = buffer_read['ID/EX']['Read data 2']

    exe = 0

    # EXE hazard
    if buffer_read['EX/MEM']['RegWrite'] == 1 and buffer_read['EX/MEM']['Rd'] == buffer_read['ID/EX']['Rs']:
        print("EXE hazard detected")
        exe = 1
        forwardA = buffer_read['EX/MEM']['ALU Result']

    if buffer_read['EX/MEM']['RegWrite'] == 1 and buffer_read['EX/MEM']['Rd'] == buffer_read['ID/EX']['Rt']:
        print("EXE hazard detected")
        exe = 1
        forwardB = buffer_read['EX/MEM']['ALU Result']

    # MEM hazard
    if buffer_read['MEM/WB']['RegWrite'] == 1 and buffer_read['MEM/WB']['Rd'] == buffer_read['ID/EX']['Rs'] and not exe:
        print("MEM hazard detected")
        if buffer_read['MEM/WB']['MemToReg'] == 0:
            forwardA = buffer_read['MEM/WB']['ALU Result']
        elif buffer_read['MEM/WB']['MemToReg'] == 1:
            forwardA = buffer_read['MEM/WB']['Read data']

    if buffer_read['MEM/WB']['RegWrite'] == 1 and buffer_read['MEM/WB']['Rd'] == buffer_read['ID/EX']['Rt'] and not exe:
        print("MEM hazard detected")
        if buffer_read['MEM/WB']['MemToReg'] == 0:
            forwardB = buffer_read['MEM/WB']['ALU Result']
        elif buffer_read['MEM/WB']['MemToReg'] == 1:
            forwardB = buffer_read['MEM/WB']['Read data']

    return forwardA, forwardB

def ALU_control():
    if buffer_read['ID/EX']['ALUOp1'] == 1 and buffer_read['ID/EX']['ALUOp0'] == 0:
        if buffer_read['ID/EX']['SEImm'][13:16] == "000":
            return "operation"
            #find out the operation using buffer_read['ID/EX']['ALUOp1'], buffer_read['ID/EX']['ALUOp0'] and buffer_read['ID/EX']['SEImm'][13:16]
            #do relevant operation on a and b
            #store in buffer_write['EX/MEM']['ALU Result'], buffer_write['EX/MEM']['Zero']

def ALU(a, b):
    if ALU_control() == "operation":
        buffer_write['EX/MEM']['ALU Result'] = format(int(a, 2) + int(b, 2), '016b')

def wb_stage():

    if not nop('MEM/WB'):
        if buffer_read['MEM/WB']['RegWrite'] == 1:
            if buffer_read['MEM/WB']['MemToReg'] == 0:
                register_file[int(buffer_read['MEM/WB']['Rd'], 2)] = buffer_read['MEM/WB']['ALU Result']
            elif buffer_read['MEM/WB']['MemToReg'] == 1:
                register_file[int(buffer_read['MEM/WB']['Rd'], 2)] = buffer_read['MEM/WB']['Read data']
        
def mem_stage():

    buffer_write['MEM/WB']['MemToReg'] = buffer_read['EX/MEM']['MemToReg']
    buffer_write['MEM/WB']['RegWrite'] = buffer_read['EX/MEM']['RegWrite']

    if not nop('EX/MEM'):
        global pc
        buffer_write['MEM/WB']['Rd'] = buffer_read['EX/MEM']['Rd']

        if buffer_read['EX/MEM']['Jump'] == 1:
            pc = buffer_read['EX/MEM']['JumpAddr']
            
        # TO-DO
        if buffer_read['EX/MEM']['Branch'] == 1 and buffer_read['EX/MEM']['Zero'] == 1:
            pc = buffer_read['EX/MEM']['BranchAdder']

        if buffer_read['EX/MEM']['MemRead'] == 1:
            buffer_write['MEM/WB']['Read data'] = data_memory[int(buffer_read['EX/MEM']['ALU Result'], 2)]
        elif buffer_read['EX/MEM']['MemRead'] == 0:
            buffer_write['MEM/WB']['ALU Result'] = buffer_read['EX/MEM']['ALU Result']
            
        # TO-DO        
        if buffer_read['EX/MEM']['MemWrite'] == 1:
            data_memory[int(buffer_read['EX/MEM']['ALU Result'], 2)] = buffer_read['EX/MEM']['Read data 2']

def ex_stage():
    buffer_write['EX/MEM']['Jump'] = buffer_read['ID/EX']['Jump']
    buffer_write['EX/MEM']['Branch'] = buffer_read['ID/EX']['Branch']
    buffer_write['EX/MEM']['Branch_NE'] = buffer_read['ID/EX']['Branch_NE']
    buffer_write['EX/MEM']['MemRead'] = buffer_read['ID/EX']['MemRead']
    buffer_write['EX/MEM']['MemWrite'] = buffer_read['ID/EX']['MemWrite']
    buffer_write['EX/MEM']['MemToReg'] = buffer_read['ID/EX']['MemToReg']
    buffer_write['EX/MEM']['RegWrite'] = buffer_read['ID/EX']['RegWrite']

    if not nop('ID/EX'):
        buffer_write['EX/MEM']['JumpAddr'] = buffer_read['ID/EX']['JumpAddr']
        buffer_write['EX/MEM']['Read data 2'] = buffer_read['ID/EX']['Read data 2']

        #Check for overflow
        buffer_write['EX/MEM']['BranchAdder'] = buffer_read['ID/EX']['PC+2'] + (int(buffer_read['ID/EX']['SEImm'], 2))

        if buffer_read['ID/EX']['RegDst'] == 0:
            buffer_write['EX/MEM']['Rd'] = buffer_read['ID/EX']['Rt']
        elif buffer_read['ID/EX']['RegDst'] == 1:
            buffer_write['EX/MEM']['Rd'] = buffer_read['ID/EX']['Rd']

        forwardA, forwardB = forwarding_unit()

        if buffer_read['ID/EX']['ALUSrc'] == 0: #R-format instruction
            ALU(forwardA, forwardB)
        elif buffer_read['ID/EX']['ALUSrc'] == 1: 
            ALU(forwardA, buffer_read['ID/EX']['SEImm'])
                        
def id_stage():
    hazard_detection_unit()
    buffer_write['ID/EX']['JumpAddr'] = int(buffer_read['IF/ID']['Instruction'][4:16], 2) * 2
    buffer_write['ID/EX']['PC+2'] = buffer_read['IF/ID']['PC+2']
    buffer_write['ID/EX']['Read data 1'] = register_file[int(buffer_read['IF/ID']['Instruction'][4:7], 2)]
    buffer_write['ID/EX']['Read data 2'] = register_file[int(buffer_read['IF/ID']['Instruction'][7:10], 2)]
    buffer_write['ID/EX']['Rs'] = buffer_read['IF/ID']['Instruction'][4:7]
    buffer_write['ID/EX']['Rt'] = buffer_read['IF/ID']['Instruction'][7:10]
    buffer_write['ID/EX']['Rd'] = buffer_read['IF/ID']['Instruction'][10:13]
    buffer_write['ID/EX']['SEImm'] = format(int(buffer_read['IF/ID']['Instruction'][10:16]), '016b')
    
def if_stage():
    global pc
    buffer_write['IF/ID']['PC+2'] = pc + 2
    buffer_write['IF/ID']['Instruction'] = instruction_memory[pc] + instruction_memory[pc+1]
    if PCWrite:
        pc += 2 #At the end of the clock cycle, write to the program counter register

def init_buffer_write():
    k1 = buffer_write.keys()
    for i in k1:
        k2 = buffer_write[i].keys()
        for j in k2:
            buffer_write[i][j] = None

def buffer_read_empty(b):
    return all(value == None for key, value in buffer_read[b].items())

def termination_check():
    return all(v2 == None for k1, v1 in buffer_read.items() for k2, v2 in buffer_read[k1].items())

def simulate():
    global buffer_read
    i = 1
    while 1:
        print("--- Cycle " + str(i) + "---")
        print(register_file)
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

simulate()
