#!/usr/bin/python

import parser

p = parser.Parser('bootstrap/test.my')
p.nextToken()
print p.parse_document()

for t in p.bad_tokens:
    print "Lex error: Invalid Token:"
    print p.tokenLocationString(t)
    print

for e in p.parseErrors:
    print "Parse error: %s"%e.message
    print p.tokenLocationString(e.token)
    print 

