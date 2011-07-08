MYCCFILES:=mycc/lex.py mycc/parser.py mycc/mycc.py

.PHONY: all clean

all: bootstrap/parser.py

clean:
	${RM} bootstrap/parser.py *~ */*~

bootstrap/parser.py: ${MYCCFILES} gramma.my
	mycc/mycc.py python gramma.my bootstrap/parser.py

