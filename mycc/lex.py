LAMBDA=None

def charRangeToStr(chars):
    l=set([c for c in chars if c == LAMBDA or (ord(c) > 31 and ord(c) < 127)])
    if len(l) == 95: return "*"
    if not LAMBDA in l and len(l) > 87:
        return "^%s"%("".join([chr(i) for i in range(32,127) if not chr(i) in l]))
    r=[]
    if None in l:
        r.append("Lambda")
        l.discard(None)
    t=set([chr(i) for i in range(ord('0'), ord('9')+1)])
    if t.issubset(l):
        l.difference_update(t)
        r.append("0-9")
    t=set([chr(i) for i in range(ord('a'), ord('z')+1)])
    if t.issubset(l):
        l.difference_update(t)
        r.append("a-z")
    t=set([chr(i) for i in range(ord('A'), ord('Z')+1)])
    if t.issubset(l):
        l.difference_update(t)
        r.append("A-Z")
    r+=l
    return "".join(r)

class FA:
    def __init__(self):
        self.states = []
        self.nextState = 0
        self.trans = {}
        self.acc = {}

    def accept(self, s, val):
        self.acc[s] = val

    def addState(self):
        i = self.nextState
        self.nextState += 1
        self.states.append(i)
        self.trans[i] = {}
        return i

    def setTransition(self, src, dst, ch):
        self.trans[src][ch] = dst

    def __str__(self):
        res = [str(self.acc)]
        for s in self.states:
            ch={}
            for d in self.states:
                ch[d] = []
            for c in self.trans[s]:
                d = self.trans[s][c]
                ch[d].append(c)
            for d in self.states:
                if not ch[d]: continue
                a=""
                if s in self.acc: a=" acc:%d"%(self.acc[s])
                res.append("%d => %d [label=%s%s]"%(s, d, charRangeToStr(ch[d]), a))
        return "\n".join(res)

    def minimize(self):
        """Crazy slow FA minimizing algorithm"""
        x=set()
        for a in self.states:
            x.add( frozenset((a, None)) )
        for a in self.states:
            for b in self.states:
                if self.acc.get(a,None) != self.acc.get(b,None):
                    x.add( frozenset((a, b)) )
        while True:
            s=len(x)
            for a in self.states:
                for b in self.states:
                    for c in frozenset(self.trans[a].keys() + self.trans[b].keys()):
                        an = self.trans[a].get(c, None)
                        bn = self.trans[b].get(c, None)
                        if frozenset((an, bn)) in x:
                            x.add( frozenset((a,b)) )
                            break
            if len(x) == s:
                break

        ns={}
        inv={}
        for a in self.states:
            if a in ns: continue
            i = len(inv)
            ns[a] = i
            inv[i] = a
            for b in self.states:
                if not frozenset( (a,b) ) in x:
                    ns[b] = ns[a]

        acc={}
        trans={}
        for i in range(len(inv)):
            s = inv[i]
            if s in self.acc: acc[i] = self.acc[s]
            trans[i] = {}
            for ch in self.trans[s]:
                trans[i][ch] = ns[self.trans[s][ch]]
        self.states = range(len(inv))
        self.acc = acc
        self.trans = trans

