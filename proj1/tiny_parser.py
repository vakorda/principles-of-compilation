"""
Víctor Carnicero Príncipe | 123123895 | Assignment #1 Principles of Compilation 2023-2024

Parser for Tiny language based on:

Tree-building parser for Kroc programming language. Returns
a complete parse tree. No attempt to optimize tree.

Kieran Herley, June 2020.
"""

"""
Tiny grammar without left recursion:

<program> ::= <stmtseq>
<stmtseq> ::= <statement> {; <statement>}
<statement> ::= <ifstmt>
            |   <repeatstmt>
            |   <assignstmt>
            |   <readstmt>
            |   <writestmt>
<ifstmt> ::= if <exp> then <stmtseq> end
         |   if <exp> then <stmtseq> else <stmtseq> end
<repeatstmt> ::= repeat <stmtseq> until <exp>
<assignstmt> ::= identifier := <exp>
<readstmt> ::= read identifier
<writestmt> ::= write <exp>
<exp> ::= <simple-expr> {<comp-op> <simple-expr>}
<comp-op> ::= < | =
<simple-expr> ::= <term> {<addop> <term>}
<addop> ::= + | -
<term> ::= <factor> {<mulop> <factor>}
<mulop> ::= * | /
<factor> ::= ( <exp> ) | number | identifier
"""

from proj1.tiny_scanner import *

try :
    from pt_node import *
except:
    class PTNode():
        """
        Implementation of generic parser-tree node.
        """
        label: str
        value: str
        children: [PTNode]

        def __init__(self, label, children, value = None):
            self.label = label
            self.value = value
            self.children = children
            
        def __str__(self):
            if self.value is None:
                return f"[{self.label}]"
            elif type(self.value) == str:
                return f"[{self.label} ('{self.value}')]"
            else:
                return f"[{self.label} ({str(self.value)})]"
        
        def dump(self, level = 0):
            print("   " * level + str(self))
            for c in reversed(self.children):
                c.dump(level + 1)


