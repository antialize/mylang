"""
Gramma gramma

GRAMMA := (TOKEN_DECL | GRAMMA_DEC | ) (#.*)? <nl>



GRAMMA_DECL := IDENT ":=" OR_EXPR

"""

GLIT='glit'
TLIT='tlit'
KEYWORD='keyword'
OP='op'

def gramma_lex(line):
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


def parse_gen(toks, i):
    assert(toks[i][0] == TLIT)
    i += 1
    assert(toks[i] == (OP, '('))
    i += 1
    l = []
    while toks[i][0] == glit:
    
    
    assert(toks[i] == (OP, ')'))
           
    
def parse_yield(toks, i):
    e, i = parse_condjunction(toks, i)
    if toks[i] != (OP, "=>"): return (e, i)
    e2, i = parse_gen(toks, i+1)
    return (YieldStmt(e,e2), i)
        

def parse_gramma(lines):
    for line in lines:
        i=0
        while i < len(line):
            if line[i] == '\\':
                i += 2
            elif line[i] == '#':
                break
            else:
                i += 1
        line = line[:i].strip()
        if not line: continue
        
        name, d = map(str.strip, line.split(":=",1))
        if name[0].isupper():
            print name, d
        else:
            toks = gramma_lex(d)
            print toks
    

f = open("../gramma.my","r")
parse_gramma(f.readlines())