class NFA:
    def __init__(self):
        self.states = []
        self.nextState = 0
        self.trans = {}
        self.acc = {}

    def accept(self, state, val):
        self.acc[state] = val

    def addState(self):
        i = self.nextState
        self.nextState += 1
        self.states.append(i)
        self.trans[i] = set()
        return i

    def addTransition(self, src, dst, ch):
        self.trans[src].add( (ch, dst) )
    
    def __str__(self):
        res = []
        for s in self.states:
            ch={}
            for d in self.states:
                ch[d] = []
            for (c, d) in self.trans[s]:
                if c == None or ord(c) > 31 and ord(c) < 127:
                    ch[d].append(c)
            for d in self.states:
                if not ch[d]: continue
                r=[]
                l = set(ch[d])
                if len(l) == 95:
                    l=set()
                    r.append("Every")
                if None in l:
                    r.append("Lambda")
                    l.discard(None)
                t=set([chr(i) for i in range(ord('0'), ord('9')+1)])
                if t.issubset(l):
                    l.difference_update(t)
                    r.append("0-9")
                t=set([chr(i) for i in range(ord('a'), ord('z')+1)])
                if t.issubset(l):
                    l.difference_update(t)
                    r.append("a-z")
                t=set([chr(i) for i in range(ord('A'), ord('Z')+1)])
                if t.issubset(l):
                    l.difference_update(t)
                    r.append("A-Z")
                r+=l
                res.append("%d => %d [label=%s]"%(s, d, ",".join(r)))
        return "\n".join(res)
    
    def lambdaClosure(self):
        for s in self.states:
            toVisit = [s]
            visited = set()
            while toVisit:
                v = toVisit.pop()
                if v in visited: continue
                visited.add(v)
                for (ch, dst) in self.trans[v]:
                    if ch == None: toVisit.append(dst)
            for d in visited:
                self.trans[s].add( (None, d) )

    def eliminateLambdas(self):
        #Must be in lambda closure state
        invlam={}
        lam={}
        nt={}
        for src in self.states:
            invlam[src] = []
            lam[src] = []
            nt[src] = set()
        for src in self.states:
            for (ch, dst) in self.trans[src]:
                if ch == None:
                    invlam[dst].append(src)
                    lam[src].append(dst)

        for s1 in self.states:
            for ch, s2 in self.trans[s1]:
                if ch == None: continue
                for s0 in invlam[s1]:
                    for s3 in lam[s2]:
                        nt[s0].add((ch,s3))
        self.trans = nt

    def determinate(self):
        #Powerset construction
        fa = FA()
        faMap = {}
        faMap[frozenset([0])] = fa.addState()
        toVisit = [frozenset([0])]
        acc={}
        while toVisit:
            s = toVisit.pop()
            a = 99999
            for src in s:
                if src in self.acc:
                    if self.acc[src] < a: a=self.acc[src]
            if a < 99999:
                fa.accept(faMap[s], a)
            tr={}
            for src in s:
                for (ch, dst) in self.trans[src]:
                    if not ch in tr: tr[ch] = set()
                    tr[ch].add(dst)
            
            for ch in tr:
                d=frozenset(tr[ch])
                if not d in faMap:
                    faMap[d] = fa.addState()
                    toVisit.append(d)
                fa.setTransition(faMap[s], faMap[d], ch)
        return fa
            
class RegexChars:
    def __init__(self, mask):
        self.mask = mask

    def __str__(self):
        c=""
        for i in xrange(256):
            if self.mask[i]:
                c += chr(i)
        if len(c) == 1: return c
        if len(c) == 256: return '.'
        if len(c) > 128: 
            c="^"
            for i in xrange(256):
                if not self.mask[i]:
                    c += chr(i)
        return '['+c+']'

    def createNFA(self, nfa):
        i = nfa.addState()
        o = nfa.addState()
        for c in xrange(256):
            if self.mask[c]:
                nfa.addTransition(i, o, chr(c) )
        return i, o

class RegexStar:
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return str(self.a)+'*'

    def createNFA(self, nfa):
        i1, o1 = self.a.createNFA(nfa)
        io = nfa.addState()
        nfa.addTransition(io, i1, LAMBDA)
        nfa.addTransition(o1, io, LAMBDA)
        return (io, io)

class RegexOpt:
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return str(self.a)+'?'

    def createNFA(self, nfa):
        i1, o1 = self.a.createNFA(nfa)
        i2 = nfa.addState()
        o2 = nfa.addState()
        nfa.addTransition(i2, i1, LAMBDA)
        nfa.addTransition(o1, o2, LAMBDA)
        nfa.addTransition(i2, o2, LAMBDA)
        return (i2, o2)

class RegexPlus:
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return str(self.a)+'+'

    def createNFA(self, nfa):
        i1, o1 = self.a.createNFA(nfa)
        i2 = nfa.addState()
        o2 = nfa.addState()
        nfa.addTransition(o2, i2, LAMBDA)
        nfa.addTransition(i2, i1, LAMBDA)
        nfa.addTransition(o1, o2, LAMBDA)
        return (i2,o2)
    
class RegexConcat:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return str(self.a)+str(self.b)

    def createNFA(self, nfa):
        i1, o1 = self.a.createNFA(nfa)
        i2, o2 = self.b.createNFA(nfa)
        nfa.addTransition(o1, i2, LAMBDA)
        return (i1, o2)

