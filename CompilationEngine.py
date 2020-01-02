from Tokenizer import Tokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable


class CompilationEngine:
    XML_LINE = "<{0}> {1} </{0}>\n"
    COMPARE_SYM_REPLACER = {'<': "&lt;", '>': "&gt;", '"': "&quot;", '&': "&amp;"}
    KEYWORD_CONSTANT = ("true", "false", "null", "this")
    DEFAULT_CLASSES = ["Output", "Math", "String", "Memory", "Array", "Sys", "Screen", "Keyboard", "Main"]

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
        self.compile_class()

        # self.__output.close()

    def write_xml(self):
        """
        writing xml line
        """
        if self.__tokenizer.token_type() == "stringConstant":
            self.__output.write(self.XML_LINE.format(self.__tokenizer.token_type(), self.__tokenizer.string_val()))
        elif self.__tokenizer.get_value() in self.COMPARE_SYM_REPLACER:
            xml_val = self.COMPARE_SYM_REPLACER[self.__tokenizer.get_value()]
            self.__output.write(self.XML_LINE.format(self.__tokenizer.token_type(), xml_val))
        else:
            self.__output.write(self.XML_LINE.format(self.__tokenizer.token_type(), self.__tokenizer.get_value()))

    def compile_class(self):
        """
        compiling the program from the class definition
        """
        # self.__output.write("<class>\n")
        # self.write_xml()
        self.__tokenizer.advance()  # skip "class"
        self.__class_name = self.__tokenizer.get_value()
        # self.write_xml()
        self.__tokenizer.advance()  # skip class name
        # self.write_xml()
        self.__tokenizer.advance()  # skip {
        current_token = self.__tokenizer.get_value()
        while current_token == "static" or current_token == "field":
            self.compile_class_var_dec()
            current_token = self.__tokenizer.get_value()
        while current_token == "constructor" or current_token == "function" or current_token == "method":
            self.compile_subroutine_dec()
            current_token = self.__tokenizer.get_value()
        # self.write_xml()
        # self.__output.write("</class>\n")
        self.__output.close()

    def compile_class_var_dec(self):
        """
        compiling the program from the class's declaration on vars
        """
        current_token = self.__tokenizer.get_value()
        while current_token == "static" or current_token == "field":
            # self.__output.write("<classVarDec>\n")
            # self.write_xml()
            index = self.__symbol.var_count(current_token)
            self.__tokenizer.advance() # get token type
            token_type = self.__tokenizer.get_value()
            # self.__output.write_push(current_token, index)
            self.__tokenizer.advance()  # get token name
            token_name = self.__tokenizer.get_value()
            self.__symbol.define(token_name, token_type, current_token)
            self.__tokenizer.advance()
            if current_token == "field":
                self.__num_of_fields += 1
            # self.write_xml()
            # self.__tokenizer.advance()
            # self.write_xml()
            # self.__tokenizer.advance()
            while self.__tokenizer.get_value() == ",":
                # self.write_xml()  # write ,
                self.__tokenizer.advance() # get token name
                token_name = self.__tokenizer.get_value()
                index = self.__symbol.var_count(current_token) # get new index
                self.__output.write_push(current_token, index)
                self.__symbol.define(token_name, token_type, current_token)
                self.__tokenizer.advance()
                if current_token == "field":
                    self.__num_of_fields += 1
                # self.write_xml()  # write value
                # self.__tokenizer.advance()
            # self.write_xml()
            self.__tokenizer.advance()
            current_token = self.__tokenizer.get_value()
            # self.__output.write("</classVarDec>\n")

    def compile_subroutine_body(self, func_name, is_ctor):
        """
        compiling the program's subroutine body
        """
        # self.__output.write("<subroutineBody>\n")
        # self.write_xml()  # write {
        counter = 0
        self.__tokenizer.advance()  # skip {
        while self.__tokenizer.get_value() == "var":
            counter += self.compile_var_dec()
        self.__output.write_function(func_name, counter)
        if is_ctor:
            self.__output.write_push("constant", str(self.__num_of_fields))
            self.__output.write_call("Memory.alloc", "1")
            self.__output.write_pop("pointer", "0")
        self.compile_statements()
        # self.write_xml()  # write }
        self.__tokenizer.advance()  # skip }
        # self.__output.write("</subroutineBody>\n")

    def compile_subroutine_dec(self):
        """
        compiling the program's subroutine declaration
        """
        # self.__output.write("<subroutineDec>\n")
        # self.write_xml()  # write constructor/function/method
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
        # self.__output.write_function(func_name, func_args)
        self.compile_subroutine_body(func_name, is_Ctor)

        # self.__output.write("</subroutineDec>\n")

    def compile_parameter_list(self, is_method):
        """
        compiling a parameter list
        """
        # self.write_xml()  # write (
        counter = 0
        self.__tokenizer.advance()  # skip (
        # self.__output.write("<parameterList>\n")
        if is_method:
            self.__symbol.define("this", self.__class_name, "argument")
        if self.__tokenizer.get_value() != ")":
            # self.write_xml()  # write type
            var_type = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip type
            # self.write_xml()  # write varName
            var_name = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip var name
            self.__symbol.define(var_name, var_type, "argument")
            counter += 1
            while self.__tokenizer.get_value() == ",":
                # self.write_xml()  # write ,
                self.__tokenizer.advance()  # skip ,
                # self.write_xml()  # type
                var_type = self.__tokenizer.get_value()
                self.__tokenizer.advance()  # skip type
                # self.write_xml()  # varName
                var_name = self.__tokenizer.get_value()
                self.__tokenizer.advance()  # skip varName
                self.__symbol.define(var_name, var_type, "argument")
                counter += 1
        # self.__output.write("</parameterList>\n")
        # self.write_xml()  # write )
        self.__tokenizer.advance()
        return counter

    def compile_var_dec(self):
        """
        compiling function's var declaration
        """
        # self.__output.write("<varDec>\n")
        # self.write_xml()  # write var
        counter = 0
        token_kind = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        # self.write_xml()  # write type
        token_type = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        # self.write_xml()  # write varName
        token_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        index = self.__symbol.var_count(token_kind)
        # self.__output.write_push(token_kind, index)
        self.__symbol.define(token_name, token_type, token_kind)
        counter += 1
        while self.__tokenizer.get_value() == ",":
            # self.write_xml()  # write ,
            self.__tokenizer.advance()  # skip ,
            # self.write_xml()
            token_name = self.__tokenizer.get_value()
            index = self.__symbol.var_count(token_kind)
            # self.__output.write_push(token_kind, index)
            self.__symbol.define(token_name, token_type, token_kind)
            self.__tokenizer.advance()
            counter += 1
        # self.write_xml()  # write ;
        self.__tokenizer.advance()  # skip ;
        # self.__output.write("</varDec>\n")
        return counter

    def compile_statements(self):
        """
        compiling statements
        """
        key = self.__tokenizer.get_value()
        # self.__output.write("<statements>\n")
        if key != "}":
            while key in self.__statements:
                self.__statements[self.__tokenizer.get_value()]()
                key = self.__tokenizer.get_value()
        # self.__output.write("</statements>\n")

    def compile_do(self):
        """
        compiling do call
        """
        # self.__output.write("<doStatement>\n")
        # self.write_xml()  # write do
        self.__tokenizer.advance()  # skip do
        self.subroutine_call()
        # self.write_xml()  # write ;
        self.__tokenizer.advance()  # skip ;
        self.__output.write_pop("temp", "0")
        # self.__output.write("</doStatement>\n")

    def compile_let(self):
        """
        compiling let call
        """
        # self.__output.write("<letStatement>\n")
        # self.write_xml()  # write let
        self.__tokenizer.advance()  # skip let
        # self.write_xml()  # write varName
        var_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()
        # if self.__tokenizer.get_value() == "[":  # todo handle array
        #     self.write_xml()  # write [
        #     self.__tokenizer.advance()
        #     self.compile_expression()
        #     self.write_xml()  # write ]
        #     self.__tokenizer.advance()
        # self.write_xml()  # write =
        self.__tokenizer.advance()  # skip =
        self.compile_expression()  # todo push the value to the stack
        # self.write_xml()  # write ;
        self.__tokenizer.advance()  # skip ;
        # self.__output.write("</letStatement>\n")
        var_kind = self.__symbol.kind_of(var_name)
        var_index = self.__symbol.index_of(var_name)
        self.__output.write_pop(var_kind, var_index)

    def compile_while(self):
        """
        compiling while loop call
        """
        label1 = "while" + str(self.__counter)
        label2 = "while_end" + str(self.__counter)
        self.__counter += 1
        self.__output.write_label(label1)
        # self.__output.write("<whileStatement>\n")
        # self.write_xml()  # write while
        self.__tokenizer.advance()  # skip while
        # self.write_xml()  # write (
        self.__tokenizer.advance()  # skip (
        self.compile_expression()
        self.__output.write_operation("not")
        self.__output.write_if(label2)
        self.__tokenizer.advance()  # skip )
        # self.write_xml()  # write {
        self.__tokenizer.advance()  # skip {
        self.compile_statements()
        self.__output.write_goto(label1)
        self.__tokenizer.advance()  # skip }
        self.__output.write_label(label2)
        # self.__output.write("</whileStatement>\n")

    def compile_return(self):
        """
        compiling return statement
        """
        # self.__output.write("<returnStatement>\n")
        # self.write_xml()  # write return
        self.__tokenizer.advance()  # skip return
        if self.__tokenizer.get_value() != ";":
            self.compile_expression()
        else:
            self.__output.write_push("constant", "0")
        # self.write_xml()  # write ;
        self.__tokenizer.advance()  # skip ;
        # self.__output.write("</returnStatement>\n")
        self.__output.write_return()

    def compile_if(self):
        """
        compiling if condition
        """
        label1 = "if_true" + str(self.__counter)
        label2 = "if_false" + str(self.__counter)
        end = "end_if" + str(self.__counter)
        self.__counter += 1
        # self.__output.write("<ifStatement>\n")
        # self.write_xml()  # write if
        self.__tokenizer.advance()  # skip if
        # self.write_xml()  # write (
        self.__tokenizer.advance()  # skip (
        self.compile_expression()
        # self.__output.write_operation("not")
        self.__output.write_if(label1)
        self.__output.write_goto(label2)
        self.__output.write_label(label1)
        # self.write_xml()  # write )
        self.__tokenizer.advance()  # skip )
        # self.write_xml()  # write {
        self.__tokenizer.advance()  # skip {
        self.compile_statements()
        self.__output.write_goto(end)
        self.__output.write_label(label2)
        # self.__output.write_goto(label2)
        # self.write_xml()  # write }
        self.__tokenizer.advance()  # skip }
        if self.__tokenizer.get_value() == "else":
            # self.write_xml()  # write else
            self.__tokenizer.advance()  # skip else
            # self.write_xml()  # write {
            self.__tokenizer.advance()  # skip {
            self.compile_statements()
            # self.write_xml()  # write }
            self.__tokenizer.advance()  # skip }
        self.__output.write_label(end)
        # self.__output.write("</ifStatement>\n")

    def compile_expression(self):
        """
        compiling expressions
        """
        # self.__output.write("<expression>\n")
        self.compile_term()
        while self.__tokenizer.is_operator():
            # self.write_xml()  # write the operator
            operator = self.__tokenizer.get_value()
            self.__tokenizer.advance()  # skip the operator
            self.compile_term()
            self.__output.write_arithmetic(operator)
        # self.__output.write("</expression>\n")

    def compile_term(self):
        """
        compiling any kind of terms
        """
        # self.__output.write("<term>\n")
        # dealing with unknown token
        curr_type = self.__tokenizer.token_type()
        # handle constant numbers
        if curr_type == "integerConstant":
            # self.write_xml()  # write the int \ string
            self.__output.write_push("constant", str(self.__tokenizer.get_value()))
            self.__tokenizer.advance()  # skip

        if curr_type == "stringConstant":  # todo
            pass

        # handle const keyword
        elif curr_type == "keyword" and self.__tokenizer.get_value() in self.KEYWORD_CONSTANT:
            self.__tokenizer.set_type("keywordConstant")
            if self.__tokenizer.get_value() == "null" or self.__tokenizer.get_value() == "false":
                self.__output.write_push("constant", "0")
            elif self.__tokenizer.get_value() == "true":
                self.__output.write_push("constant", "0")
                self.__output.write_operation("not")
            # self.write_xml()  # write key word
            else:
                self.__output.write_push("argument", "0")
            self.__tokenizer.advance()

        elif curr_type == "identifier":
            # handle var names
            if self.__tokenizer.get_next_token() != "(" and self.__tokenizer.get_next_token() != ".":
                # self.write_xml()  # write the var name
                name = self.__tokenizer.get_value()
                self.__output.write_push(self.__symbol.kind_of(name), self.__symbol.index_of(name))
                self.__tokenizer.advance() # skip var name
                if self.__tokenizer.get_value() == "[": # todo: deal with array
                    pass
                    # self.write_xml()  # write [
                    # self.__tokenizer.advance()
                    # self.compile_expression()
                    # self.write_xml()  # write ]
                    # self.__tokenizer.advance()
            # handle function calls
            else:
                self.subroutine_call()
        # handle expression
        elif curr_type == "symbol" and self.__tokenizer.get_value() == "(":
            # self.write_xml()  # write (
            self.__tokenizer.advance() # skip (
            self.compile_expression()
            # self.write_xml()  # write )
            self.__tokenizer.advance()  # skip )

        # handle -
        elif self.__tokenizer.get_value() == "-":
            self.__tokenizer.advance()  # skip op
            self.compile_term()
            self.__output.write_operation("neg")
        # handle ~
        elif self.__tokenizer.get_value() == "~":
            self.__tokenizer.advance()  # skip op
            self.compile_term()
            self.__output.write_arithmetic("~")
        # self.__output.write("</term>\n")

    def subroutine_call(self):
        """
        compiling the program's subroutine call
        """
        var_type = self.__class_name
        var_name = self.__tokenizer.get_value()
        self.__tokenizer.advance()  # skip var name
        if self.__tokenizer.get_value() == ".":
            # self.write_xml()  # write name
            if var_name in self.DEFAULT_CLASSES:
                var_type = var_name
            elif self.__tokenizer.get_next_token() == "new":
                var_type = var_name
            else:
                var_type = self.__symbol.type_of(var_name)
                if var_type != self.__class_name:
                    self.__output.write_push(self.__symbol.kind_of(var_name), self.__symbol.index_of(var_name))
            # ind = self.__symbol.index_of(var_name)
            # self.__output.write_pop(var_kind, ind)
            # # self.write_xml()  # write .
            self.__tokenizer.advance()  # skip .
        # self.write_xml()  # write name
        func_name = var_type + "." + self.__tokenizer.get_value()
        self.__tokenizer.advance()  # skip name
        # self.write_xml()  # write (
        self.__tokenizer.advance()  # skip (
        num_args = self.compile_expression_list()
        # self.write_xml()  # write )
        self.__tokenizer.advance()  # skip )
        self.__output.write_call(func_name, num_args)

    def compile_expression_list(self):
        """
        compiling expression list
        """
        # self.__output.write("<expressionList>\n")
        counter = 0
        if self.__tokenizer.get_value() != ")":
            self.compile_expression()
            counter += 1
            while self.__tokenizer.get_value() == ",":
                # self.write_xml()  # write ,
                self.__tokenizer.advance()  # skip ,
                self.compile_expression()
                counter += 1
        # self.__output.write("</expressionList>\n")
        return counter


