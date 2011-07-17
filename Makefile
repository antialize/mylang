MYCCFILES:=mycc/lex.py mycc/mycc.py

.PHONY: all clean

all: bootstrap/parser.py

clean:
	${RM} bootstrap/parser.py *~ */*~

bootstrap/parser.py bootstrap/astclasses.py: ${MYCCFILES} gramma.my bootstrap/astclassbase.py
	mycc/mycc.py python gramma.my bootstrap/parser.py bootstrap/astclasses.py bootstrap/astclassbase.py

