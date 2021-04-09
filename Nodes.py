from llvmlite.binding import value
from Passport import Data, Get, Passport
import llvmlite.binding as llvm
import llvmlite.ir as ll

from copy import deepcopy

class Basket:
    def __init__(self, children) -> None:
        self.children = children
    
    def build(self, passport):
        for child in self.children:
            child.build(passport)

class Etch:
    def __init__(self, mod, value) -> None:
        self.mod = mod
        self.value = value
    
    def build(self, passport: Passport) -> None:
        passport.flags["modifiers"] = {}
        passport.flags["modparams"] = []

        self.mod.build(passport)
        self.value.build(passport)

        passport.flags["modifiers"] = {}
        passport.flags["modparams"] = []

class Modifier:
    def __init__(self, mod, parameters) -> None:
        self.mod = mod
        self.parameters = parameters
    
    def build(self, passport: Passport) -> None:        
        self.parameters.build(passport)
        passport.modifiers[self.mod](passport.flags["modparams"], passport)

class Modparam:
    def __init__(self, value) -> None:
        self.value = value
    
    def build(self, passport: Passport) -> None:
        passport.flags["modparams"].append(self.value)

class Struct:
    def __init__(self, name, fields) -> None:
        self.name = name
        self.fields = fields
    
    def build(self, passport: Passport) -> None:
        passport.flags["fields"] = []
        passport.flags["fieldllvm"] = []

        passport.flags["currently"] = 0
        passport.flags["size"] = 0

        self.fields.build(passport)

        lookup = {}

        for i,field in enumerate(passport.flags["fields"]):
            lookup[field.get("name")] = i

        tmp = ll.global_context.get_identified_type("struct."+self.name)
        tmp.set_body(*passport.flags["fieldllvm"])
        

        passport.structs[self.name] = Data({
            "type"  : "Struct",
            "name"  : self.name,
            "size"  : passport.flags["size"],
            "lookup": lookup,
            "fields": passport.flags["fields"],
            "fieldl": passport.flags["fieldllvm"],
            "llvm"  : tmp,         
        })

        passport.methods[self.name] = {}

        passport.types[self.name] = passport.structs[self.name].get("llvm")
        passport.sizes[self.name] = passport.flags["size"]

class Field:
    def __init__(self, combo) -> None:
        self.combo = combo
    
    def build(self, passport: Passport) -> Passport:
        self.combo.build(passport)

        passport.flags["size"] += passport.sizes[passport.flags["kind"]]

        passport.flags["fields"].append(
            Data({
                "type" : "Field",
                "name" : passport.flags["name"],
                "kind" : passport.flags["kind"],
                "llvm" : passport.flags["llvm"],
                "depth": passport.flags["depth"],
                "value"  : None
            })
        )

        passport.flags["fieldllvm"].append(passport.flags["llvm"])
        passport.flags["currently"] += 1

class Method:
    def __init__(self, name, kind, arguments, statements, target):
        self.name = name
        self.target = target
        self.kind = kind
        self.arguments = arguments
        self.statements = statements

    def build(self, passport: Passport) -> None:
        self.target.build(passport)

        target_kind = passport.flags["kind"]
        target_depth = passport.flags["depth"]
        target_llvm = passport.flags["llvm"]

        method_name = target_kind + "_" + self.name

        self.kind.build(passport)

        fn_kind = passport.flags["kind"]
        fn_llvm = passport.flags["llvm"]

        passport.flags["arguments"] = [Data({
            "type": "This",
            "name"  : "this",
            "kind"  : target_kind,
            "depth" : target_depth,
            "llvm"  : target_llvm,
            "value" : None
        })]

        self.arguments.build(passport)

        fntype = ll.FunctionType(
            fn_llvm,
            [x.flags["llvm"] for x in passport.flags["arguments"]],
            Get(passport.flags["modifiers"], "variable")
        )

        fn = ll.Function(
            passport.module,
            fntype,
            method_name
        )

        passport.methods[target_kind][self.name] = Data({
            "type" : "Method",
            "name" : method_name,
            "kind" : self.kind.kind,
            "llvm" : passport.flags["llvm"],
            "depth": passport.flags["depth"],
            "mods" : passport.flags["modifiers"],
            "args" : passport.flags["arguments"],
            "value": fn,
            "target": self.target,
        })

        for index, argument in enumerate(fn.args):
            passport.flags["arguments"][index].set("value", argument)
                
        visa = passport()
        visa.block = fn.append_basic_block(self.name)
        visa.builder = ll.IRBuilder(visa.block)

        for argument in visa.flags["arguments"]:
            visa.variables[argument.get("name")] = argument

        visa.flags["current"] = passport.methods[target_kind][self.name]
        self.statements.build(visa)

        if Get(visa.flags, "returned") != True:
            visa.builder.ret_void()

