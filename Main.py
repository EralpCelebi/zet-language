from os import system
from os.path import splitext

from colorama import init, Fore, Back, Style
from llvmlite.ir import module

from Passport import Passport
from Grammer import Grammer
from Syntax import Syntax

from sys import argv

import llvmlite.binding as llvm
import llvmlite.ir as ll

syntax = Syntax().Build()
grammer= Grammer().Build()

llvm.initialize()
llvm.initialize_all_targets()
llvm.initialize_native_asmprinter()

init()

data = ""

with open(argv[1], "r") as f:
    data = f.read()
    
out = grammer.parse(syntax.lex(data))

passport = Passport()

out.build(passport)

print(Fore.RED + Style.BRIGHT + "==================== IR ====================" + Fore.RESET)

print(passport.module)

with open(splitext(argv[1])[0]+".ll", "w") as f:
    f.write(str(passport.module))

system("llc --filetype asm " + splitext(argv[1])[0]+".ll")

with open(splitext(argv[1])[0]+".s", "r") as f:
    data = f.read()

print(Fore.RED + Style.BRIGHT + "=================== ASM ====================" + Fore.RESET)
#print(data)

system("clang " + splitext(argv[1])[0]+".s")