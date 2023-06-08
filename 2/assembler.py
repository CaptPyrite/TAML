file = "assembly.lasm"


commands = ["mov", "jmp", "int", "section", "global", "db", "dd", ".text", ".data"]

characters = [":", ",", "[", "]", "%", "#", ";", " "]

registers = {
  "eax":"",
  "ebx":"",
  "ecx":"",
  "ebx":"",
  "edx":"",
  "esi":"",
  "edi":"",
  "esp":"",
  "ebp":""
}

RAM = {}

Sections = {".global":[],
            ".text":[],
            ".data":[]}

def parse(expression):
    stack = [''] 
    for c in expression:
        if c in (commands + characters):
            stack += [c, ''] # Splits stack
        elif c != ' ':
            stack[-1] += c # Adding to the previous index
    return stack 

def line_split(ln, Lines):
  rtn = [ln] # Starts from said line
  for cN, c in enumerate(Lines[ln:]):
    if c.startswith(" "):
      pass
    
    elif not(c.startswith(" ")):
      rtn.append(ln+cN) # Appends line number where the section ends
      break
  return rtn
  
with open(file, "r") as File:
  Lines = File.readlines()
  Lines.append("\n")
  
  # Sections
  for line_num, line in enumerate(Lines):
    line = line.lower().replace("\n", "").split(";")[0]
    
    if line: # if line is valid and not just a list
      parseln = parse(line) # Raw
      Sparseln = parse(line.strip()) # Avoiding tabs
      
      # .data, .text sectioner
      if parseln[0] == "section":
        sect_name = parseln[0:3][-1]
        if sect_name in Sections.keys():
          Sections[sect_name] = line_split(line_num + 1, Lines)
      
      # Storing data into `RAM`
      if ("dd" in Sparseln) or ("db" in Sparseln):
        op = {"db": lambda x: str(x.split('"')[1::2][0]),
              "dd": lambda x: int(x.split(" ")[-1])}
        try:
          RAM[Sparseln[0]] = op[Sparseln[2]](line)
        except:
          RAM[Sparseln[0]] = RAM[line.split(" ")[-1]]
          
      # Global code sectioner  
      if Sparseln[0] == "global":
        Sections[".global"] = "".join(Sparseln[1:]).strip()
        
      elif Sparseln[0] == Sections[".global"]:
        Sections[".global"] = line_split(line_num + 1, Lines)
      
      
  # Compiling
  global_start = Sections[".global"][0]
  global_end = Sections[".global"][1]
  code = Lines[global_start:global_end]
  for lines in code:
    parseln = parse(lines.replace(" ","").strip())
    
    if parseln[0] == "mov":
      loc1 = parseln[2]
      loc2 = parseln[4]
      
      if loc1.startswith("$"):
        registers[loc2] = RAM[loc1[1:]]
      else:
        registers[loc2] = registers[loc1]
    
print(registers)
