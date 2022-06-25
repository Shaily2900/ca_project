import sys
#Opening Output file 
stdoutOrigin =sys.stdout
sys.stdout = open("output_Ca.txt", "w")

Address = {'AL' : 1, 'AH' : 2, 'BL' : 3, 'BH' : 4, 'CL' : 5, 'CH' : 6, 'DL' : 7, 'DH' : 8 }
op = {'MOV': 1,'ADD': '2','SUB': 3,'INC': 4,'DEC': 5,'AND': 6,'OR': 7,'XOR': 8,'NOT': 9,'NEG': 10,'PUSH': 11,'POP': 12,'XCHG': 13,'NOP':14,'HLT':15}
R_values = {'AL' : 0, 'AH' : 0, 'BL' : 0, 'BH' : 0, 'CL' : 0, 'CH' : 0, 'DL' : 0, 'DH' : 0 }

#Flag Registers 
F = [0,0,1,0,0,0,0,0,0]
#Memory
Mem = [0]*16

#Parity Calculating Function
def Parity(s):
    count = 0
    output = 1
    for i in s:
        if(i=="1"):
            count = count +1
    if(count%2):
        output = 0
    return output

#Stack Segment
stack_segment = []

def decode(data):
    opcode = 0
    rd = 0
    rs = 0
    rs2 = 0
    imm = 0
    dm = 0
    type = 0
    data = data.strip()
    inst = data.split()
    args = []
    out = ''
    Flag = 0
    for i in range (len(inst)):
        if (inst[i] != ""):
           if(inst[i]!="\n"):
                 args.append(inst[i])
    #For Length 1
    if(len(args)==1):
        opcode = op[args[0]]
        type = 0
        if(args[0]=='HLT'):
            Flag = 1
            out = "Program Terminated \n"
            
    #for Length 2
    elif(len(args)==2):
        opcode = op[args[0]]
        if(args[0]!="PUSH"):
           rd = Address[args[1]]
           ini = R_values[args[1]]
        type = 0
        if(args[0]=="INC"): #For INC Operation
            out = args[1]
            R_values[args[1]] = R_values[args[1]] + 1
            value = R_values[args[1]]
            out = out + " = " + format(R_values[args[1]],'02x') +"H"
            #Updating Flag Registers
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = int((format(R_values[args[1]],'08b')[0]!=format(ini,'08b')[0]))
            F[4] = int((R_values[args[1]]<0))
            F[5] = int((R_values[args[1]]==0))

        if(args[0]=="DEC"): #For DEC Operation
            out = args[1]
            R_values[args[1]] = R_values[args[1]] - 1
            
            value = R_values[args[1]]
            out = out + " = " + format(R_values[args[1]],'02x')[-2] + format(R_values[args[1]],'02x')[-1] +"H"
            #Updating Flag Registers
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = int((format(R_values[args[1]],'08b')[0]!=format(ini,'08b')[0]))
            F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
            F[5] = int((R_values[args[1]]==0))

        if(args[0]=="NOT"): #For NOT Opertaion
            out = args[1] + " = "
            temp = format(R_values[args[1]],'08b')
            temp = temp[::-1]
            R_values[args[1]] = 0
            for i in range(len(temp)):
                if(temp[i]=="0"):
                    R_values[args[1]] = R_values[args[1]] + 2**i 
           
            out  += format(R_values[args[1]],"02x")   +"H"
            #Updating Flag Registers
            F[8] = 0
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = 0
            F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
            F[5] = int((R_values[args[1]]==0))

        if(args[0]=="NEG"): # NEG Mneomonics
            out = args[1] + " = "
            temp = format(R_values[args[1]],'08b') 
            temp = temp[::-1]
            R_values[args[1]] = 0
            ini = R_values[args[1]]
            for i in range(len(temp)):
                if(temp[i]=="0"):
                    R_values[args[1]] = R_values[args[1]] + 2**i
            R_values[args[1]] += 1 
            
            out  += format(R_values[args[1]],"02x")[-2]+format(R_values[args[1]],"02x")[-1]  +"H"
            #Updating Flag Registers
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = int((format(R_values[args[1]],'08b')[0]!=format(ini,'08b')[0]))
            F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
            F[5] = int((R_values[args[1]]==0))

        if(args[0]=="PUSH"): #For Push Operation
            a = int(args[1][:-1],16)
            stack_segment.append(a)

        if(args[0]=="POP"): #For POP Operation
            b = stack_segment.pop()
            R_values[args[1]] = b
            out = args[1] + " = " + format(R_values[args[1]],"02x") +"H"

    #For length 3
    elif(len(args)==3):
        opcode = op[args[0]]
        if(args[1][0] == '['):
            if(args[2][0]!='['):
                rd = Address[args[2]]
        else:
            rd = Address[args[1]]
        if(args[2] in Address):
            rs = Address[args[2]]
            type = 0
        else:
            if(args[2][0]=='['):
                if(args[2][-2]=='H'):
                    dm = args[2][1:-2]
                else:
                    dm = args[2][1:-1]
                type = 3
            else:
                if(args[2][-1]=="H"):
                        imm = args[2][:-1]
                        a = int(imm,16)
                else:
                        imm = args[2]
                        a = int(imm,16)
                type = 2
        if(args[0]=="MOV"): #For MOV Operation
            if(args[1][0]=='['):
                out = args[2] + " = "
                if(args[2][0]!='['):
                    Mem[int(args[2][-3],16)] = R_values[args[2]]
                    out  += format(R_values[args[2]],"02x") +"H"
                else:
                    out = "Error"
            else:
                out = args[1] + " = "
                if(args[2] in Address):
                    R_values[args[1]] = R_values[args[2]]
                    out  += format(R_values[args[1]],"02x") + "H"
                else:
                    if(args[2][0]=='['):
                        R_values[args[1]] = Mem[int(args[2][-3],16)]
                        out  += format(R_values[args[1]],"02x") +"H"
                    else:
                        R_values[args[1]] = a
                        
                        out  += format(R_values[args[1]],"02x") +"H"
            
        if(args[0]=="AND"): #For AND Operation
            if(args[1][0]=='['):
                out = args[2] + " = "
                if(args[2][0]!='['):
                    Mem[int(args[2][-2],16)] = Mem[int(args[2][-2],16)] & R_values[args[2]]
                    out  += format(R_values[args[2]],"02x") +"H"
                else:
                    out = "Error"
            else:
                out = args[1] + " = "
                if(args[2] in Address):
                    R_values[args[1]] = R_values[args[1]] & R_values[args[2]]
                    out  += format(R_values[args[1]],"02x") +"H"
                else:
                    if(args[2][0]=='['):
                        R_values[args[1]] = R_values[args[1]] & Mem[int(args[2][-3],16)]
                        out  += format(R_values[args[1]],"02x") +"H"
                    else:
                        R_values[args[1]] = R_values[args[1]] & a
                        out  += format(R_values[args[1]],"02x") +"H"
            #Updating Flag Registers
            F[8] = 0
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = 0
            F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
            F[5] = int((R_values[args[1]]==0))

        if(args[0]=="OR"): #For OR Operation
             if(args[1][0]=='['):
                    out = args[2] + " = "
                    if(args[2][0]!='['):
                         Mem[int(args[2][-3],16)] = Mem[int(args[2][-3],16)] | R_values[args[2]]
                         out  += format(R_values[args[2]],"02x") +"H"
                    else:
                        out = "Error"
             else:
                out = args[1] + " = "
                if(args[2] in Address):
                    R_values[args[1]] = R_values[args[1]] | R_values[args[2]]
                    out  += format(R_values[args[1]],"02x") +"H"
                else:
                    if(args[2][0]=='['):
                        R_values[args[1]] = R_values[args[1]] | Mem[int(args[2][-3],16)]
                        out  += format(R_values[args[1]],"02x") +"H"
                    else:
                        R_values[args[1]] = R_values[args[1]] | a
                        out  += format(R_values[args[1]],"02x") +"H"
            #Updating Flag Registers
             F[8] = 0
             F[7] = Parity(format(R_values[args[1]],'08b'))
             F[0] = 0
             F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
             F[5] = int((R_values[args[1]]==0))

        if(args[0]=="XOR"): #For XOR Operation
             if(args[1][0]=='['):
                    out = args[2] + " = "
                    if(args[2][0]!='['):
                        Mem[int(args[2][-3],16)] = Mem[int(args[2][-3],16)] ^ R_values[args[2]]
                        out  += format(R_values[args[2]],"02x") +"H"
                    else:
                        out = "Error"
             else:
                out = args[1] + " = "
                if(args[2] in Address):
                    R_values[args[1]] = R_values[args[1]] ^ R_values[args[2]]
                    out  += format(R_values[args[1]],"02x") +"H"
                else:
                    if(args[2][0]=='['):
                        R_values[args[1]] = R_values[args[1]] ^ Mem[int(args[2][-3],16)]
                        out  += format(R_values[args[1]],"02x") +"H"
                    else:
                        R_values[args[1]] = R_values[args[1]] ^ a
                        out  += format(R_values[args[1]],"02x") +"H"
            #Updating Flag Registers
             F[8] = 0
             F[7] = Parity(format(R_values[args[1]],'08b'))
             F[0] = 0
             F[4] = int((R_values[args[1]]<0))
             F[5] = int((R_values[args[1]]==0))

        if(args[0]=="XCHG"): #For XCHG Operation
            out = args[1] + " = "
            a = R_values[args[1]]
            R_values[args[1]] = R_values[args[2]]
            R_values[args[2]] = a
            out  += format(R_values[args[1]],"02x") +"H"
            out+= " " + args[2] + " = "
            out  += format(R_values[args[2]],"02x") +"H"

        if(args[0]=="ADD"): #For ADD Operation
            out = args[1] + " = "
            if(args[1][0]!='['):
                if(args[2] in Address):
                    R_values[args[1]] += R_values[args[2]]
                    out  += format(R_values[args[1]],"02x") +"H"
                else:
                    if(args[2][0]=='['):
                        R_values[args[1]] = R_values[args[1]] + Mem[int(args[2][-3],16)]
                        out  += format(R_values[args[1]],"02x") +"H"
                    else:
                        R_values[args[1]] = R_values[args[1]] + a
                        out  += format(R_values[args[1]],"02x") +"H"
            else:
                out = "Error"
            #Updating Flag Registers
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = 0
            F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
            F[5] = int((R_values[args[1]]==0))

        if(args[0]=="SUB"): #For SUB Operation
            out = args[1] + " = "
            if(args[1][0]!='['):
                if(args[2] in Address):
                    R_values[args[1]] -= R_values[args[2]]
                    out  += format(R_values[args[1]],"02x") +"H"
                else:
                    if(args[2][0]=='['):
                        R_values[args[1]] = R_values[args[1]] - Mem[int(args[2][-3],16)]
                        out  += format(R_values[args[1]],"02x") +"H"
                    else:
                        R_values[args[1]] = R_values[args[1]] - a
                        out  += format(R_values[args[1]],"02x") +"H"
            else:
                out = "Error"
            #Updating Flag Registers
            F[7] = Parity(format(R_values[args[1]],'08b'))
            F[0] = 0
            F[4] = int(format(R_values[args[1]],'08b')[0]=='1')
            F[5] = int((R_values[args[1]]==0))
    

    instruction = convert_Hexadecimal(opcode,type,rd,rs,rs2,imm,dm)
    if(type==2):
        instruction += " " + imm + "  "
    elif(type==3):
        instruction += " " + dm

    print("{:<20} {:<30} {:<30}".format(instruction,data,out),"\n")
    print("Flag Register: ")
    print("_"*33)
    print("|X|X|X|X|{0}|{1}|{2}|{3}|{4}|{5}|X|{6}|X|{7}|X|{8}|".format(F[0],F[1],F[2],F[3],F[4],F[5],F[6],F[7],F[8]))
    print("-"*65)
    return Flag

def convert_Hexadecimal(opcode,type,rd,rs,rs2,imm,dm):
    opstr = format(int(opcode),'04b')
    typestr = format(type,'02b')
    rdstr = format(rd,'04b')
    rsstr = format(rs,'04b')
    Instruction = opstr + typestr + rdstr + rsstr
    if(type==1):
        rs2str = format(rs2,'04b')
        Instruction += rs2str
    return format(int(Instruction, 2), '04x')

file = open('input.txt','r') #Opening File
data = file.readlines() #Reading file Line By Line
out = ""
print ("{:<20} {:<30} {:<30}".format('OPCODE','Mnemonic codes','Output'),"\n")
print("-"*65)
for i in range (len(data)):
    if (data[i] != ""):
       a =  decode(data[i].upper())
       if(a):
           break

        