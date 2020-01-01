import os
import sys
from CompilationEngine import CompilationEngine


def main():
    """
    the main function, opens the input jack file and convert it to new xml file
    """
    if len(sys.argv) != 2:
        print('Usage: ', sys.argv[0], '<input file or directory>')
    path = sys.argv[1]
    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".jack"):
                output_name = path + os.path.sep + file
                output_name = output_name.replace(".jack", ".xml")
                CompilationEngine(path + os.path.sep + file, output_name)
    else:
        output_name = path.replace(".jack", ".xml")
        CompilationEngine(path, output_name)


if __name__ == '__main__':
    main()
