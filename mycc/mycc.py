#!/usr/bin/python

from lex import Lexer
import sys
from bisect import bisect_left

def isname(c):
    return c.isalnum() or c in "_"

GLIT='glit'
TLIT='tlit'
KEYWORD='keyword'
SLIT='slit'

class Glex:
    def __init__(self, t):
        self.t=t
        self.i=0
        self.line_index=[0]
        x=0
        while True:
            x=t.find("\n",x+1)
            if x == -1: break
            self.line_index.append(x)
            
        self.kws=[':','(',')','+','|','*','?',':=','[]','+=',';','.', 'class', 'return','construct', '{', '}',',','=', 'var','this']
        self.kws.sort(key=lambda x: -len(x))

    def tloc(self, t):
        if not t: return "End of file"
        c=t[2]
        li = bisect_left(self.line_index, c)-1
        x=max(self.line_index[li]+1, c-20)
        y=c+len(t[1])
        z=min(self.line_index[li+1], y+20)
        return "line %d: %s^%s^%s"%(li+1,
                                    self.t[x:c],
                                    self.t[c:y],
                                    self.t[y:z])
    
    def skip(self):
        while self.i < len(self.t):
            if self.t[self.i] in "\n\r\t ":
                self.i += 1
            elif self.t[self.i] == '#':
                while self.i < len(self.t) and self.t[self.i] != '\n':
                    self.i += 1
            else:
                break
        
    def nextToken(self):
        self.skip()

        if self.i >= len(self.t): return None
        for x in self.kws:
            if self.t[self.i:].startswith(x):
                res=(KEYWORD, x, self.i)
                self.i += len(x)
                return res
        if isname(self.t[self.i]):
            j=self.i
            t=None
            while j < len(self.t) and isname(self.t[j]):
                if not t:
                    if self.t[j].islower():
                        t=GLIT
                    elif self.t[j].isupper():
                        t=TLIT
                j += 1
            res = (t, self.t[self.i:j], self.i)
            self.i = j
            return res
        j=self.i
        assert(self.t[self.i] == '"')
        self.i += 1
        while self.t[self.i] != '"':
            if self.t[self.i] == '\\': self.i += 1
            self.i += 1
        self.i += 1
        return (SLIT, self.t[j: self.i], j) 

    def nextRegexp(self):
        self.skip()
        j=self.i
        while j < len(self.t) and self.t[j] not in ("#\r\n"):
            if self.t[j] == '\\': j += 1
            j += 1
        r = self.t[self.i:j].strip()
        self.i=j
        return r

target=sys.argv[1]

class GConstructor:
    def __init__(self):
        self.arguments = []

class GConstructorCall:
    def __init__(self, name):
        self.name = name
        self.arguments = []

    def emit(self, line):
        line.append(self.name[1])
        line.append("(")
        for a in self.arguments:
            a.emit(line)
            line.append(",")
        if not self.arguments: line.append(",")
        line[-1] = ")"

class GType:
    def __init__(self, name):
        self.name = name
        self.isArray = False
        
class GClass:
    def __init__(self, name):
        self.name = name
        self.constructors = []
        self.vardecls = []
        self.extends = []
        
    def emit(self, lines):
        e=""
        if self.extends: e="(%s)"%(", ".join(
            map(lambda (a,b,c): b, self.extends)),)
        lines.append("class %s%s:"%(self.name[1],e))
        lines.append("\tdef __setup_vars__(self):")
        for var in self.vardecls:
            if var.ty.isArray:
                lines.append("\t\tself.%s=[]"%(var.name[1]))
            else:
                lines.append("\t\tself.%s=None"%(var.name[1]))
        lines.append("")
        for c in self.constructors:
            line=["\tdef __init__(self"]
            for n,t in c.arguments:
                line.append(", %s"%n[1])
            line.append("):")
            lines.append("".join(line))
            lines.append("\t\tself.__setup_vars__()")
            c.block.emit(lines, "\t\t")
        #print self.vardecls
        
class GClassVarDecl:
    def __init__(self, name, ty):
        self.name = name
        self.ty = ty
        
class GBlock:
    def __init__(self):
        self.stmts = []

    def emit(self, lines, indent):
        for stmt in self.stmts:
            stmt.emit(lines, indent)
        
