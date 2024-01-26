import sys
import os

def rc(s:str)->str: return s.replace(',','')

def join(*args)->str: return " ".join(args)

addrstore = {}
cmpstore = []
isObj = ""
def interpret_cmd(line: list, addr: int)->str:
    global addrstore, cmpstore
    ret = ""

    ## Storing
    if line[0] == "stwu":
        ret = join("Stack Size +=", line[2][1:-4])
    elif line[0] == "stb" or line[0] == "sth" or line[0] == "stw" or line[0] == "stfs" or line[0] == "stfd":
        if "r1" in line[2]: ret = "Stack"
        else: ret = line[2][(line[2].index("(")+1):-1]

        ret += join(f"[{line[2][:(line[2].index('('))]}]",
            "=",
            rc(line[1])
        )

        if "b" in line[0]: ret += join("", "(s8/u8)")
        elif "h" in line[0]: ret += join("", "(s16/u16)")
        elif "w" in line[0]: ret += join("", "(s32/u32)")
        elif "fs" in line[0]: ret += join("", "(f32)")
        elif "fd" in line[0]: ret += join("", "(f64)")
    elif line[0] == "stbx" or line[0] == "sthx" or line[0] == "stwx" or line[0] == "stfsx":
        if "r1" in line[2]: ret = "Stack"
        else: ret = rc(line[2])

        ret += join(f"[{line[3]}]",
            "=",
            rc(line[1])
        )

        if "b" in line[0]: ret += join("", "(s8/u8)")
        elif "h" in line[0]: ret += join("", "(s16/u16)")
        elif "w" in line[0]: ret += join("", "(s32/u32)")
        elif "f" in line[0]: ret += join("", "(f32)")
    elif line[0] == "psq_st":
        if "r1" in line[2]: ret = "Stack"
        else: ret = line[2][(line[2].index("(")+1):-1]

        ret += join(f"[{line[2][:(line[2].index('('))]}]",
            "=",
            f"rotate({line[1]} {line[4]})",
            "(128-bit)"
        )
    
    ## Moving
    elif line[0] == "mflr":
        ret = join(line[1], "set to Link Register ")
    elif line[0] == "mtlr":
        ret = join("Link Register set to", line[1])
    elif line[0] == "mtctr":
        ret = join("Count Register set to", line[1])
    elif line[0] == "mr" or line[0] == "fmr":
        ret = join(rc(line[1]), "=", line[2])
    
    ## Loading
    elif line[0] == "lbz" or line[0] == "lha" or line[0] == "lhz" or line[0] == "lwz" or line[0] == "lwzu" or line[0] == "lfs" or line[0] == "lfd":
        ret = join(rc(line[1]), "=")
        if "r1" in line[2]: ret += join("", "Stack")
        else: ret += join("", line[2][(line[2].index("(")+1):-1])

        ret += f"[{line[2][:(line[2].index('('))]}]"

        if "b" in line[0]: ret += join("", "(s8/u8)")
        elif "h" in line[0]: ret += join("", "(s16/u16)")
        elif "w" in line[0]: ret += join("", "(s32/u32)")
        elif "fs" in line[0]: ret += join("", "(f32)")
        elif "fd" in line[0]: ret += join("", "(f64)")
    elif line[0] == "lbzx" or line[0] == "lhax" or line[0] == "lhzx" or line[0] == "lwzx" or line[0] == "lfsx":
        ret = join(rc(line[1]), "=")
        if "r1" in line[2]: ret += join("", "Stack")
        else: ret += join("", rc(line[2]))

        ret += f"[{line[3]}]"

        if "b" in line[0]: ret += join("", "(s8/u8)")
        elif "h" in line[0]: ret += join("", "(s16/u16)")
        elif "w" in line[0]: ret += join("", "(s32/u32)")
        elif "f" in line[0]: ret += join("", "(f32)")
    elif line[0] == "psq_l":
        ret = join(f"+ rotate({line[1]} {line[4]})", "=")
        if "r1" in line[2]: ret += join("", "Stack")
        else: ret += join("", rc(line[2]))

        ret += join(f"[{line[2][:(line[2].index('('))]}]",
                    "(128-bit)")
    elif line[0] == "lis":
        ret = join("(^u16)", rc(line[1]), "=")
        if line[2][-3:] == "@ha":
            ret += join("", "(^u16)", line[2][:-3])
        else: ret += join("", line[2])
    elif line[0] == "li":
        ret = join(rc(line[1]), "=", line[2])
    
    ## Bitwise Operations
    elif "and" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "&=")
        else:
            ret += join("", "=", rc(line[2]), "&")
        
        ret += join("", line[3])
    elif "xor" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "^=")
        else:
            ret += join("", "=", rc(line[2]), "^")
        
        ret += join("", line[3])
    elif "or" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "|=")
        else:
            ret += join("", "=", rc(line[2]), "|")
        
        ret += join("", line[3])
    elif "neg" in line[0]:
        ret = join(rc(line[1]), "=", "-"+line[2])
    elif line[0] == "slw" or line[0] == "slwi" or line[0] == "slawi":
        ret = join(rc(line[1]), "=", rc(line[2]), "<<", line[3], "(s32/u32)", "(signed)" if line[0] == "slawi" else "")
    elif line[0] == "srwi" or line[0] == "srawi":
        ret = join(rc(line[1]), "=", rc(line[2]), ">>", line[3], "(s32/u32)", "(signed)" if line[0] == "srawi" else "")
    
    ## Math
    elif "add" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "+=")
        else:
            ret += join("", "=", rc(line[2]), "+")

        if line[3][-2:] == "@l":
            ret += join("", "(vu16)")
            ret += join("", line[3][:-2])
        else: ret += join("", line[3])
    elif "sub" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "-=")
        else:
            ret += join("", "=", rc(line[2]), "-")

        ret += join("", line[3])
    elif "mul" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "*=")
        else:
            ret += join("", "=", rc(line[2]), "*")
        
        ret += join("", line[3])
    elif "div" in line[0]:
        ret = rc(line[1])
        if rc(line[1]) == rc(line[2]):
            ret += join("", "/=")
        else:
            ret += join("", "=", rc(line[2]), "/")
        
        ret += join("", line[3])
    elif "sqrt" in line[0]:
        ret = join(rc(line[1]), f"= sqrt({line[2]})")
    elif "abs" in line[0]:
        ret = join(rc(line[1]), f"= abs({line[2]})")

    ## Compare And Branch
    elif "cmp" in line[0] and "w" in line[0]:
        cmpstore = line
        cmpstore.append("(s32/u32)")
        ret = "(cmp)"
    elif line[0] == "fcmpo":
        cmpstore = line
        ret = join("(cmp", rc(line[1])+")")
    elif "cmp" in line[0] and "f" in line[0]:
        cmpstore = line
        cmpstore.pop(1)
        cmpstore.append("(f32/f64)")
        ret = "(cmp)"
    elif line[0] == "cror":
        cmpsym = ""
        if line[2] == "gt,": cmpsym += ">"
        elif line[2] == "lt,": cmpsym += "<"
        cmpsym += "="

        ret = join(
            "check", rc(cmpstore[2]),
            cmpsym, cmpstore[3],
        )
    elif line[0] == "beq":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join(
            "if", rc(cmpstore[1]),
            "==", cmpstore[2],
            ": goto", hex(int(line[1][3:], 16)), cmpstore[3]
        )
    elif line[0] == "bge":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join(
            "if", rc(cmpstore[1]),
            ">=", cmpstore[2],
            ": goto", hex(int(line[1][3:], 16)), cmpstore[3]
        )
    elif line[0] == "bne":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join(
            "if", rc(cmpstore[1]),
            "!=", cmpstore[2],
            ": goto", hex(int(line[1][3:], 16)), cmpstore[3]
        )
    elif line[0] == "ble":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join(
            "if", rc(cmpstore[1]),
            "<=", cmpstore[2],
            ": goto", hex(int(line[1][3:], 16)), cmpstore[3]
        )
    elif line[0] == "blt":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join(
            "if", rc(cmpstore[1]),
            "<", cmpstore[2],
            ": goto", hex(int(line[1][3:], 16)), cmpstore[3]
        )
    elif line[0] == "bgt":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join(
            "if", rc(cmpstore[1]),
            ">", cmpstore[2],
            ": goto", hex(int(line[1][3:], 16)), cmpstore[3]
        )
    elif line[0] == "blr":
        ret = "return"
    elif line[0] == "bctrl":
        ret = "Call to Subroutine"
    elif line[0] == "bctr":
        ret = "Jump to Subroutine"
    elif line[0] == "b":
        addrstore[hex(int(line[1][3:], 16))] = hex(addr)
        ret = join("goto", hex(int(line[1][3:], 16)))
    elif line[0] == "bl":
        ret = join("call", line[1])
    
    ## Misc
    elif line[0] == "crclr":
        ret = f"clear({line[1]})"
    elif line[0] == "crset":
        ret = f"set({line[1]})"
    elif line[0] == "extsh":
        ret = join("(s32)", rc(line[1]), "= (s16)", line[2])
    elif line[0] == "extsb":
        ret = join("(s32)", rc(line[1]), "= (s8)", line[2])
    elif line[0] == "clrlwi":
        ret = join(rc(line[1]), "=", f"remove({line[2]} {line[3]})")
    elif line[0] == "rlwinm":
        ret = join(rc(line[1]), "=", f"rotate({line[2]} {rc(line[3])})", "& (bits", rc(line[4]), "to", line[5]+")")
    elif line[0] == "frsp":
        ret = join("(f32)", rc(line[1]), "= (f64)", line[2])
    elif line[0] == "fctiwz":
        ret = join("(s32)", rc(line[1]), "= (float)", line[2])
    elif line[0] == "cntlzw":
        ret = join(rc(line[1]), f"= num_leading_zeroes({line[2]})")
    else:
        print(line, "\n", [],"\n")
        return "unable to interpret: "+str(line)
    return ret

