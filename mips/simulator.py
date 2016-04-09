import re
import csv

pc = 0
instruction_memory = []
data_memory = []
register_file = ["00000000", "00000001", "00000010", "00000011", "00000100", "00000000", "00000000", "00000000"]
machine_code_file = open("test.mips", "r")

for each in machine_code_file:
    i = re.sub('\s+', '', each)
    instruction_memory.append(i[0:8])
    instruction_memory.append(i[8:16])

for i in range(8):
    data_memory.append([None] * 4)

"""
PIPELINE REGISTERS
IF/ID: stores 16-bit instruction
ID/EX: stores EX, MEM, WB control signals + Read data 1, Read data 2, Rt, Rd, SEImm
EX/MEM: stores MEM, WB control signals + Zero, ALU Result, Read data 2, Write register
MEM/WB: stores WB control signals + ALU Result, Read data
"""

buffer = {'IF/ID': {'Instruction': None}, \
           'ID/EX': {'RegDst': None, 'ALUSrc': None, 'ALUOp1': None, 'ALUOp0': None, 'Branch': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'Read data 1': None, 'Read data 2': None, 'Rt': None, 'Rd': None, 'SEImm': None}, \
           'EX/MEM': {'Branch': None, 'MemRead': None, 'MemWrite': None, 'MemToReg': None, 'RegWrite': None, 'Zero': None, 'ALU Result': None, 'Read data 2': None}, \
           'MEM/WB': {'MemToReg': None, 'RegWrite': None, 'ALU Result': None, 'Read data': None}}

def control_unit(opcode):
    if opcode == "0000": #R-format
        buffer['ID/EX']['RegDst'] = 1
        buffer['ID/EX']['ALUSrc'] = 0
        buffer['ID/EX']['ALUOp1'] = 1
        buffer['ID/EX']['ALUOp0'] = 0
        buffer['ID/EX']['Branch'] = 0
        buffer['ID/EX']['MemRead'] = 0
        buffer['ID/EX']['MemWrite'] = 0
        buffer['ID/EX']['MemToReg'] = 0
        buffer['ID/EX']['RegWrite'] = 1
    elif opcode == "0111" : #lw
        buffer['ID/EX']['RegDst'] = 0
        buffer['ID/EX']['ALUSrc'] = 1
        buffer['ID/EX']['ALUOp1'] = 0
        buffer['ID/EX']['ALUOp0'] = 0
        buffer['ID/EX']['Branch'] = 0
        buffer['ID/EX']['MemRead'] = 1
        buffer['ID/EX']['MemWrite'] = 0
        buffer['ID/EX']['MemToReg'] = 1
        buffer['ID/EX']['RegWrite'] = 1
    elif opcode == "1010" : #sw
        buffer['ID/EX']['RegDst'] = "X"
        buffer['ID/EX']['ALUSrc'] = 1
        buffer['ID/EX']['ALUOp1'] = 0
        buffer['ID/EX']['ALUOp0'] = 0
        buffer['ID/EX']['Branch'] = 0
        buffer['ID/EX']['MemRead'] = 0
        buffer['ID/EX']['MemWrite'] = 1
        buffer['ID/EX']['MemToReg'] = "X"
        buffer['ID/EX']['RegWrite'] = 0
    elif opcode == "0011" : #beq
        buffer['ID/EX']['RegDst'] = "X"
        buffer['ID/EX']['ALUSrc'] = 0
        buffer['ID/EX']['ALUOp1'] = 0
        buffer['ID/EX']['ALUOp0'] = 1
        buffer['ID/EX']['Branch'] = 1
        buffer['ID/EX']['MemRead'] = 0
        buffer['ID/EX']['MemWrite'] = 0
        buffer['ID/EX']['MemToReg'] = "X"
        buffer['ID/EX']['RegWrite'] = 0

def ALU_control(b):
    a = buffer['ID/EX']['Read data 1'] # Read data 1
    if buffer['ID/EX']['ALUOp1'] == 1 and buffer['ID/EX']['ALUOp0'] == 0:
        if buffer['ID/EX']['SEImm'][13:16] == "000":
            buffer['EX/MEM']['ALU Result'] = format(int(a, 2) + int(b, 2), '08b')
            #find out the operation using buffer['ID/EX']['ALUOp1'], buffer['ID/EX']['ALUOp0'] and buffer['ID/EX']['SEImm'][13:16]
            #do relevant operation on a and b
            #store in buffer['EX/MEM']['ALU Result'], buffer['EX/MEM']['Zero']

def wb_stage():
    if buffer['MEM/WB']['RegWrite'] == 1:
        if buffer['MEM/WB']['MemToReg'] == 0:
            register_file[int(buffer['MEM/WB']['Write register'], 2)] = buffer['MEM/WB']['ALU Result']
        else:
            register_file[int(buffer['MEM/WB']['Write register'], 2)] = buffer['MEM/WB']['Read data']

    clear_buffer("MEM/WB")
                        
        
def mem_stage():
    buffer['MEM/WB']['MemToReg'] = buffer['EX/MEM']['MemToReg']
    buffer['MEM/WB']['RegWrite'] = buffer['EX/MEM']['RegWrite']
    buffer['MEM/WB']['Write register'] = buffer['EX/MEM']['Write register']
        
    # TO-DO
    if buffer['EX/MEM']['Branch'] == 1:
        if buffer['EX/MEM']['Zero'] == 1:                        
            #PC calculation
            return;

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
    buffer['EX/MEM']['Read data 2'] = buffer['ID/EX']['Read data 2']

    if buffer['ID/EX']['RegDst'] == 1:
        buffer['EX/MEM']['Write register'] = buffer['ID/EX']['Rd']
    else:
        buffer['EX/MEM']['Write register'] = buffer['ID/EX']['Rt']

    if buffer['ID/EX']['ALUSrc'] == 0: #R-format instruction
        ALU_control(buffer['ID/EX']['Read data 2'])
    else: 
        ALU_control(buffer['ID/EX']['SEImm'])

    clear_buffer("ID/EX")
                        
def id_stage():
    buffer['ID/EX']['Read data 1'] = register_file[int(buffer['IF/ID']['Instruction'][4:7], 2)]
    buffer['ID/EX']['Read data 2'] = register_file[int(buffer['IF/ID']['Instruction'][7:10], 2)]
    buffer['ID/EX']['Rt'] = buffer['IF/ID']['Instruction'][7:10]
    buffer['ID/EX']['Rd'] = buffer['IF/ID']['Instruction'][10:13]
    buffer['ID/EX']['SEImm'] = format(int(buffer['IF/ID']['Instruction'][10:16]), '016b')
    control_unit(buffer['IF/ID']['Instruction'][0:4])
    clear_buffer("IF/ID")
        
def if_stage():
    global pc
    buffer['IF/ID']['Instruction'] = instruction_memory[pc] + instruction_memory[pc+1]
    pc += 2

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
