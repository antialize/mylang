import lex

GLIT='glit'
TLIT='tlit'
KEYWORD='keyword'
OP='op'

class TreeClass:
    def __init__(self):
        self.vars=[]
        self.constructor=None

class Condjunction:
    def __init__(self):
        self.subjects=[]

class Star:
    def __init__(self):
        self.inner=None

class Concat:
    def __init__(self):
        self.subjects=[]

class RuleRef:
    def __init__(self):
        self.rule=""

class Token:
    def __init__(self):
        self.tok=""

class Emition:
    def __init__(self):
        self.statements = []

class Parser:
    def __init__(self):
        self.GLIT = GLIT
        self.TLIT = TLIT
        self.KEYWORD = KEYWORD
        self.OP = OP
        
    def lex(self, line):
        i=0
        toks=[]
        while i < len(line):
            if line[i] == ' ':
                i += 1
            elif line[i] in ['(',')','+','|','*','?',':']:
                toks.append( (OP,line[i]) )
                i += 1
            elif i+1 < len(line) and line[i:i+2] == '=>':
                toks.append( (OP, line[i:i+2]) )
                i += 2
            elif line[i].islower():
                j=i
                while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'): j += 1
                toks.append( (GLIT, line[i:j]) )
                i=j
            elif line[i].isupper():
                j=i
                while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'): j += 1
                toks.append( (TLIT, line[i:j]) )
                i=j
            elif line[i] == '"':
                j=i+1
                while line[j] != '"': j += 1
                toks.append( (KEYWORD, line[i+1:j] ) )
                i=j+1
            else:
                raise Exception("Bad gramma, unexpected bad token '%s'"%line[i:])
        return toks


    # def parseCmd(self, i, toks):
    #     self.atok(toks, i, GLIT)
    #     n=[toks[i]]
    #     i += 1
    #     while self.ctok(toks, i, OP, '.'):
    #         self.atok(toks, i+1, GLIT)
    #         n.append(toks[i+1])
    #         i += 2
    def parseYield(self, i, toks):
        i, r = parseCondjunction(i, toks)
        
        if not self.ctok(toks, i, OP, '=>'):
            return (i,r)
        self.atok(toks,i+1, TLIT)
        cname = toks[i+1]
        self.atok(toks,i+2, OP, '(')
        i += 3
        args = []
        while not self.ctok(toks, i, OP, ')'):
            self.atok(toks, i, GLIT)
            n1=toks[i]
            n2=toks[i]
            i += 1
            if self.ctok(toks, i, OP, ':'):
                self.atok(toks, i+1, GLIT)
                n2 = toks[i+1]
                i += 2
            if self.ctok(toks, i, OP, ','):
                i += 1
            args.append( (n1,n2) )

        g = Generator(cname, args)
        

        if self.ctok(toks, i, OP, ','):
            self.atok(toks, i+1, GLIT)
            
        return Generator()
        
    def addRule(self, tokens):
        print tokens
        pass

    def generate(self, target):
        return []


