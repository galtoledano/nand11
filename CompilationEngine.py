from Tokenizer import Tokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable


class CompilationEngine:
    KEYWORD_CONSTANT = ("true", "false", "null", "this")
    DEFAULT_CLASSES = ["Output", "Math", "String", "Memory", "Array", "Sys", "Screen", "Keyboard", "Main"]
    PRIMITIVE_LST = ["int", "boolean", "char", "void"]

    def __init__(self, input_stream, output_stream):
        """
        constructor of the Compilation Engine object
        :param input_stream: the input stream
        :param output_stream: the output stream
        """
        self.__tokenizer = Tokenizer(input_stream)  # Tokenizer object
        self.__output = VMWriter(output_stream)
        self.__symbol = SymbolTable()
        self.__class_name = ""
        self.__statements = {"let": self.compile_let, "if": self.compile_if, "while": self.compile_while,
                             "do": self.compile_do, "return": self.compile_return}
        self.__counter = 0
        self.__return_value = ""
        self.__num_of_fields = 0
        self.__in_array = 0
        self.compile_class()


    def compile_class(self):
        """
        compiling the program from the class definition
        """
        self.__tokenizer.advance()  # skip "class"
        self.__class_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()  # skip class name
        self.__tokenizer.advance()  # skip {
        current_token = self.__tokenizer.get_value()
        while current_token == "static" or current_token == "field":
            self.compile_class_var_dec()
            current_token = self.__tokenizer.get_value()
        while current_token == "constructor" or current_token == "function" or current_token == "method":
            self.compile_subroutine_dec()
            current_token = self.__tokenizer.get_value()
        self.__output.close()

    def compile_class_var_dec(self):
        """
        compiling the program from the class's declaration on vars
        """
        current_token = self.__tokenizer.get_value()
        while current_token == "static" or current_token == "field":
            self.__tokenizer.advance()  # get token type
            token_type = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # get token name
            token_name = self.__tokenizer.get_value()
            self.__symbol.define(token_name, token_type, current_token)
            self.__tokenizer.advance()
            if current_token == "field":
                self.__num_of_fields += 1
            while self.__tokenizer.get_value() == ",":
                self.__tokenizer.advance()  # get token name
                token_name = self.__tokenizer.get_value()
                self.__symbol.define(token_name, token_type, current_token)
                self.__tokenizer.advance()
                if current_token == "field":
                    self.__num_of_fields += 1
            self.__tokenizer.advance()
            current_token = self.__tokenizer.get_value()

    def compile_subroutine_body(self, func_name, is_ctor, is_method):
        """
        compiling the program's subroutine body
        """
        counter = 0
        self.__tokenizer.advance()  # skip {
        while self.__tokenizer.get_value() == "var":
            counter += self.compile_var_dec()
        self.__output.write_function(func_name, counter)
        if is_method:
            self.__output.write_push("argument", "0")
            self.__output.write_pop("pointer", "0")
        if is_ctor:
            self.__output.write_push("constant", str(self.__num_of_fields))
            self.__output.write_call("Memory.alloc", "1")
            self.__output.write_pop("pointer", "0")
        self.compile_statements()
        self.__tokenizer.advance()  # skip }

    def compile_subroutine_dec(self):
        """
        compiling the program's subroutine declaration
        """
        self.__symbol.start_subroutine()
        func_args = 0
        method_flag = False
        is_Ctor = False
        if self.__tokenizer.get_value() == "method":
            func_args = 1
            method_flag = True
        elif self.__tokenizer.get_value() == "constructor":
            is_Ctor = True
        self.__tokenizer.advance()  # skip constructor/function/method
        self.__return_value = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        func_name = self.__class_name + "." + self.__tokenizer.get_value()
        self.__tokenizer.advance()
        func_args += self.compile_parameter_list(method_flag)
        self.compile_subroutine_body(func_name, is_Ctor, method_flag)


    def compile_parameter_list(self, is_method):
        """
        compiling a parameter list
        """
        counter = 0
        self.__tokenizer.advance()  # skip (
        if is_method:
            self.__symbol.define("this", self.__class_name, "argument")  # todo  ?
            counter += 1
        if self.__tokenizer.get_value() != ")":
            var_type = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip type
            var_name = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip var name
            self.__symbol.define(var_name, var_type, "argument")
            counter += 1
            while self.__tokenizer.get_value() == ",":
                self.__tokenizer.advance()  # skip ,
                var_type = self.__tokenizer.get_value()
                self.__tokenizer.advance()  # skip type
                var_name = self.__tokenizer.get_value()
                self.__tokenizer.advance()  # skip varName
                self.__symbol.define(var_name, var_type, "argument")
                counter += 1
        self.__tokenizer.advance()
        return counter

    def compile_var_dec(self):
        """
        compiling function's var declaration
        """
        counter = 0
        token_kind = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        token_type = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        token_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        self.__symbol.define(token_name, token_type, token_kind)
        counter += 1
        while self.__tokenizer.get_value() == ",":
            self.__tokenizer.advance()  # skip ,
            token_name = self.__tokenizer.get_value()
            self.__symbol.define(token_name, token_type, token_kind)
            counter += 1
            self.__tokenizer.advance()
        self.__tokenizer.advance()  # skip ;
        return counter

    def compile_statements(self):
        """
        compiling statements
        """
        key = self.__tokenizer.get_value()
        if key != "}":
            while key in self.__statements:
                self.__statements[self.__tokenizer.get_value()]()
                key = self.__tokenizer.get_value()

    def compile_do(self):
        """
        compiling do call
        """
        self.__tokenizer.advance()  # skip do
        if self.__tokenizer.get_next_token() != ".":
            self.__output.write_push("pointer", "0")
        self.subroutine_call()

        self.__tokenizer.advance()  # skip ;
        self.__output.write_pop("temp", "0")

    def compile_let(self):
        """
        compiling let call
        """
        self.__tokenizer.advance()  # skip let
        var_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        if self.__tokenizer.get_value() == "[":
            self.__in_array += 1
            var_kind = self.__symbol.kind_of(var_name)
            var_index = self.__symbol.index_of(var_name)
            self.__tokenizer.advance()  # skip [
            self.compile_expression(True)
            self.__tokenizer.advance()  # skip =
            self.__output.write_push(var_kind, var_index)
            self.__output.write_arithmetic("+")
            self.compile_expression()
            self.__tokenizer.advance()  # skip ;
            self.__output.write_pop("temp", self.__symbol.get_temp())
            self.__output.write_pop("pointer", "1")
            self.__output.write_push("temp", self.__symbol.get_temp())
            self.__output.write_pop("that", "0")
            self.__symbol.set_temp()
        else:
            self.__tokenizer.advance()  # skip =
            self.compile_expression()
            self.__tokenizer.advance()  # skip ;
            var_kind = self.__symbol.kind_of(var_name)
            var_index = self.__symbol.index_of(var_name)
            self.__output.write_pop(var_kind, var_index)

    def close_array(self, is_let, cur_type):
        inner_array = self.__in_array != 0
        if is_let:
            if cur_type == "integerConstant" and inner_array:
                self.__output.write_arithmetic("+")
                self.__output.write_pop("pointer", "1")
                self.__output.write_push("that", "0")

            elif cur_type == "identifier":
                self.__output.write_pop("pointer", "1")
                self.__output.write_push("that", "0")
                self.__output.write_arithmetic("+")

        else:
            self.__output.write_arithmetic("+")
            self.__output.write_pop("pointer", "1")
            self.__output.write_push("that", "0")

    def compile_while(self):
        """
        compiling while loop call
        """
        label1 = "while" + str(self.__counter)
        label2 = "while_end" + str(self.__counter)
        self.__counter += 1
        self.__output.write_label(label1)
        self.__tokenizer.advance()  # skip while
        self.__tokenizer.advance()  # skip (
        self.compile_expression()
        self.__output.write_operation("not")
        self.__output.write_if(label2)
        self.__tokenizer.advance()  # skip )
        self.__tokenizer.advance()  # skip {
        self.compile_statements()
        self.__output.write_goto(label1)
        self.__tokenizer.advance()  # skip }
        self.__output.write_label(label2)

    def compile_return(self):
        """
        compiling return statement
        """
        self.__tokenizer.advance()  # skip return
        if self.__tokenizer.get_value() != ";":
            self.compile_expression()
        else:
            self.__output.write_push("constant", "0")
        self.__tokenizer.advance()  # skip ;
        self.__output.write_return()

    def compile_if(self):
        """
        compiling if condition
        """
        label1 = "IF_TRUE" + str(self.__counter)
        label2 = "IF_FALSE" + str(self.__counter)
        end = "end_if" + str(self.__counter)
        self.__counter += 1
        self.__tokenizer.advance()  # skip if
        self.__tokenizer.advance()  # skip (
        self.compile_expression()
        self.__output.write_if(label1)
        self.__output.write_goto(label2)
        self.__output.write_label(label1)
        self.__tokenizer.advance()  # skip )
        self.__tokenizer.advance()  # skip {
        self.compile_statements()
        self.__tokenizer.advance()  # skip }
        if self.__tokenizer.get_value() == "else":
            self.__output.write_goto(end)
            self.__output.write_label(label2)
            self.__tokenizer.advance()  # skip else
            self.__tokenizer.advance()  # skip {
            self.compile_statements()
            self.__tokenizer.advance()  # skip }
            self.__output.write_label(end)
        else:
            self.__output.write_label(label2)

    def compile_expression(self, is_let=False, name=None):
        """
        compiling expressions
        """
        curr_type = self.compile_term(is_let)
        if name and (self.__tokenizer.get_value() == "]" or self.__in_array % 2 == 0):
            self.__output.write_push(self.__symbol.kind_of(name), self.__symbol.index_of(name))
            self.close_array(is_let, curr_type)
        while self.__tokenizer.is_operator() and not is_let:
            operator = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip the operator
            self.compile_term()
            self.__output.write_arithmetic(operator)
            if name and self.__tokenizer.get_value() == "]":
                self.__output.write_push(self.__symbol.kind_of(name), self.__symbol.index_of(name))
                self.close_array(is_let, curr_type)

        self.__symbol.clear_temp()
        if self.__in_array != 0 and self.__tokenizer.get_value() == "]":
            self.__tokenizer.advance()
            self.__in_array -= 1

    def compile_term(self, is_let=False):
        """
        compiling any kind of terms
        """
        curr_type = self.__tokenizer.token_type()
        curr_value = self.__tokenizer.get_value()
        # handle constant numbers
        if curr_type == "integerConstant":
            self.__output.write_push("constant", str(self.__tokenizer.get_value()))
            self.__tokenizer.advance()  # skip
            if self.__tokenizer.get_value() == "]" and is_let:
                self.__in_array -= 1
                self.__tokenizer.advance()  # skip ]

        if curr_type == "stringConstant":
            the_string = self.__tokenizer.string_val()
            length = len(the_string)
            self.__output.write_push("constant", length)
            self.__output.write_call("String.new", "1")
            for i in range(length):
                self.__output.write_push("constant", ord(the_string[i]))
                self.__output.write_call("String.appendChar", "2")
            self.__tokenizer.advance()
            while self.__tokenizer.get_value() == "]":
                self.__in_array -= 1
                self.__tokenizer.advance()  # skip ]

        # handle const keyword
        elif curr_type == "keyword" and self.__tokenizer.get_value() in self.KEYWORD_CONSTANT:
            self.__tokenizer.set_type("keywordConstant")
            if self.__tokenizer.get_value() == "null" or self.__tokenizer.get_value() == "false":
                self.__output.write_push("constant", "0")
            elif self.__tokenizer.get_value() == "true":
                self.__output.write_push("constant", "0")
                self.__output.write_operation("not")
            else:
                self.__output.write_push("pointer", "0")
            self.__tokenizer.advance()

        elif curr_type == "identifier":
            # handle var names
            if self.__tokenizer.get_next_token() != "(" and self.__tokenizer.get_next_token() != ".":
                name = self.__tokenizer.get_value()
                self.__tokenizer.advance()  # skip var name
                if self.__tokenizer.get_value() == "[":
                    self.__in_array += 1
                    self.__tokenizer.advance()  # skip [
                    curr_type = self.__tokenizer.token_type()
                    self.compile_expression(is_let, name)
                else:
                    self.__output.write_push(self.__symbol.kind_of(name), self.__symbol.index_of(name))

            # handle function calls
            else:
                self.subroutine_call()

        # handle expression
        elif curr_type == "symbol" and self.__tokenizer.get_value() == "(":
            self.__tokenizer.advance()  # skip (
            self.compile_expression()
            self.__tokenizer.advance()  # skip )

        # handle -
        elif curr_value == "-":
            self.__tokenizer.advance()  # skip op
            self.compile_term()
            self.__output.write_operation("neg")
        # handle ~
        elif curr_value == "~":
            self.__tokenizer.advance()  # skip op
            self.compile_term()
            self.__output.write_arithmetic("~")
        return curr_type

    def subroutine_call(self):
        """
        compiling the program's subroutine call
        """
        var_type = self.__class_name
        var_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()  # skip var name
        num_args = 0
        if self.__tokenizer.get_value() == ".":
            if var_name in self.DEFAULT_CLASSES:
                var_type = var_name
            elif not self.__symbol.in_class(var_name):
                var_type = var_name
            else:
                var_type = self.__symbol.type_of(var_name)
                if var_type != self.__class_name:
                    self.__output.write_push(self.__symbol.kind_of(var_name), self.__symbol.index_of(var_name))
                    num_args += 1
            self.__tokenizer.advance()  # skip .
            func_name = var_type + "." + self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip name
        else:
            if var_type == self.__class_name or self.__symbol.in_class(var_name):
                num_args += 1
            func_name = var_type + "." + var_name
        self.__tokenizer.advance()  # skip (
        num_args += self.compile_expression_list()
        self.__tokenizer.advance()  # skip )
        self.__output.write_call(func_name, num_args)

    def compile_expression_list(self):
        """
        compiling expression list
        """
        counter = 0
        if self.__tokenizer.get_value() != ")":
            self.compile_expression()
            counter += 1
            while self.__tokenizer.get_value() == ",":
                self.__tokenizer.advance()  # skip ,
                self.compile_expression()
                counter += 1
        return counter

    def __is_obj(self, var_to_check):
        if self.__symbol.type_of(var_to_check) in self.PRIMITIVE_LST:
            return True
        return False