class MethodDeclaration:
    def __init__(self, name, kind, arguments, target) -> None:
        self.name = name
        self.kind = kind
        self.arguments = arguments
        self.target = target
    
    def build(self, passport: Passport):
        self.target.build(passport)

        target_kind = passport.flags["kind"]
        target_depth = passport.flags["depth"]
        target_llvm = passport.flags["llvm"]

        method_name = target_kind + "_" + self.name

        self.kind.build(passport)

        kind = passport.flags["llvm"]

        passport.flags["arguments"] = [Data({
            "type": "This",
            "name"  : "this",
            "kind"  : target_kind,
            "depth" : target_depth,
            "llvm"  : target_llvm,
            "value" : None
        })]

        self.arguments.build(passport)

        fntype = ll.FunctionType(
            kind,
            [x.flags["llvm"] for x in passport.flags["arguments"]],
            Get(passport.flags["modifiers"], "variable")
        )

        fn = ll.Function(
            passport.module,
            fntype,
            method_name
        )

        passport.methods[target_kind][self.name] = Data({
            "type" : "Method",
            "name" : method_name,
            "kind" : self.kind.kind,
            "llvm" : passport.flags["llvm"],
            "depth": passport.flags["depth"],
            "mods" : passport.flags["modifiers"],
            "args" : passport.flags["arguments"],
            "value": fn,
        })

class Function:
    def __init__(self, name, kind, arguments, statements) -> None:
        self.name = name
        self.kind = kind
        self.arguments = arguments
        self.statements = statements
    
    def build(self, passport: Passport):
        self.kind.build(passport)

        kind = passport.flags["llvm"]

        passport.flags["arguments"] = []
        self.arguments.build(passport)

        fntype = ll.FunctionType(
            kind,
            [x.flags["llvm"] for x in passport.flags["arguments"]],
            Get(passport.flags["modifiers"], "variable")
        )

        fn = ll.Function(
            passport.module,
            fntype,
            self.name
        )

        passport.functions[self.name] = Data({
            "type" : "Function",
            "name" : self.name,
            "kind" : self.kind.kind,
            "llvm" : passport.flags["llvm"],
            "depth": passport.flags["depth"],
            "mods" : passport.flags["modifiers"],
            "args" : passport.flags["arguments"],
            "value": fn,
        })

        for index, argument in enumerate(fn.args):
            passport.flags["arguments"][index].set("value", argument)
        
        visa = passport()
        visa.block = fn.append_basic_block(self.name)
        visa.builder = ll.IRBuilder(visa.block)

        for argument in visa.flags["arguments"]:
            visa.variables[argument.get("name")] = argument

        visa.flags["current"] = passport.functions[self.name]
        self.statements.build(visa)

        if Get(visa.flags, "returned") != True:
            visa.builder.ret_void()

class Declaration:
    def __init__(self, name, kind, arguments) -> None:
        self.name = name
        self.kind = kind
        self.arguments = arguments
    
    def build(self, passport: Passport):
        self.kind.build(passport)

        kind = passport.flags["llvm"]

        passport.flags["arguments"] = []
        self.arguments.build(passport)

        fntype = ll.FunctionType(
            kind,
            [x.flags["llvm"] for x in passport.flags["arguments"]],
            Get(passport.flags["modifiers"], "variable")
        )

        fn = ll.Function(
            passport.module,
            fntype,
            self.name
        )

        passport.functions[self.name] = Data({
            "type" : "Function",
            "name" : self.name,
            "kind" : self.kind.kind,
            "llvm" : passport.flags["llvm"],
            "depth": passport.flags["depth"],
            "mods" : passport.flags["modifiers"],
            "args" : passport.flags["arguments"],
            "value": fn,
        })

class Argument:
    def __init__(self, combo) -> None:
        self.combo = combo
    
    def build(self, passport: Passport):
        self.combo.build(passport)
        passport.flags["arguments"].append(
            Data({
                "type"  : "Argument",
                "name"  : passport.flags["name"],
                "kind"  : passport.flags["kind"],
                "depth" : passport.flags["depth"],
                "llvm"  : passport.flags["llvm"],
                "value" : None
            })
        )

