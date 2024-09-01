"""
Tree-walking  compiler for the Kroc programming language. Generates
three-address code. Performs no error checking.

Kieran Herley, June 2020.

To Do:
1) Divert output to file rather than standard output.
2) Use __t123 and __l456 convention for tmporary variables and labels.
"""

from proj1.examples.kroc_parser_tree import *
from proj1.tiny_parser import *
from pt_node import *
import sys

class TinyCompiler:

    def k__init__(self, sourcepath):
        """ Create a compiler object for Kroc program with source at
        'sourcepath'.
        """
        self.parse_tree = KrocParser(sourcepath).parse_program()
        self.__varcount = 0
        self.__labcount = 0
      
    def translate(self):
        """ Generate three-address code for the Kroc program represented
        by the parse-tree name 'parse_tree'. Output appears in standard
        output. 
        """
        self.__varcount, self.__labcount = 0, 0
        self.__codegen(self.parse_tree)
        print("halt;")

    def __codegen_condition(self, root):
        """ Generate TAC for condition represented by subtree 'root'.
        """
        conditvar = self.__new_var()
        e1var = self.__codegen_expression(root.children[0])
        
        if len(root.children) == 1:
            print("%s := %s;" % (conditvar, e1var))
        else:
            relop = root.children[1].value
            e2var = self.__codegen_expression(root.children[2])
            print("%s := %s %s %s;" % (conditvar, e1var, relop, e2var))
        
        return conditvar

    def __codegen_expression(self, root):
        """ Generate TAC for expression represented by subtree 'root'.
        """
        total_var = self.__new_var()
        print("%s := 0;" % total_var)
        op = "+"
        for c in root.children:
            if c.label == "term":
                tvar = self.__codegen_term(c)
                print("%s := %s %s %s;" % (total_var, total_var, op, tvar))
            else:
                op = c.value
        return total_var

    def __codegen_term(self, root):
        """ Generate TAC for subexpression represented by subtree 'root'.
        """
        total_var = self.__new_var()
        print("%s := 1;" % total_var)
        op = "*"
        for c in root.children:
            if c.label == "factor":
                fvar = self.__codegen_factor(c)
                print("%s := %s %s %s;" % (total_var, total_var, op, fvar))
            else:
                op = c.value
        return total_var

    def __codegen_factor(self, root):
        """ Generate TAC for subexpression represented by subtree 'root'.
        """
        fval = root.value
        if type(fval) == int:
            var = self.__new_var()
            print("%s := %d;" % (var, fval))
            return var
        elif type(fval) == str:
            var = self.__new_var()
            print("%s := %s;" % (var, fval))
            return var
        else:
            exprvar = self.__codegen_expression(root.children[0])
            return exprvar

    def __codegen_read(self, root):
        """ Generate TAC for read statement represented by subtree 'root'.
        """
        varname = root.value
        print("%s := in;" % varname)

    def __codegen_write(self, root):
        """ Generate TAC for write statement represented by subtree 
        'root'.
        """
        exprvar = self.__codegen_expression(root.children[0])
        print("out := %s;" % exprvar)

    def __codegen_assign(self, root):
        """ Generate TAC for assignment statement represented by subtree 
        'root'.
        """
        destvar = root.value
        rhsvar = self.__codegen_expression(root.children[0])
        print("%s := %s;" % (destvar, rhsvar))

    def __codegen_selection(self, root):
        """ Generate TAC for if statement represented by subtree 
       'root'.
        """
        skiptrue_label = self.__new_label()
        conditvar = self.__codegen_condition(root.children[0])
        print("if (%s == 0) goto %s" % (conditvar, skiptrue_label))
        self.__codegen(root.children[1])
        
        if len(root.children) <= 2:
            print("%s:" % skiptrue_label)
        else:
            skipfalse_label = self.__new_label()
            print("goto %s;" % skipfalse_label)
            print("%s:" % skiptrue_label)
            self.__codegen(root.children[2])
            print("%s:" % skipfalse_label)

    def __new_var(self):
        """ Generate and return fresh temporray variable name.
        """
        self.__varcount += 1
        return "t%d" % self.__varcount

    def __new_label(self):
        """ Generate and return fresh label name.
        """
        self.__labcount += 1
        return "l%d" % self.__labcount
        
    def __codegen_iteration(self, root):
        """ Generate TAC for while statement represented by subtree 
        'root'.
        """
        top_label = self.__new_label()
        bottom_label = self.__new_label()
        
        print("%s:" % top_label)
        conditvar = self.__codegen_condition(root.children[0])
        print("if (%s == 0) goto %s" % (conditvar, bottom_label))
        
        self.__codegen(root.children[1])
        print("goto %s" % top_label)
        print("%s:" % bottom_label)

    def __codegen_statement_list(self, root):
        """ Generate TAC for statement list represented by subtree 
        'root'.
        """
        for c in root.children:
            self.__codegen(c)

    def __codegen(self, root):
        """ Generate TAC for onstruct represented by subtree 
        'root'.
        """
        label = root.label
        children = root.children
        value = root.value
        
        actions = {
        "read_stmt" : self.__codegen_read,
        "write_stmt" : self.__codegen_write,
        "assign_stmt" : self.__codegen_assign,
        "selection_stmt" : self.__codegen_selection,
        "iteration_stmt" : self.__codegen_iteration,
        "statement_list" : self.__codegen_statement_list
        }
        if label in actions:
            actions[label](root)
        else:
            self.__codegen(children[0])

    def __init__(self, sourcepath):
        """ Create a compiler object for Kroc program with source at
        'sourcepath'.
        """
        self.oparse_tree = TinyParser(sourcepath).parse_program()
        #self.oparse_tree.dump()
        self.o__varcount = 0
        self.o__labcount = 0

    def o__new_label(self):
        self.o__labcount += 1
        return f"l{self.o__labcount}"
    
    def o__new_var(self):
        self.o__varcount += 1
        return f"t{self.o__varcount}"
    
    def o__cstart(self):
        # start
        self.o__varcount, self.o__labcount = 0, 0
        self.o__cp(self.oparse_tree)
        print("halt;")
    
    def o__cp(self, root):
        # program
        self.o__css(root.children[0])

    def o__css(self, root):
        # statement sequence
        for c in root.children:
            self.o__cs(c)
    
    def o__cs(self, root):
        # statement
        label = root.label
        
        match label:
            case "ifstmt":
                self.o__ci(root)
            case "repeatstmt":
                self.o__cru(root)
            case "assignstmt":
                self.o__ca(root)
            case "readstmt":
                self.o__crd(root)
            case "writestmt":
                self.o__cw(root)
            case _:
                self.o__cs(root.children[0])
    
    def o__ci(self, root):
        # if
        bottom_label = self.o__new_label()
        
        # Condition
        self.o__ce(root.children[0])
        print(f"if (t{self.o__varcount} == 0) goto {bottom_label}")
        # Statements
        self.o__css(root.children[1])
        
        # Else
        if len(root.children) > 2:
            self.o__cs(root.children[2])

        print(f"{bottom_label}:")
    
    def o__ce(self, root):
        # exp
        var = self.o__new_var()
        self.o__cse(root.children[0])
        if len(root.children) > 1:
            self.o__cse(root.children[2])
            print(f"t{var} := t{self.o__varcount - 1} {root.children[1].value} t{self.o__varcount}")

    def o__cru(self, root):
        # repeat until
        top_label = self.o__new_label()
        
        print(f"{top_label}:")
        self.o__css(root.children[0])
        self.o__ce(root.children[1])
        print(f"if (t{self.o__varcount} == 0) goto {top_label}")
    
    def o__ca(self, root):
        # assign
        self.o__ce(root.children[0])
        print(f"{root.value} := t{self.o__varcount}")
    
    def o__crd(self, root):
        # read
        print(f"{root.value} := in")

    def o__cw(self, root):
        # write
        self.o__ce(root.children[0])
        print(f"out := t{self.o__varcount}")

    def o__cse(self, root):
        # simple expression
        self.o__ct(root.children[0])
        if len(root.children) > 1:
            self.o__ct(root.children[2])
            print(f"t{self.o__varcount} := t{self.o__varcount - 1} {root.children[1].value} t{self.o__varcount}")
    
    def o__ct(self, root):
        # term
        self.o__cf(root.children[0])
        if len(root.children) > 1:
            self.o__cf(root.children[2])
            print(f"t{self.o__varcount} := t{self.o__varcount - 1} {root.children[1].value} t{self.o__varcount}")
    
    def o__cf(self, root):
        # factor
        if root.value is not None:
            var = self.o__new_var()
            print(f"t{var} := {root.value}")
        else:
            self.o__ce(root.children[0])
    
if __name__ == "__main__":

    fpath = "./proj1/fact.tny"
    compiler = TinyCompiler(fpath)
    print("Compiler output:")
    print("-" * 25)
    compiler.o__cstart()
    print("=" * 25)
    print()




   
   
             
