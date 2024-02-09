import sys
import myparser
import cool_ast as AST 
#import parser.parser as psr
import check_semantic as chk
import cil_to_mips as mips
import cool_to_cil as cilv

def main():
    code = ''
    path = ''
    for file in sys.argv[1:]:
        try:
            if not file.endswith('.cl'):
                print('Error: File extension must be .cl.')
                return
            tcode = open(file,'r').read()
            code += tcode
            path = file
        except:
            print('Error: File not found or cannot be accessed.')
            return
    #cp = myparser.CoolParser()
    p = myparser.CoolParser()
    print('Executing Lexical and Syntactic Analysis....')
    a = p.parse(code)
    if not a:
        print('Parsing error exception!!')
        return
    print('Done!!.')
    print('Starting Semantic Analysis....')
    seman = chk.Semantic_Analizer()
    cool_ast = seman.check_sematic(a)
    print(cool_ast)
    if not cool_ast:
        for err in seman.errors:
            print(err)
        return
    print('Done!!.')
    print('Translating to CIL')
    cil1 = cilv.COOL_To_CIL()
    cil_ast = cil1.visit(cool_ast)
   
    print('Done!!.')
    print('Translating to MIPS...')
    mips_instructions =  mips.MipsWriter(cil1.inherit_graph, path[:len(path)-3]+'.asm')
    mips_instructions.visit(cil_ast)
    print('Done!!.')
main()