class Hints:
    def __init__(self, combo) -> None:
        self.combo = combo
    
    def build(self, passport: Passport):
        self.combo.build(passport)
        passport.flags["arguments"].append(
            Data({
                "type"  : "Hint",
                "kind"  : passport.flags["kind"],
                "depth" : passport.flags["depth"],
                "llvm"  : passport.flags["llvm"],
                "value" : None
            })
        )

class Return:
    def __init__(self, value) -> None:
        self.value = value
    
    def build(self, passport: Passport) -> None:
        passport.flags["llvm"] = passport.flags["current"].get("llvm")
        passport.flags["returned"] = True

        self.value.build(passport)
        passport.builder.ret(passport.flags["value"])

class MethodCall:
    def __init__(self, source, name, parameters) -> None:
        self.source = source
        self.name = name
        self.parameters = parameters
    
    def build(self, passport: Passport) -> None:
        self.source.build(passport)

        target = passport.flags["target"].get("value").get("kind")
        target_value = passport.flags["target"].get("value").get("value")
        target_depth = passport.flags["target"].get("value").get("depth")

        this_depth = passport.methods[target][self.name].get("args")[0].get("depth")

        print(target_depth, this_depth)

        while target_depth != this_depth:
            target_depth -= 1
            target_value = passport.builder.load(target_value)            

        passport.flags["parameters"] = []
        passport.flags["arguments"] = []

        for argument in passport.methods[target][self.name].get("args"):
            passport.flags["arguments"].append(argument.get("llvm"))

        passport.flags["arguments"].reverse()

        passport.flags["parameters"].append(target_value)
        self.parameters.build(passport)

        passport.flags["value"] = passport.builder.call(
            passport.methods[target][self.name].get("value"),
            passport.flags["parameters"]
        )

class Call:
    def __init__(self, name, parameters) -> None:
        self.name = name
        self.parameters = parameters
    
    def build(self, passport: Passport) -> None:
        passport.flags["parameters"] = []
        passport.flags["arguments"] = []

        for argument in passport.functions[self.name].get("args"):
            passport.flags["arguments"].append(argument.get("llvm"))

        passport.flags["arguments"].reverse()
        
        self.parameters.build(passport)
        
        passport.flags["value"] = passport.builder.call(
            passport.functions[self.name].get("value"),
            passport.flags["parameters"]
        )

class Parameter:
    def __init__(self, value) -> None:
        self.value = value
    
    def build(self, passport: Passport) -> None:
        try:
            passport.flags["llvm"] = passport.flags["arguments"].pop()
        except:
            passport.flags["llvm"] = None

        self.value.build(passport)

        passport.flags["parameters"].append(passport.flags["value"])

class Cast:
    def __init__(self, value, target) -> None:
        self.value = value
        self.target = target

    def build(self, passport: Passport) -> None:
        self.value.build(passport)
        self.target.build(passport)


        passport.flags["value"] = passport.builder.bitcast(passport.flags["value"], passport.flags["llvm"])

class Shallow:
    def __init__(self, pointers, target) -> None:
        self.pointers = pointers
        self.target = target

    def build(self, passport: Passport) -> None:
        passport.flags["depth"] = 0

        self.pointers.build(passport)
        self.target.build(passport)

        target = passport.flags["target"]
        value = deepcopy(target.flags["value"])

        for i in range(passport.flags["depth"]):
            value.flags["depth"] -= 1
            value.flags["value"] = passport.builder.load(
                value.flags["value"]
            ) 

        target.flags["value"] = value
        passport.flags["target"] = target

class Ref:
    def __init__(self, value) -> None:
        self.value = value

    def build(self, passport: Passport) -> None:
        self.value.build(passport)
        
        tmp = passport.builder.alloca(passport.flags["value"].type)
        passport.builder.store(passport.flags["value"], tmp)
        passport.flags["value"] = tmp
        
class Deref:
    def __init__(self, value) -> None:
        self.value = value

    def build(self, passport: Passport) -> None:
        self.value.build(passport)
        passport.flags["value"] = passport.builder.load(passport.flags["value"])

class Address:
    def __init__(self, value) -> None:
        self.value = value

    def build(self, passport: Passport) -> None:
        self.value.build(passport)
        passport.flags["value"] = passport.builder.inttoptr(passport.flags["value"], passport.flags["llvm"].as_pointer())

