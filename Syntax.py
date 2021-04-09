from rply import LexerGenerator

class Syntax:
    def __init__(self) -> None:
        self.lg = LexerGenerator()
    
    def Build(self):

        self.lg.add(";",";")
        self.lg.add(".","\.")
        self.lg.add(",",",")
        self.lg.add("(","\(")
        self.lg.add(")","\)")
        self.lg.add("{","\{")
        self.lg.add("}","\}")
        self.lg.add("[","\[")
        self.lg.add("]","\]")

        self.lg.add("=","\=")

        self.lg.add("->","\-\>")
        self.lg.add("*", "\*")

        self.lg.add("STRING", '["]([^"\\\n]|\\.|\\\n)*["]')

        self.lg.add("&","\&")
        self.lg.add("*","\*")
        self.lg.add("@","\@")

        self.lg.add("NUMBER","[-]*[0-9]+")

        self.lg.add("STRUCT","struct ")

        self.lg.add("FN","fn ")
        self.lg.add("RETURN","return ")

        self.lg.add("TO","to ")

        self.lg.add("IDENTIFIER","[_\w][_\w0-9]*")

        

        self.lg.ignore("\s+")
        
        return self.lg.build()