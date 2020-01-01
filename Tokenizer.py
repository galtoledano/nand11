class Tokenizer:
    keyWords = ("class", "constructor", "function", "method", "field", "static", "var", "int", "char",
                "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return")
    symbols = ("(", ")", "{", "}", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~")
    operators = ("+", "-", "*", "/", "&", "|", "<", ">", "=")

    def __init__(self, file):
        """
        constructor to tokenizer object
        :param file: the jack file to convert to tokens
        """
        self.__file = []
        self.__index = 0
        self.__current_token = None
        self.__current_token_type = None
        self.__read_file(file)
        self.advance()

    def remove_comments(self, line, is_comment):
        """
        removing comments from command line
        :param line: the command line
        :param is_comment: flag to know is we are at comment or not
        :return: the line with out the comments and the is comment flag
        """
        # remove comment
        line = line.strip()
        line = line.split("//")[0]

        # remove multi line comments
        start_index = line.find("/*")
        if start_index != -1:
            end_index = line.find("*/")
            if end_index == -1:
                return line[:start_index], True
            return line[:start_index] + line[end_index+2:], False
        if is_comment:
            end_index = line.find("*/")
            if end_index == -1:
                return "", True
            return line[end_index+2:], False
        return line, is_comment

    def __remove_invalid_syntax(self, line, is_comment):
        """
        removing comments and empty lines from the text file
        :param line: single line to process
        :param is_comment: flag that indicates if the line is at the middle of multi line comment or not
        :return: the processed line and the in multi line comment flag
        """
        # finding string indexing
        start_index = line.find('"')
        comment_index = line.find("//")
        difrent_comment_index = line.find("/*")
        if (comment_index != -1 and comment_index < start_index) \
                or (difrent_comment_index < start_index and difrent_comment_index != -1):
            return self.remove_comments(line, is_comment)
        if start_index != -1 and not is_comment:
            end_index = line.find('"', start_index + 1, len(line))
            before_string = line[:start_index]
            the_string = line[start_index:end_index+1]
            after_string = line[end_index+1:]
            before_string, is_comment = self.remove_comments(before_string, is_comment)
            after_string, is_comment = self.remove_comments(after_string, is_comment)
            return (before_string + the_string + after_string), is_comment
        else:
            return self.remove_comments(line, is_comment)

    def __read_file(self, original_file):
        """
        reading the text file and convert it to array
        :param original_file: the program's test file to read
        """
        file = open(original_file, 'r')
        line = file.readline()
        is_comment = False
        while line:
            current_line, is_comment = self.__remove_invalid_syntax(line, is_comment)
            if current_line != "":
                # add spaces between symbols
                for char in current_line:
                    if char in self.symbols:
                        current_line = current_line.replace(char, " " + char + " ")
                self.__file += current_line.split()
            line = file.readline()
        file.close()
        self.find_string()

    def find_string(self):
        """
        finding a string object and marge it to one object
        """
        final_file = []
        is_word = False
        temp = ""
        for i in range(len(self.__file)):
            if is_word:
                temp += self.__file[i] + " "
                if self.__file[i].endswith('"'):
                    is_word = False
                    final_file.append(temp)
            else:
                if self.__file[i].startswith('"'):
                    if self.__file[i].endswith('"') and len(self.__file[i]) > 1:
                        final_file.append(self.__file[i])
                    else:
                        is_word = True
                        temp = self.__file[i] + " "
                else:
                    final_file.append(self.__file[i])
        self.__file = final_file

    def get_value(self):
        """
        :return: the current token's value
        """
        return self.__current_token

    def has_more_tokens(self):
        """
        :return: return True if there is  more tokens to process left, false otherwise
        """
        return self.__index != len(self.__file)

    def advance(self):
        """
        advance to the next token at the program
        """
        if self.has_more_tokens():
            self.__current_token = self.__file[self.__index]
            self.__current_token_type = self.token_type()
            self.__index += 1

    def token_type(self):
        """
        :return: the current token's type
        """
        # returns the token's type.
        temp_token = self.__current_token.strip()
        if temp_token in self.keyWords:
            return "keyword"
        elif temp_token in self.symbols:
            return "symbol"
        elif temp_token.isdigit():
            return "integerConstant"
        elif temp_token.startswith('"') and temp_token.endswith('"'):
            return "stringConstant"
        else:
            return "identifier"

    def get_next_token(self):
        """
        getter to the next token
        :return: the next token's value
        """
        return self.__file[self.__index]

    def set_type(self, new_type):
        """
        set the token's type
        :param new_type: a new type to set
        """
        self.__current_token_type = new_type

    def keyword(self):
        """
        :return: the keybord value
        """
        return str(self.__current_token)

    def symbol(self):
        """
        :return: the symbol's char
        """
        return chr(self.__current_token)

    def identifier(self):
        """
        :return: the identifier
        """
        return str(self.__current_token)

    def int_val(self):
        """
        :return: the int value
        """
        return int(self.__current_token)

    def string_val(self):
        """
        :return: a string value
        """
        temp_token = self.__current_token.strip()
        return str(temp_token[1:-1])

    def is_operator(self):
        """
        checks if the current token is operator or not
        :return: true is it is a operator, flase is not
        """
        return self.__current_token in self.operators
