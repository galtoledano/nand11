class VMWriter:
    OPERATORS = {"+": "add\n", "-": "sub\n", "*": "call Math.multiply 2\n", "/": "call Math.divide 2\n",
                 "&": "and\n", "|": "or\n", "<": "lt\n", ">": "gt\n", "=": "eq\n", "~": "not\n"}

    def __init__(self, output_path):
        self.__out = open(output_path, "w")

    def write_push(self, segment, index):
        print("push {0} {1}\n".format(segment, index))
        self.__out.write("push {0} {1}\n".format(segment, index))

    def write_pop(self, segment, index):
        print("pop {0} {1}\n".format(segment, index))
        self.__out.write("pop {0} {1}\n".format(segment, index))

    def write_arithmetic(self, command):
        print(self.OPERATORS[command])
        self.__out.write(self.OPERATORS[command])

    def write_label(self, label):
        print("label {0}\n".format(label))
        self.__out.write("label {0}\n".format(label))

    def write_goto(self, label):
        print("goto {0}\n".format(label))
        self.__out.write("goto {0}\n".format(label))

    def write_if(self, label):
        print("if-goto {0}\n".format(label))
        self.__out.write("if-goto {0}\n".format(label))

    def write_call(self, name, num_of_args):
        print("call {0} {1}\n".format(name, num_of_args))
        self.__out.write("call {0} {1}\n".format(name, num_of_args))

    def write_function(self, name, num_of_locals):
        print("function {0} {1}\n".format(name, num_of_locals))
        self.__out.write("function {0} {1}\n".format(name, num_of_locals))

    def write_return(self):
        print("return\n")
        self.__out.write("return\n")

    def write_operation(self, exp):
        print(exp + "\n")
        self.__out.write(exp + "\n")

    def close(self):
        self.__out.close()
