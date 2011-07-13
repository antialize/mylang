import parser


p = parser.Parser(open('bootstrap/test.my','r').read())
while p.nextToken():
    print p.currentToken, p.tokenText(p.currentToken)