def parseElm(reg, i):
    if reg[i] == '[':
        mask=[False for _ in range(256)]
        neg=False
        i += 1
        while reg[i] != ']':
            if reg[i] == '^':
                neg=True
                i += 1
            if reg[i] == '.':
                for i in range(256):
                    mask[i] = True
            elif reg[i] == '\\':
                if reg[i+1] == 't':
                    mask[ord('\t')] = True
                elif reg[i+1] == 'n':
                    mask[ord('\n')] = True
                else:
                    mask[ord(reg[i+1])]=True
                i += 2
            elif reg[i+1] == '-':
                j=ord(reg[i])
                while j <= ord(reg[i+2]):
                    mask[j] = True
                    j += 1
                i += 3
            else:
                mask[ord(reg[i])] = True
                i += 1
        if neg:
            for j in range(256):
                mask[j] = not mask[j]
        return i+1, RegexChars(mask)
    elif reg[i] == '\\':
        mask=[False for _ in range(256)]
        mask[ord(reg[i+1])] = True
        return i+2, RegexChars(mask)
    elif reg[i] == '.':
        mask=[True for _ in range(256)]
        return i+1, RegexChars(mask)
    elif reg[i] == '(':
        i, e = parseOr(reg, i+1)
        assert reg[i] == ')'
        return i+1, e
    else:
        mask=[False for _ in range(256)]
        mask[ord(reg[i])] = True
        return i+1, RegexChars(mask)
        
def parseCnt(reg, i):
    i, e = parseElm(reg, i)
    if reg[i] == '?':
        return i+1, RegexOpt(e)
    if reg[i] == '*':
        return i+1, RegexStar(e)
    if reg[i] == '+':
        return i+1, RegexPlus(e)
    return i, e

def parseConcat(reg, i):
    i, c = parseCnt(reg, i)
    while reg[i] not in ('|', ')'):
        i, c2 = parseCnt(reg, i)
        c = RegexConcat(c, c2)
    return i, c

def parseOr(reg, i):
    i, e = parseConcat(reg, i)
    while i+1 < len(reg) and reg[i] == '|':
        i, e2 = parseConcat(reg, i)
        e = RegexOr(e, e2)
    return i, e

def parseRegex(reg):
    i,e=parseOr(reg+"|", 0)
    return e

class Lexer:
    def __init__(self):
        self.kwc=0
        self.rules=[]
        self.kwds={}
        self.acc={}
        
    def addKeyword(self, kwd):
        if not kwd in self.kwds:
            n="KW_%d"%(self.kwc)
            self.kwc += 1
            k=""
            for c in kwd:
                if c in ['[',']','\\','|','?','*','+']: k += '\\'
                k += c
            self.rules.insert(0, (n, k) )
            self.kwds[kwd]=n
        return self.kwds[kwd]

    def addClass(self, name, regex):
        self.rules.append( (name, regex) )

    def outputPython(self, fa):
        out=[]
        out.append("#Token constants")
        am = {}
        i = len(fa.states)
        for name in self.acc:
            am[self.acc[name]] = i
            out.append("%s=%d"%(name, i))
            i += 1
        badtoken=i
        out.append("BADTOKEN=%d"%i)
        out.append("")
        out.append("#State Table")
        out.append("st=[")
        for s in fa.states:
            o=[]
            if s in fa.acc:
                a="%2d"%(am[fa.acc[s]])
            else:
                a="%2d"%(badtoken)
            for i in range(256):
                if chr(i) in fa.trans[s]:
                    o.append("%2d"%fa.trans[s][chr(i)])
                else:
                    o.append(a)
            out.append( "  [%s],"%(",".join(o)))
        out.append("]")
        out.append("")
        out.append("""def tokenize(inp):
  inp+="\\0"
  tokens = []
  i=0
  j=0
  s=0
  while i < len(inp):
    s=st[s][ord(inp[i])]
    if s >= %d:
      if s == BADTOKEN: break
      tokens.append( (s, inp[j:i]) )
      s=0
      j=i
    else:
      i+=1
  return tokens
"""%(len(fa.states)))
        return out

        
    def generate(self, lang):
        nfa=NFA()
        s0 = nfa.addState()

        i=0
        for name,regex in self.rules:
            self.acc[name] = i
            x = parseRegex(regex)
            (i0, o) = x.createNFA(nfa)
            nfa.addTransition(s0, i0, LAMBDA)
            y = nfa.addState()
            nfa.addTransition(o, y, LAMBDA)
            nfa.accept(y, i)
            i += 1

        nfa.lambdaClosure()
        nfa.eliminateLambdas()
        fa = nfa.determinate()
        fa.minimize()

        return self.outputPython(fa)
        
        
#def parseRegex(reg):
#    i,e=parseOr(reg+"|", 0)
#    return e
