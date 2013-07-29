
#*.* coding=utf-8 *.*

import sys
import copy
import collections

sys.path.append("/Users/zhaonf/github/breed/src")
sys.path.append("/Users/zhaonf/github/breed")

import lex
import file_
import yacc


def help():
	print """
		LR(0) parser v0.0.1
		author by zhao_nf
		command line is main.py -shortoptions args
		example : python main.py --file $HOME/project/xxxx.java
	"""
def getopts():
	try:
		import getopt
		opts, args = getopt.getopt(sys.argv[1:], "", ["file=", "version","help","debug"])
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		sys.exit(2)
	filename = ""
	debug = False
	for o,a in opts:
		if o == "--file":
			filename = a
		if o == "--help":
			help()
		if o == "--version":
			help()
		if o == "--debug":
			debug = True

	main(filename,debug)

def main(filename,debug=False):
	lexer = lex.getlex()

	s = file_.getSource( filename )

	lexer.input(s)

	parser()

	#for x in file_.getTokenList(lexer):
	#	print x


#-------------------------------------------------
#			parser method 
#-------------------------------------------------

startTag = "$S"

endTag = "$end"

class RuleObject(object):
	"""docstring for ItemObject"""
	def __init__(self,Item):
		self.position = 0
		self.expressionName = Item[0]
		self.item = Item[1:]
		self.pr = list(self.item)
		self.pr.insert(self.position,".")

	def lrNext(self):
		if self.position+1 > len(self.item) :
			return False
		else:
			self.position += 1
		self.pr = list(self.item)
		self.pr.insert(self.position,".")
		return True

	def __str__(self):
		if self.item:
			return "%s -> %s" % (self.expressionName," ".join(self.pr))
		else:
			return "%s -> <empty>" % self.expressionName

	def __repr__(self):
		return "LRItem(%s)" % ( str(self) )

	def lrCurrent(self):
		if self.position >= len(self.item) : return None
		return self.item[self.position]
	def __eq__(self, other):
		if other.__class__ is RuleObject :
			#print other.expressionName
			#print self.expressionName
			#print "-----"
			if other.expressionName == self.expressionName:
				if other.item == self.item:
					return True
			return False
		else:
			return False

class RuleList(list):
	def __contains__(self, item):
		for x in self:
			if item == x :
				return True
		return False

grammar = {
	'S' : [
		RuleObject( ['S' , 'start'] )
	],
	'start' : [ 
		RuleObject( ['start' ,'expression'] ) 
	],
	'expression' : [
		RuleObject( ['expression','multExpression'] ),
		RuleObject( ['expression','expression','PLUS','multExpression'] ),
		RuleObject( ['expression','expression','DASH','multExpression'] )
	],
	'multExpression' : [
		RuleObject( ['multExpression','subExpression' ] ),
		RuleObject( ['multExpression','multExpression', 'MULT', 'subExpression'] ),
		RuleObject( ['multExpression','multExpression', 'SLASH', 'subExpression'] )
	],
	'subExpression' : [
		RuleObject( ['subExpression','LPAREN', 'expression', 'RPAREN'] ) ,
		RuleObject( ['subExpression','primary' ] )
	],
	'primary' : [ RuleObject(['primary','NON_INTEGER_3']) ]
}

nonTerminals = ['start','expression','multExpression','subExpression','primary']

terminals = ['PLUS','DASH','MULT','SLASH','LPAREN','RPAREN','NON_INTEGER_3']


#make a goto table and a Action table

def parser():
	lr0Item(grammar)

def lr0Item(G):
	C = collections.deque( [ lr0Closure(G['S']) ] );

	p = copy.deepcopy(C)
	while True:
		x = C.pop()
		sysum = {}
		for i in x:
			if i.lrCurrent() != None:
				sysum[i.lrCurrent()] = None
		if x not in p : p.append(x)
		if sysum == {} :
			continue
		for s in sysum :
			sub = lr0GOTO(copy.deepcopy(x),s)
			if sub not in p : C.append(copy.deepcopy(sub))		
		if len(C) == 0 : break
	"""
	ii = 1
	for x in p:
		print  ii 
		for y in x:
			print y
		print "==="
		ii += 1
	print len(C)
	"""


def lr0Closure(I):
	O = collections.deque(I)
	p = []
	while True:
		x = O.pop()
		if x.lrCurrent() in nonTerminals and x.lrCurrent() != x.expressionName :
			for y in grammar[x.lrCurrent()]:
				O.appendleft(copy.deepcopy(y))
		p.append(x)
		if len(O) == 0 : break
	return p

def lr0GOTO(I,X):
	
	J = RuleList()
	for i in I:
		if i.lrCurrent() == X:
			i.lrNext()
			J.append(copy.deepcopy(i) )
	return lr0Closure(J)

if __name__ == '__main__':
 	getopts() 