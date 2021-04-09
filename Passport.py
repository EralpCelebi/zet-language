from LCI import Attribute, Static
import llvmlite.binding as llvm
import llvmlite.ir as ll

class Passport:
    def __init__(self) -> None:
        self.module: ll.Module = ll.Module("zet")
        self.module.triple = llvm.get_default_triple() 

        self.block : ll.Block = None
        self.builder: ll.IRBuilder = None

        self.variables = {}

        self.functions = {}
        self.methods = {}
        self.structs = {}


        self.flags = { "string" : 0 }

        self.modifiers = {
            "attribute" : Attribute(),
            "static": Static(),
        }

        self.sizes = {
            "i32" : 4,
            "i8"  : 1,
            "str" : 1,
            "void": 0,
        }

        self.types = {
            "i32" : ll.IntType(32),
            "i8"  : ll.IntType(8),
            "str" : ll.IntType(8).as_pointer(),
            "void": ll.VoidType()
        }
    
    def __call__(self):
        tmp = Passport()
        tmp.module = self.module
        
        tmp.functions = self.functions
        tmp.methods = self.methods
        tmp.structs = self.structs
        tmp.flags = self.flags

        tmp.types = self.types
        tmp.sizes = self.sizes
        
        tmp.variables = self.variables.copy()

        return tmp

class Data:
    def __init__(self, flags) -> None:
        self.flags = flags
    
    def set(self, flag, value):
        self.flags[flag] = value

    def get(self, flag):
        try:
            return self.flags[flag]
        except:
            return False


def Get(target, value):
    try:
        return target[value]
    except:
        return False