class GAssign:
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def emit(self, lines, indent):
        line=[]
        self.var.emit(line)
        line.append("=")
        self.val.emit(line)
        lines.append("%s%s"%(indent, "".join(line)))
        
class GReturn:
    def __init__(self, val):
        self.val = val

    def emit(self, lines, indent):
        line=[]
        self.val.emit(line)
        lines.append("%sreturn %s"%(indent, "".join(line)))

class GAppend:
    def __init__(self, to, val):
        self.to = to
        self.val = val

    def emit(self, lines, indent):
        line=[]
        self.to.emit(line)
        line.append(".append(")
        self.val.emit(line)
        line.append(")")
        lines.append("%s%s"%(indent, "".join(line)))
                    
class GConjunction:
    def __init__(self):
        self.items = []

    def computeFirstToken(self, p):
        self.optional=False
        self.firstToken=set()
        for item in self.items:
            item.computeFirstToken(p)
            if not self.firstToken.isdisjoint(item.firstToken):
                raise ParseError("None disjoint first tokens in conjunction", None)
            self.firstToken.update(item.firstToken)
            if item.optional:
                self.optional=True

    def emit(self, lines, indent):
        lines.append("%sif self.tokenIs(%s):"%(indent, ", ".join(self.items[1].firstToken)))
        self.items[0].emit(lines, indent+"\t")
        for item in self.items[1:-1]:
            lines.append("%selif self.tokenIs(%s):"%(indent, ", ".join(item.firstToken)))
        lines.append("%selse:"%indent)
        self.items[-1].emit(lines, indent+"\t")
            
                         
        
class GContinuation:
    def __init__(self):
        self.items = []

    def computeFirstToken(self, p):
        for item in self.items:
            if isinstance(item, GBlock): continue
            item.computeFirstToken(p)
            
        self.optional=False
        self.firstToken=set()
        for item in self.items:
            if isinstance(item, GBlock): continue
            if not self.firstToken.isdisjoint(item.firstToken):
                raise ParseError("Foobar")
                
            self.firstToken.update(item.firstToken)
            if not item.optional: return
        self.optional=True


    def emit(self, lines, indent):
        for item in self.items:
            if isinstance(item, GBlock):
                item.emit(lines, indent)
                continue
            if not item.optional:
                lines.append("%sself.tokenAssert(%s)"%(indent, ",".join(item.firstToken)))
            item.emit(lines, indent)
                
class GTokenRef:
    def __init__(self, t):
        self.token = t
        self.tname = t[1]
        self.displayName = None
        self.name = None

    def computeFirstToken(self, p):
        self.firstToken=set([self.tname])
        self.optional=False

    def emit(self, lines, indent):
        if self.name:
            lines.append("%s%s=self.currentToken()"%(indent, self.name[1]))
        lines.append("%sself.nextToken()"%indent)
        
class GGrammaRef:
    def __init__(self, t):
        self.gramma = t
        self.name = None

    def computeFirstToken(self, p):
        self.firstToken, self.optional = p.computeRuleFirstToken(self.gramma)

    def emit(self, lines, indent):
        lines.append("%sself.parse_%s()"%(indent, self.gramma[1]))
        
class GOpt:
    def __init__(self, t):
        self.inner = t

class GThislookup:
    def __init__(self, t):
        self.this = t
        
    def emit(self, line):
        line.append("self")
        
class GVarlookup:
    def __init__(self, t):
        self.name = t

    def emit(self, line):
        line.append(self.name[1])

class GClasslookup:
    def __init__(self, on, name):
        self.on = on
        self.name = name

    def emit(self, line):
        self.on.emit(line)
        line.append(".")
        line.append(self.name[1])
            
class GStar:
    def __init__(self, t):
        self.inner = t

    def computeFirstToken(self, p):
        self.inner.computeFirstToken(p)
        self.firstToken = self.inner.firstToken
        self.optional=True

    def emit(self, lines, indent):
        lines.append("%swhile self.tokenIs(%s):"%(indent, ", ".join(self.firstToken)))
        self.inner.emit(lines, indent+"\t")
        
class GPlus:
    def __init__(self, t):
        self.inner = t

class ParseError(BaseException):
    def __init__(self, msg, tok):
        self.msg = msg
        self.tok = tok

