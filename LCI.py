
class Attribute:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def __call__(arguments, passport) -> None:
        if arguments[0] == "variable":
            passport.flags["modifiers"]["variable"] = True
        
        if arguments[0] == "packed":
            passport.flags["modifiers"]["packed"] = True

class Static:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def __call__(arguments, passport) -> None:
        if arguments[0] == "static":
            passport.flags["modifiers"]["static"] = True
        