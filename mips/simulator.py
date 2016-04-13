import re
import csv

machine_code_file = open("test.mips", "r")

pc = 0
instruction_memory = []

# Registers $6 and $7 will be reserved as base addresses for referencing data memory
register_file = ["0000000000000000", "0000000000000001", "0000000000000010", "0000000000000011", "0000000000000100", None, None, None]

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
IF/ID: stores 16-bit instruction + PC+2
ID/EX: stores EX, MEM, WB control signals + JumpAddr, PC+2, Read data 1, Read data 2, Rt, Rd, SEImm
EX/MEM: stores MEM, WB control signals + JumpAddr, BranchAdder, Zero, ALU Result, Read data 2, Write register
MEM/WB: stores WB control signals + ALU Result, Read data, Write register
"""

buffer = {'IF/ID': {'PC+2': None, 'Instruction': None}, \
           'ID/EX': {'RegDst': None, 'ALUSrc': None, 'ALUOp1': None, 'ALUOp0': None, 'Jump': None, 'Branch': None, 'Branch_NE': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None,  'JumpAddr': None, 'PC+2': None, 'Read data 1': None, 'Read data 2': None, 'Rt': None, 'Rd': None, 'SEImm': None}, \
           'EX/MEM': {'Jump': None, 'Branch': None, 'Branch_NE': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'JumpAddr': None, 'BranchAdder': None, 'Zero': None, 'ALU Result': None, 'Read data 2': None, 'Write register': None}, \
           'MEM/WB': {'MemToReg': None, 'RegWrite': None, 'ALU Result': None, 'Read data': None, 'Write register': None}}

def init_signals(RegDst, ALUSrc, ALUOp1, ALUOp0, Jump, Branch, Branch_NE, MemRead, MemWrite, MemToReg, RegWrite):
    buffer['ID/EX']['RegDst'] = RegDst
    buffer['ID/EX']['ALUSrc'] = ALUSrc
    buffer['ID/EX']['ALUOp1'] = ALUOp1
    buffer['ID/EX']['ALUOp0'] = ALUOp0
    buffer['ID/EX']['Jump'] = Jump
    buffer['ID/EX']['Branch'] = Branch
    buffer['ID/EX']['Branch_NE'] = Branch_NE
    buffer['ID/EX']['MemRead'] = MemRead
    buffer['ID/EX']['MemWrite'] = MemWrite
    buffer['ID/EX']['MemToReg'] = MemToReg
    buffer['ID/EX']['RegWrite'] = RegWrite

def control_unit(opcode):
    if opcode == "0000": #R-format
        init_signals(1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1)
    elif opcode == "0111" : #lw
        init_signals(0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1)
    elif opcode == "1010" : #sw
        init_signals("X", 1, 0, 0, 0, 0, 0, 0, 1, "X", 0)
    elif opcode == "0011" : #beq
        init_signals("X", 0, 0, 1, 0, 1, 0, 0, 0, "X", 0)

def ALU_control():
    if buffer['ID/EX']['ALUOp1'] == 1 and buffer['ID/EX']['ALUOp0'] == 0:
        if buffer['ID/EX']['SEImm'][13:16] == "000":
            return "operation"
            #find out the operation using buffer['ID/EX']['ALUOp1'], buffer['ID/EX']['ALUOp0'] and buffer['ID/EX']['SEImm'][13:16]
            #do relevant operation on a and b
            #store in buffer['EX/MEM']['ALU Result'], buffer['EX/MEM']['Zero']

def ALU(b):
    a = buffer['ID/EX']['Read data 1'] # Read data 1
    if ALU_control() == "operation":
        buffer['EX/MEM']['ALU Result'] = format(int(a, 2) + int(b, 2), '016b')

def wb_stage():
    if buffer['MEM/WB']['RegWrite'] == 1:
        if buffer['MEM/WB']['MemToReg'] == 0:
            register_file[int(buffer['MEM/WB']['Write register'], 2)] = buffer['MEM/WB']['ALU Result']
        elif buffer['MEM/WB']['MemToReg'] == 1:
            register_file[int(buffer['MEM/WB']['Write register'], 2)] = buffer['MEM/WB']['Read data']

    clear_buffer("MEM/WB")
                        
        
def mem_stage():
    global pc
    buffer['MEM/WB']['MemToReg'] = buffer['EX/MEM']['MemToReg']
    buffer['MEM/WB']['RegWrite'] = buffer['EX/MEM']['RegWrite']
    buffer['MEM/WB']['Write register'] = buffer['EX/MEM']['Write register']

    if buffer['EX/MEM']['Jump'] == 1:
        pc = buffer['MEM/WB']['JumpAddr']
        
    # TO-DO
    if buffer['EX/MEM']['Branch'] == 1 and buffer['EX/MEM']['Zero'] == 1:
        pc = buffer['MEM/WB']['BranchAdder']

    if buffer['EX/MEM']['MemRead'] == 1:
        buffer['MEM/WB']['Read data'] = data_memory[int(buffer['EX/MEM']['ALU Result'], 2)]
    else:
        buffer['MEM/WB']['ALU Result'] = buffer['EX/MEM']['ALU Result']
        
    # TO-DO        
    if buffer['EX/MEM']['MemWrite'] == 1:
        data_memory[int(buffer['EX/MEM']['ALU Result'], 2)] = buffer['EX/MEM']['Read data 2']

    clear_buffer("EX/MEM")

def ex_stage():
    buffer['EX/MEM']['Branch'] = buffer['ID/EX']['Branch']
    buffer['EX/MEM']['MemRead'] = buffer['ID/EX']['MemRead']
    buffer['EX/MEM']['MemWrite'] = buffer['ID/EX']['MemWrite']
    buffer['EX/MEM']['MemToReg'] = buffer['ID/EX']['MemToReg']
    buffer['EX/MEM']['RegWrite'] = buffer['ID/EX']['RegWrite']

    buffer['EX/MEM']['JumpAddr'] = buffer['ID/EX']['JumpAddr']
    buffer['EX/MEM']['Read data 2'] = buffer['ID/EX']['Read data 2']

    #Check for overflow
    buffer['EX/MEM']['BranchAdder'] = buffer['ID/EX']['PC+2'] + (int(buffer['ID/EX']['SEImm'], 2))

    if buffer['ID/EX']['RegDst'] == 0:
        buffer['EX/MEM']['Write register'] = buffer['ID/EX']['Rt']
    elif buffer['ID/EX']['RegDst'] == 1:
        buffer['EX/MEM']['Write register'] = buffer['ID/EX']['Rd']

    if buffer['ID/EX']['ALUSrc'] == 0: #R-format instruction
        ALU(buffer['ID/EX']['Read data 2'])
    elif buffer['ID/EX']['ALUSrc'] == 1: 
        ALU(buffer['ID/EX']['SEImm'])

    clear_buffer("ID/EX")
                        
def id_stage():
    buffer['ID/EX']['JumpAddr'] = int(buffer['IF/ID']['Instruction'][4:16], 2) * 2
    buffer['ID/EX']['PC+2'] = buffer['IF/ID']['PC+2']
    buffer['ID/EX']['Read data 1'] = register_file[int(buffer['IF/ID']['Instruction'][4:7], 2)]
    buffer['ID/EX']['Read data 2'] = register_file[int(buffer['IF/ID']['Instruction'][7:10], 2)]
    buffer['ID/EX']['Rt'] = buffer['IF/ID']['Instruction'][7:10]
    buffer['ID/EX']['Rd'] = buffer['IF/ID']['Instruction'][10:13]
    buffer['ID/EX']['SEImm'] = format(int(buffer['IF/ID']['Instruction'][10:16]), '016b')
    control_unit(buffer['IF/ID']['Instruction'][0:4])
    clear_buffer("IF/ID")
        
def if_stage():
    global pc
    buffer['IF/ID']['PC+2'] = pc + 2
    buffer['IF/ID']['Instruction'] = instruction_memory[pc] + instruction_memory[pc+1]
    pc += 2 #At the end of the clock cycle, write to the program counter register

def clear_buffer(b):
    keys = buffer[b].keys()
    for k in keys:
        buffer[b][k] = None

def buffer_empty(b):
    return all(value == None for key, value in buffer[b].items())

def termination_check():
    return all(v2 == None for k1, v1 in buffer.items() for k2, v2 in buffer[k1].items())

def simulate():
    i = 1
    while 1:
        print("--- Cycle " + str(i) + "---")
        print(register_file[0])
        if not buffer_empty("MEM/WB"):
            print("WB stage")
            wb_stage()
        if not buffer_empty("EX/MEM"):
            print("MEM stage")
            mem_stage()
        if not buffer_empty("ID/EX"):
            print("EX stage")
            ex_stage()
        if not buffer_empty("IF/ID"):
            print("ID stage")
            id_stage()
        if pc < len(instruction_memory):
            print("IF stage")
            if_stage()
        if termination_check():
            break;
        i += 1
    print("--- End of simulation ---")
    print(register_file[0])

simulate()