class Load:
    def __init__(self, value) -> None:
        self.value = value
    
    def build(self, passport: Passport) -> None:
        self.value.build(passport)
        target = passport.flags["target"]

        if target.get("type") == "Variable":
            if target.get("sub") == "Allocate":
                passport.flags["value"] = passport.builder.load(
                    target.get("value").get("value")
                )
            elif target.get("sub") == "Field":
                passport.flags["value"] = target.get("value").get("value")

            elif target.get("sub") == "Argument" or target.get("sub") == "This":
                passport.flags["value"] = target.get("value").get("value")

class Store:
    def __init__(self, target, value) -> None:
        self.target = target
        self.value = value
    
    def build(self, passport: Passport) -> None:
        self.target.build(passport)

        target = passport.flags["target"]

        passport.flags["kind"] = target.get("value").get("kind")
        passport.flags["llvm"] = target.get("value").get("llvm")

        self.value.build(passport)

        passport.builder.store(
            passport.flags["value"],
            target.get("value").get("value")
        )

class Access:
    def __init__(self, source, member) -> None:
        self.source = source
        self.member = member
        self.is_target = False
    
    def build(self, passport: Passport) -> None:
        self.source.build(passport)

        struct = passport.flags["target"].get("value").get("kind")
        pointer= passport.flags["target"].get("value").get("value")
        depth  = passport.flags["target"].get("value").get("depth") 
        lookup = passport.structs[struct].get("lookup")
        fields = passport.structs[struct].get("fields")
        index  = lookup[self.member]
       
        while depth > 1:
                depth -=1
                pointer = passport.builder.load(pointer)
        

        field = fields[index]

        field.set("value", passport.builder.gep(
            pointer,
            [ll.IntType(32)(0), ll.IntType(32)(index)],
            inbounds=True
        ))

        passport.flags["target"] = Data({
            "type" : "Variable",
            "sub"  : "Field",
            "value": field
        })

class Variable:
    def __init__(self, value) -> None:
        self.value = value
    
    def build(self, passport: Passport) -> None:
        passport.flags["target"] = Data({
            "type": "Variable",
            "sub" : passport.variables[self.value].get("type"),
            "value" : passport.variables[self.value]
        })

class Allocate:
    def __init__(self, combo) -> None:
        self.combo = combo
    
    def build(self, passport: Passport) -> None:
        self.combo.build(passport)

        tmp = passport.builder.alloca(
            passport.flags["llvm"],
            name=passport.flags["name"]
        )

        passport.variables[passport.flags["name"]] = Data({
                "type"  : "Allocate",
                "name"  : passport.flags["name"],
                "kind"  : passport.flags["kind"],
                "depth" : passport.flags["depth"] + 1,
                "llvm"  : passport.flags["llvm"],
                "value" : tmp 
            })

class Number:
    def __init__(self, value) -> None:
        self.value = value
    
    def build(self, passport: Passport) -> None:
        try:
            while passport.flags["llvm"].is_pointer:
                passport.flags["llvm"] = passport.flags["llvm"].pointee
            
            passport.flags["value"] = passport.flags["llvm"](self.value)
        except:
            passport.flags["value"] = ll.IntType(32)(self.value)

class String:
    def __init__(self, value: str) -> None:
        self.value = value.strip("\"") + "\0"
        self.value = self.value.replace("\\n", "\n")

    def build(self, passport: Passport) -> None:
        string = ll.Constant(ll.ArrayType(ll.IntType(8), len(self.value)),
                        bytearray(self.value.encode("utf8")))

        passport.flags["string"] += 1

        globl = ll.GlobalVariable(passport.module, string.type, name="str-"+str(passport.flags["string"]))
        globl.linkage = "internal"
        globl.global_constant = True
        globl.initializer = string

        passport.flags["value"] = passport.builder.bitcast(globl, ll.IntType(8).as_pointer())

class Combo:
    def __init__(self, kind, name) -> None:
        self.kind = kind
        self.name = name
    
    def build(self, passport: Passport) -> None:
        passport.flags["name"] = self.name
        self.kind.build(passport)

class Kind:
    def __init__(self, kind, pointers) -> None:
        self.kind = kind
        self.pointers = pointers
    
    def build(self, passport: Passport) -> None:
        passport.flags["depth"] = 0
        passport.flags["kind"] = self.kind
        passport.flags["llvm"] = passport.types[self.kind]

        self.pointers.build(passport)

        for i in range(passport.flags["depth"]):
            passport.flags["llvm"] = passport.flags["llvm"].as_pointer()


class Pointer:
    def __init__(self) -> None:
        pass

    def build(self, passport) -> None:
        passport.flags["depth"] += 1
        