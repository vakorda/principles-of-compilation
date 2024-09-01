"""
Víctor Carnicero Príncipe | 123123895 | Assignment #1 Principles of Compilation 2023-2024

Scanner for Tiny language Based on:
Simple lexical scanner for Kroc programming language
Bare-bones implementation with no error checking.

Kieran Herley, June 2020
"""

import re
import sys
import traceback
import os

# Define RE to caputure tiny comments.
COMMENT_RE = re.compile(r"\{[^}]*\}")

# Define RE to capture tiny tokens.
TOKENS_RE = re.compile(r"[a-z]+"
                       r"|[0-9]+"
                       r"|[()+*/;\-]"
                       r"|=|<|:="
                       r"|\n"
    )

# Define Kroc's reserved words and their labels. 'EOS' (end of scource
# symbol) is treated as an honorary reserved word.
RESERVED_WORDS = {
    "read" : "READ", "write" : "WRITE", "repeat" : "REPEAT", "until" : "UNTIL",
    "if" : "IF", "else" : "ELSE", "then": "THEN", "end": "END", "EOS" : "EOS"
    }

# Define Kroc's repertiore of symbols and their labels.
SYMBOLS = {
     ";" : "SEMI", "(" : "LPAREN", ")" : "RPAREN", ":=" : "ASSIGN", "<" : "LT",
     "=" : "EQ", "+" : "PLUS",  "-" : "MINUS", "*" : "TIMES", "/" : "OVER", 
     "STATEMENT" : "STATEMENT"
    }

LOGPAD = " " * 10

class TinyToken:
    """ Represents a single token."""
    # The string representation of this token.
    string: str
    # The label for this token.
    kind: str
    # The numerical value of this token (if any).
    value: (int, str)

    def __init__(self, tkn):
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
            print("Illegal symbol '%s'." % tkn)
            sys.exit(-1)


    def __str__(self):
        """ Return string representation of this token. """
        return (f"[Token: '{self.string}' ({self.kind})]")

class TinyScanner:
    """ Lexical scanner for Tiny."""
    # The current token.
    current: TinyToken
    # Verbose/silent output.
    verbose: bool
    # The source file.
    __source: str
    # The current line number.
    __line: int
    # The token sequence.
    __tokens: [str]

    def __init__(self, fpath, verbose = False):
        try:
            self.__source = open(fpath, "r").read()
        except Exception:
            traceback.print_exc()
            sys.exit(-1)
            
        # Set verbose/silent output.
        self.verbose = verbose
        self.__line = 1
        # Eliminate comments.
        self.__source = COMMENT_RE.sub("", self.__source)
        
        # Set up token sequence.
        self.__tokens = TOKENS_RE.findall(self.__source)
        self.__tokens.append("EOS")
       
        # Tee up the first token.
        self.current = None
        self.advance()
    
    @property
    def tokens(self):
        return [tok for tok in self.__tokens if tok != "\n"]
    
    @property
    def line(self):
        return self.__line

    def __next_token(self):
        """ Return the next token (or None)."""
        while self.__tokens[0] == "\n":
            self.__line += 1
            self.__tokens.pop(0)
        if self.current != "EOS":
            tkn =  self.__tokens.pop(0)
            return TinyToken(tkn)
        else:
            return None
        
    def shriek(self, msg):
        """ Print error message 'msg' and terminate execution."""
        print(f"\033[0;31m*** TinyScanner: Line {self.line}, {msg}\x1b[0m")
        sys.exit(-1)
     
    def log_nopad(self, msg):
        """ Print 'msg'. """
        if self.verbose:
            print(msg)
        
    def log(self,  msg, pad = True):
        """ Print 'msg'.  Indent if 'pad' is set. """
        if self.verbose:
            print(f"{LOGPAD if pad else ''}{msg}") 
        
    def has_more(self):
        """ Return True if some tokens yet unread."""
        return len(self.tokens) > 0
  
    def advance(self):
        """ Advance one token forward.
        """
        if self.has_more:
            self.current = self.__next_token()
            self.log_nopad(f"['{self.current.string}']")
       
    def match(self, expected):
        """ If current token matches 'expected', then advance one token 
        forward, otherwise issue error and terminate.
        """
        val = self.current
        if self.current.kind != expected:
           self.shriek(f"Expected '{expected}', saw '{self.current.string}'.")
  
        self.advance()
        return val
  
if __name__ == "__main__":

    fpath = "onetoten.tny"
  
    scanner = TinyScanner(fpath, verbose = False)

    print(scanner.__dict__)
    while scanner.has_more():
        print(repr(scanner.current))
        scanner.advance()
    print("Done.")

    print(scanner.__dict__)