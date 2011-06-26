
# class NFA:
#     def __init__(self):
#         self.nextState = 0
#         self.states = []
#         self.accept = {}
#         self.trans = {}

#     def eleminate_lambdas(self):
#         """Remove all lambda transitions"""
#         inv={}
#         for s in self.states:
#             inv[s] = set()

#         lam=set()
#         for s in self.states:
#             for c, dst in self.trans[s]:
#                 if c == None:
#                     lam.add( (s, dst) )
#                 inv[dst].add( (c, s) )

#         while lam:
#             int, dst = lam.pop()
           
#             inv[dst].discard( (None, int) )
#             self.trans[int].discard( (None, dst) )
           
#             if int == dst: continue 
           
#             for (c, src) in inv[int]:
#                 self.trans[src].add( (c, dst) )
#                 self.inv[dst].add( (c, src) )
#                 if c == None: lam.add( (src, dst) )
                    
#     def determinate():
#         """Create DFA using powerset construction"""
#         m = {}
#         toCreate = [set([0])]
#         while toCreate:
#             s = toCreate.pop()
#             if s in m: continue
            
#             for c in range(0,256):
#                 d = set()
#                 for st in s:


def parseRegex(str):
    
