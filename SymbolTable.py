class SymbolTable:
    def __init__(self):
        self.__class_scoop = {}  # static / field
        self.__subroutine_scoop = {}  # arg / var
        self.__counters = {"static": 0, "field": 0, "argument": 0, "var": 0, "temp": 0}

    def start_subroutine(self):
        # delete all names at the privies subroutine scoop
        self.__subroutine_scoop = {}
        self.__counters["argument"] = 0
        self.__counters["var"] = 0
        self.__counters["temp"] = 0

    def define(self, name, this_type, kind):
        index = self.__counters[kind]
        self.__counters[kind] += 1
        if kind == "static" or kind == "field":
            self.__class_scoop[name] = [kind, this_type, index]
        else:
            self.__subroutine_scoop[name] = [kind, this_type, index]

    def var_count(self, kind):
        # returns int
        return self.__counters[kind]  # todo kind in uppercase ?

    def kind_of(self, name):
        # return kind
        if name in self.__subroutine_scoop.keys():
            if self.__subroutine_scoop[name][0] == "var":
                return "local"
            return self.__subroutine_scoop[name][0]
        elif name in self.__class_scoop.keys():
            if self.__class_scoop[name][0] == "field":
                return "this"
            return self.__class_scoop[name][0]
        return "NONE"  # todo not a string ?

    def type_of(self, name):
        if name in self.__subroutine_scoop.keys():
            return self.__subroutine_scoop[name][1]
        elif name in self.__class_scoop.keys():
            return self.__class_scoop[name][1]
        return "NONE"  # todo not a string ?

    def index_of(self, name):
        if name in self.__subroutine_scoop.keys():
            return self.__subroutine_scoop[name][2]
        elif name in self.__class_scoop.keys():
            return self.__class_scoop[name][2]
        return "NONE"  # todo not a string ?

    def in_class(self, name):
        return name in self.__subroutine_scoop or name in self.__class_scoop

    def get_temp(self):
        return self.__counters["temp"]

    def set_temp(self):
        self.__counters["temp"] += 1