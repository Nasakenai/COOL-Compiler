import sys
sys.path.append('..')

import cool_ast as COOL
import cil_ast as cil
import visitor as visitor
from settings import *

class COOL_To_CIL:

	def __init__(self):
		self.dottype = [cil.CIL_Type(VOID_TYPE, [], [])]

		self.dotdata = []

		self.dotcode = []

		self.current_class_name = ""

		self.current_function_name = ""
		self.localvars = []
		self.instructions = []

		self.ind_map = {}

		self.mth_map = {}

		self.internal_var_count = 0			
		self.internal_label_count = 0			

		self.class_depth = {}

		self.inherit_graph = tuple()
		self.empty_string = self.register_data("")



	def define_internal_label(self):
		label = f'LABEL_{self.internal_label_count}'
		self.internal_label_count += 1
		return label


	def register_data(self, value):
		vname = f'data_{len(self.dotdata)}'
		same_data = [data for data in self.dotdata if data.value == value]
		if same_data != []:
			return same_data[0].dest

		data_node = cil.CIL_Data(vname, value)
		self.dotdata.append(data_node)
		return data_node.dest

	def build_internal_vname(self, vname):
		vname = f'_{vname}_{self.internal_var_count}'
		return vname

	def register_internal_local(self):
		return self.register_local('internal')

	def register_local(self, vname):
		vname = self.build_internal_vname(vname)
		self.localvars.append(cil.CIL_Local(vname))
		self.internal_var_count +=1
		return vname

	def register_instruction(self, instruction_type, *args):
		instruction = instruction_type(*args)
		self.instructions.append(instruction)
		return instruction

	def register_function(self, function):
		self.dotcode.append(function)

	def build_new_object(self, dest, ttype):
		self.register_instruction(cil.CIL_Allocate, dest, ttype)
		self.register_instruction(cil.CIL_Push, dest)
		self.register_instruction(cil.CIL_Call, dest, f'{ttype}_{INIT_CIL_SUFFIX}')
		self.register_instruction(cil.CIL_Pop, dest)

	def build_inheritance_graph_and_class_depth(self, program: COOL.Program):
		g = {}
		root = None

		# Initialize class depth dictionary
		for c in program.classes:
			self.class_depth[c.name] = 0
			g[c.name] = []

		for klass in program.classes:
			if klass.parent:
				# Build inheritance graph
				g[klass.parent].append(klass)

				# Build the class depth dictionary
				self.class_depth[klass.name] = self.class_depth[klass.parent] + 1

			if klass.name == OBJECT_CLASS:
				root = klass

		self.inherit_graph = g, root



	@visitor.on('node')
	def visit(self, node):
		pass





	@visitor.when(COOL.Program)
	def visit(self, node: COOL.Program):
		self.build_inheritance_graph_and_class_depth(node)
		childs, root = self.inherit_graph

		visited = {}
		for klass in node.classes:
			visited[klass.name] = False

		def dfs(node, attrs, methods, initializers):
			if visited[node.name]:
				return

			node.inherited_attrs = attrs.copy()
			node.inherited_methods = methods.copy()
			node.inherited_initializers = initializers

			new_type, initializer = self.visit(node)
			visited[node.name] = True
			self.dottype.append(new_type)

			for klass in childs[node.name]:
				dfs(klass, new_type.attributes, new_type.methods, initializers + [initializer])

		dfs(root, [], [], [])

		for func in self.dotcode:
			for inst in func.body:
				#print(type(inst))
				if isinstance(inst, cil.CIL_VCall):
					inst.f = self.mth_map[inst.f]
				if (isinstance(inst, cil.CIL_SetAttr) or isinstance(inst, cil.CIL_GetAttr)) \
				 and isinstance(inst.attribute, str):

					inst.attribute = self.ind_map[inst.attribute]
					#print(inst.attribute)

		return cil.CILProgram(self.dottype, self.dotdata, self.dotcode)


	@visitor.when(COOL.Class)
	def visit(self, node: COOL.Class):

		self.current_class_name = node.name

		attributes = node.inherited_attrs	
		methods = node.inherited_methods
		initializers = node.inherited_initializers

		#print(self.current_class_name)
		#print(attributes)
		# for meth in methods:
		# 	print(type(meth))
		# 	print(meth)
		#print(initializers)

		#print(node)

		# Store the offset of inherited atributes and methods
		#print(node.name)
		for i in range(len(attributes)):
			#print(attributes[i].name)
			self.ind_map[f'{self.current_class_name}_{attributes[i].name[attributes[i].name.index("_")+1:]}'] = i
		for i in range(len(methods)):
			self.mth_map[f'{self.current_class_name}_{methods[i].name}'] = i
			# If the method will be redefined, the offset will be replaced.

		# Translate all the properties (COOL) into attributes (CIL)
		# and build an initializer function
		self.localvars = []
		self.instructions = []
		self.internal_var_count = 0
		self.current_function_name = f'{self.current_class_name}_{INIT_CIL_SUFFIX}'

		# Build the initializer function and attributes list
		for initializer in initializers:
			self.register_instruction(cil.CIL_Push, LOCAL_SELF_NAME)
			self.register_instruction(cil.CIL_Call, None, initializer)	# Call superclasses's initializers
			self.register_instruction(cil.CIL_Pop, None)

		ind = len(attributes)
		for feature in node.features:
			if isinstance(feature, COOL.ClassAttribute):
				#print('Mojon verde')
				#print(feature.name)
				feature.index = ind
				attributes.append(self.visit(feature))
				ind += 1

		# Register the initializer function
		self.register_instruction(cil.CIL_Return, LOCAL_SELF_NAME)
		func = cil.CIL_Functions(self.current_function_name, [cil.CIL_Arg(LOCAL_SELF_NAME)], self.localvars, self.instructions)
		self.register_function(func)

		# Translate all Class Methods (COOL) into Type Methods (CIL)
		# and the functions associated will be automatically registered by the visitor
		ind = len(methods)
		for feature in node.features:
			if isinstance(feature, COOL.ClassMethod):
				feature.index = ind

				# Check if this method is being redefined
				for i in range(len(methods)):
					if methods[i].name == feature.name:
						# If it's being redefined, use the offset of the function already defined
						feature.index = i
						del methods[i]
						ind -= 1
						break

				#print(feature.name)
				method = self.visit(feature)
				methods.insert(feature.index, method)
				ind += 1
		#print(methods)
		# Return CIL resulting function and the initializer function's name
		return cil.CIL_Type(node.name, attributes, methods), f'{self.current_class_name}_{INIT_CIL_SUFFIX}'


	@visitor.when(COOL.ClassAttribute)
	def visit(self, node: COOL.ClassAttribute):
		if node.init_expr:
			rname = self.visit(node.init_expr)
			self.register_instruction(cil.CIL_SetAttr, '__self', node.index, rname)
		elif node.attr_type == '__prim_zero_slot':
			self.register_instruction(cil.CIL_SetAttr, '__self', node.index, 0)
		elif node.attr_type == '__prim_empty_slot':
			self.register_instruction(cil.CIL_SetAttr, '__self', node.index, self.empty_string)
		else:
			_temp = self.register_internal_local()
			if node.attr_type == 'Int':
				self.build_new_object(_temp, 'Int')
			elif node.attr_type == 'Bool':
				self.build_new_object(_temp, 'Bool')
			elif node.attr_type == 'String':
				self.build_new_object(_temp, 'String')
			else:
				self.register_instruction(cil.CIL_Allocate, _temp, 'Void')

			self.register_instruction(cil.CIL_SetAttr, '__self', node.index, _temp)

		self.ind_map[f'{self.current_class_name}_{node.name}'] = node.index
		return cil.CIL_Attribute(f'{self.current_class_name}_{node.name}')


	@visitor.when(COOL.ClassMethod)
	def visit(self, node: COOL.ClassMethod):
		#print(self.current_class_name)

		self.localvars = []
		self.instructions = []
		self.internal_var_count = 0
		self.current_function_name = f'{self.current_class_name}_{node.name}'

		# Reset the name mappings
		self.name_map = NameTable()


		# Self argument
		arguments = [cil.CIL_Arg(LOCAL_SELF_NAME)]

		# User defined arguments
		for formal_param in node.formal_params:
			arguments.append(self.visit(formal_param))

		
		if self.current_class_name in BUILT_IN_CLASSES:
			# If the current class is a Built-In class then leave the method implementation for the next phase
			pass
		else:
			#print(self.current_class_name)
			#print('Este es node.body {}'.format(node.body))
			#print(node.body == None)
			return_val = self.visit(node.body)

			self.register_instruction(cil.CIL_Return, return_val)


		#----- Register the function and return the corresponding method node
		func = cil.CIL_Functions(self.current_function_name, arguments, self.localvars, self.instructions)
		self.register_function(func)

		# Register the method's offset index
		self.mth_map[func.name] = node.index

		return cil.CIL_Method(node.name, func.name)


	@visitor.when(COOL.FormalParameter)
	def visit(self, node: COOL.FormalParameter):
		self.name_map.is_define_variable(node.name, f'_{node.name}')
		return cil.CIL_Arg(f'_{node.name}')




	@visitor.when(COOL.Object)
	def visit(self, node: COOL.Object):
		obj_vname = self.name_map.get_cil_name(node.name)
		if obj_vname:
			return obj_vname
		else:
			vname = self.register_local(node.name)
			attribute_cil_name = f'{self.current_class_name}_{node.name}'
			self.register_instruction(cil.CIL_GetAttr, vname, LOCAL_SELF_NAME, attribute_cil_name)

			return vname 


	@visitor.when(COOL.Self)
	def visit(self, node: COOL.Self):
		return LOCAL_SELF_NAME





	@visitor.when(COOL.Integer)
	def visit(self, node: COOL.Integer):
		boxed_int = self.register_internal_local()
		self.register_instruction(cil.CIL_Allocate, boxed_int, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, boxed_int, 0, node.content)
		return boxed_int


	@visitor.when(COOL.String)
	def visit(self, node: COOL.String):
		data_vname = self.register_data(node.content)
		boxed_string = self.register_internal_local()
		boxed_int = self.register_internal_local()
		self.register_instruction(cil.CIL_Allocate, boxed_int, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, boxed_int, 0, len(node.content))

		self.register_instruction(cil.CIL_Allocate, boxed_string, STRING_CLASS)
		self.register_instruction(cil.CIL_SetAttr, boxed_string, 0, boxed_int)
		self.register_instruction(cil.CIL_SetAttr, boxed_string, 1, data_vname)
		return boxed_string


	@visitor.when(COOL.Boolean)
	def visit(self, node: COOL.Boolean):
		boxed_bool = self.register_internal_local()
		self.register_instruction(cil.CIL_Allocate, boxed_bool, BOOLEAN_CLASS)
		if node.content:
			self.register_instruction(cil.CIL_SetAttr, boxed_bool, 0, 1)
		else:
			self.register_instruction(cil.CIL_SetAttr, boxed_bool, 0, 0)
		return boxed_bool




	@visitor.when(COOL.NewObject)
	def visit(self, node: COOL.NewObject):
		vname = self.register_internal_local()
		_temp = self.register_internal_local()

		self.register_instruction(cil.CIL_Allocate, vname, node.type)
		self.register_instruction(cil.CIL_Push, vname)
		self.register_instruction(cil.CIL_Call, _temp, f'{node.type}_{INIT_CIL_SUFFIX}')
		self.register_instruction(cil.CIL_Pop, vname)
		return vname


	@visitor.when(COOL.IsVoid)
	def visit(self, node: COOL.IsVoid):
		# LOCAL <isvoid.value>
		# LOCAL <expr.locals>
		# LOCAL <temp_var>
		# 	...
		# <expr.code>
		# ARG <expr.value>
		# <isvoid.value> = Call isvoid

		# <.locals>
		value = self.register_internal_local()

		# <.code>
		expr_val = self.visit(node.expr)
		self.register_instruction(cil.CIL_Push, expr_val)
		self.register_instruction(cil.CIL_Call, value, ISVOID_FUNC)
		self.register_instruction(cil.CIL_Pop, expr_val)

		return value 

	@visitor.when(COOL.Assignment)
	def visit(self, node: COOL.Assignment):
		rname = self.visit(node.expr)

		cil_name = self.name_map.get_cil_name(node.instance.name)

		if cil_name:
			self.register_instruction(cil.CIL_Assign, cil_name, rname)
		else:
			attribute_cil_name = f'{self.current_class_name}_{node.instance.name}'
			self.register_instruction(cil.CIL_SetAttr, LOCAL_SELF_NAME, attribute_cil_name, rname)
		return rname


	@visitor.when(COOL.Block)
	def visit(self, node: COOL.Block):

		block_value = None
		for expr in node.expr_list:
			block_value = self.visit(expr)
		return block_value


	@visitor.when(COOL.Let)
	def visit(self, node: COOL.Let):
	
		self.name_map = self.name_map.create_child_scope()
		for variable in node.variables:
			self.visit(variable)

		res_vname = self.visit(node.body)
		self.name_map.exit_child_scope()

		return res_vname


	@visitor.when(COOL.LetVariable)
	def visit(self, node: COOL.LetVariable):
		var_name = ""

		if node.initialization:
			var_name = self.visit(node.initialization)
		else:
			var_name = self.register_local(node.name)

			if node.ttype == INTEGER_CLASS:
				self.build_new_object(var_name, INTEGER_CLASS)
			elif node.ttype == BOOLEAN_CLASS:
				self.build_new_object(var_name, BOOLEAN_CLASS)
			elif node.ttype == STRING_CLASS:
				self.build_new_object(var_name, STRING_CLASS)
			elif node.ttype == UNBOXED_PRIMITIVE_DEFAULT_ZERO:
				self.register_instruction(cil.CIL_SetAttr, LOCAL_SELF_NAME, node.index, 0)
			elif node.ttype == UNBOXED_PRIMITIVE_DEFAULT_EMPTY:
				self.register_instruction(cil.CIL_SetAttr, LOCAL_SELF_NAME, node.index, self.empty_string)
			else:
				self.register_instruction(cil.CIL_Allocate, var_name, VOID_TYPE)

		self.name_map.is_define_variable(node.name, var_name)


	@visitor.when(COOL.If)
	def visit(self, node: COOL.If):
	
		if_value = self.register_internal_local()
		condition_unboxed = self.register_internal_local()
		then_lbl = self.define_internal_label()
		continue_lbl = self.define_internal_label()

		condition_value = self.visit(node.predicate)
		self.register_instruction(cil.CIL_GetAttr, condition_unboxed, condition_value, 0)
		self.register_instruction(cil.CIL_IfGoto, condition_unboxed, then_lbl)
		else_value = self.visit(node.else_body)
		self.register_instruction(cil.CIL_Assign, if_value, else_value)
		self.register_instruction(cil.CIL_Goto, continue_lbl)
		self.register_instruction(cil.CIL_Label, then_lbl)
		then_value = self.visit(node.then_body)
		self.register_instruction(cil.CIL_Assign, if_value, then_value)
		self.register_instruction(cil.CIL_Label, continue_lbl)

		return if_value


	@visitor.when(COOL.WhileLoop)
	def visit(self, node: COOL.WhileLoop):
	
		#variables locales
		while_value = self.register_internal_local()
		condition_unboxed = self.register_internal_local()
		start_lbl = self.define_internal_label()
		body_lbl = self.define_internal_label()
		continue_lbl = self.define_internal_label()

		#instrucciones dentro del cuerpo
		self.register_instruction(cil.CIL_Label, start_lbl)
		condition_value = self.visit(node.predicate)		# Generate <condition.body> and <condition.locals>
		self.register_instruction(cil.CIL_GetAttr, condition_unboxed, condition_value, 0)
		self.register_instruction(cil.CIL_IfGoto, condition_unboxed, body_lbl)
		self.register_instruction(cil.CIL_Goto, continue_lbl)
		self.register_instruction(cil.CIL_Label, body_lbl)
		self.visit(node.body)
		self.register_instruction(cil.CIL_Goto, start_lbl)
		self.register_instruction(cil.CIL_Label, continue_lbl)
		self.register_instruction(cil.CIL_Allocate, while_value, VOID_TYPE)

		return while_value


	@visitor.when(COOL.Case)
	def visit(self, node: COOL.Case):
		
		actions = list(node.actions)
		actions.sort(key = lambda x: self.class_depth[x.action_type], reverse = True)

		_temp = self.register_internal_local()
		expr_type = self.register_local("expression_type")
		case_value = self.register_internal_local()
		

		#Se crea un label por cada case para saltar hacia esas instrucciones segun el caso
		labels = []
		for _ in node.actions:
			labels.append(self.define_internal_label())
		end_label = self.define_internal_label()

		expr_value = self.visit(node.expr)
		self.register_instruction(cil.CIL_TypeOf, expr_type, expr_value)
		for i in range(len(actions)):
			self.register_instruction(cil.CIL_Push, actions[i].action_type)
			self.register_instruction(cil.CIL_Push, expr_type)
			self.register_instruction(cil.CIL_Call, _temp, CONFORMS_FUNC)
			self.register_instruction(cil.CIL_Pop, None)
			self.register_instruction(cil.CIL_Pop, None)
			self.register_instruction(cil.CIL_IfGoto, _temp, labels[i])


		for i in range(len(actions)):
			self.register_instruction(cil.CIL_Label, labels[i])
			self.name_map.is_define_variable(actions[i].name, expr_value)
			self.name_map = self.name_map.create_child_scope()
			expr_i = self.visit(actions[i])
			self.name_map.exit_child_scope()
			self.register_instruction(cil.CIL_Assign, case_value, expr_i)
			self.register_instruction(cil.CIL_Goto, end_label)
			
		self.register_instruction(cil.CIL_Label, end_label)
		return case_value


	@visitor.when(COOL.Action)
	def visit(self, node: COOL.Action):
		return self.visit(node.body)



	@visitor.when(COOL.DynamicDispatch)
	def visit(self, node: COOL.DynamicDispatch):
		instance_vname = self.visit(node.instance)
		ttype = self.register_internal_local()
		result = self.register_internal_local()

		pops = []
		for i in range(len(node.arguments)-1, -1, -1):
			param = node.arguments[i]
			param_vname = self.visit(param)
			self.register_instruction(cil.CIL_Push, param_vname)
			pops.append(param_vname)

		self.register_instruction(cil.CIL_Push, instance_vname)

		self.register_instruction(cil.CIL_TypeOf, ttype, instance_vname)

		method_name = f'{node.instance.stype}_{node.method}'
		self.register_instruction(cil.CIL_VCall, result, ttype, method_name)
		self.register_instruction(cil.CIL_Pop, instance_vname)

		for i in range(len(pops)-1, -1, -1):
			self.register_instruction(cil.CIL_Pop, pops[i])

		return result

	@visitor.when(COOL.StaticDispatch)
	def visit(self, node: COOL.StaticDispatch):
		instance_vname = self.visit(node.instance)
		result = self.register_internal_local()

		pops = []
		for i in range(len(node.arguments)-1, -1, -1):
			param = node.arguments[i]
			param_vname = self.visit(param)
			self.register_instruction(cil.CIL_Push, param_vname)
			pops.append(param_vname)

		self.register_instruction(cil.CIL_Push, instance_vname)

		method_name = f'{node.instance.stype}_{node.method}'
		self.register_instruction(cil.CIL_VCall, result, node.dispatch_type, method_name)
		self.register_instruction(cil.CIL_Pop, instance_vname)


		for i in range(len(pops)-1, -1, -1):
			self.register_instruction(cil.CIL_Pop, pops[i])

		return result




	@visitor.when(COOL.IntegerComplement)
	def visit(self, node: COOL.IntegerComplement):
		unboxed_val = self.register_internal_local()
		_temp = self.register_internal_local()
		result = self.register_internal_local()

		boxed_val = self.visit(node.integer_expr)
		self.register_instruction(cil.CIL_GetAttr, unboxed_val, boxed_val, 0)
		self.register_instruction(cil.CIL_Minus, _temp, 0, unboxed_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.BooleanComplement)
	def visit(self, node: COOL.BooleanComplement):
		
		unboxed_val = self.register_internal_local()
		_temp = self.register_internal_local()
		result = self.register_internal_local()

		boxed_val = self.visit(node.boolean_expr)
		self.register_instruction(cil.CIL_GetAttr, unboxed_val, boxed_val, 0)
		self.register_instruction(cil.CIL_Minus, _temp, 1, unboxed_val)
		self.register_instruction(cil.CIL_Allocate, result, BOOLEAN_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result



	@visitor.when(COOL.Addition)
	def visit(self, node: COOL.Addition):
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.CIL_GetAttr, first_val, first_boxed, 0)
		self.register_instruction(cil.CIL_GetAttr, second_val, second_boxed, 0)
		self.register_instruction(cil.CIL_Sum, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.Subtraction)
	def visit(self, node: COOL.Subtraction):
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.CIL_GetAttr, first_val, first_boxed, 0)
		self.register_instruction(cil.CIL_GetAttr, second_val, second_boxed, 0)
		self.register_instruction(cil.CIL_Minus, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.Multiplication)
	def visit(self, node: COOL.Multiplication):
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.CIL_GetAttr, first_val, first_boxed, 0)
		self.register_instruction(cil.CIL_GetAttr, second_val, second_boxed, 0)
		self.register_instruction(cil.CIL_Mult, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.Division)
	def visit(self, node: COOL.Division):
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.CIL_GetAttr, first_val, first_boxed, 0)
		self.register_instruction(cil.CIL_GetAttr, second_val, second_boxed, 0)
		self.register_instruction(cil.CIL_Div, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.Equal)
	def visit(self, node: COOL.Equal):
		_temp = self.register_internal_local()
		result = self.register_internal_local()

		first_val = self.visit(node.first)
		second_val = self.visit(node.second)
		self.register_instruction(cil.CIL_Equal, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, BOOLEAN_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.LessThan)
	def visit(self, node: COOL.LessThan):
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.CIL_GetAttr, first_val, first_boxed, 0)
		self.register_instruction(cil.CIL_GetAttr, second_val, second_boxed, 0)
		self.register_instruction(cil.CIL_LessThan, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


	@visitor.when(COOL.LessThanOrEqual)
	def visit(self, node: COOL.LessThanOrEqual):
		_temp = self.register_internal_local()
		first_val = self.register_internal_local()
		second_val = self.register_internal_local()
		result = self.register_internal_local()

		first_boxed = self.visit(node.first)
		second_boxed = self.visit(node.second)
		self.register_instruction(cil.CIL_GetAttr, first_val, first_boxed, 0)
		self.register_instruction(cil.CIL_GetAttr, second_val, second_boxed, 0)
		self.register_instruction(cil.CIL_EqualOrLessThan, _temp, first_val, second_val)
		self.register_instruction(cil.CIL_Allocate, result, INTEGER_CLASS)
		self.register_instruction(cil.CIL_SetAttr, result, 0, _temp)
		return result


class NameTable:
	def __init__(self, parent=None):
		self.table = {}
		self.parent = parent

	def is_define_variable(self, name, cilname):
		if name in self.table.keys():
			raise Exception("There are a variabel alredy defined with that name {}".format(name))
		self.table[name] = cilname

	def create_child_scope(self):
		child_scope = NameTable(self)
		return child_scope

	def exit_child_scope(self):
		self.table = self.parent.table
		self.parent = self.parent.parent

	def get_cil_name(self, name):
		if not name in self.table.keys():
			return self.parent.get_cil_name(name) if self.parent else None
		else:
			return self.table[name]