def interpret_obj(line: list)->str:
    global isObj
    ret = ""

    if line[0] == "\t.4byte":
        if isObj == True:
            ret = "{\n"
        ret += join("\t(s32)", line[1])
    elif line[0] == "\t.string":
        ret = join("\t(char[])", " ".join(line[1:]))
    elif line[0] == "\t.skip":
        ret = join("\tsizeof =", line[1])
    elif line[0] == "\t.double":
        ret = join("\t(f64)", line[1])
    elif line[0] == "\t.float":
        ret = join("\t(f32)", line[1])

    return ret

def interpret_line(line: list)->str:
    global addrstore, isObj
    line = line.split(" ")
    line[-1] = line[-1].replace("\n","")
    ret = ""

    if line[0] == ".fn":
        ret = join(line[2], "function", rc(line[1])+":")
    elif line[0] == ".endfn":
        ret = join(line[1], "end\n")
    elif line[0] == ".obj":
        ret = rc(line[1])+":"
        isObj = True
    elif line[0] == ".endobj" and isObj == True:
        ret = "}"
        isObj = False
    elif ".L" in line[0]:
        try:
            ret = join("\n\tfrom", addrstore[hex(int(line[0][3:-1], 16))]+":")
        except:
            ret = "\n\tfrom later address:"
    elif line[0] == "/*":
        address = int(line[1], 16)
        line[8] = line[8].replace("*/\t","")
        ret = join("\t", hex(address), "|",
                   interpret_cmd(line[8:], address)
        )
    elif "\t" in line[0]:
        ret = interpret_obj(line)

    isObj = line[0]
    print(line, "\n", ret, "\n")
    return ret

def interpret_file(file)->None:
    curdir = os.path.dirname(os.path.abspath(__file__))
    fs = file.split("/")[-1]

    os.system(f"mkdir {curdir}/output")
    f = open(file)
    g = open(f"{curdir}/output/{fs[:(fs.index('.'))]}-output.txt", "w")
    line = f.readline()
    while line:
        ret = interpret_line(line)
        g.write(ret+"\n" if ret != "" else "")
        line = f.readline()
    g.close()
    f.close()

try:
    interpret_file(sys.argv[1])
except Exception:
    if len(sys.argv) == 1:
        print("interpretasm.py")
        print("Usage: python3 interpretasm.py [file]")
        print("Accepts all files that use the generated asm from ninja")
    else:
        raise Exception
    
