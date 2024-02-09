import visitor
import cool_ast as AST
from collections import defaultdict
from logging import warning
from scope import *


UNBOXED_PRIMITIVE_VALUE_TYPE = "__prim_slot"
IO_CLASS = "IO"
OBJECT_CLASS = "Object"
INTEGER_CLASS = "Int"
BOOLEAN_CLASS = "Bool"
STRING_CLASS = "String"


'''
!!!!!!!Poner valor por defecto en los atributos!!!!!!!!!!
Hacer que las clases hereden de Object
Ordenar las clases de program segun el orden topologico
Revisar el grafo de herencia en el visit de las clases  
'''

class Semantic_Analizer:
    def __init__(self):
        self.classes_map = {}
        self.inheritance_graph = defaultdict(set)
        self.errors = []
        self.sorted_classes = []
        self.ast = None


    def topological_sort(self, classes):
        for _class in classes:
            if _class in self.sorted_classes: continue
            self.cosa1(_class)
    
    def cosa1(self,_class: AST.Class):
        if _class.parent == 'Object':
            self.sorted_classes.append(_class)
        else:
            self.cosa1(self.classes_map[_class.parent])
            self.sorted_classes.append(_class)



    def check_sematic(self, program):
        if not isinstance(program,AST.Program):
            raise Exception('The AST entry point must be a Program node.')

        self.ast = self.add_builtin_types_to_ast(program)
        self.scan_ast(self.ast)
        
        # if not self.check_cyclic_inheritance() or not self.check_not_inherit_from_builtin_types() or not self.check_for_Main():
        #     return False
        self.topological_sort(program.classes)
        program.classes =  self.sorted_classes
        #print('Start visit')
        return self.visit(self.ast)


    def check_cyclic_inheritance(self):
        global OBJECT_CLASS
        seen = {class_name:False for class_name in self.classes_map.keys()}
        self.dfs_graph_traverse(OBJECT_CLASS,seen)
        for class_name, was_seen in seen.items():
            if not was_seen:
                self.errors.append('Class {} completes an inheritance cycle'.format(class_name))
                return False
        return True

    def scan_ast(self,program:AST.Program):
        global OBJECT_CLASS

        if program is None:
            raise Exception("Program AST cannot be None.")

        if not isinstance(program, AST.Program):
            raise Exception(
                "Expected argument to be of type AST.Program, but got {} instead.".format(type(program)))
        
        classes_map = {}
        inheritance_graph = defaultdict(set)

        for _class in program.classes:
            if _class.name in classes_map:
                raise Exception("Class \"{}\" is already defined!".format(_class.name))
            classes_map[_class.name] = _class

            if _class.name == "Object":
                continue

            _class.parent = _class.parent if _class.parent else OBJECT_CLASS
            inheritance_graph[_class.parent].add(_class.name)

        self.classes_map = classes_map
        self.inheritance_graph = inheritance_graph

    def add_builtin_types_to_ast(self,program:AST.Program):

        if not isinstance(program,AST.Program):
            self.errors.append('COOL Ast Program node not found')
            return None
        
        global UNBOXED_PRIMITIVE_VALUE_TYPE

        object_class = AST.Class(name='Object', parent=None, features=[
            # Abort method: halts the program.
            AST.ClassMethod(name="abort", formal_params=[], return_type="Object", body=None),

            # Copy method: copies the object.
            AST.ClassMethod(name="copy", formal_params=[], return_type="SELF_TYPE", body=None),

            # type_name method: returns a string representation of the class name.
            AST.ClassMethod(name="type_name", formal_params=[], return_type="String", body=None)
        ])

        # IO Class
        io_class = AST.Class(name='IO', parent="Object", features=[
            # in_int: reads an integer from stdio
            AST.ClassMethod(name="in_int", formal_params=[], return_type="Int", body=None),

            # in_string: reads a string from stdio
            AST.ClassMethod(name="in_string", formal_params=[], return_type="String", body=None),

            # out_int: outputs an integer to stdio
            AST.ClassMethod(name="out_int",
                            formal_params=[AST.FormalParameter("arg", "Int")],
                            return_type="SELF_TYPE",
                            body=None),

            # out_string: outputs a string to stdio
            AST.ClassMethod(name="out_string",
                            formal_params=[AST.FormalParameter("arg", "String")],
                            return_type="SELF_TYPE",
                            body=None)
        ])

        # Int Class
        int_class = AST.Class(name= 'Int', parent=object_class.name, features=[
            # _val attribute: integer un-boxed value
            AST.ClassAttribute(name="_val", attr_type=UNBOXED_PRIMITIVE_VALUE_TYPE, init_expr=None)
        ])

        # Bool Class
        bool_class = AST.Class(name='Bool', parent=object_class.name, features=[
            # _val attribute: boolean un-boxed value
            AST.ClassAttribute(name="_val", attr_type=UNBOXED_PRIMITIVE_VALUE_TYPE, init_expr=None)
        ])

        # String Class
        string_class = AST.Class(name='String', parent=object_class.name, features=[
            # _val attribute: string length
            AST.ClassAttribute(name='_val', attr_type='Int', init_expr=None),

            # _str_field attribute: an un-boxed, untyped string value
            AST.ClassAttribute('_str_field', UNBOXED_PRIMITIVE_VALUE_TYPE, None),

            # length method: returns the string's length
            AST.ClassMethod(name='length', formal_params=[], return_type='Int', body=None),

            # concat method: concatenates this string with another
            AST.ClassMethod(name='concat',
                            formal_params=[AST.FormalParameter('arg', 'String')],
                            return_type='String',
                            body=None),

            # substr method: returns the substring between two integer indices
            AST.ClassMethod(name='substr',
                            formal_params=[AST.FormalParameter('arg1', 'Int'), AST.FormalParameter('arg2', 'Int')],
                            return_type='String',
                            body=None)
        ])

        # Built in classes collection
        builtin_classes = (object_class, io_class, int_class, bool_class, string_class)
        for builtin_class in builtin_classes:
            self.sorted_classes.append(builtin_class)
        # All classes
        all_classes = builtin_classes + program.classes
        
        return AST.Program(classes=all_classes)

    def check_not_inherit_from_builtin_types(self):
        if not self.inheritance_graph or len(self.inheritance_graph) == 0:
            warning("Inheritance Graph is empty!")

        if not self.classes_map or len(self.classes_map) == 0:
            warning("Classes Map is empty!")

        global INTEGER_CLASS, STRING_CLASS, BOOLEAN_CLASS

        for parent__class in [INTEGER_CLASS, STRING_CLASS, BOOLEAN_CLASS]:
            for child__class in self.inheritance_graph[parent__class]:
                self.errors.append( "Not Allowed! Class \"{0}\" is inheriting from built-in class \"{1}\".".format(
                        child__class, parent__class))
                return None

    def check_for_Main(self):
        if 'Main' not in self.classes_map.keys():
            self.errors.append('Main Class is not defined.')
            return False
        main = self.classes_map['Main']
        for item in main.features:
            if isinstance(item,AST.ClassMethod):
                if item.name == 'main': 
                    if len(item.formal_params) > 0:
                        self.errors.append('Main method signature is not correct.')
                        return False
                    return True
        self.errors.append('Main class has not contain a main method.')
        return False

    def dfs_graph_traverse(self,initNode,visit):
        if visit is None:
            visit = {}

        visit[initNode] = True

        # If the starting node is not a parent class for any child classes, then return!
        if initNode not in self.inheritance_graph:
            return True

        # Traverse the children of the current node
        for child_node in self.inheritance_graph[initNode]:
            self.dfs_graph_traverse(initNode=child_node, visit=visit)

        return True

    @visitor.on('node')
    def visit(self,node):
        pass

    @visitor.when(AST.Program)
    def visit(self, program):
        if program.classes is None: return None
        
        classes = {}
        for _class in self.sorted_classes:
            classes[_class.name] = _class.parent

        scopes = {}
        methods = {c:[] for c in classes }

        for _class in self.sorted_classes:
            if _class.parent is None:
                scopes[_class.name] = Scope(_class.name,classes,methods)
            else:
                scopes[_class.name] = Scope(_class.name,classes, methods,scopes[_class.parent])
            
            for feature in _class.features:
                if isinstance(feature,AST.ClassMethod):
                    method_signature = scopes[_class.name].is_define_method(_class.name,feature.name)
                    f_sig = tuple([param.param_type for param in feature.formal_params] + [feature.return_type])
                    if method_signature and f_sig != method_signature:
                        self.errors.append('Class method {}\'s redefinition signature does not match inherited signature at line {}'.format(feature.name, feature.lineno))
                        return None
                    else:
                        f_tuple = tuple([feature.name]) + f_sig
                        scopes[_class.name].M(_class.name, f_tuple)
                if isinstance(feature,AST.ClassAttribute):
                    if scopes[_class.name].is_define_obj(feature.name):
                        self.errors.append('Class Attribute {} already define at line {}'.format(feature.name,feature.lineno))
                    else:
                        scopes[_class.name].O(feature.name, feature.attr_type)
        #print(scopes.keys())
        for _class in self.sorted_classes:
            
            if not self.visit(self.classes_map[_class.name],scopes[_class.name]): return None 
        return program

    @visitor.when(AST.Class)
    def visit(self,_class,scope):
        if _class.name not in ['Int','String','IO','Bool','Object']:
            for feature in _class.features:
                feature.class_name = _class.name
                if not self.visit(feature,scope): 
                    #print('Fallo en {} de la clase {}'.format(feature.name,_class.name))
                    return False
        return True

    @visitor.when(AST.Object)
    def visit(self,obj,scope):
       # print('visit Object')
        define = scope.is_define_obj(obj.name)
        if not define:
            self.errors.append('Object {} not define at line {}'.format(obj.name,obj.lineno))
            return False

        if define == 'SELF_TYPE':
            obj.stype = scope.is_define_obj('self')
        else: obj.stype = define
        return True

