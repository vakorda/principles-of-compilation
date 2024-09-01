import re

# Warning: seriously ugly code ahead! REWRITE!!!
COMMENT = re.compile(r"#.*")
PREFIX = re.compile(
    r"(?P<ikey>[a-z][a-z0-9]*)")
ASSIGN = re.compile(
    r"(?P<addr1>[a-z]+[a-z0-9]*)\s*:=\s*(?P<oprnd2>\w*)"
    r"(\s*(?P<op>[-+*\<>=!]+)\s*(?P<oprnd3>\w*))?")
LABEL = re.compile(
    r"(?P<label>[a-z][a-z0-9]*)\s*:")
GOTO = re.compile(
    r"goto\s+(?P<label>[a-z][a-z0-9]*)")
IF = re.compile(
    r"if\s*\(\s*(?P<oprnd>[a-z][a-z0-9]*)\s*(?P<op>==|!=)\s*0\s*\)"
        r"\s*goto\s+(?P<label>[a-z][a-z0-9]*)")

class TacReader:
    
    def __init__(self, path):
        self.__source = open(path, "r")
        self.program = TacExecutable()
       
        for line in self.__source:
            currtkn = None
            
            #print("Processing line '%s'" % line)
        
            line = COMMENT.sub("", line)
        
            if line.isspace():
                continue
        
            match = PREFIX.search(line)
            if match  is not None:
                #print("Matched '%s'" % match.group().strip())
                spelling = match.group("ikey")
                
                if spelling == "if":
                    #print("if instruction")
                    match = IF.search(line)
                    oprnd = match.group("oprnd")
                    op = match.group("op")
                    label = match.group("label")
                    if op == "==":
                        currtkn = TacInstruction("jumpfalse", 
                            oprnd, None, None, op, label)
                    elif op == "!=":
                        currtkn = TacInstruction("jumptrue",
                            oprnd, None, None, op, label )
                    else:
                        print("*** Error illegal operator %s." % op)
                elif spelling == "goto":
                    #print("goto instruction")
                    match = GOTO.search(line)
                    label = match.group("label")
                    currtkn = TacInstruction("goto",
                        None, None, None, None, label)
                elif spelling == "halt":
                    #print("halt instruction")
                    currtkn = TacInstruction("halt",
                        None, None, None, None, None)
                else:
                    match = ASSIGN.search(line)
                    if match is not None:
                        addr1  = match.group("addr1")
                        oprnd2 = match.group("oprnd2")
                        if match.group("oprnd3") is not None:
                            op = match.group("op")
                            oprnd3 = match.group("oprnd3")
                            currtkn = TacInstruction("threeaddress",
                                addr1, oprnd2, oprnd3, op, None)
                        else:
                            if oprnd2 == "in":
                                currtkn = TacInstruction("in",
                                addr1, oprnd2, None, None, None)
                            elif addr1 == "out":
                                currtkn = TacInstruction("out",
                                addr1, oprnd2, None, None, None)
                            else:
                                currtkn = TacInstruction("twoaddress",
                                addr1, oprnd2, None, None, None)
                    else:
                        match = LABEL.search(line)
                        label =match.group("label")
                        currtkn = TacInstruction("label",
                                None, None, None, None, label)
            
            if currtkn is not None:
                self.program.add(currtkn)

class TacInstruction:
   
    def __init__(self, kind, addr1, addr2, addr3, op, label):
        self.kind = kind
        self.addr1, self.addr2, self.addr3 = addr1, addr2, addr3
        self.op = op
        self.label = label
        
    def __str__(self):
        stringification = {
            "threeaddress" : "%s := %s %s %s;" % (
                self.addr1,  self.addr2,self.op,  self.addr3),
            "twoaddress": "%s = %s;" %(self.addr1, self.addr2),
            "goto": "goto %s;" % self.label,
            "jumptrue": "if (%s != 0) goto %s;" % (self.addr1, self.label),
            "jumpfalse": "if (%s == 0) goto %s;" % (self.addr1, self.label),
            "in": "%s := in;" % self.addr1,
            "out": "out := %s;" % self.addr2,
            "label": " %s:" % self.label,
            "halt": "halt;",
            }
        return stringification[self.kind]

class TacProgram:
    
    def __init__(self):
        self._instructions = []
       
    def add(self, instr):
        self._instructions.append(instr)
       
    def show(self):
        for index, instr in enumerate(self._instructions):
            print("[%2d]" % index, end = "")
            if instr.kind != "label":
                print("   ", end = "")
            print(str(instr))
          
class TacExecutable (TacProgram):
    
    __EVALUATE = {
            "+" : lambda x, y: x + y,
            "-" : lambda x, y: x - y,
            "*" : lambda x, y: x * y,
            "/" : lambda x, y: x // y,
            "<" : lambda x, y: 1 if x < y else 0,
            "<=" : lambda x, y: 1 if x <= y else 0,
            ">" : lambda x, y: 1 if x > y else 0,
            ">=" : lambda x, y: 1 if x >= y else 0,
            "==" : lambda x, y: 1 if x == y else 0,
            "!=" : lambda x, y: 1 if x != y else 0
            }
              
    def __lookup_label(self, name):
        if name not in self.__labels:
            print("*** Unknown label '%s'." % name)
        else:
            return self.__labels[name]
            
    def __lookup_name(self, name):
        if name not in self.__names:
            return int(name)
        else:
            return self.__names[name]
           
    def execute(self):
        self.__names = {}
        self.__labels = {}
        for index, instr in enumerate(self._instructions):
            if instr.kind == "label":
                self.__labels[instr.label] = index
            
            
        #print("Labels:")
        for l in self.__labels:
            print(l, self.__labels[l])
        
        pc, done  = 0, False
        while not done:
            
            instr = self._instructions[pc]
            #print("Executing ", instr)
            instr_kind = instr.kind
            pc = pc + 1
            
            if instr_kind == "threeaddress":
                dest = instr.addr1
                value = TacExecutable.__EVALUATE[instr.op](
                    self.__lookup_name(instr.addr2),
                    self.__lookup_name(instr.addr3))
                #print("Result %s <- %d" % (dest, value))
                self.__names[dest] = value
            elif instr_kind == "twoaddress":
                dest = instr.addr1
                value = self.__lookup_name(instr.addr2)
                #print("Result %s <- %d" % (dest, value))
                self.__names[dest] = value
            elif instr_kind == "goto":
                pc = self.__lookup_label(instr.label)
            elif instr_kind == "jumptrue":
                if self.__lookup_name(instr.addr1) != 0:
                    pc = self.__lookup_label(instr.label)
            elif instr_kind == "jumpfalse":
                if self.__lookup_name(instr.addr1) == 0:
                    pc = self.__lookup_label(instr.label)
            elif instr_kind == "in":
                value = int(input("? "))
                self.__names[instr.addr1] = value
            elif instr_kind == "out":
                value = self.__lookup_name(instr.addr2)
                print("! %d" % value)
            elif instr_kind == "label":
                pass
            elif instr_kind == "halt":
                done = True
            else:
                pass
                #print("Unknown instruction %s" % str(instr)) 
   

tr = TacReader("fact.tac")
p = tr.program
p.show()

p.execute()
