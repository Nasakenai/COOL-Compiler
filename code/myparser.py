import sys
sys.path.append('..')

import ply.yacc as yacc
import cool_ast as AST
import settings as settings
from mylexer import Lexer


class CoolParser(object):
	"""
	CoolParser class.

	Deals with Syntax Analysis of COOL Programs.

	To use the parser, create an object from it and feed the source code by calling the parse() method 
	passing in the code as a string.
	"""

	def __init__(self):
		# Initialize self.parser and self.tokens to None
		self.tokens = None
		self.lexer = None
		self.parser = None

		# Collection of errors encountered during parsing
		self.error_list = []

		# Build lexer for Ply.Yacc
		self.lexer = Lexer()

		# Cool Tokens and Reserved keywords required for Ply.Yacc
		self.tokens = Lexer.token_names + tuple(Lexer.reserved_keywords.values())

		# Builds the PyCoolParser instance with yaac.yaac() by binding the lexer object and its tokens list in the
		# current instance scope.
		self.parser = yacc.yacc(module=self)


	def parse(self, source):
		"""
		Parses a COOL program source code passed as a string.
		"""

		return self.parser.parse(source)
	

	####################################### PRECEDENCE RULES ##########################################


	precedence = (
		('right', 'ASSIGN'),
		('right', 'NOT'),
		('nonassoc', 'LTEQ', 'LT', 'EQ'),
		('left', 'PLUS', 'MINUS'),
		('left', 'MULTIPLY', 'DIVIDE'),
		('right', 'ISVOID'),
		('right', 'INT_COMP'),
		('left', 'AT'),
		('left', 'DOT')
	)


	#################################### GRAMMAR RULES DECLARATION ###################################


	def p_program(self, parse):
		"""
		program : class_list
		"""
		parse[0] = AST.Program(classes=parse[1])
		parse[0].lineno = 1

	def p_class_list(self, parse):
		"""
		class_list : class_list class SEMICOLON
						| class SEMICOLON
		"""
		if len(parse) == 3:
			parse[0] = (parse[1],)
		else:
			parse[0] = parse[1] + (parse[2],)

	def p_class(self, parse):
		"""
		class : CLASS TYPE LBRACE features_list_opt RBRACE
		"""
		parse[0] = AST.Class(name=parse[2],  parent=settings.OBJECT_CLASS, features=parse[4])
		parse[0].lineno = parse.lineno(1)

	def p_class_inherits(self, parse):
		"""
		class : CLASS TYPE INHERITS TYPE LBRACE features_list_opt RBRACE
		"""
		parse[0] = AST.Class(name=parse[2], parent=parse[4], features=parse[6])
		parse[0].lineno = parse.lineno(1)

	def p_feature_list_opt(self, parse):
		"""
		features_list_opt : features_list
								| empty
		"""
		parse[0] = tuple() if parse.slice[1].type == "empty" else parse[1]

	def p_feature_list(self, parse):
		"""
		features_list : features_list feature SEMICOLON
							| feature SEMICOLON
		"""
		if len(parse) == 3:
			parse[0] = (parse[1],)
		else:
			parse[0] = parse[1] + (parse[2],)

	def p_feature_method(self, parse):
		"""
		feature : ID LPAREN formal_params_list RPAREN COLON TYPE LBRACE expression RBRACE
		"""
		parse[0] = AST.ClassMethod(name=parse[1], formal_params=parse[3], return_type=parse[6], body=parse[8])
		parse[0].lineno = parse.lineno(1)

	def p_feature_method_no_formals(self, parse):
		"""
		feature : ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE
		"""
		parse[0] = AST.ClassMethod(name=parse[1], formal_params=tuple(), return_type=parse[5], body=parse[7])
		parse[0].lineno = parse.lineno(1)

	def p_feature_attr_initialized(self, parse):
		"""
		feature : ID COLON TYPE ASSIGN expression
		"""
		parse[0] = AST.ClassAttribute(name=parse[1], attr_type=parse[3], init_expr=parse[5])
		parse[0].lineno = parse.lineno(1)

	def p_feature_attr(self, parse):
		"""
		feature : ID COLON TYPE
		"""
		parse[0] = AST.ClassAttribute(name=parse[1], attr_type=parse[3], init_expr=None)
		parse[0].lineno = parse.lineno(1)

	def p_formal_list_many(self, parse):
		"""
		formal_params_list  : formal_params_list COMMA formal_param
									| formal_param
		"""
		if len(parse) == 2:
			parse[0] = (parse[1],)
		else:
			parse[0] = parse[1] + (parse[3],)

	def p_formal(self, parse):
		"""
		formal_param : ID COLON TYPE
		"""
		parse[0] = AST.FormalParameter(name=parse[1], param_type=parse[3])
		parse[0].lineno = parse.lineno(1)

	def p_expression_object_identifier(self, parse):
		"""
		expression : ID
		"""
		parse[0] = AST.Object(name=parse[1])
		parse[0].lineno = parse.lineno(1)

	def p_expression_integer_constant(self, parse):
		"""
		expression : INTEGER
		"""
		parse[0] = AST.Integer(content=parse[1])
		parse[0].lineno = parse.lineno(1)

	def p_expression_boolean_constant(self, parse):
		"""
		expression : BOOLEAN
		"""
		parse[0] = AST.Boolean(content=parse[1])
		parse[0].lineno = parse.lineno(1)

	def p_expression_string_constant(self, parse):
		"""
		expression : STRING
		"""
		parse[0] = AST.String(content=parse[1])
		parse[0].lineno = parse.lineno(1)

	def p_expr_self(self, parse):
		"""
		expression  : SELF
		"""
		parse[0] = AST.Self()
		parse[0].lineno = parse.lineno(1)

	def p_expression_block(self, parse):
		"""
		expression : LBRACE block_list RBRACE
		"""
		parse[0] = AST.Block(expr_list=parse[2])
		parse[0].lineno = parse.lineno(1)

	def p_block_list(self, parse):
		"""
		block_list : block_list expression SEMICOLON
						| expression SEMICOLON
		"""
		if len(parse) == 3:
			parse[0] = (parse[1],)
		else:
			parse[0] = parse[1] + (parse[2],)

	def p_expression_assignment(self, parse):
		"""
		expression : ID ASSIGN expression
		"""
		parse[0] = AST.Assignment(AST.Object(name=parse[1]), expr=parse[3])
		parse[0].lineno = parse[0].instance.lineno = parse.lineno(1)

	# ######################### METHODS DISPATCH ######################################

	def p_expression_dispatch(self, parse):
		"""
		expression : expression DOT ID LPAREN arguments_list_opt RPAREN
		"""
		parse[0] = AST.DynamicDispatch(instance=parse[1], method=parse[3], arguments=parse[5])
		parse[0].lineno = parse.lineno(2)

	def p_arguments_list_opt(self, parse):
		"""
		arguments_list_opt : arguments_list
								| empty
		"""
		parse[0] = tuple() if parse.slice[1].type == "empty" else parse[1]

	def p_arguments_list(self, parse):
		"""
		arguments_list : arguments_list COMMA expression
							| expression
		"""
		if len(parse) == 2:
			parse[0] = (parse[1],)
		else:
			parse[0] = parse[1] + (parse[3],)

	def p_expression_static_dispatch(self, parse):
		"""
		expression : expression AT TYPE DOT ID LPAREN arguments_list_opt RPAREN
		"""
		parse[0] = AST.StaticDispatch(instance=parse[1], dispatch_type=parse[3], method=parse[5], arguments=parse[7])
		parse[0].lineno = parse.lineno(2)

	def p_expression_self_dispatch(self, parse):
		"""
		expression : ID LPAREN arguments_list_opt RPAREN
		"""
		parse[0] = AST.DynamicDispatch(instance=AST.Self(), method=parse[1], arguments=parse[3])
		parse[0].lineno = parse.lineno(2)


	################################ PARENTHESIZED, MATH & COMPARISONS ################################


	def p_expression_math_operations(self, parse):
		"""
		expression : expression PLUS expression
						| expression MINUS expression
						| expression MULTIPLY expression
						| expression DIVIDE expression
		"""
		if parse[2] == '+':
			parse[0] = AST.Addition(first=parse[1], second=parse[3])
		elif parse[2] == '-':
			parse[0] = AST.Subtraction(first=parse[1], second=parse[3])
		elif parse[2] == '*':
			parse[0] = AST.Multiplication(first=parse[1], second=parse[3])
		elif parse[2] == '/':
			parse[0] = AST.Division(first=parse[1], second=parse[3])
		parse[0].lineno = parse.lineno(2)


	def p_expression_math_comparisons(self, parse):
		"""
		expression : expression LT expression
						| expression LTEQ expression
						| expression EQ expression
		"""
		if parse[2] == '<':
			parse[0] = AST.LessThan(first=parse[1], second=parse[3])
		elif parse[2] == '<=':
			parse[0] = AST.LessThanOrEqual(first=parse[1], second=parse[3])
		elif parse[2] == '=':
			parse[0] = AST.Equal(first=parse[1], second=parse[3])
		parse[0].lineno = parse.lineno(2)

	def p_expression_with_parenthesis(self, parse):
		"""
		expression : LPAREN expression RPAREN
		"""
		parse[0] = parse[2]

	
	################################## CONTROL FLOW EXPRESSIONS #####################################


	def p_expression_if_conditional(self, parse):
		"""
		expression : IF expression THEN expression ELSE expression FI
		"""
		parse[0] = AST.If(predicate=parse[2], then_body=parse[4], else_body=parse[6])
		parse[0].lineno = parse.lineno(1)

	def p_expression_while_loop(self, parse):
		"""
		expression : WHILE expression LOOP expression POOL
		"""
		parse[0] = AST.WhileLoop(predicate=parse[2], body=parse[4])
		parse[0].lineno = parse.lineno(1)


	#################################### LET EXPRESSIONS ############################################


	def p_expression_let(self, parse):
		"""
		expression : let_expression
		"""
		parse[0] = parse[1]

	def p_expression_let_simple(self, parse):
		"""
		let_expression : LET let_variables_list IN expression
		"""
		parse[0] = AST.Let(variables=parse[2], body=parse[4])
		parse[0].lineno = parse.lineno(1)

	def p_let_variables_list(self, parse):
		"""
		let_variables_list : let_variables_list COMMA let_variable
									| let_variable
		"""
		if len(parse) == 4:
			parse[0] = parse[1] + (parse[3],)
		else:
			parse[0] = (parse[1],)

	def p_let_variable(self, parse):
		"""
		let_variable : ID COLON TYPE
							| ID COLON TYPE ASSIGN expression
		"""

		if len(parse) == 4:
			parse[0] = AST.LetVariable(parse[1], parse[3], None)
		else:
			parse[0] = AST.LetVariable(parse[1], parse[3], parse[5])
		parse[0].lineno = parse.lineno(1)


	##################################### CASE EXPRESSION ############################################


	def p_expression_case(self, parse):
		"""
		expression : CASE expression OF actions_list ESAC
		"""
		parse[0] = AST.Case(expr=parse[2], actions=parse[4])
		parse[0].lineno = parse.lineno(1)

	def p_actions_list(self, parse):
		"""
		actions_list : actions_list action
						| action
		"""
		if len(parse) == 2:
			parse[0] = (parse[1],)
		else:
			parse[0] = parse[1] + (parse[2],)

	def p_action_expr(self, parse):
		"""
		action : ID COLON TYPE ARROW expression SEMICOLON
		"""
		parse[0] = AST.Action(parse[1], parse[3], parse[5])
		parse[0].lineno = parse.lineno(1)


	####################################### UNARY OPERATIONS #########################################


	def p_expression_new(self, parse):
		"""
		expression : NEW TYPE
		"""
		parse[0] = AST.NewObject(parse[2])
		parse[0].lineno = parse.lineno(1)

	def p_expression_isvoid(self, parse):
		"""
		expression : ISVOID expression
		"""
		parse[0] = AST.IsVoid(parse[2])
		parse[0].lineno = parse.lineno(1)

	def p_expression_integer_complement(self, parse):
		"""
		expression : INT_COMP expression
		"""
		parse[0] = AST.IntegerComplement(parse[2])
		parse[0].lineno = parse.lineno(1)

	def p_expression_boolean_complement(self, parse):
		"""
		expression : NOT expression
		"""
		parse[0] = AST.BooleanComplement(parse[2])
		parse[0].lineno = parse.lineno(1)


	###################################### THE EMPTY PRODUCTION ##########################################


	def p_empty(self, parse):
		"""
		empty :
		"""
		parse[0] = None


	###################################### PARSE ERROR HANDLER ############################################

	def p_error(self, parse):
		"""
		Error rule for Syntax Errors handling and reporting.
		"""
		if parse is None:
			print("Error! Unexpected end of input!")
		else:
			error = "Syntax error! Line: {}, position: {}, character: {}, type: {}".format(
					parse.lineno, parse.lexpos, parse.value, parse.type)
			self.error_list.append(error)
			self.parser.errok()


# #----------- TESTS

# s = CoolParser()
# fpath = "..\..\examples\mytest.cl"
# with open(fpath, encoding="utf-8") as file:
# 	cool_program_code = file.read()
# 	print(s.parse(cool_program_code))