class TinyParser:
    
    def __init__(self, fpath):
        self.__scanner = TinyScanner(fpath)

    def parse_program(self):
        """
        <program> ::= <stmtseq>
        """
        c = [self.parse_stmtseq()]
        if (self.__scanner.has_more()):
            self.__scanner.shriek("Error, expected end of statement sequence.")
        return PTNode("program", c)

    def parse_stmtseq(self):
        """
        <stmtseq> ::= <statement> {; <statement>}
        """
        c = [self.parse_stmt()]
        while self.__scanner.current.kind == "SEMI":
            self.__scanner.match("SEMI")
            c.append(self.parse_stmt())
        return PTNode("stmtseq", c)

    def parse_stmt(self):
        """
        <statement> ::= <ifstmt>
                    |   <repeatstmt>
                    |   <assignstmt>
                    |   <readstmt>
                    |   <writestmt>
        """
        c = []
        if self.__scanner.current.kind == "IF":
            c.append(self.parse_ifstmt())
        elif self.__scanner.current.kind == "REPEAT":
            c.append(self.parse_repeatstmt())
        elif self.__scanner.current.kind == "ID":
            c.append(self.parse_assignstmt())
        elif self.__scanner.current.kind == "READ":
            c.append(self.parse_readstmt())
        elif self.__scanner.current.kind == "WRITE":
            c.append(self.parse_writestmt())
        else:
            self.__scanner.shriek("Error, expected statement.")
        return PTNode("statement", c)

    def parse_ifstmt(self):
        """
        <ifstmt> ::= if <exp> then <stmtseq> end
                |   if <exp> then <stmtseq> else <stmtseq> end
        """
        self.__scanner.match("IF")
        c=[self.parse_exp()]
        self.__scanner.match("THEN")
        c.append(self.parse_stmtseq())
        if self.__scanner.current.kind == "ELSE":
            self.__scanner.match("ELSE")
            c.append(self.parse_stmtseq())
            self.__scanner.match("END")
        elif self.__scanner.current.kind == "END":
            self.__scanner.match("END")
        else:
            self.__scanner.shriek("Error, expected END or ELSE.")
        return PTNode("ifstmt", c)

    def parse_repeatstmt(self):
        """
        <repeatstmt> ::= repeat <stmtseq> until <exp>
        """
        self.__scanner.match("REPEAT")
        c = [self.parse_stmtseq()]
        self.__scanner.match("UNTIL")
        c.append(self.parse_exp())
        return PTNode("repeatstmt", c)

    def parse_assignstmt(self):
        """
        <assignstmt> ::= identifier := <exp>
        """
        val = self.__scanner.match("ID")
        self.__scanner.match("ASSIGN")
        c = [self.parse_exp()]
        return PTNode("assignstmt", [PTNode("leaf", [], value = val.value)] + c)

    def parse_readstmt(self):
        """
        <readstmt> ::= read identifier
        """
        self.__scanner.match("READ")
        id = self.__scanner.match("ID")
        return PTNode("readstmt", [PTNode("leaf", [], value = id.value)])

    def parse_writestmt(self):
        """
        <writestmt> ::= write <exp>
        """
        self.__scanner.match("WRITE")
        c = [self.parse_exp()]
        return PTNode("writestmt", c)

    def parse_exp(self):
        """
        <exp> ::= <simple-expr> {<comp-op> <simple-expr>}
        """
        c = [self.parse_simple_expr()]
        while self.__scanner.current.kind in {"LT", "EQ"}:
            c.append(self.parse_compop())
            c.append(self.parse_simple_expr())
        return PTNode("exp", c)

    def parse_compop(self):
        """
        <comp-op> ::= < | =
        """
        if self.__scanner.current.kind in {"LT", "EQ"}:
            val = self.__scanner.match(self.__scanner.current.kind)
        else:
            self.__scanner.shriek("Error, expected comparison operator.")
        return PTNode("comp-op", [PTNode("leaf", [], value = val.value)])

    def parse_simple_expr(self):
        """
        <simple-expr> ::= <term> {<addop> <term>}
        """
        c = [self.parse_term()]
        while self.__scanner.current.kind in {"PLUS", "MINUS"}:
            c.append(self.parse_addop())
            c.append(self.parse_term())
        return PTNode("simple-expr", c)

    def parse_addop(self):
        """
        <addop> ::= + | -
        """
        if self.__scanner.current.kind in {"PLUS", "MINUS"}:
            val = self.__scanner.match(self.__scanner.current.kind)
        else:
            self.__scanner.shriek("Error, expected addition operator.")
        return PTNode("addop", [PTNode("leaf", [], value = val.value)])

    def parse_term(self):
        """
        <term> ::= <factor> {<mulop> <factor>}
        """
        c = [self.parse_factor()]
        while self.__scanner.current.kind in {"TIMES", "OVER"}:
            c.append(self.parse_mulop())
            c.append(self.parse_factor())
        return PTNode("term", c)

    def parse_mulop(self):
        """
        <mulop> ::= * | /
        """
        if self.__scanner.current.kind in {"TIMES", "OVER"}:
            val = self.__scanner.match(self.__scanner.current.kind)
        else:
            self.__scanner.shriek("Error, expected multiplication/division operator.")
        return PTNode("mulop", [PTNode("leaf", [], value = val.value)])

    def parse_factor(self):
        """
        <factor> ::= ( <exp> ) | number | identifier
        """
        if self.__scanner.current.kind == "LPAREN":
            self.__scanner.match("LPAREN")
            c = [self.parse_exp()]
            self.__scanner.match("RPAREN")
            return PTNode("factor", c)
        elif self.__scanner.current.kind == "INT":
            val = self.__scanner.match("INT")
            return PTNode("factor", [PTNode("leaf", [], value = val.value)])
        elif self.__scanner.current.kind == "ID":
            val = self.__scanner.match("ID")
            return PTNode("factor", [PTNode("leaf", [], value = val.value)])
        else:
            self.__scanner.shriek("Error, expected factor.")


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
        with open("teses.json", "r") as f:
            test_cases = json.load(f)
            test_cases = {test["name"]: test for test in test_cases}

        passed = 0
        failed = 0
        # run tests
        for file in test_cases:
            pas = True
            parser = TinyParser("tests/" + file + ".tny")
            try:
                ptroot = parser.parse_program()
            except:
                pas = False
            if pas == (True if test_cases[file]["correct"] == "true" else False):
                print("\x1b[32mTest passed: \x1b[0m" + file)
                passed += 1
            else:
                print("\x1b[31mTest failed: \x1b[0m" + file)
                failed += 1
        
        print("\n\x1b[32mPassed: \x1b[0m" + str(passed) + " | \x1b[31mFailed: \x1b[0m" + str(failed))
    else:
        fpath = "./proj1/onetoten.tny"
        parser = TinyParser(fpath)
        ptroot = parser.parse_program()

        print("Parse tree:") 
        print("-" * 25)
        ptroot.dump()
        print("=" * 25)
        print()
    
   



   
   
             