#Revisar esto si no funciona
    @visitor.when(AST.Assignment)
    def visit(self, assign,scope):
        if not self.visit(assign.expr,scope):return False
        if not self.visit(assign.instance,scope):return False
        #inherit_type = self.classes_map[assign.instance.name]
        if not scope.inherit(assign.expr.stype, assign.instance.stype):
            self.errors.append('Invalid assignment at line {}, types doesn\'t match'.format(assign.lineno))
            return False
        assign.stype = assign.expr.stype
        return True


    @visitor.when(AST.Boolean)
    def visit(self, boolean,scope):
        #print('visit Boolean')
        boolean.stype = 'Bool'
        return True

    @visitor.when(AST.Integer)
    def visit(self, integer,scope):
        #print('visit Integer')
        integer.stype = 'Int'
        return True

    @visitor.when(AST.String)
    def visit(self, string,scope):
        #print('visit String')
        string.stype = 'String'
        return True

    @visitor.when(AST.Block)
    def visit(self, block, scope):
        #print('visit Block')
        for e in block.expr_list:
            if not self.visit(e, scope):
                return False
        block.stype = block.expr_list[-1].stype
        return True
    
    @visitor.when(AST.Action)
    def visit(self, action, scope):
        #print('visit Action')
        t = scope.is_define_obj('self') if action.action_type == 'SELF_TYPE' else action.action_type
        if not scope.is_define_type(t):
            self.errors.append('Type {} is not defined at line {}'.format(action.action_type, action.lineno))
            return False
        child = scope.createChildScope()
        child.O(action.name, t)
        if not self.visit(action.body, child):
            return False
        action.stype = action.body.stype
        return True

    @visitor.when(AST.WhileLoop)
    def visit(self, loop, scope):
        #print('visit WhileLoop')
        if not self.visit(loop.predicate, scope):
            return False
        if loop.predicate.stype != 'Bool':
            self.errors.append('While condition must have Bool type at line {}'.format(loop.lineno))
            return False
        if not self.visit(loop.body, scope):
            return False
        loop.stype = 'Object'
        return True

    @visitor.when(AST.IsVoid)
    def visit(self, void, scope):
        #print('visit IsVoid')
        if not self.visit(void.expr, scope):
            return False
        void.stype = 'Bool'
        return True
		
    @visitor.when(AST.BooleanComplement)
    def visit(self, bcompl, scope):
        #print('visit BooleanComplement')
        if not self.visit(bcompl.boolean_expr, scope):
            return False
        if not bcompl.boolean_expr.stype == 'Bool':
            self.errors.append('Boolean complement expression must have Bool type at line {}'.format(bcompl.lineno))
            return False
        bcompl.stype = 'Bool'
        return True


    @visitor.when(AST.LessThan)
    def visit(self, comp, scope):
        #print('visit LessThan')
        if not self.visit(comp.first, scope):
            return False
        if not self.visit(comp.second, scope):
            return False
        if comp.first.stype != 'Int' or comp.second.stype != 'Int':
            self.errors.append('Comparison must be between Integers at line {}'.format(comp.lineno))
            return False
        comp.stype = 'Bool'
        return True

    @visitor.when(AST.LessThanOrEqual)
    def visit(self, comp, scope):
        #print('visit LessThanOrEqual')
        if not self.visit(comp.first, scope):
            return False
        if not self.visit(comp.second, scope):
            return False
        if comp.first.stype != 'Int' or comp.second.stype != 'Int':
            self.errors.append('Comparison must be between Integers at line {}'.format(comp.lineno))
            return False
        comp.stype = 'Bool'
        return True

    @visitor.when(AST.IntegerComplement)
    def visit(self, icompl, scope):
        #print('visit IntegerComplement')
        if not self.visit(icompl.integer_expr, scope):
            return False
        if not icompl.integer_expr.stype == 'Int':
            self.errors.append('Int complement expression must have Int static type at line {}'.format(icompl.lineno))
            return False
        icompl.stype = 'Int'
        return True

    @visitor.when(AST.Addition)
    def visit(self, add, scope):
        #print('visit Addition')
        if not self.visit(add.first, scope):
            return False
        if not self.visit(add.second, scope):
            return False
        if add.first.stype != 'Int' or add.second.stype != 'Int':
            self.errors.append('Invalid arithmetic operator types at line {}'.format(add.lineno))
            return False
        add.stype = 'Int'
        return True

    @visitor.when(AST.Self)
    def visit(self, s,scope):
        s.stype = scope.is_define_obj('self')
        return True

    @visitor.when(AST.Subtraction)
    def visit(self, sub, scope):
        #print('visit Substraction')
        if not self.visit(sub.first, scope):
            return False
        if not self.visit(sub.second, scope):
            return False
        if sub.first.stype != 'Int' or sub.second.stype != 'Int':
            self.errors.append('Invalid arithmetic operator types at line {}'.format(sub.lineno))
            return False
        sub.stype = 'Int'
        return True

    @visitor.when(AST.Multiplication)
    def visit(self, mul, scope):
        #print('visit multiplication')
        if not self.visit(mul.first, scope):
            return False
        if not self.visit(mul.second, scope):
            return False
        if mul.first.stype != 'Int' or mul.second.stype != 'Int':
            self.errors.append('Invalid arithmetic operator types at line {}'.format(mul.lineno))
            return False
        mul.stype = 'Int'
        return True

    @visitor.when(AST.Division)
    def visit(self, div, scope):
        #print('visit Division')
        if not self.visit(div.first, scope):
            return False
        if not self.visit(div.second, scope):
            return False
        if div.first.stype != 'Int' or div.second.stype != 'Int':
            self.errors.append('Invalid arithmetic operator types at line {}'.format(div.lineno))
            return False
        div.stype = 'Int'
        return True

    @visitor.when(AST.Equal)
    def visit(self, eq, scope):
        #print('visit Equal')
        if not self.visit(eq.first, scope):
            return False
        if not self.visit(eq.second, scope):
            return False
        if (eq.first.stype == 'Int' or eq.first.stype == 'String' or eq.first.stype == 'Bool') and not eq.first.stype == eq.second.stype:
            self.errors.append(' Comparison must be performed between expressions of the same types, error at line {}'.format(eq.lineno))
            return False
        eq.stype = 'Bool'
        return True

    @visitor.when(AST.ClassAttribute)
    def visit(self, attr, scope):
        # print('Check semantic attr.name {}'.format(attr.name))
        # print('visit ClassAtributte')
        t = scope.is_define_obj('self') if attr.attr_type == 'SELF_TYPE' else attr.attr_type
        if not scope.is_define_type(t):
            self.errors.append('Type {} is not defined at line {}'.format(t, attr.lineno))
            return False
        if attr.init_expr:
            if not self.visit(attr.init_expr, scope):
                return False
            if not scope.inherit(attr.init_expr.stype, t):
                self.errors.append('Attribute initialization type does not conform declared type at line {}'.format(attr.lineno))
                return False
        attr.stype = t
        #print(attr.stype)
        return True
		
    @visitor.when(AST.FormalParameter)
    def visit(self, param, scope):
        #print('visit FormalParameter')
        if not scope.is_define_type(param.param_type):
            self.errors.append('Type {} is not defined at line {}'.format(param.param_type, param.lineno))
            return False
        param.stype = param.param_type
        #print('end formal')
        return True
	
    @visitor.when(AST.ClassMethod)
    def visit(self, method, scope):
        #print('visit ClassMethod')

        for p in method.formal_params:
            if not self.visit(p, scope):
                return False
        child = scope.createChildScope()
        for p in method.formal_params:
            #print(p)
            child.O(p.name, p.param_type)
            #print(method.body)
        if not self.visit(method.body, child):
            return False
        t = scope.is_define_obj('self') if method.return_type == 'SELF_TYPE' else method.return_type
        if not scope.is_define_type(t):
            self.errors.append('Type {} is not defined at line {}'.format(t, method.lineno))
            return False
        if not scope.inherit(method.body.stype, t):
            self.errors.append('Method {}\'s body type does not conform declared return type at line {}'.format(method.name, method.lineno))
            return False
        if (scope.inherit(method.class_name, OBJECT_CLASS) and method.name in ['abort', 'copy', 'type_name']) or \
            (scope.inherit(method.class_name, IO_CLASS) and method.name in ['in_int', 'in_string', 'out_int', 'out_string']) or \
            (scope.inherit(method.class_name, STRING_CLASS) and method.name in ['length', 'concat', 'substr']):
            self.errors.append('Built-in method {} cannot be redefined at line {}'.format(method.name, method.lineno))
            return None
        method.stype = t
        return True

    @visitor.when(AST.If)
    def visit(self, cond, scope):
        if not self.visit(cond.predicate, scope):
            return False
        if not cond.predicate.stype == 'Bool':
            self.errors.append('If\'s condition must have Bool static type at line {}'.format(cond.line))
            return False
        if not self.visit(cond.then_body, scope):
            return False
        if not self.visit(cond.else_body, scope):
            return False
        cond.stype = scope.join(cond.then_body.stype, cond.else_body.stype)
        return True

    @visitor.when(AST.NewObject)
    def visit(self,nobj,scope):
        #print('visit NewObject')
        t = scope.is_define_obj('self') if nobj.type == 'SELF_TYPE' else nobj.type
        if not scope.is_define_type(t):
            self.errors.append('Type {} is not defined at line {}'.format(t, nobj.lineno))
            return False
        nobj.stype = t
        return True

    @visitor.when(AST.DynamicDispatch)
    def visit(self, ddispatch, scope):
        #print('visit Dynamic Dispatch')
        if not self.visit(ddispatch.instance, scope):
            return False
        for arg in ddispatch.arguments:
            if not self.visit(arg, scope):
                return False
        m = scope.is_define_method(ddispatch.instance.stype, ddispatch.method)
        if not m:
            self.errors.append('Method {} not found at line {}'.format(ddispatch.method, ddispatch.lineno))
            return False
        if len(ddispatch.arguments) != len(m) - 1:
            self.errors.append('Missing arguments for method dispatch at line {}'.format(ddispatch.lineno))
            return False
        for i in range(len(ddispatch.arguments)):
            if not scope.inherit(ddispatch.arguments[i].stype, m[i]):
                self.errors.append('Type of argument {} does not conform declared type in function call at line {}'.format(i+1, ddispatch.lineno))
                return False
        ddispatch.stype = ddispatch.instance.stype if m[-1] == 'SELF_TYPE' else m[-1]
        return True
    
    @visitor.when(AST.StaticDispatch)
    def visit(self, sdispatch, scope):
        #print('visit static Dispatch')
        if not self.visit(sdispatch.instance, scope):
            return False
        t = scope.is_define_obj('self') if sdispatch.dispatch_type == 'SELF_TYPE' else sdispatch.dispatch_type
        if not scope.is_define_type(t):
            self.errors.append('Type {} is not defined at line {}'.format(t, sdispatch.lineno))
            return False
        if not scope.inherit(sdispatch.instance.stype, t):
            self.errors.append('Type to the left of @ : {} must conform the type specified to the right of @: {}, at line {}'.format(sdispatch.instance.stype, t, sdispatch.lineno))
            return False
        for arg in sdispatch.arguments:
            if not self.visit(arg, scope):
	            return False
        m = scope.is_define_method(sdispatch.instance.stype, sdispatch.method)
        if not m:
            self.errors.append('Method {} not found at line {}'.format(sdispatch.method, sdispatch.lineno))
            return False
        if len(sdispatch.arguments) != len(m) - 1:
            self.errors.append('Missing arguments for method dispatch at line {}'.format(sdispatch.lineno))
            return False
        for i in range(len(sdispatch.arguments)):
            if not scope.inherit(sdispatch.arguments[i].stype, m[i]):
                self.errors.append('Type of argument {} does not conform declared type in function call at line {}'.format(i+1, sdispatch.lineno))
                return False
        sdispatch.stype = sdispatch.instance.stype if m[-1] == 'SELF_TYPE' else m[-1]
        return True

    @visitor.when(AST.Let)
    def visit(self, let, scope):
        child = scope.createChildScope()
        for letvar in let.variables:
            if not self.visit(letvar, child):
                return False
        if not self.visit(let.body, child):
            return False
        let.stype = let.body.stype
        return True

    @visitor.when(AST.LetVariable)
    def visit(self, letvar, scope):
        t = scope.is_define_obj('self') if letvar.ttype == 'SELF_TYPE' else letvar.ttype
        if not scope.is_define_type(t):
            self.errors.append('Type {} is not defined at line {}'.format(t, letvar.lineno))
            return False
        if letvar.initialization:
            if not self.visit(letvar.initialization, scope):
                return False
            if not scope.inherit(letvar.initialization.stype, t):
                self.errors.append("Type {} does not conform type {} at line {}". format(letvar.initialization.stype, t, letvar.lineno))
                return False
        scope.O(letvar.name, t)
        letvar.stype = letvar.initialization.stype if letvar.initialization else t
        return True

    @visitor.when(AST.Case)
    def visit(self, case, scope):
        if not self.visit(case.expr, scope):
            return False
        for act in case.actions:
            if not self.visit(act, scope):
                return False
        stype = case.actions[0].stype
        for act in case.actions[1:]:
            stype = scope.join(stype, act.stype)
        case.stype = stype
        return True