class GParser:
    def __init__(self, gramma):
        self.gl = Glex(open(gramma).read())
        self.lexer = Lexer()
        self.classes = []
        self.rules = {}
        
    def gnt(self):
        self.nt = self.gl.nextToken()

    def tis(self, t, v=None):
        if not self.nt: return False
        return self.nt[0] == t and (not v or self.nt[1]==v)

    def tass(self, t, v=None):
        if self.tis(t, v): return
        if v:
            raise ParseError("Expected '%s'"%v, self.nt)
        else:
            raise ParseError("Expected %s"%t, self.nt)

    def parseType(self):
        self.tass(TLIT) #Name
        t = GType(self.nt)
        self.gnt()
        if self.tis(KEYWORD, '[]'):#In an array
            t.isArray=True
            self.gnt()
        return t
    
    def parseExpr(self):
        if self.tis(TLIT):
            c = GConstructorCall(self.nt)
            self.gnt()
            self.tass(KEYWORD, '(')
            self.gnt()
            if not self.tis(KEYWORD,')'):
                while True:
                    c.arguments.append(self.parseExpr())
                    if not self.tis(KEYWORD,','): break
                    self.gnt()

            self.tass(KEYWORD, ')')
            self.gnt()
            return c
        if self.tis(KEYWORD, 'this'):
            x = GThislookup(self.nt)
        else:
            self.tass(GLIT)
            x = GVarlookup(self.nt)
        self.gnt()
        while True:
            if not self.tis(KEYWORD, '.'): break
            self.gnt()
            self.tass(GLIT)
            x = GClasslookup(x, self.nt)
            self.gnt()
        return x

                 
    def parseBlock(self):
        b = GBlock()
        while True:
            if self.tis(KEYWORD,'var'):
                v = GVar()
                self.gnt()
                self.tass(GLIT);
                v.name = self.nt
                self.gnt()
                self.tass(KEYWORD, ':')
                self.gnt()
                self.tass(TLIT);
                v.type = self.nt
                self.gnt()
                self.tass(KEYWORD, ';')
                self.gnt()
                b.stmts.append(v);
                continue
            if self.tis(KEYWORD,'return'):
                self.gnt()
                b.stmts.append(GReturn(self.parseExpr()));
                self.tass(KEYWORD, ';')
                self.gnt()
                continue
            if not self.tis(GLIT) and not self.tis(TLIT) and not self.tis(KEYWORD,'this'): break
            e=self.parseExpr()
            if self.tis(KEYWORD, '+='):
                self.gnt()
                e=GAppend(e,self.parseExpr())
            elif self.tis(KEYWORD, '='):
                self.gnt()
                e=GAssign(e,self.parseExpr())
            self.tass(KEYWORD, ';')
            self.gnt()
            b.stmts.append(e)
        return b
     
    def parseClass(self):
        self.gnt()
        self.tass(TLIT) #Name
        c = GClass(self.nt)
        self.gnt()

        if self.tis(KEYWORD, '('):
            self.gnt()
            while True:
                self.tass(TLIT) #Extend name
                c.extends.append(self.nt)
                self.gnt()
                if not self.tis(KEYWORD, ','): break
                self.gnt()
            self.tass(KEYWORD, ')')
            self.gnt()
            
        self.tass(KEYWORD, '{')
        self.gnt()
        while True:
            if self.tis(KEYWORD,'construct'):
                con = GConstructor()
                self.gnt()
                self.tass(KEYWORD, '(')
                self.gnt()
                while True:
                    self.tass(GLIT) #Name
                    n=self.nt
                    self.gnt()
                    self.tass(KEYWORD, ':')
                    self.gnt()
                    t=self.parseType()
                    con.arguments.append( (n,t) )
                    if not self.tis(KEYWORD,','): break
                    self.gnt()
                self.tass(KEYWORD, ')')
                self.gnt()
                self.tass(KEYWORD, '{')
                self.gnt()
                con.block = self.parseBlock()
                self.tass(KEYWORD, '}')
                self.gnt()
                c.constructors.append(con)
            elif self.tis(KEYWORD, 'var'):
                self.gnt()
                self.tis(GLIT)
                n = self.nt
                self.gnt()
                self.tass(KEYWORD, ':')
                self.gnt()
                ty = self.parseType()
                self.tass(KEYWORD, ';')
                self.gnt()
                c.vardecls.append(GClassVarDecl(n, ty))
            else:
                break

        self.tass(KEYWORD, '}')    
        self.gnt()
        return c

    def parseContinuation(self):
        r = GContinuation()
        while True:
            if self.tis(KEYWORD, '{'):
                self.gnt()
                r.items.append(self.parseBlock())
                self.tass(KEYWORD, '}')
                self.gnt()
                continue
            x=None
            if self.tis(KEYWORD, '('):
                self.gnt()
                x=self.parseConjunction()
                self.tass(KEYWORD, ')')
                self.gnt()
            else:
                if self.tis(SLIT):
                    x=GTokenRef(self.nt)
                    v = self.nt[1][1:-1]
                    x.tname = self.lexer.addKeyword(v)
                    x.displayname = v
                    self.gnt()
                elif self.tis(TLIT):
                    x=GTokenRef(self.nt)
                    self.gnt()
                elif self.tis(GLIT):
                    x=GGrammaRef(self.nt)
                    self.gnt()
                else:
                    break
                if self.tis(KEYWORD, ':'):
                    self.gnt()
                    self.tass(GLIT)
                    x.name = self.nt
                    self.gnt()
            if self.tis(KEYWORD, '*'):
                x = GStar(x)
                self.gnt()
            elif self.tis(KEYWORD, '+'):
                x = GPlus(x)
                self.gnt()
            elif self.tis(KEYWORD, '?'):
                x = GOpt(x)
                self.gnt()
            r.items.append(x)
        return r
    
    def parseConjunction(self):
        r = self.parseContinuation()
        if self.tis(KEYWORD,'|'):
            c=GConjunction()
            c.items.append(r)
            r=c
        while self.tis(KEYWORD,'|'):
            self.gnt()
            r.items.append(self.parseContinuation())
        return r
    
    def parse(self):
        try:
            self.gnt()
            while self.nt:
                if self.tis(TLIT):
                    v = self.nt[1]
                    self.gnt()
                    self.tass(KEYWORD, ':=')
                    r = self.gl.nextRegexp()
                    self.lexer.addClass(v, r)
                    self.gnt()
                    continue
                if self.tis(KEYWORD, 'class'):
                    self.classes.append(self.parseClass())
                    continue
                self.tass(GLIT)
                v = self.nt
                self.gnt()
                self.tass(KEYWORD, ':=')
                self.gnt()
                self.rules[v[1]] = (v, self.parseConjunction())
                self.tass(KEYWORD, ';')
                self.gnt()
        except ParseError, e:
            print "ParseError: %s\nat %s"%(e.msg, self.gl.tloc(e.tok))


    def computeRuleFirstToken(self, tok):
        rule=tok[1]
        if not rule in self.rules:
            raise ParseError("Unknow gramma rule reference", tok) 
        r = self.rules[rule][1]
        if not rule in self.computed:
            if rule in self.current:
                raise ParseError("Left recurtion found", tok)
            self.current.add(rule)
            r.computeFirstToken(self)
            self.current.remove(rule)
        return (r.firstToken, r.optional)
    
    def computeFirstTokens(self):
        try:
            self.computed = set()
            self.current = set()
            for rule in self.rules:
                self.computeRuleFirstToken(self.rules[rule][0])
        except ParseError,e :
            print "ParseError: %s\nat %s"%(e.msg, self.gl.tloc(e.tok))   

    def emitParser(self, lang):
        lines=["""
class Parser:
\tdef __init__(self, i):
\t\tself.input = i+'\\0'
\t\tself.__setupLexer__()
"""]

        lines += self.lexer.generate(lang)
        for rule in self.rules:
            lines.append("\tdef parse_%s(self):"%(rule))
            self.rules[rule][1].emit(lines, "\t\t")
            lines.append("")
        return "\n".join(lines)


    def emitClasses(self, lang):
        lines=[]
        for c in self.classes:
            c.emit(lines)
        return "\n".join(lines)
            
gparser = GParser(sys.argv[2])
gparser.parse()
gparser.computeFirstTokens()

print "Generating ast classes"
f = open(sys.argv[4],'w')
f.write(gparser.emitClasses("python"))

f = open(sys.argv[3],'w')
print "Generating parser and lexer"
f.write(gparser.emitParser("python"))

