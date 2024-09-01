#
# Simple lexical scanner for Kroc programming language
# Bare-bones implementation with no error checking.
#
# Kieran Herley, June 2020
#
#
# Notes:
# 1) Python-style # comments only (no /* */)
# 2) variable names-- letters only
# 3) unsigned integer constants only

import re
import sys
import traceback

# Define RE to caputure Kroc comments.
COMMENT_RE = re.compile(r"#.*\n")

# Define RE to capture Kroc tokens.
TOKENS_RE = re.compile(r"[a-z]+"
                       r"|[0-9]+"
                       r"|[(){}+*/;\-]"
                       r"|==|!=|<=|<|>=|>|="
    )

# Define Kroc's reserved words and their labels. 'EOS' (end of scource
# symbol) is treated as an honorary reserved word.
RESERVED_WORDS = {
    "read" : "READ", "write" : "WRITE", "while" : "WHILE", 
    "if" : "IF", "else" : "ELSE", "EOS" : "EOS"
    }

# Define Kroc's repertiore of symbols and their labels.
SYMBOLS = {
    "{" : "CLPAREN", "}" : "CRPAREN", ";" : "SEMI", 
    "(" : "LPAREN", ")" : "RPAREN", "=" : "ASSIGN",
    "<=" : "LTE", "<" : "LT",  ">" : "GT",  
    ">=" : "GTE", "==" : "EQ",  "!=" : "NOTEQ",
    "+" : "PLUS",  "-" : "MINUS", "*" : "TIMES", 
    "/" : "OVER", "STATEMENT" : "STATEMENT"
    }

LOGPAD = " " * 10

class KrocToken:
    """ Implement class to represent Kroc token objects.
    """
    def __init__(self, tkn):
        """ Create a token object for 'tkn'.
        Public members:
           string: string representation of thsi token
           kind: label for this token
           value: numerical value (integers only)
        """
        self.string = tkn
        self.value = tkn
        
        if tkn.isalpha():
            self.spelling = tkn
            if tkn in RESERVED_WORDS:
                self.kind = RESERVED_WORDS[tkn]
            else:
                self.kind = "ID"
                #self.value = tkn
        elif tkn.isdigit():
            self.kind = "INT"
            self.value = int(tkn)
        elif tkn in SYMBOLS:
            self.kind = SYMBOLS[tkn]
        else:
            self.shriek("Illegal symbol '%s'." % tkn)
    
    def __repr__(self):
        """ Return string representation of this token. """
        return str(self.__dict__)

    def __str__(self):
        """ Return string representation of this token. """
        return ("[Token: '%s' (%s)]" 
               % (self.string, self.kind) )

class KrocScanner:
    """ Implement class to perform lexical analysis on Kroc source.
    """
   
    def __init__(self, fpath, verbose = False):
        """ Create scanner object wrapped around file at path 'fpath'.
        """
        try:
            self.__source = open(fpath, "r").read()
        except Exception:
            traceback.print_exc()
            sys.exit(-1)
            
        # Set verbose/silent output.
        self.verbose = verbose
            
        # Eliminate comments.
        self.__source = COMMENT_RE.sub("", self.__source)
        
        # Set up token sequence.
        self.__tokens = TOKENS_RE.findall(self.__source)
        self.__tokens.append("EOS")
       
        # Tee up the first token.
        self.current = None
        self.advance()
    
    def __next_token(self):
        """ Return the next token (or None).
        """
        if self.current != "EOS":
            tkn =  self.__tokens.pop(0)
            return KrocToken(tkn)
        else:
            return None
        
    def shriek(self, msg):
        """ Print error message 'msg' and terminate execution.
        """
        self.log("*** KrocScanner: %s" % msg, pad = False)
        sys.exit(-1)
     
    def log_nopad(self, msg):
        """ Print 'msg'. """
        if self.verbose:
            print(msg)
        
    def log(self,  msg, pad = True):
        """ Print 'msg'.  Indent if 'pad' is set. """
        if self.verbose:
            print("%s%s" % (LOGPAD if pad else "", msg)) 
        
    def has_more(self):
        """ Return True if some tokens yet unread.
        """
        return len(self.__tokens) > 0
  
    def advance(self):
        """ Advance one token forward.
        """
        if self.has_more:
            self.current = self.__next_token()
            self.log_nopad("['%s']" % self.current.string)
       
    def match(self, expected):
        """ If current token matches 'expected', then advance one token 
        forward, otherwise issue error and terminate.
        """
        val = self.current.value
        if self.current.kind != expected:
           self.shriek("Expected '%s', saw '%s'." 
                % (expected, self.current.string))
  
        self.advance()
        return val
  
if __name__ == "__main__":

    fpath = "./proj1/examples/write17.krc"
  
    scanner = KrocScanner(fpath, verbose = True)

    print(scanner.__dict__)
    while scanner.has_more():
        print(repr(scanner.current))
        scanner.advance()
    print("Done.")

    print(scanner.__dict__)