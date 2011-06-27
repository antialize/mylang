import lex
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
    name=toks[i][1]
    i += 1
    assert(toks[i] == (OP, '('))
    i += 1
    l = []
    while toks[i][0] == glit:
        l.append(toks[i][1])
        i += 1
        assert(toks[i][1] in (',',')'))
        if toks[i][1] == ',': i += 1
    assert(toks[i] == (OP, ')'))
    i += 1
    return (Generator(name, l), i)


def parse_concat(toks, i):
    es=[]
    while i < len(toks):
        if toks[i] == (OP, '('):
            cj, i = parse_condjunction(toks, i+1)
            assert(toks[i] == (OP, ')'))
            i += 1
            es.append(cj)
        elif toks[i][0] in (KEYWORD, GLIT, TLIT):
            if toks[i][0] == KEYWORD:
                e = Keyword(toks[i][1])
            elif toks[i][0] == GLIT:
                e = GrammaRef(toks[i][1])
            else:
                e = TokenRef(toks[i][1])
            i += 1
            if i < len(toks) and toks[i] == (OP, ':'):
                i += 1
                assert(toks[i][0] == GLIT)
                e.output = toks[i][1]
                i += 1
            es.append(e)
        else:
            break

    assert(len(es) != 0)
    if len(es) == 1:
        return (es[0], i)
    return (Concat(es), i)

def parse_condjunction(toks, i):
    cc, i = parse_concat(toks, i)
    if toks[i] != (OP, '|'): return (cc, i)
    ccs = [cc]
    while toks[i] == (OP, '|'):
        cc, i = parse_concat(toks, i+1)
        ccs.append(cc)
    return (Conjunction(ccs), i)


def parse_yield(toks, i):
    e, i = parse_condjunction(toks, i)
    if toks[i] != (OP, "=>"): return (e, i)
    e2, i = parse_gen(toks, i+1)
    return (Yield(e,e2), i)

def parse_gramma(lines):
    lexer = lex.Lexer() 
    
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
            lexer.addClass(name, d)
        else:
            toks = gramma_lex(d)
            for i in range(len(toks)):
                if toks[i][0] != KEYWORD: continue
                toks[i] = (TLIT, lexer.addKeyword(toks[i][1]))
    lexer.generate('python')
    

f = open("../gramma.my","r")
parse_gramma(f.readlines())
