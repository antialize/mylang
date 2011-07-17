import parser

p = parser.Parser(open('bootstrap/test.my','r').read())
p.nextToken()
print p.parse_document()

