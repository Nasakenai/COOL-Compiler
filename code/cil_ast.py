class CIL_AST:
    pass

class CILProgram(CIL_AST):
    def __init__(self,type_s,data_s,code_s):
        self.type_section = type_s
        self.data_section = data_s
        self.code_section = code_s
    
class CIL_Type(CIL_AST):
    def __init__(self, name,attr,meth):
        self.attributes = attr
        self.type_name = name
        self.methods = meth
        
class CIL_Data(CIL_AST):
    def __init__(self, vname, val):
        self.dest = vname
        self.value = val

class CIL_Attribute(CIL_AST):
    def __init__(self,name):
        self.name = name

class CIL_Method(CIL_AST):
    def __init__(self, name, fname):
        self.name = name
        self.function_name = fname

class CIL_Functions(CIL_AST):
    def __init__(self, name, args,vlocals,body):
        self.name = name
        self.vlocals = vlocals
        self.args = args
        self.body = body

class CIL_Arg(CIL_AST):
    def __init__(self, name):
        self.name = name

class CIL_Local(CIL_AST):
    def __init__(self, name):
        self.name = name

class CIL_Statement(CIL_AST):
    pass

class CIL_Assign(CIL_Statement):
    def __init__(self,dest,source):
        self.dest = dest
        self.source = source

class CIL_Arith(CIL_Statement):
    def __init__(self,dest,left,right):
        self.dest = dest
        self.left = left
        self.right = right

class CIL_Sum(CIL_Arith):
    pass

class CIL_Minus(CIL_Arith):
    pass

class CIL_Mult(CIL_Arith):
    pass

class CIL_Div(CIL_Arith):
    pass

class CIL_LessThan(CIL_Arith):
    pass

class CIL_Greater(CIL_Arith):
    pass

class CIL_Equal(CIL_Arith):
    pass

class CIL_GetAttr(CIL_Statement):
    def __init__(self,dest, instance,attr):
        self.dest =  dest
        self.instance = instance
        self.attribute = attr

class CIL_SetAttr(CIL_Statement):
    def __init__(self,instance,attr,src):
        self.instance = instance
        self.attribute = attr
        self.src = src

class CIL_GetIndex(CIL_GetAttr):
	def to_readable(self):
		return "{} = GETINDEX {} {}\n".format(self.dest, self.instance, self.attribute)


class CIL_SetIndex(CIL_SetAttr):
	def to_readable(self):
		return "SETINDEX {} {} {}\n".format(self.instance, self.attribute, self.src)


class CIL_Allocate(CIL_Statement):
    def __init__(self,dest, ttype):
        self.dest = dest
        self.ttype = ttype

class CIL_TypeOf(CIL_Statement):
    def __init__(self,dest,instance):
        self.dest = dest
        self.instance = instance

class CIL_Array(CIL_Statement):
    def __init__(self,dest,size):
        self.dest = dest
        self.src = size

class CIL_Call(CIL_Statement):
    def __init__(self,dest,f):
        self.dest = dest
        self.f = f

class CIL_VCall(CIL_Statement):
    def __init__(self,dest,ttype,f):
        self.dest =dest
        self.ttype = ttype
        self.f = f

class CIL_Push(CIL_Statement):
    def __init__(self,name):
        self.name = name

class CIL_Pop(CIL_Statement):
    def __init__(self,name):
        self.name = name

class CIL_Return(CIL_Statement):
    def __init__(self,val=None):
        self.value = val

class CIL_Label(CIL_Statement):
    def __init__(self,name):
        self.name = name

class CIL_Goto(CIL_Statement):
    def __init__(self, label):
        self.label = label

class CIL_IfGoto(CIL_Statement):
    def __init__(self, condition,label):
        self.condition = condition
        self.label = label

class CIL_Load(CIL_Statement):
    def __init__(self,dest,msg):
        self.dest = dest
        self.msg = msg

class CIL_Length(CIL_Statement):
    def __init__(self,dest,str_addr):
        self.dest = dest
        self.str_addr = str_addr

class CIL_Concat(CIL_Statement):
    def __init__(self,dest, first,second):
        self.dest= dest
        self.first = first
        self.second = second

class CIL_SubString(CIL_Statement):
    def __init__(self,dest,str_addr,pos_left = 0,pos_right = -1):
        self.dest = dest
        self.str_addr = str_addr
        self.pos_left =pos_left
        self.pos_right = pos_right

class CIL_ToString(CIL_Statement):
	def __init__(self, dest, num):
		self.dest = dest
		self.num = num

class CIL_Read(CIL_Statement):
	def __init__(self, dest):
		self.dest = dest

class CIL_Print(CIL_Statement):
	def __init__(self, str_addr):
		self.str_addr = str_addr

class CIL_EqualOrLessThan(CIL_Arith):
	def __init__(self, dest, left, right):
		super(CIL_EqualOrLessThan, self).__init__(dest, left, right)