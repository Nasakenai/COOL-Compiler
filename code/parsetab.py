
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'rightASSIGNrightNOTnonassocLTEQLTEQleftPLUSMINUSleftMULTIPLYDIVIDErightISVOIDrightINT_COMPleftATleftDOTARROW ASSIGN AT BOOLEAN CASE CLASS COLON COMMA DIVIDE DOT ELSE EQ ESAC FI ID IF IN INHERITS INTEGER INT_COMP ISVOID LBRACE LET LOOP LPAREN LT LTEQ MINUS MULTIPLY NEW NOT OF PLUS POOL RBRACE RPAREN SELF SEMICOLON STRING THEN TYPE WHILE\n\t\tprogram : class_list\n\t\t\n\t\tclass_list : class_list class SEMICOLON\n\t\t\t\t\t\t| class SEMICOLON\n\t\t\n\t\tclass : CLASS TYPE LBRACE features_list_opt RBRACE\n\t\t\n\t\tclass : CLASS TYPE INHERITS TYPE LBRACE features_list_opt RBRACE\n\t\t\n\t\tfeatures_list_opt : features_list\n\t\t\t\t\t\t\t\t| empty\n\t\t\n\t\tfeatures_list : features_list feature SEMICOLON\n\t\t\t\t\t\t\t| feature SEMICOLON\n\t\t\n\t\tfeature : ID LPAREN formal_params_list RPAREN COLON TYPE LBRACE expression RBRACE\n\t\t\n\t\tfeature : ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE\n\t\t\n\t\tfeature : ID COLON TYPE ASSIGN expression\n\t\t\n\t\tfeature : ID COLON TYPE\n\t\t\n\t\tformal_params_list  : formal_params_list COMMA formal_param\n\t\t\t\t\t\t\t\t\t| formal_param\n\t\t\n\t\tformal_param : ID COLON TYPE\n\t\t\n\t\texpression : ID\n\t\t\n\t\texpression : INTEGER\n\t\t\n\t\texpression : BOOLEAN\n\t\t\n\t\texpression : STRING\n\t\t\n\t\texpression  : SELF\n\t\t\n\t\texpression : LBRACE block_list RBRACE\n\t\t\n\t\tblock_list : block_list expression SEMICOLON\n\t\t\t\t\t\t| expression SEMICOLON\n\t\t\n\t\texpression : ID ASSIGN expression\n\t\t\n\t\texpression : expression DOT ID LPAREN arguments_list_opt RPAREN\n\t\t\n\t\targuments_list_opt : arguments_list\n\t\t\t\t\t\t\t\t| empty\n\t\t\n\t\targuments_list : arguments_list COMMA expression\n\t\t\t\t\t\t\t| expression\n\t\t\n\t\texpression : expression AT TYPE DOT ID LPAREN arguments_list_opt RPAREN\n\t\t\n\t\texpression : ID LPAREN arguments_list_opt RPAREN\n\t\t\n\t\texpression : expression PLUS expression\n\t\t\t\t\t\t| expression MINUS expression\n\t\t\t\t\t\t| expression MULTIPLY expression\n\t\t\t\t\t\t| expression DIVIDE expression\n\t\t\n\t\texpression : expression LT expression\n\t\t\t\t\t\t| expression LTEQ expression\n\t\t\t\t\t\t| expression EQ expression\n\t\t\n\t\texpression : LPAREN expression RPAREN\n\t\t\n\t\texpression : IF expression THEN expression ELSE expression FI\n\t\t\n\t\texpression : WHILE expression LOOP expression POOL\n\t\t\n\t\texpression : let_expression\n\t\t\n\t\tlet_expression : LET let_variables_list IN expression\n\t\t\n\t\tlet_variables_list : let_variables_list COMMA let_variable\n\t\t\t\t\t\t\t\t\t| let_variable\n\t\t\n\t\tlet_variable : ID COLON TYPE\n\t\t\t\t\t\t\t| ID COLON TYPE ASSIGN expression\n\t\t\n\t\texpression : CASE expression OF actions_list ESAC\n\t\t\n\t\tactions_list : actions_list action\n\t\t\t\t\t\t| action\n\t\t\n\t\taction : ID COLON TYPE ARROW expression SEMICOLON\n\t\t\n\t\texpression : NEW TYPE\n\t\t\n\t\texpression : ISVOID expression\n\t\t\n\t\texpression : INT_COMP expression\n\t\t\n\t\texpression : NOT expression\n\t\t\n\t\tempty :\n\t\t'
    
