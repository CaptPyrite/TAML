file = "assembly.lasm"

DEBUG = False
commands = ["mov", "global", "db", 
            "dd", ".text", ".data", 
            "call", "add", "sub"]

characters = [":", ",", "[", "]", "%", "#", ";"]

registers = {
  "eax":0,"ebx":0,"ecx":0,
  "ebx":0,"edx":0,"esi":0,
  "edi":0,"esp":0,"ebp":0
}

RAM = {}
command_registry = {}
code_registry = {}
builtin_registry = {}

def resolve(operand):
    """
    if $ -> search `RAM`
    else -> search `registgers`
    """
    if "$" in operand:
        return RAM[operand[1:]]
    return registers[operand]


def parse(expression):
    tokens = []
    current = ""
    in_string = False

    i = 0
    while i < len(expression):
        c = expression[i]

        # Handle string mode
        if c == '"':
            if in_string:
                current += c
                tokens.append(current)
                current = ""
                in_string = False
            else:
                if current:
                    tokens.append(current)
                    current = ""
                current += c
                in_string = True

        elif in_string:
            current += c

        # Handle symbols
        elif c in characters:
            if current:
                tokens.append(current)
                current = ""
            tokens.append(c)

        # Handle spaces
        elif c == " ":
            if current:
                tokens.append(current)
                current = ""

        # Normal characters
        else:
            current += c

        i += 1

    if current:
        tokens.append(current)

    return tokens

def line_split(ln, Lines):
    rtn = [ln]
    for cN, c in enumerate(Lines[ln:], ln):
        if not c.startswith(" "):
            rtn.append(cN)
            break
    return rtn

def command(name, registry=command_registry):
    def decorator(func):
        if name == "RUNTIME":
            print('e')
        else:
            registry[name] = func
            return func
    return decorator

def execute(function_name):
    for code in code_registry[function_name]:
        keyword = code[0]
        args = [Args for Args in code[1:] if Args != ',']

        command_registry[keyword](args)

@command("mov")
def mov_handler(args):
    
    src, dst = args[0], args[1]
    value = resolve(src)
    registers[dst] = value

@command("add")
def add_handler(args):
    num1, num2, dest = args[0], args[1], args[2]
    
    num1 = resolve(num1)
    num2 = resolve(num2)

    if isinstance(num1, int) and isinstance(num2, int):
        registers[dest] = int(num1) + int(num2)
    else:
        registers[dest] = str(num1) + str(num2)

      
@command("sub")
def sub_handler(args):
    num1, num2, dest = args[0], args[1], args[2]
    num1 = resolve(num1)
    num2 = resolve(num2)

    if isinstance(num1, int) and isinstance(num2, int):
        registers[dest] = int(num1) - int(num2)
    else:
        registers[dest] = str(num1) - str(num2)


@command("call")
def call_handler(args):
    function_name = args[0]
    if function_name == "%":
        """
        Built-in functions
        """
        function = args[1]
        builtin_registry[function](args)

    else:
        execute(function_name)


"""
Built-in functions handler (print)
"""
@command("0x80", builtin_registry)
def printf_handler(args):
    print(resolve(args[2]))

"""
Runtime functions
"""
@command("RUNTIME_funct_0")
def code_chunker_(args):
    if args[1] == ":":
        if args[0] == ".global":
            code_registry[args[0]] = args[2]
            return
        code_registry[args[0]] = []

    
    else:
        last_section = list(code_registry.keys())[-1]
        code_registry[last_section].append(args)
    
    

with open(file, "r") as File:
    lines = File.readlines()
    lines.append("\n")

    for line_num, line in enumerate(lines):
        line = line.strip("\n")
        tokens = parse(line)
        
        try:
            """
            Splitting the sections
            -i.e: 
                    main: 
                    code line 1
                    func1:
                        code line 3
            main = (code line 1 - ...)
            func1 = (code line 3 - ...)
            """
            if len(tokens) > 1:
                command_registry[f"RUNTIME_funct_0"](tokens)
        except KeyError:
            pass
        
File.close()

"""
Variable declaration Section -> .data
"""
for data_lines in code_registry[".data"]:
    if data_lines[1] == "dd":
        RAM[data_lines[0]] = int(data_lines[2])
    else:
        RAM[data_lines[0]] = data_lines[2:][0][1:-1]


#Only function that will run upon execution
global_code = code_registry[".global"]
execute(global_code)

if DEBUG:
    print("Registers:", registers)
    print("RAM:", RAM)
