import re
import csv

pc = 0
instruction_memory = []
memory = []
register_file = [None] * 8
machine_code_file = open("machine_code.mips", "r")

for each in machine_code_file:
    instruction = re.sub('\s+', '', each)
    instruction_memory.append(instruction[0:8])
    instruction_memory.append(instruction[8:16])

for i in range(8):
    memory.append([None] * 4)

def signed_binary_to_decimal(b):
    d = int(b, 2)
    if b[0] == "1":
        d = d - (1 << 6)
    return d 

def id_stage(instruction):
    if instruction[0:4] == "0000":
        shift = "$"
        if instruction[13:16] == "000":
            print("add ", end="")
        elif instruction[13:16] == "001":
            print("and ", end="")
        elif instruction[13:16] == "010":
            print("xor ", end="")
        elif instruction[13:16] == "011":
            print("or ", end="")
        elif instruction[13:16] == "101":
            print("slt ", end="")
        elif instruction[13:16] == "100":
            print("sll ", end="")
            shift = ""
        elif instruction[13:16] == "110":
            print("srl ", end="")
            shift = ""
        elif instruction[13:16] == "111":
            print("sub ", end="")

        print("$" + str(int(instruction[10:13], 2)) + ", $" + str(int(instruction[4:7], 2)) + ", " + shift + str(int(instruction[7:10], 2)))
        
    elif instruction[0:4] == "0101":
        i = int(instruction[4:16], 2)
        print("j to instruction at " + str(i) + ": " + instruction_memory[i*2] + instruction_memory[(i*2)+1])
        #update PC

    elif instruction[0:4] == "xxxx":
        print("Placeholder instruction: return statement") 

    else:
        readmem = 0
        if instruction[0:4] == "0001":
            print("addi ", end="")
        elif instruction[0:4] == "0010":
            print("andi ", end="")
        elif instruction[0:4] == "0011":
            print("beq ", end="")
        elif instruction[0:4] == "0100":
            print("bne ", end="")
        elif instruction[0:4] == "0111":
            print("lw ", end="")
            readmem = 1
        elif instruction[0:4] == "1000":
            print("ori ", end="")
        elif instruction[0:4] == "1001":
            print("slti ", end="")
        elif instruction[0:4] == "1010":
            print("sw ", end="")
            readmem = 1

        if readmem:
            print("$" + str(int(instruction[7:10], 2)) + ", " + str(int(instruction[10:16], 2)) + "($" + str(int(instruction[4:7], 2)) + ")")
        else:
            print("$" + str(int(instruction[7:10], 2)) + ", $" + str(int(instruction[4:7], 2)) + ", " + str(signed_binary_to_decimal(instruction[10:16])))
            

while pc < len(instruction_memory):
    print(str(int(pc/2)) + ": ", end="")
    id_stage(instruction_memory[pc] + instruction_memory[pc+1])
    pc += 2