_lr_action_items = {'CLASS':([0,2,6,8,],[4,4,-3,-2,]),'$end':([1,2,6,8,],[0,-1,-3,-2,]),'SEMICOLON':([3,5,14,17,18,28,35,40,41,42,43,44,45,50,71,76,77,78,79,85,92,93,94,95,96,97,98,99,100,102,110,111,121,124,129,130,134,140,142,143,],[6,8,19,-4,23,-13,-5,-17,-12,-18,-19,-20,-21,-43,101,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,115,-40,-11,-32,-44,-10,-42,-49,-26,-41,-31,144,]),'TYPE':([4,10,21,30,33,37,52,62,108,132,],[7,16,28,36,39,57,76,91,123,137,]),'LBRACE':([7,16,34,39,46,47,48,49,51,53,54,55,57,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[9,22,46,58,46,46,46,46,46,46,46,46,83,46,46,46,46,46,46,46,46,46,46,46,46,-24,46,46,46,46,46,-23,46,46,46,46,]),'INHERITS':([7,],[10,]),'RBRACE':([9,11,12,13,19,22,23,29,40,42,43,44,45,50,70,76,77,78,79,84,85,92,93,94,95,96,97,98,99,101,102,109,111,115,121,129,130,134,140,142,],[-57,17,-6,-7,-9,-57,-8,35,-17,-18,-19,-20,-21,-43,99,-53,-54,-55,-56,110,-25,-33,-34,-35,-36,-37,-38,-39,-22,-24,-40,124,-32,-23,-44,-42,-49,-26,-41,-31,]),'ID':([9,12,19,20,22,23,32,34,46,47,48,49,51,53,54,55,56,58,59,60,61,63,64,65,66,67,68,69,70,83,101,103,104,105,106,107,112,113,114,115,118,119,128,131,133,135,141,144,],[15,15,-9,24,15,-8,24,40,40,40,40,40,40,40,40,40,82,40,40,40,90,40,40,40,40,40,40,40,40,40,-24,40,40,120,40,82,40,40,127,-23,120,-51,40,-50,40,40,40,-52,]),'LPAREN':([15,34,40,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,90,101,103,104,106,112,113,115,127,128,133,135,141,],[20,47,60,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,113,-24,47,47,47,47,47,-23,135,47,47,47,47,]),'COLON':([15,24,26,31,82,120,],[21,30,33,37,108,132,]),'RPAREN':([20,25,27,36,38,40,42,43,44,45,50,60,72,76,77,78,79,85,86,87,88,89,92,93,94,95,96,97,98,99,102,111,113,121,125,126,129,130,134,135,139,140,142,],[26,31,-15,-16,-14,-17,-18,-19,-20,-21,-43,-57,102,-53,-54,-55,-56,-25,111,-27,-28,-30,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-57,-44,-29,134,-42,-49,-26,-57,142,-41,-31,]),'COMMA':([25,27,36,38,40,42,43,44,45,50,76,77,78,79,80,81,85,87,89,92,93,94,95,96,97,98,99,102,111,121,122,123,125,129,130,134,138,140,142,],[32,-15,-16,-14,-17,-18,-19,-20,-21,-43,-53,-54,-55,-56,107,-46,-25,112,-30,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-44,-45,-47,-29,-42,-49,-26,-48,-41,-31,]),'ASSIGN':([28,40,123,],[34,59,133,]),'INTEGER':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,42,-24,42,42,42,42,42,-23,42,42,42,42,]),'BOOLEAN':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,-24,43,43,43,43,43,-23,43,43,43,43,]),'STRING':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,-24,44,44,44,44,44,-23,44,44,44,44,]),'SELF':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,-24,45,45,45,45,45,-23,45,45,45,45,]),'IF':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,-24,48,48,48,48,48,-23,48,48,48,48,]),'WHILE':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,-24,49,49,49,49,49,-23,49,49,49,49,]),'CASE':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,51,-24,51,51,51,51,51,-23,51,51,51,51,]),'NEW':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,-24,52,52,52,52,52,-23,52,52,52,52,]),'ISVOID':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,53,-24,53,53,53,53,53,-23,53,53,53,53,]),'INT_COMP':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,54,-24,54,54,54,54,54,-23,54,54,54,54,]),'NOT':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,55,-24,55,55,55,55,55,-23,55,55,55,55,]),'LET':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,101,103,104,106,112,113,115,128,133,135,141,],[56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,56,-24,56,56,56,56,56,-23,56,56,56,56,]),'DOT':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,91,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,61,-18,-19,-20,-21,-43,61,61,61,61,61,-53,61,61,61,61,61,61,114,61,61,61,61,61,61,61,-22,61,-40,61,-32,61,61,61,61,-42,-49,-26,61,61,-41,-31,61,]),'AT':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,62,-18,-19,-20,-21,-43,62,62,62,62,62,-53,62,62,62,62,62,62,62,62,62,62,62,62,62,-22,62,-40,62,-32,62,62,62,62,-42,-49,-26,62,62,-41,-31,62,]),'PLUS':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,63,-18,-19,-20,-21,-43,63,63,63,63,63,-53,-54,-55,63,63,63,63,-33,-34,-35,-36,63,63,63,-22,63,-40,63,-32,63,63,63,63,-42,-49,-26,63,63,-41,-31,63,]),'MINUS':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,64,-18,-19,-20,-21,-43,64,64,64,64,64,-53,-54,-55,64,64,64,64,-33,-34,-35,-36,64,64,64,-22,64,-40,64,-32,64,64,64,64,-42,-49,-26,64,64,-41,-31,64,]),'MULTIPLY':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,65,-18,-19,-20,-21,-43,65,65,65,65,65,-53,-54,-55,65,65,65,65,65,65,-35,-36,65,65,65,-22,65,-40,65,-32,65,65,65,65,-42,-49,-26,65,65,-41,-31,65,]),'DIVIDE':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,66,-18,-19,-20,-21,-43,66,66,66,66,66,-53,-54,-55,66,66,66,66,66,66,-35,-36,66,66,66,-22,66,-40,66,-32,66,66,66,66,-42,-49,-26,66,66,-41,-31,66,]),'LT':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,67,-18,-19,-20,-21,-43,67,67,67,67,67,-53,-54,-55,67,67,67,67,-33,-34,-35,-36,None,None,None,-22,67,-40,67,-32,67,67,67,67,-42,-49,-26,67,67,-41,-31,67,]),'LTEQ':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,68,-18,-19,-20,-21,-43,68,68,68,68,68,-53,-54,-55,68,68,68,68,-33,-34,-35,-36,None,None,None,-22,68,-40,68,-32,68,68,68,68,-42,-49,-26,68,68,-41,-31,68,]),'EQ':([40,41,42,43,44,45,50,71,72,73,74,75,76,77,78,79,84,85,89,92,93,94,95,96,97,98,99,100,102,109,111,116,117,121,125,129,130,134,136,138,140,142,143,],[-17,69,-18,-19,-20,-21,-43,69,69,69,69,69,-53,-54,-55,69,69,69,69,-33,-34,-35,-36,None,None,None,-22,69,-40,69,-32,69,69,69,69,-42,-49,-26,69,69,-41,-31,69,]),'THEN':([40,42,43,44,45,50,73,76,77,78,79,85,92,93,94,95,96,97,98,99,102,111,121,129,130,134,140,142,],[-17,-18,-19,-20,-21,-43,103,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-44,-42,-49,-26,-41,-31,]),'LOOP':([40,42,43,44,45,50,74,76,77,78,79,85,92,93,94,95,96,97,98,99,102,111,121,129,130,134,140,142,],[-17,-18,-19,-20,-21,-43,104,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-44,-42,-49,-26,-41,-31,]),'OF':([40,42,43,44,45,50,75,76,77,78,79,85,92,93,94,95,96,97,98,99,102,111,121,129,130,134,140,142,],[-17,-18,-19,-20,-21,-43,105,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-44,-42,-49,-26,-41,-31,]),'ELSE':([40,42,43,44,45,50,76,77,78,79,85,92,93,94,95,96,97,98,99,102,111,116,121,129,130,134,140,142,],[-17,-18,-19,-20,-21,-43,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,128,-44,-42,-49,-26,-41,-31,]),'POOL':([40,42,43,44,45,50,76,77,78,79,85,92,93,94,95,96,97,98,99,102,111,117,121,129,130,134,140,142,],[-17,-18,-19,-20,-21,-43,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,129,-44,-42,-49,-26,-41,-31,]),'FI':([40,42,43,44,45,50,76,77,78,79,85,92,93,94,95,96,97,98,99,102,111,121,129,130,134,136,140,142,],[-17,-18,-19,-20,-21,-43,-53,-54,-55,-56,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-44,-42,-49,-26,140,-41,-31,]),'IN':([40,42,43,44,45,50,76,77,78,79,80,81,85,92,93,94,95,96,97,98,99,102,111,121,122,123,129,130,134,138,140,142,],[-17,-18,-19,-20,-21,-43,-53,-54,-55,-56,106,-46,-25,-33,-34,-35,-36,-37,-38,-39,-22,-40,-32,-44,-45,-47,-42,-49,-26,-48,-41,-31,]),'ESAC':([118,119,131,144,],[130,-51,-50,-52,]),'ARROW':([137,],[141,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'class_list':([0,],[2,]),'class':([0,2,],[3,5,]),'features_list_opt':([9,22,],[11,29,]),'features_list':([9,22,],[12,12,]),'empty':([9,22,60,113,135,],[13,13,88,88,88,]),'feature':([9,12,22,],[14,18,14,]),'formal_params_list':([20,],[25,]),'formal_param':([20,32,],[27,38,]),'expression':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,103,104,106,112,113,128,133,135,141,],[41,71,72,73,74,75,77,78,79,84,85,89,92,93,94,95,96,97,98,100,109,116,117,121,125,89,136,138,89,143,]),'let_expression':([34,46,47,48,49,51,53,54,55,58,59,60,63,64,65,66,67,68,69,70,83,103,104,106,112,113,128,133,135,141,],[50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,]),'block_list':([46,],[70,]),'let_variables_list':([56,],[80,]),'let_variable':([56,107,],[81,122,]),'arguments_list_opt':([60,113,135,],[86,126,139,]),'arguments_list':([60,113,135,],[87,87,87,]),'actions_list':([105,],[118,]),'action':([105,118,],[119,131,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> class_list','program',1,'p_program','myparser.py',69),
  ('class_list -> class_list class SEMICOLON','class_list',3,'p_class_list','myparser.py',76),
  ('class_list -> class SEMICOLON','class_list',2,'p_class_list','myparser.py',77),
  ('class -> CLASS TYPE LBRACE features_list_opt RBRACE','class',5,'p_class','myparser.py',86),
  ('class -> CLASS TYPE INHERITS TYPE LBRACE features_list_opt RBRACE','class',7,'p_class_inherits','myparser.py',93),
  ('features_list_opt -> features_list','features_list_opt',1,'p_feature_list_opt','myparser.py',100),
  ('features_list_opt -> empty','features_list_opt',1,'p_feature_list_opt','myparser.py',101),
  ('features_list -> features_list feature SEMICOLON','features_list',3,'p_feature_list','myparser.py',107),
  ('features_list -> feature SEMICOLON','features_list',2,'p_feature_list','myparser.py',108),
  ('feature -> ID LPAREN formal_params_list RPAREN COLON TYPE LBRACE expression RBRACE','feature',9,'p_feature_method','myparser.py',117),
  ('feature -> ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE','feature',8,'p_feature_method_no_formals','myparser.py',124),
  ('feature -> ID COLON TYPE ASSIGN expression','feature',5,'p_feature_attr_initialized','myparser.py',131),
  ('feature -> ID COLON TYPE','feature',3,'p_feature_attr','myparser.py',138),
  ('formal_params_list -> formal_params_list COMMA formal_param','formal_params_list',3,'p_formal_list_many','myparser.py',145),
  ('formal_params_list -> formal_param','formal_params_list',1,'p_formal_list_many','myparser.py',146),
  ('formal_param -> ID COLON TYPE','formal_param',3,'p_formal','myparser.py',155),
  ('expression -> ID','expression',1,'p_expression_object_identifier','myparser.py',162),
  ('expression -> INTEGER','expression',1,'p_expression_integer_constant','myparser.py',169),
  ('expression -> BOOLEAN','expression',1,'p_expression_boolean_constant','myparser.py',176),
  ('expression -> STRING','expression',1,'p_expression_string_constant','myparser.py',183),
  ('expression -> SELF','expression',1,'p_expr_self','myparser.py',190),
  ('expression -> LBRACE block_list RBRACE','expression',3,'p_expression_block','myparser.py',197),
  ('block_list -> block_list expression SEMICOLON','block_list',3,'p_block_list','myparser.py',204),
  ('block_list -> expression SEMICOLON','block_list',2,'p_block_list','myparser.py',205),
  ('expression -> ID ASSIGN expression','expression',3,'p_expression_assignment','myparser.py',214),
  ('expression -> expression DOT ID LPAREN arguments_list_opt RPAREN','expression',6,'p_expression_dispatch','myparser.py',223),
  ('arguments_list_opt -> arguments_list','arguments_list_opt',1,'p_arguments_list_opt','myparser.py',230),
  ('arguments_list_opt -> empty','arguments_list_opt',1,'p_arguments_list_opt','myparser.py',231),
  ('arguments_list -> arguments_list COMMA expression','arguments_list',3,'p_arguments_list','myparser.py',237),
  ('arguments_list -> expression','arguments_list',1,'p_arguments_list','myparser.py',238),
  ('expression -> expression AT TYPE DOT ID LPAREN arguments_list_opt RPAREN','expression',8,'p_expression_static_dispatch','myparser.py',247),
  ('expression -> ID LPAREN arguments_list_opt RPAREN','expression',4,'p_expression_self_dispatch','myparser.py',254),
  ('expression -> expression PLUS expression','expression',3,'p_expression_math_operations','myparser.py',265),
  ('expression -> expression MINUS expression','expression',3,'p_expression_math_operations','myparser.py',266),
  ('expression -> expression MULTIPLY expression','expression',3,'p_expression_math_operations','myparser.py',267),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_math_operations','myparser.py',268),
  ('expression -> expression LT expression','expression',3,'p_expression_math_comparisons','myparser.py',283),
  ('expression -> expression LTEQ expression','expression',3,'p_expression_math_comparisons','myparser.py',284),
  ('expression -> expression EQ expression','expression',3,'p_expression_math_comparisons','myparser.py',285),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_with_parenthesis','myparser.py',297),
  ('expression -> IF expression THEN expression ELSE expression FI','expression',7,'p_expression_if_conditional','myparser.py',307),
  ('expression -> WHILE expression LOOP expression POOL','expression',5,'p_expression_while_loop','myparser.py',314),
  ('expression -> let_expression','expression',1,'p_expression_let','myparser.py',325),
  ('let_expression -> LET let_variables_list IN expression','let_expression',4,'p_expression_let_simple','myparser.py',331),
  ('let_variables_list -> let_variables_list COMMA let_variable','let_variables_list',3,'p_let_variables_list','myparser.py',338),
  ('let_variables_list -> let_variable','let_variables_list',1,'p_let_variables_list','myparser.py',339),
  ('let_variable -> ID COLON TYPE','let_variable',3,'p_let_variable','myparser.py',348),
  ('let_variable -> ID COLON TYPE ASSIGN expression','let_variable',5,'p_let_variable','myparser.py',349),
  ('expression -> CASE expression OF actions_list ESAC','expression',5,'p_expression_case','myparser.py',364),
  ('actions_list -> actions_list action','actions_list',2,'p_actions_list','myparser.py',371),
  ('actions_list -> action','actions_list',1,'p_actions_list','myparser.py',372),
  ('action -> ID COLON TYPE ARROW expression SEMICOLON','action',6,'p_action_expr','myparser.py',381),
  ('expression -> NEW TYPE','expression',2,'p_expression_new','myparser.py',392),
  ('expression -> ISVOID expression','expression',2,'p_expression_isvoid','myparser.py',399),
  ('expression -> INT_COMP expression','expression',2,'p_expression_integer_complement','myparser.py',406),
  ('expression -> NOT expression','expression',2,'p_expression_boolean_complement','myparser.py',413),
  ('empty -> <empty>','empty',0,'p_empty','myparser.py',424),
]