
import sys

import cil_ast as cil
import visitor as visitor
from settings import *





class MipsWriter:
	def __init__(self, inherit_graph, destination_path="mips_code.mips"):
		self.inherit_graph, _ = inherit_graph
		
		self.offset = dict()
		self.type_index = []
		self.dispatchtable_code = []
		self.prototypes_code = []
		self.cur_labels_id = 0

		self.output_file = destination_path

	def push(self):
		self.write('sw $a0 0($sp)')
		self.write('addiu $sp $sp -4')

	def pop(self, dest=None):
		self.write(f'addiu $sp $sp 4')


	def write(self, msg, mode = "a", tabbed=True):
		f = open(self.output_file, mode)
		f.write("{}{}\n".format("\t" if tabbed else "", msg))
		f.close()

	def allocate(self, size=None, register=False):
		if register:
			self.write('move $a0 {}'.format(size))
		else:
			if size:
				self.write('li $a0 {}'.format(size))
		self.write('li $v0 9')
		self.write('syscall')

	def new_labels_id(self):
		self.cur_labels_id += 1
		return self.cur_labels_id


	@visitor.on('node')
	def visit(self, node):
		pass



	@visitor.when(cil.CILProgram)
	def visit(self, node):
		self.write('', "w")
		self.write('.data', tabbed = False)

		self.static_datas()

		for data in node.data_section:
			self.visit(data)
		self.write('')

		for i in range(len(node.type_section)):
			self.type_index.append(node.type_section[i].type_name)
			self.write('classname_{}: .asciiz \"{}\"'.format(node.type_section[i].type_name,node.type_section[i].type_name))

		self.write(f'type_void: .asciiz \"\"')

		self.write('\n.text')
		self.main()

		self.write('\n############## Buit-in types functions ##############n')
		# CONFORMS
		self.conforms()
		# IS_VOID
		self.isvoid()
		# OBJECT
		self.object_abort()
		self.object_copy()
		self.object_typename()
		# STRING
		self.string_length()
		self.string_concat()
		self.string_substr()
		# IO
		self.io_in_int()
		self.io_in_string()
		self.io_out_int()
		self.io_out_string()

		for t in node.type_section:
			self.visit(t)

		self.write('\n############## TABLES ################\n')

		self.write('function_build_class_name_table:', tabbed=False)
		self.allocate(len(node.type_section) * 4)
		self.write('move $s1 $v0') 
		for i in range(len(node.type_section)):
			self.write('la $t1 classname_{}'.format(node.type_section[i].type_name))
			self.write('sw $t1 {}($s1)'.format(4 * i))
		self.write('')

		self.write('function_allocate_prototypes_table:', tabbed=False)
		self.allocate(8 * len(self.type_index))
		self.write('move $s0 $v0') 
		self.write('')

		self.write('function_build_prototypes:', tabbed=False)
		for ins in self.prototypes_code:
			self.write(ins)
		self.write('')

        #Aqui se generan las instrucciones para crear las tablas para las llamas que realiza el dispatch
		self.write('function_build_dispatch_tables:', tabbed=False)
		for ins in self.dispatchtable_code:
    			self.write(ins)
		self.write('')
		
		self.write('function_build_class_parents_table:', tabbed=False)
		self.allocate(4 * len(self.type_index))
		self.write('move $s2 $v0') 
		self.write('')


		for parent in self.inherit_graph.keys():
			p_index = self.type_index.index(parent)
			for child in self.inherit_graph[parent]:
				ch_index = self.type_index.index(child.name)
				self.write(f'li $t0 {ch_index}')
				self.write(f'mul $t0 $t0 4')
				self.write(f'add $t0 $t0 $s2')
				self.write(f'li $t1 {p_index}')
				self.write(f'sw $t1 0($t0)')
				self.write('')

		self.write('')


		#Aqui se generan las funciones definidas en el programa de COOL
		self.write('\n########### COOL FUNCTIONS ##########\n')
		for func in node.code_section:
			is_built_in = False
			if not INIT_CIL_SUFFIX in func.name:
				is_built_in = [x for x in BUILT_IN_CLASSES if f'{x}_' in func.name] != []
			if not is_built_in:
				self.visit(func)
		self.write('\n#####################################\n')





	@visitor.when(cil.CIL_Data)
	def visit(self, node):
		self.write(f'{node.dest}: .asciiz \"{str(node.value.encode())[2:-1]}\"')


	@visitor.when(cil.CIL_Type)
	def visit(self, node):
		# Allocate
		self.dispatchtable_code.append(f'# Type {node.type_name}')
		self.dispatchtable_code.append('li $a0 {}'.format(4 * len(node.methods)))
		self.dispatchtable_code.append('li $v0 9')
		self.dispatchtable_code.append('syscall')

		
		for i in range(len(node.methods)):
			self.dispatchtable_code.append('la $t1 function_{}'.format(node.methods[i].function_name))
			self.dispatchtable_code.append('sw $t1 {}($v0)'.format(4 * i))
		self.dispatchtable_code.append('lw $t0 {}($s0)'.format(8 * self.type_index.index(node.type_name)))
		self.dispatchtable_code.append('sw $v0 8($t0)')
		self.dispatchtable_code.append('')

		
		self.prototypes_code.append(f'# Type {node.type_name}')
		self.prototypes_code.append('li $a0 {}'.format(12 + 4 * len(node.attributes)))
		self.prototypes_code.append('li $v0 9')
		self.prototypes_code.append('syscall')

		class_index = self.type_index.index(node.type_name)
		self.prototypes_code.append('li $a0 {}'.format(class_index))
		self.prototypes_code.append('sw $a0 0($v0)')
		self.prototypes_code.append('li $a0 {}'.format(12 + 4 * len(node.attributes)))
		self.prototypes_code.append('sw $a0 4($v0)')
		self.prototypes_code.append('sw $v0 {}($s0)'.format(8 * class_index))
		self.prototypes_code.append('')


	@visitor.when(cil.CIL_Functions)
	def visit(self, node):
		self.write(f'function_{node.name}:', tabbed=False)

		self.write(f'move $fp, $sp')
		self.write(f'subu $sp, $sp, {4 * len(node.vlocals)}')

		for i in range(len(node.args)):
			self.offset[node.args[i].name] = 12 + i * 4

		for i in range(len(node.vlocals)):
			self.offset[node.vlocals[i].name] = i * (-4)

		for inst in node.body:
			if isinstance(inst, cil.CIL_Equal) or isinstance(inst, cil.CIL_Div):
				inst.id = self.new_labels_id()

			self.visit(inst)

		self.write(f'addiu $sp, $sp, {4 * len(node.vlocals)}')

		self.write('jr $ra')

		self.write('')


	@visitor.when(cil.CIL_Assign)
	def visit(self, node):
		self.write('# ASSIGN')
		self.write('lw $a0, {}($fp)'.format(self.offset[node.source]))
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write('')


	@visitor.when(cil.CIL_Sum)
	def visit(self, node):
		self.write('# +')
		self.write('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write('add $a0, $a0, $a1')
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write('')

	@visitor.when(cil.CIL_Minus)
	def visit(self, node):
		self.write('# -')
		if isinstance(node.left, int):
			self.write('li $a0 {}'.format(node.left))
		else:
			self.write('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write('sub $a0, $a0, $a1')
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write('')

	@visitor.when(cil.CIL_Mult)
	def visit(self, node):
		self.write('# *')
		self.write('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write('mul $a0, $a0, $a1')
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write('')

	@visitor.when(cil.CIL_Div)
	def visit(self, node):
		self.write('# /')
		self.write('lw $a0, {}($fp)'.format(self.offset[node.left]))
		self.write('lw $a1, {}($fp)'.format(self.offset[node.right]))
		self.write(f'beqz $a1 _div_error_{node.id}_')
		self.write('div $a0, $a0, $a1')
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write(f'b _div_end_{node.id}_')
		self.write(f'_div_error_{node.id}_:',tabbed=False)
		self.write('la $a0 _div_zero_msg')
		self.write('li $v0 4')
		self.write('syscall')
		self.write('la $a0 _abort_msg')
		self.write('li $v0 4')
		self.write('syscall')
		self.write('li $v0 10')
		self.write('syscall')
		self.write(f'_div_end_{node.id}_:',tabbed=False)


	@visitor.when(cil.CIL_Equal)
	def visit(self, node):
		self.write('lw $t0 {}($fp)'.format(self.offset[node.left]))
		self.write('lw $t1 {}($fp)'.format(self.offset[node.right]))
		self.write(f'beq $t0 $zero _eq_false_{node.id}_')  
		self.write(f'beq $t1 $zero _eq_false_{node.id}_') 
		self.write('lw $a0 0($t0)')	
		self.write('lw $a1 0($t1)')	
		self.write(f'bne $a0 $a1 _eq_false_{node.id}_')	
		self.write('li $a2 {}'.format(self.type_index.index('Int')))	
		self.write(f'beq $a0 $a2 _eq_int_bool_{node.id}')	# Integers
		self.write('li $a2 {}'.format(self.type_index.index('Bool')))	
		self.write(f'beq $a0 $a2 _eq_int_bool_{node.id}')	
		self.write('li $a2 {}'.format(self.type_index.index("String")))   
		self.write(f'bne $a0 $a2 _not_basic_type_{node.id}_') 

		self.write(f'_eq_str_{node.id}_:', tabbed = False) 	
		self.write('lw	$t3 12($t0)')  
		self.write('lw	$t3 12($t3)') 
		self.write('lw	$t4, 12($t1)') 
		self.write('lw	$t4, 12($t4)') 
		self.write(f'bne $t3 $t4 _eq_false_{node.id}_') 
		self.write(f'beq $t3 $0 _eq_true_{node.id}_')	  

		self.write('addu $t0 $t0 16')
		self.write('lw $t0 0($t0)')
		self.write('addu $t1 $t1 16') 	
		self.write('lw $t1 0($t1)')
		self.write('move $t2 $t3')		
		self.write(f'_verify_ascii_sequences_{node.id}_:', tabbed = False)
		self.write('lb $a0 0($t0)')	
		self.write('lb $a1 0($t1)')	
		self.write(f'bne $a0 $a1 _eq_false_{node.id}_') 
		self.write('addu $t0 $t0 1')
		self.write('addu $t1 $t1 1')
		self.write('addiu $t2 $t2 -1')	
		self.write(f'bnez $t2 _verify_ascii_sequences_{node.id}_')
		self.write(f'b _eq_true_{node.id}_')		# end of strings

		self.write(f'_not_basic_type_{node.id}_:', tabbed = False)
		self.write(f'bne $t0 $t1 _eq_false_{node.id}_')
		self.write(f'b _eq_true_{node.id}_')

		# equal int or boolf
		self.write(f'_eq_int_bool_{node.id}:', tabbed = False)	# handles booleans and ints
		self.write('lw $a3 12($t0)')	# load value variable_1
		self.write('lw $t4 12($t1)') # load variable_2
		self.write(f'bne $a3 $t4 _eq_false_{node.id}_') # value of int or bool are distinct

		#return true
		self.write(f'_eq_true_{node.id}_:', tabbed = False)
		self.write('li $a0 1')
		self.write('sw $a0 {}($fp)'.format(self.offset[node.dest]))
		self.write(f'b end_equal_{node.id}_')

		#return false
		self.write(f'_eq_false_{node.id}_:', tabbed = False)
		self.write('li $a0 0')
		self.write('sw $a0 {}($fp)'.format(self.offset[node.dest]))
		self.write(f'end_equal_{node.id}_:', tabbed = False)

	@visitor.when(cil.CIL_LessThan)
	def visit(self, node):
		self.write('# <')
		self.write('lw $a1, {}($fp)'.format(self.offset[node.left]))
		self.write('lw $a2, {}($fp)'.format(self.offset[node.right]))
		self.write('slt $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write('')

	@visitor.when(cil.CIL_EqualOrLessThan)
	def visit(self, node):
		self.write('# <=')
		self.write('lw $a1, {}($fp)'.format(self.offset[node.left]))
		self.write('lw $a2, {}($fp)'.format(self.offset[node.right]))
		self.write('sle $a0, $a1, $a2'.format(self.offset[node.right]))
		self.write('sw $a0, {}($fp)'.format(self.offset[node.dest]))
		self.write('')


	@visitor.when(cil.CIL_GetAttr)
	def visit(self, node):
		self.write('# GETATTR')
		self.write(f'lw $a1 {self.offset[node.instance]}($fp)')
		self.write(f'lw $a0 {12 + 4 * node.attribute}($a1)')
		self.write(f'sw $a0 {self.offset[node.dest]}($fp)')
		self.write('')


	@visitor.when(cil.CIL_SetAttr)
	def visit(self, node):
		self.write('# SETATTR')
		self.write(f'lw $a1 {self.offset[node.instance]}($fp)')
		if isinstance(node.src, int):
			self.write(f'li $a0, {node.src}')
		elif node.src[:5] == "data_":
			self.write(f'la $a0, {node.src}')
		else:
			self.write(f'lw $a0 {self.offset[node.src]}($fp)')
		self.write(f'sw $a0 {12 + 4 * node.attribute}($a1)')
		self.write('')


	@visitor.when(cil.CIL_TypeOf)
	def visit(self, node):
		self.write('# TYPEOF')
		self.write(f'lw $a1 {self.offset[node.instance]}($fp)')
		self.write(f'lw $a0 0($a1)')
		self.write(f'sw $a0 {self.offset[node.dest]}($fp)')
		self.write('')


	@visitor.when(cil.CIL_Allocate)
	def visit(self, node):
		self.write('# ALLOCATE')
		if node.ttype == 'Void':
			self.write(f'la $v0 type_void')
			self.write(f'sw $v0 {self.offset[node.dest]}($fp)')			
		else:
			offset_proto = self.type_index.index(node.ttype) * 8
			self.write('lw $t0 {}($s0)'.format(offset_proto))
			self.write('sw $t0, 0($sp)')
			self.write('addiu $sp, $sp, -4')
			self.write('')
			self.visit(cil.CIL_Call(dest = node.dest, f = "Object_copy"))
			self.write('addiu $sp, $sp, 4')
		self.write('')


	@visitor.when(cil.CIL_Call)
	def visit(self, node):
		self.write('# CALL')

		self.write(f'addiu $sp, $sp, -8')
		self.write(f'sw $ra, 4($sp)')
		self.write(f'sw $fp, 8($sp)')

		self.write(f'jal function_{node.f}')

		self.write(f'lw $fp, 8($sp)')
		self.write(f'lw $ra, 4($sp)')
		self.write(f'addiu $sp, $sp, 8')

		if node.dest:
			self.write(f'sw $v0 {self.offset[node.dest]}($fp)')

		self.write('')


	@visitor.when(cil.CIL_VCall)
	def visit(self, node):
		self.write('# VCALL')

		self.write(f'addiu $sp, $sp, -8')
		self.write(f'sw $ra, 4($sp)')
		self.write(f'sw $fp, 8($sp)')

		if node.ttype[0] == "_":
			self.write(f'lw $a2, {self.offset[node.ttype]}($fp)')
		else:
			self.write(f'li $a2, {self.type_index.index(node.ttype)}')
		self.write(f'mul $a2, $a2, 8')
		self.write(f'addu $a2, $a2, $s0')
		self.write(f'lw $a1, 0($a2)')

		self.write(f'lw $a2, 8($a1)')
		self.write(f'lw $a0 {node.f * 4}($a2)')

		self.write(f'jalr $a0')

		self.write(f'lw $fp, 8($sp)')
		self.write(f'lw $ra, 4($sp)')
		self.write(f'addiu $sp, $sp, 8')

		self.write(f'sw $v0 {self.offset[node.dest]}($fp)')

		if node.ttype[0] != '_':
			self.write(f'li $a2, {self.type_index.index(node.ttype)}')
		else:
			self.write(f'lw $a2, {self.offset[node.ttype]}($fp)')

		self.write('')


	@visitor.when(cil.CIL_Push)
	def visit(self, node):
		self.write('# PUSHPARAM')
		if node.name[0] != "_":
			self.write('li $a0, {}'.format(self.type_index.index(node.name)))
		else:
			self.write('lw $a0, {}($fp)'.format(self.offset[node.name]))
		self.push()
		self.write('')


	@visitor.when(cil.CIL_Pop)
	def visit(self, node):
		self.write('# POPPARAM')
		self.pop(node.name)
		self.write('')


	@visitor.when(cil.CIL_Return)
	def visit(self, node):
		self.write('# RETURN')
		self.write('lw $v0, {}($fp)'.format(self.offset[node.value]))


	@visitor.when(cil.CIL_Label)
	def visit(self, node):
		self.write('_cil_label_{}:'.format(node.name), tabbed=False)


	@visitor.when(cil.CIL_Goto)
	def visit(self, node):
		self.write('# GOTO')
		self.write('j _cil_label_{}'.format(node.label))
		self.write('')


	@visitor.when(cil.CIL_IfGoto)
	def visit(self, node):
		self.write('# IF GOTO')
		self.write('lw $a0, {}($fp)'.format(self.offset[node.condition]))
		self.write('bnez $a0, _cil_label_{}'.format(node.label))
		self.write('')



	def static_datas(self):
		# Buffer for reading strings
		self.write('str_buffer: .space 1025')		
		self.write('')

		# Declare error mensages
		self.write('_index_negative_msg: .asciiz \"The index is negative\\n\"')
		self.write('_index_out_msg: .asciiz \"Index out range exception\\n\"')
		self.write('_abort_msg: .asciiz \"Execution aborted\\n\"')
		self.write('_div_zero_msg: .asciiz \"Divide by zero, really nigga??\\n\"')

		self.write('')

	#----- ENTRY FUNCTION

	def main(self):
		self.write('main:', tabbed=False)
		self.visit(cil.CIL_Call(dest = None, f = 'build_class_name_table'))
		self.visit(cil.CIL_Call(dest = None, f = 'allocate_prototypes_table'))
		self.visit(cil.CIL_Call(dest = None, f = 'build_prototypes'))
		self.visit(cil.CIL_Call(dest = None, f = 'build_dispatch_tables'))
		self.visit(cil.CIL_Call(dest = None, f = 'build_class_parents_table'))
		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Main'))

		# Push main self
		self.write('sw $v0 0($sp)')
		self.write('addiu $sp $sp -4')

		self.visit(cil.CIL_Call(dest = None, f = f'Main_{INIT_CIL_SUFFIX}'))
		self.write('addiu $sp $sp 4')

		# Push main self
		self.write('sw $v0 0($sp)')
		self.write('addiu $sp $sp -4')

		self.visit(cil.CIL_Call(dest = None, f = 'Main_main'))
		self.write('addiu $sp $sp 4')

		self.write('li $v0 10')
		self.write('syscall')

	#----- OBJECT METHODS

	def object_abort(self):
		self.write('function_Object_abort:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.write('jr $ra')
		self.write('')

	def object_copy(self):
		self.write('function_Object_copy:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.write('lw $t0 12($fp)')# recoger la instancia a copiar
		self.write('lw $a0 4($t0)')
		self.write('move $t4 $a0')
		self.write('li $v0 9')
		self.write('syscall')# guarda en v0 la direccion de memoria que se reservo
		self.write('move $t2 $v0')# salvar la direccion donde comienza el objeto
		self.write('li $t3 0') # size ya copiado
		self.write('_objcopy_loop:', tabbed=False)
		self.write('lw $t1 0($t0)') # cargar la palabra por la que voy
		self.write('sw $t1 0($v0)') # copiar la palabra
		self.write('addiu $t0 $t0 4') # posiciona el puntero en la proxima palabra a copiar
		self.write('addiu $v0 $v0 4')	# posiciona el puntero en la direccion donde copiar la proxima palabra
		self.write('addiu $t3 $t3 4') # actualizar el size copiado
		self.write('ble $t4 $t3 _objcopy_loop') # verificar si la condicion es igual o menor igual
		self.write('_objcopy_div_end_:', tabbed=False)
		self.write('move $v0 $t2') # dejar en v0 la direccion donde empieza el nuevo objeto
		self.write('jr $ra')
		self.write('')

	def object_typename(self):
		self.write('function_Object_type_name:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		# Box the string reference
		self.visit(cil.CIL_Allocate(dest = None, ttype = 'String'))		# Create new String object
		self.write('move $v1 $v0')

		# Box string's length
		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Int')	)		# Create new Int object

		self.write('lw $a1 12($fp)')			# self
		self.write('lw $a1 0($a1)')
		self.write('mul $a1 $a1 4')			# self's class tag
		self.write('addu $a1 $a1 $s1')			# class name table entry address
		self.write('lw $a1 0($a1)')				# Get class name address

		self.write('move $a2 $0')				# Compute string's length
		self.write('move $t2 $a1')
		self.write('_str_len_clsname_:', tabbed=False)
		self.write('lb $a0 0($t2)')
		self.write('beq $a0 $0 _end_clsname_len_')
		self.write('addiu $a2 $a2 1')
		self.write('addiu $t2 $t2 1')
		self.write('j _str_len_clsname_')
		self.write('_end_clsname_len_:', tabbed=False)

		self.write('sw $a2, 12($v0)')			# Store string's length

		self.write('sw $v0, 12($v1)')			# Fill String attributes
		self.write('sw $a1, 16($v1)')

		self.write('move $v0 $v1')
		self.write('jr $ra')
		self.write('')


	#----- STRING METHODS

	def string_length(self):
		self.write('function_String_length:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.write('lw $a0 12($fp)')			# Self
		self.write('lw $v0 12($a0)')
		self.write('jr $ra')
		self.write('')

	def string_concat(self):
		self.write('function_String_concat:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Int'))		# Create new Int object
		self.write('move $v1 $v0')												# Save new Int Object

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'String'))		# Create new String object
		self.write('move $t3 $v0')			# Store new String object

		self.write('lw $a1 12($fp)')		# Self
		self.write('lw $a2 16($fp)')		# Boxed String to concat

		self.write('lw $t1 12($a1)')		# Self's length Int object
		self.write('lw $t1 12($t1)')		# Self's length

		self.write('lw $t2 12($a2)')		# strings to concat's length Int object
		self.write('lw $t2 12($t2)')		# strings to concat's length

		self.write('addu $t0 $t2 $t1') 		# New string's length
		self.write('sw $t0 12($v1)')			# Store new string's length into box

		self.write('lw $a1 16($a1)')		# Unbox strings
		self.write('lw $a2 16($a2)')

		self.write('addiu $t0 $t0 1')		# Add space for \0
		self.allocate('$t0', register=True)	# Allocate memory for new string
		self.write('move $t5 $v0')					# Keep the string's reference in v0 and use t7


		# a1: self's string		a2: 2nd string			t1: length self     t2: 2nd string length
		#									v1: new string's int object

		self.write('move $t4 $a1')			# Index for iterating the self string
		self.write('addu $a1 $a1 $t1')		# self's copy limit
		self.write('_strcat_copy_:', tabbed=False)
		self.write('beq $t4 $a1 _end_strcat_copy_')	# No more characters to copy

		self.write('lb $a0 0($t4)')			# Copy the character
		self.write('sb $a0 0($t5)')

		self.write('addiu $t5 $t5 1')		# Advance indices
		self.write('addiu $t4 $t4 1')
		self.write('j _strcat_copy_')
		self.write('_end_strcat_copy_:', tabbed=False)

		# Copy 2nd string

		self.write('move $t4 $a2')			# Index for iterating the strings
		self.write('addu $a2 $a2 $t2')		# self's copy limit
		self.write('_strcat_copy_snd_:', tabbed=False)
		self.write('beq $t4 $a2 _end_strcat_copy_snd_')	# No more characters to copy

		self.write('lb $a0 0($t4)')			# Copy the character
		self.write('sb $a0 0($t5)')

		self.write('addiu $t5 $t5 1')		# Advance indices
		self.write('addiu $t4 $t4 1')
		self.write('j _strcat_copy_snd_')
		self.write('_end_strcat_copy_snd_:', tabbed=False)

		self.write('sb $0 0($t5)')			# End string with \0

		# $v0: reference to new string			$v1: length int object
		# 						$t3: new string object
		# -> Create boxed string

		self.write('sw $v1 12($t3)')		# New length
		self.write('sw $v0 16($t3)')		# New string

		self.write('move $v0 $t3')			# Return new String object in $v0
		self.write('jr $ra')
		self.write('')

	def string_substr(self):
		self.write('function_String_substr:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')
		self.write(f'lw $t5 12($fp)') # self param
		self.write(f'lw $a1 16($fp)') # reference of object int that represent i
		self.write(f'lw $a1 12($a1)') # value of i
		self.write(f'lw $a2 20($fp)') # reference of object int that represent j
		self.write(f'lw $a2 12($a2)') # value of j that is length to copy
		self.write(f'blt $a1 $0 _index_negative') # index i is negative
		self.write(f'blt $a2 $0 _index_negative') # length j is negative
		self.write(f'add $a2 $a1 $a2') # finish index
		self.write(f'lw $a3 12($t5)')
		self.write(f'lw $a3 12($a3)') # length of string
		self.write(f'bgt $a2 $a3 _index_out') # j > lenght

		# not errors
		self.visit(cil.CIL_Allocate(dest = None, ttype = 'String'))
		self.write(f'move $v1 $v0') # new string

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Int'))
		self.write(f'move $t0 $v0') # lenght of string
		self.write(f'move $t7 $a2')
		self.write(f'subu $t7 $t7 $a1')
		self.write(f'sw $t7 12($t0)') # save number that represent lenght of new string

		self.allocate('$a2', register=True)	# $v0 -> address of the string

		self.write(f'sw $t0 12($v1)') # store length
		self.write(f'sw $v0 16($v1)') # store address of new string to String object

		# generate substring
		self.write('move $t1 $v0')				# Index for iterating the new string	
		
		self.write('lw $t5 16($t5)')			# Index for iterating the self string
		self.write('move $t4 $t5')
		self.write('addu $t4 $t4 $a1') # self's copy start
		self.write('addu $t5 $t5 $a2')	# self's copy limit

		self.write('_substr_copy_:', tabbed=False)
		self.write('bge $t4 $t5 _end_substr_copy_')	# No more characters to copy

		self.write('lb $a0 0($t4)')			# Copy the character
		self.write('sb $a0 0($t1)')

		self.write('addiu $t1 $t1 1')		# Advance indices
		self.write('addiu $t4 $t4 1')
		self.write('j _substr_copy_')

		# errors sections
		self.write(f'_index_negative:',tabbed=False)
		self.write(f'la $a0 _index_negative_msg')	
		self.write(f'b _subst_abort')

		self.write(f'_index_out:',tabbed=False)
		self.write(f'la $a0 _index_out_msg')	
		self.write(f'b _subst_abort')

		# abort execution 
		self.write(f'_subst_abort:',tabbed=False)
		self.write(f'li $v0 4') 
		self.write(f'syscall')
		self.write('la	$a0 _abort_msg')
		self.write(f'li $v0 4')
		self.write(f'syscall')
		self.write(f'li $v0 10')
		self.write(f'syscall') # exit

		# successful execution 
		self.write('_end_substr_copy_:', tabbed=False)

		self.write('move $v0 $v1')
		self.write('jr $ra')
		self.write('')

	#----- IO

	def io_in_int(self):
		self.write('function_IO_in_int:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Int'))			# Create new Int object

		self.write('move $t0 $v0')				# Save Int object

		self.write('li $v0 5')					# Read int
		self.write('syscall')

		self.write('sw $v0 12($t0)')			# Store int

		self.write('move $v0 $t0')
		self.write('jr $ra')
		self.write('')

	def io_in_string(self):
		self.write('function_IO_in_string:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Int'))		# Create new Int object for string's length
		self.write('move $v1 $v0')			# $v1: Int pbject

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'String'))			# Create new String object
		self.write('sw $v1 12($v0)')
		self.write('move $t5 $v0')			# $t5: String object

		# Read String and store in a temp buffer
		self.write('la $a0 str_buffer')
		self.write('li $a1 1025')
		self.write('li $v0 8')					# Read string
		self.write('syscall')

		# Compute string's length
		self.write('move $a0 $0')
		self.write('la $t2 str_buffer')
		self.write('_in_string_str_len_:', tabbed=False)
		self.write('lb $t0 0($t2)')
		self.write('beq $t0 $0 _end_in_string_str_len_')
		self.write('beq $t0 10 _end_in_string_str_len_')
		self.write('addiu $a0 $a0 1')
		self.write('addiu $t2 $t2 1')
		self.write('j _in_string_str_len_')
		self.write('_end_in_string_str_len_:', tabbed=False)

		# Store string's length into Integer class
		self.write('sw $a0 12($v1)')

		# Allocate size in $a0 ... string's length
		self.allocate()

		# $a0: string's length 			$v0: string's new address			$t5: String object

		# Copy string from buffer to new address
		self.write('la $t4 str_buffer')			# Index for iterating the string buffer
		self.write('move $t1 $v0')					# Index for iterating new string address

		self.write('_in_str_copy_:', tabbed=False)
		self.write('lb $t0 0($t4)')			# Load a character
		self.write('beq $t0 $0 _end_in_str_copy_')	# No more characters to copy
		self.write('beq $t0 10 _end_in_str_copy_')	# No more characters to copy

		self.write('sb $t0 0($t1)')			# Copy the character

		self.write('addiu $t4 $t4 1')		# Advance indices
		self.write('addiu $t1 $t1 1')
		self.write('j _in_str_copy_')
		self.write('_end_in_str_copy_:', tabbed=False)

		# Store string
		self.write('sw $v0 16($t5)')	

		# Clean string buffer
		self.write('la $t4 str_buffer')			# Index for iterating the string buffer
		self.write('_in_str_clean_:', tabbed=False)
		self.write('lb $t0 0($t4)')			# Load a character
		self.write('beq $t0 $0 _end_in_str_clean_')	# No more characters to clean

		self.write('sb $0 0($t4)')			# Clean the character

		self.write('addiu $t4 $t4 1')		# Advance indices
		self.write('j _in_str_clean_')
		self.write('_end_in_str_clean_:', tabbed=False)

		# Return new string in $v0
		self.write('move $v0 $t5')
		self.write('jr $ra')
		self.write('')

	def io_out_int(self):
		self.write('function_IO_out_int:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.write('lw $a0 16($fp)')			# Get Int object
		self.write('lw $a0 12($a0)')

		self.write('li $v0 1')					# Print int
		self.write('syscall')

		self.write('lw $v0 12($fp)')				# Return self
		self.write('jr $ra')
		self.write('')

	def io_out_string(self):
		self.write('function_IO_out_string:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.write('lw $a0 16($fp)')			# Get String object
		self.write('lw $a0 16($a0)')

		self.write('li $v0 4')					# Print string
		self.write('syscall')

		self.write('lw $v0 12($fp)')				# Return self
		self.write('jr $ra')
		self.write('')

	#------ CONFORMS

	def conforms(self):
		self.write(f'function_{CONFORMS_FUNC}:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.write(f'lw $t0 12($fp)')		# First arg's class tag
		self.write(f'lw $t1 16($fp)')		# Second arg's class tag

        
		# 2nd arg == Object -> return true
		self.write(f'beq $t1 {self.type_index.index(OBJECT_CLASS)} _conforms_ret_true_')	

		self.write('_conforms_loop_:', tabbed=False)

		# current == 2nd arg -> return true
		self.write('beq $t0 $t1 _conforms_ret_true_')	

		# current == Object -> return false
		self.write(f'beq $t0 {self.type_index.index(OBJECT_CLASS)} _conforms_ret_false_')		

		# Query parents's class tag from $s2 ... class parent table
		self.write('mul $t0 $t0 4')
		self.write('addu $t0 $t0 $s2')		
		self.write('lw $t0 0($t0)')			# current = current.parent
		self.write('j _conforms_loop_')
		
		self.write('_conforms_ret_true_:', tabbed=False)
		self.write('li $v0 1')
		self.write('j _conforms_ret_')

		self.write('_conforms_ret_false_:', tabbed=False)
		self.write('li $v0 0')
		
		# No need to store result in a Bool class
		self.write('_conforms_ret_:')
		self.write('jr $ra')
		self.write('')

	#------ ISVOID

	def isvoid(self):
		self.write(f'function_{ISVOID_FUNC}:', tabbed=False)
		# Set up stack frame
		self.write(f'move $fp, $sp')

		self.visit(cil.CIL_Allocate(dest = None, ttype = 'Bool'))
		# $v0 contains new Bool object

		self.write(f'lw $t0 12($fp)')					# 1st arg is an object address
		self.write(f'la $t1 {VOID_MIPS_NAME}')

		self.write(f'beq $t0 $t1 _is_void_true_')	# arg == void type
		self.write(f'sw $0 12($v0)')					# return False
		self.write(f'j _is_void_end_')

		self.write(f'_is_void_true_:', tabbed=False)
		self.write(f'li $t0 1')
		self.write(f'sw $t0 12($v0)')					# return True
		self.write(f'_is_void_end_:', tabbed=False)

		# Return Bool object in $v0
		self.write(f'jr $ra')
		self.write(f'')