Cache_size = 64  # bits
registers = {
    "ax": "0" * Cache_size,
    "cx": "0" * Cache_size,
    "dx": "0" * Cache_size,
    "bx": "0" * Cache_size,
    "sp": "0" * Cache_size,
    "bp": "0" * Cache_size,
    "si": "0" * Cache_size,
    "di": "0" * Cache_size,
}

RAM_size = 1  # KB
RAM = {hex(addr): [0] * 8 for addr in range(RAM_size * 1024)}

commands = ["mov", "jmp", "ldr", "str",
            "add", "sub", "and", "or",
            "call", "ret", "push", "pop",
            "in", "out", "int", "syscall", 
            "org", "db", "dw", 'ds', "xor"]

characters = [":", ",", "[", "]", "%", "#", "$", "@", ".", "_", ";"]

def parse(expression):
    stack = ['']
    for c in expression:
        if c in (commands + characters):
            stack += [c, '']
        elif c != ' ':
            stack[-1] += c
    return stack

def CRE(*args):  # Check if register exists
    return all(a in registers for a in args)

def logic_statement(a, b, statement, mode=0):
    gates = {
        'and': lambda x, y: x and y,
        'xor': lambda x, y: x ^ y,
        'or': lambda x, y: x or y
    }
    if not mode:
        return "".join([str(gates[statement](int(bits[0]), int(bits[1]))) for bits in zip(a, b)])
    else:
        return "".join([str(gates[statement](int(bit), int(b))) for bit in a])


file = "assembly.lasm"

with open(file, "r") as File:
  for line in File.readlines():  # lines
    line = line.lower().replace("\n", "").split(";")[0]
    parseln = parse(line)

    if parseln[0] == "mov":
      d1 = parseln[parseln.index(":") + 1]
      d2 = parseln[parseln.index(d1) + 2]

      if CRE(d1, d2):
        registers[d2] = registers[d1]
      else:
        try:
          registers[d1] = bin(int(d2) & 0xFF)[2:].zfill(64)
        except:
          registers[d1] = ''.join(['{0:08b}'.format(ord(char)) for char in d2]).replace(" ", "").zfill(64)

    elif parseln[0] in ("and", "or", "xor"):
      d1 = parseln[parseln.index(":") + 1]
      d2 = parseln[parseln.index(d1) + 2]
      try:
        registers[d1] = logic_statement(registers[d1], registers[d2], parseln[0], mode=0)
      except:
        registers[d1] = logic_statement(registers[d1], d2, parseln[0], mode=1)

    elif parseln[0] in ("ldr", "str"):
      d1 = parseln[parseln.index(":") + 1]
      d2 = parseln[parseln.index(d1) + 2]
      
      if parseln[0] =="ldr":
        registers[d1] = "".join([str(b) for b in RAM[d2]]).zfill(64)
      else:
        RAM[d1] = registers[d2]

print(registers)
