from Nodes import Access, Address, Allocate, Argument, Basket, Call, Cast, Combo, Declaration, Deref, Etch, Field, Function, Hints, Kind, Load, Method, MethodCall, MethodDeclaration, Modifier, Modparam, Number, Parameter, Pointer, Ref, Return, Shallow, Store, String, Struct, Variable
from rply import ParserGenerator

class Grammer:
    def __init__(self) -> None:
        self.pg = ParserGenerator(
            ["IDENTIFIER", "NUMBER", "STRING",
            "FN", "STRUCT", "RETURN", "TO",
            ";", ".", ",", "(", ")", "[", "]", "{", "}", "->", "=", "*", "&", "@"]
        )
    
    def Build(self):
        @self.pg.production("root : definitions")
        def root(p):
            return p[0]
        
        @self.pg.production("definitions : definitions definition")
        @self.pg.production("definitions : definition")
        def definitions(p):
            return Basket(p)

        @self.pg.production("definition : etch")
        def definition(p):
            return p[0]
        
        @self.pg.production("etch : modifier method")
        def function(p):
            return Etch(p[0], p[1])

        @self.pg.production("etch : method")
        def function(p):
            return Etch(Basket([]), p[0])
        
        @self.pg.production("etch : modifier function")
        def function(p):
            return Etch(p[0], p[1])

        @self.pg.production("etch : function")
        def function(p):
            return Etch(Basket([]), p[0])
        
        @self.pg.production("etch : modifier struct")
        def function(p):
            return Etch(p[0], p[1])

        @self.pg.production("etch : struct")
        def function(p):
            return Etch(Basket([]), p[0])
        
        @self.pg.production("struct : STRUCT IDENTIFIER { fields }")
        def struct(p):
            return Struct(p[1].getstr(), p[3])
            
        @self.pg.production("struct : STRUCT IDENTIFIER { }")
        def struct(p):
            return Struct(p[1].getstr(), Basket([]))

        @self.pg.production("fields : fields fields")
        def fields(p):
            return Basket(p)

        @self.pg.production("fields : field ;")
        def fields(p):
            return p[0]

        @self.pg.production("field : combo")
        def field(p):
            return Field(p[0])

        @self.pg.production("function : FN IDENTIFIER ( arguments ) -> kind { statements }")
        def function(p):
            return Function(p[1].getstr(), p[6], p[3], p[8])

        @self.pg.production("function : FN IDENTIFIER ( ) -> kind { statements }")
        def function(p):
            return Function(p[1].getstr(), p[5], Basket([]), p[7])

        @self.pg.production("function : FN IDENTIFIER ( arguments ) -> kind {  }")
        def function(p):
            return Function(p[1].getstr(), p[6], p[3], Basket([]))

        @self.pg.production("function : FN IDENTIFIER ( ) -> kind { }")
        def function(p):
            return Function(p[1].getstr(), p[5], Basket([]), Basket([]))
        
        @self.pg.production("function : FN IDENTIFIER ( hints ) -> kind ;")
        def function(p):
            return Declaration(p[1].getstr(), p[6], p[3])

        @self.pg.production("function : FN IDENTIFIER ( ) -> kind ;")
        def function(p):
            return Declaration(p[1].getstr(), p[5], Basket([]))

        # ==========================0
        @self.pg.production("method : FN ( kind ) IDENTIFIER ( arguments ) -> kind { statements }")
        def function(p):
            return Method(p[4].getstr(), p[9], p[6], p[11], p[2])

        @self.pg.production("method : FN ( kind ) IDENTIFIER ( ) -> kind { statements }")
        def function(p):
            return Method(p[4].getstr(), p[8], Basket([]), p[10], p[2])

        @self.pg.production("method : FN ( kind ) IDENTIFIER ( arguments ) -> kind {  }")
        def function(p):
            return Method(p[4].getstr(), p[9], p[6], Basket([]), p[2])

        @self.pg.production("method : FN ( kind ) IDENTIFIER ( ) -> kind { }")
        def function(p):
            return Method(p[4].getstr(), p[8], Basket([]), Basket([]), p[2])

        @self.pg.production("method : FN ( kind ) IDENTIFIER ( hints ) -> kind ;")
        def function(p):
            return MethodDeclaration(p[4].getstr(), p[9], p[6], p[2])

        @self.pg.production("method : FN ( kind ) IDENTIFIER ( ) -> kind ;")
        def function(p):
            return MethodDeclaration(p[4].getstr(), p[8], Basket([]), p[2])

        # ==========================0

        @self.pg.production("modifier : [ IDENTIFIER ( modparams ) ]")
        def modifier(p):
            return Modifier(p[1].getstr(), p[3])

        @self.pg.production("modifier : [ IDENTIFIER ( ) ]")
        def modifier(p):
            return Modifier(p[1].getstr(), Basket([]))

        @self.pg.production("modparams : modparams , modparams")
        def modparams(p):
            return Basket([p[0], p[2]])

        @self.pg.production("modparams : IDENTIFIER")
        def modparams(p):
            return Modparam(p[0].getstr())

        @self.pg.production("arguments : arguments , arguments")
        def arguments(p):
            return Basket([p[0],p[2]])

        @self.pg.production("arguments : combo")
        def arguments(p):
            return Argument(p[0])

        @self.pg.production("hints : hints , hints")
        def arguments(p):
            return Basket([p[0], p[2]])

        @self.pg.production("hints : kind")
        def arguments(p):
            return Hints(p[0])

        @self.pg.production("statements : statements statement")
        @self.pg.production("statements : statement")
        def statements(p):
            return Basket(p)
        
        @self.pg.production("statement : call ;")
        @self.pg.production("statement : method_call ;")
        @self.pg.production("statement : return ;")
        @self.pg.production("statement : store ;")
        @self.pg.production("statement : allocate ;")
        def statement(p):
            return p[0]

        @self.pg.production("expression : ( expression )")
        def expression(p):
            return p[1]

        @self.pg.production("expression : call")
        @self.pg.production("expression : method_call")
        @self.pg.production("expression : load")
        @self.pg.production("expression : number")
        @self.pg.production("expression : string")
        @self.pg.production("expression : ref")
        @self.pg.production("expression : deref")
        @self.pg.production("expression : addr")
        @self.pg.production("expression : cast")
        def expression(p):
            return p[0]

        @self.pg.production("source : ( source )")
        def source(p):
            return p[1]
        
        @self.pg.production("target : ( target )")
        def target(p):
            return p[1]

        @self.pg.production("cast : expression TO kind")
        def cast(p):
            return Cast(p[0], p[2])

        @self.pg.production("ref : & expression")
        def ref(p):
            return Ref(p[1])
            
        @self.pg.production("deref : * expression")
        def deref(p):
            return Deref(p[1])

        @self.pg.production("addr : @ expression")
        def addr(p):
            return Address(p[1])

        @self.pg.production("return : RETURN expression")
        def ret(p):
            return Return(p[1])

        @self.pg.production("method_call : source . IDENTIFIER ( parameters )")
        @self.pg.production("method_call : target . IDENTIFIER ( parameters )")
        def mcall(p):
            return MethodCall(p[0], p[2].getstr(), p[4])

        @self.pg.production("method_call : source . IDENTIFIER ( )")
        @self.pg.production("method_call : target . IDENTIFIER ( )")
        def mcall(p):
            return MethodCall(p[0], p[2].getstr(), Basket([]))

        @self.pg.production("call : IDENTIFIER ( parameters )")
        def call(p):
            return Call(p[0].getstr(), p[2])

        @self.pg.production("call : IDENTIFIER ( )")
        def call(p):
            return Call(p[0].getstr(), Basket([]))
        
        @self.pg.production("parameters : parameters , parameters")
        def parameters(p):
            return Basket([p[0], p[2]])
        
        @self.pg.production("parameters : parameter")
        def parameters(p):
            return p[0]

        @self.pg.production("parameter : expression")
        def parameter(p):
            return Parameter(p[0])

        @self.pg.production("store : target = expression")
        def store(p):
            return Store(p[0], p[2])

        @self.pg.production("load : source")
        def load(p):
            return Load(p[0])
        
        @self.pg.production("source : access")
        @self.pg.production("source : variable")
        def target(p):
            return p[0]

        @self.pg.production("target : allocate")
        def target(p):
            return Basket([p[0], Variable(p[0].combo.name)])

        @self.pg.production("target : access")
        def target(p):
            p[0].is_target = True
            return p[0]
        
        @self.pg.production("target : shallow")
        @self.pg.production("target : variable")
        def target(p):
            return p[0]
        
        @self.pg.production("shallow : pointer variable")
        def shallow(p):
            return Shallow(p[0], p[1])

        @self.pg.production("access : source . IDENTIFIER")
        def access(p):
            return Access(p[0], p[2].getstr())

        @self.pg.production("variable : IDENTIFIER")
        def variable(p):
            return Variable(p[0].getstr())

        @self.pg.production("allocate : combo")
        def allocate(p):
            return Allocate(p[0])

        @self.pg.production("string : STRING")
        def string(p):
            return String(p[0].getstr())

        @self.pg.production("number : NUMBER")
        def number(p):
            return Number(int(p[0].getstr()))

        @self.pg.production("combo : kind IDENTIFIER")
        def combo(p):
            return Combo(p[0], p[1].getstr())
        
        @self.pg.production("kind : IDENTIFIER pointer")
        def kind(p):
            return Kind(p[0].getstr(), p[1])
        
        @self.pg.production("kind : IDENTIFIER")
        def kind(p):
            return Kind(p[0].getstr(), Basket([]))
        
        @self.pg.production("pointer : pointer pointer")
        def pointer(p):
            return Basket(p)

        @self.pg.production("pointer : *")
        def pointer(p):
            return Pointer()

        return self.pg.build()