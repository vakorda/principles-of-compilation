"""
Víctor Carnicero Príncipe | 123123895 | Assignment #2 Principles of Compilation 2023-2024

Tiny laguage parser. Parses a Tiny program, builds a parse tree, and
generates a three-address code representation of the program.

Based on:

Tree-walking  compiler for the Kroc programming language. Generates
three-address code. Performs no error checking.

Kieran Herley, June 2020.
"""

import pickle

class TinyCompiler:
    __code = ""
    def __init__(self, sourcepath):
        """ Create a compiler object for Tiny program with a pickled source at
        'sourcepath'.
        """
        # If using the parser uncomment this line
        #self.parse_tree = TinyParser(sourcepath).parse_program()
        p2file = open(sourcepath, "rb")
        self.parse_tree = pickle.load(p2file)
        p2file.close()
        self.name = p2file.name.split(".")[0]
        self.__varcount = 0
        self.__labcount = 0

    @property
    def code(self):
        # read only property
        return self.__code

    def newline(self, str):
        self.__code += str + "\n"

    def save_code(self):
        self.__code = self.__code[:-1] if self.__code[-1] == "\n" else self.__code
        with open(self.name + ".tac", "w") as f:
            f.write(self.__code)

    def __new_label(self):
        self.__labcount += 1
        return f"l{self.__labcount}"
    
    def __new_var(self):
        self.__varcount += 1
        return f"t{self.__varcount}"
    
    def translate(self):
        """ Generate TAC for the Tiny program """
        self.__varcount, self.__labcount = 0, 0
        self.__codegen_program(self.parse_tree)
        self.newline("halt;")
        self.save_code()
    
    def __codegen_program(self, root):
        """Generate TAC for node 'program' in the parse tree"""
        self.__codegen_statement_sequence(root.children[0])

    def __codegen_statement_sequence(self, root):
        """Generate TAC for node 'stmtseq' in the parse tree"""
        for c in root.children:
            self.__codegen_statement(c)
    
    def __codegen_statement(self, root):
        """Generate TAC for node 'statement' in the parse tree"""
        label = root.label
        
        match label:
            case "ifstmt":
                self.__codegen_ifstmt(root)
            case "repeatstmt":
                self.__codegen_repeatstmt(root)
            case "assignstmt":
                self.__codegen_assignstmt(root)
            case "readstmt":
                self.__codegen_readstmt(root)
            case "writestmt":
                self.__codegen_writestmt(root)
            case _:
                self.__codegen_statement(root.children[0])
    
    def __codegen_ifstmt(self, root):
        """Generate TAC for node 'ifstmt' in the parse tree"""
        bottom_label = self.__new_label()
        
        # Condition
        var = self.__codegen_exp(root.children[0])
        self.newline(f"if ({var} == 0) goto {bottom_label}")
        # Statements
        self.__codegen_statement_sequence(root.children[1])
        
        # else
        if len(root.children) == 2:
            self.newline(f"{bottom_label}:")
        else:
            skip_label = self.__new_label()
            self.newline(f"goto {skip_label}")
        
            self.newline(f"{bottom_label}:")
        
            self.__codegen_statement(root.children[2])
            self.newline(f"{skip_label}:")
            
    def __codegen_exp(self, root):
        """Generate TAC for node 'exp' in the parse tree"""
        var = self.__codegen_simple_expr(root.children[0])
        if len(root.children) > 1:
            cvar = self.__codegen_simple_expr(root.children[2])
            self.newline(f"{var} := {var} {root.children[1].children[0].value} {cvar}")
        return var

    def __codegen_repeatstmt(self, root):
        """Generate TAC for node 'repeatstmt' in the parse tree"""
        top_label = self.__new_label()
        
        self.newline(f"{top_label}:")
        self.__codegen_statement_sequence(root.children[0])
        var = self.__codegen_exp(root.children[1])
        self.newline(f"if ({var} == 0) goto {top_label}")
    
    def __codegen_assignstmt(self, root):
        """Generate TAC for node 'assignstmt' in the parse tree"""
        var = self.__codegen_exp(root.children[1])
        self.newline(f"{root.children[0].value} := {var}")
    
    def __codegen_readstmt(self, root):
        """Generate TAC for node 'readstmt' in the parse tree"""
        self.newline(f"{root.children[0].value} := in")

    def __codegen_writestmt(self, root):
        """Generate TAC for node 'writestmt' in the parse tree"""
        var = self.__codegen_exp(root.children[0])
        self.newline(f"out := {var}")

    def __codegen_simple_expr(self, root):
        """Generate TAC for node 'simple-expr' in the parse tree"""
        var = self.__codegen_term(root.children[0])
        if len(root.children) > 1:
            cvar = self.__codegen_term(root.children[2])
            self.newline(f"{var} := {var} {root.children[1].children[0].value} {cvar}")
        return var
    
    def __codegen_term(self, root):
        """Generate TAC for node 'term' in the parse tree"""
        var = self.__codegen_factor(root.children[0])
        for i in range(1, len(root.children), 2):
            cvar = self.__codegen_factor(root.children[i+1])
            self.newline(f"{var} := {var} {root.children[i].children[0].value} {cvar}")
        return var
    
    def __codegen_factor(self, root):
        """Generate TAC for node 'factor' in the parse tree"""
        if root.children[0].label == "leaf":
            var = self.__new_var()
            self.newline(f"{var} := {root.children[0].value}")
        else:
            var = self.__codegen_exp(root.children[0])
        return var

    
if __name__ == "__main__":


    import json

    if run_tests := False:
        if create_files := False:
            with open("teses.json", "r") as f:
                tests = json.load(f)
                for test in tests:
                    with open("tests/" + test["name"] + ".tny", "w") as f:
                        f.write(test["prog"])

        test_cases = []
        with open("proj1/teses.json", "r") as f:
            test_cases = json.load(f)
            test_cases = {test["name"]: test for test in test_cases}

        passed = 0
        failed = 0
        # run tests
        for file in list(test_cases.keys())[0:40]:
            if test_cases[file]["correct"] == "true":
                print("----------------------------------------")
                with open("proj1/tests/" + file + ".tny", "r") as f:
                    print(f.read())
                print("::::::::::::::::::::::::::::::::::::::::")
                parser = TinyCompiler("proj1/tests/" + file + ".tny")
                parser.o__cstart()
                print("----------------------------------------")
                
    else:

        #p2file = open("proj2/examples/readwrite_pt_kh.pkl", "rb")
        compiler = TinyCompiler("proj2/examples/readwrite_pt_kh.pkl")

        #fpath = "./proj1/fact.tny"
        #compiler = TinyCompiler(fpath)
        #print("Compiler output:")
        #print("-" * 25)
        compiler.translate()
        #print("=" * 25)
        #print()





   
   
             
