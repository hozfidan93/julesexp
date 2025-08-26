import re
import sys

class CppToPythonTranslator:
    """
    A class to translate C++ code to Python code.
    This is a simplified translator and works for a subset of C++.
    """

    def __init__(self, cpp_code):
        self.cpp_code = cpp_code
        self.python_code = ""
        self.used_math = False

    def _translate_erase_remove_if(self, match):
        vector_name = match.group(1)
        arg_name = match.group(2)
        condition = match.group(3)
        return f"{vector_name} = [{arg_name} for {arg_name} in {vector_name} if not ({condition})]"

    def _map_type_to_default(self, cpp_type):
        if cpp_type == 'int':
            return '0'
        if cpp_type == 'float' or cpp_type == 'double':
            return '0.0'
        if cpp_type == 'string':
            return '""'
        if cpp_type == 'bool':
            return 'False'
        return 'None'

    def _translate_pointer_alloc(self, match):
        cpp_type = match.group(1)
        var_name = match.group(2)
        size = match.group(3)
        default_value = self._map_type_to_default(cpp_type)
        return f"{var_name} = [{default_value}] * {size}"

    def _remove_arg_types(self, match):
        args = match.group(3)
        # Remove types from arguments, e.g., "int n, string s" -> "n, s"
        processed_args = re.sub(r'\b(int|double|float|string|bool)\s+', '', args)
        return f"def {match.group(2)}({processed_args}):"

    def translate(self):
        code = self.cpp_code
        code = re.sub(r'}\s*else', '}\nelse', code)
        lines = code.split('\n')

        # Pre-process for const
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('const '):
                new_lines.append('# const')
                new_lines.append(stripped_line.replace('const ', '', 1))
            else:
                new_lines.append(line)
        lines = new_lines

        processed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Comments
            line = re.sub(r'//(.*)', r'#\1', line)
            if '/*' in line or '*/' in line:
                # Basic multi-line comment handling, not perfect
                line = re.sub(r'/\*.*?\*/', '"""', line)

            # Includes and using namespace
            if '#include' in line or 'using namespace' in line:
                continue

            # main
            line = re.sub(r'int main\s*\(.*\)\s*{', 'def main():', line)

            # Functions
            line = re.sub(r'(\w+)\s+(\w+)\s*\((.*?)\)\s*{', self._remove_arg_types, line)

            # Control Structures
            line = re.sub(r'(\w+)\.erase\(std::remove_if\(\1\.begin\(\), \1\.end\(\), \[\]\(.*?\s+(\w+)\)\{\s*return\s+(.*?);\s*\}\), \1\.end\(\)\);', self._translate_erase_remove_if, line)
            line = re.sub(r'for\s*\(\s*int\s+([a-zA-Z_]\w*)\s*=\s*(\d+);\s*\1\s*<\s*(.*?);\s*(?:\1\+\+|\+\+\1)\s*\)\s*{', r'for \1 in range(\2, \3):', line)
            line = re.sub(r'while\s*\((.*?)\)\s*{', r'while \1:', line)
            line = re.sub(r'if\s*\((.*?)\)\s*{', r'if \1:', line)
            line = re.sub(r'else if\s*\((.*?)\)\s*{', r'elif \1:', line)
            line = re.sub(r'else\s*{', 'else:', line)

            # IO
            line = re.sub(r'std::cout\s*<<\s*(.*?)\s*<<\s*std::endl\s*;', r'print(\1)', line)
            line = re.sub(r'std::cout\s*<<\s*(.*?)\s*;', r'print(\1)', line)

            # Type declarations
            line = re.sub(r'(\w+)\s*\*\s*(\w+)\s*=\s*new\s+\w+\[(.*)\]', self._translate_pointer_alloc, line)
            line = re.sub(r'delete\[\]\s*\w+;', '', line)
            line = re.sub(r'std::vector<.*?>\s+(\w+);', r'\1 = []', line)
            line = re.sub(r'std::pair<.*?>\s+(\w+);', r'\1 = (None, None)', line)
            line = re.sub(r'\b(int|double|float|string|bool)\s+([a-zA-Z_]\w*)\s*=', r'\2 =', line)
            line = re.sub(r'\b(int|double|float|string|bool)\s+([a-zA-Z_]\w*);', r'\2 = None', line)

            # Math functions
            math_map = {
                'expf': 'math.exp',
                'fmaxf': 'math.fmax',
                'fminf': 'math.fmin',
                'sqrtf': 'math.sqrt',
            }
            for cpp_func, py_func in math_map.items():
                if cpp_func in line:
                    line = re.sub(r'\b' + cpp_func + r'\b', py_func, line)
                    self.used_math = True

            # Operators
            line = re.sub(r'\.push_back\((.*?)\)', r'.append(\1)', line)
            line = re.sub(r'(\w+)\.size\(\)', r'len(\1)', line)
            line = re.sub(r'std::make_pair\((.*?)\)', r'(\1)', line)
            line = re.sub(r'\.first', '[0]', line)
            line = re.sub(r'\.second', '[1]', line)
            line = re.sub(r'->', '.', line)
            line = re.sub(r'std::min\((.*?)\)', r'min(\1)', line)
            line = re.sub(r'std::max\((.*?)\)', r'max(\1)', line)
            line = re.sub(r'&&', 'and', line)
            line = re.sub(r'\|\|', 'or', line)
            line = re.sub(r'true', 'True', line)
            line = re.sub(r'false', 'False', line)

            # Semicolons
            line = re.sub(r';', '', line)

            processed_lines.append(line)

        # Indentation
        indented_code = []
        indent_level = 0
        for line in processed_lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped == '}':
                indent_level = max(0, indent_level - 1)
                continue

            if stripped.endswith('}'):
                indent_level = max(0, indent_level - 1)
                stripped = stripped[:-1].strip()

            if stripped:
                if stripped.startswith('def ') and indented_code:
                    indented_code.append('')
                indented_code.append('    ' * indent_level + stripped)

            if stripped.endswith(':'):
                indent_level += 1

        final_code = '\n'.join(indented_code)

        # Add main guard
        if 'def main():' in final_code:
            final_code += '\n\nif __name__ == "__main__":\n    main()'

        if self.used_math:
            final_code = 'import math\n\n' + final_code

        self.python_code = final_code.strip()
        return self.python_code

def run_tests():
    """
    Runs a series of test cases to verify the translator's functionality.
    """
    test_cases = [
        {
            "name": "Hello World",
            "cpp": """\
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
""",
            "python": """\
def main():
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "Erase-remove_if idiom",
            "cpp": """\
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> my_vector;
    my_vector.push_back(1);
    my_vector.push_back(2);
    my_vector.push_back(3);
    my_vector.push_back(4);
    my_vector.erase(std::remove_if(my_vector.begin(), my_vector.end(), [](int i){ return i % 2 == 0; }), my_vector.end());
    for (int i = 0; i < my_vector.size(); ++i) {
        std::cout << my_vector[i] << std::endl;
    }
    return 0;
}
""",
            "python": """\
def main():
    my_vector = []
    my_vector.append(1)
    my_vector.append(2)
    my_vector.append(3)
    my_vector.append(4)
    my_vector = [i for i in my_vector if not (i % 2 == 0)]
    for i in range(0, len(my_vector)):
        print(my_vector[i])
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "Pointer as array",
            "cpp": """\
#include <iostream>

int main() {
    int* my_array = new int[10];
    my_array[0] = 5;
    std::cout << my_array[0] << std::endl;
    delete[] my_array;
    return 0;
}
""",
            "python": """\
def main():
    my_array = [0] * 10
    my_array[0] = 5
    print(my_array[0])
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "std::vector",
            "cpp": """\
#include <iostream>
#include <vector>

int main() {
    std::vector<int> my_vector;
    my_vector.push_back(10);
    my_vector.push_back(20);
    std::cout << my_vector[0] << std::endl;
    std::cout << my_vector.size() << std::endl;
    return 0;
}
""",
            "python": """\
def main():
    my_vector = []
    my_vector.append(10)
    my_vector.append(20)
    print(my_vector[0])
    print(len(my_vector))
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "std::pair",
            "cpp": """\
#include <iostream>
#include <utility>

int main() {
    std::pair<int, int> my_pair;
    my_pair = std::make_pair(10, 20);
    std::cout << my_pair.first << std::endl;
    std::cout << my_pair.second << std::endl;
    return 0;
}
""",
            "python": """\
def main():
    my_pair = (None, None)
    my_pair = (10, 20)
    print(my_pair[0])
    print(my_pair[1])
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "Arrow operator",
            "cpp": """\
int main() {
    my_object->do_something();
    return 0;
}
""",
            "python": """\
def main():
    my_object.do_something()
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "Math functions",
            "cpp": """\
#include <iostream>
#include <cmath>

int main() {
    double x = 2.0;
    std::cout << expf(x) << std::endl;
    return 0;
}
""",
            "python": """\
import math

def main():
    x = 2.0
    print(math.exp(x))
    return 0

if __name__ == "__main__":
    main()
"""
        },
        # More test cases will be added here.
        {
            "name": "If-Else statement",
            "cpp": """\
#include <iostream>

int main() {
    int x = 10;
    if (x > 5) {
        std::cout << "x is greater than 5" << std::endl;
    } else {
        std::cout << "x is not greater than 5" << std::endl;
    }
    return 0;
}
""",
            "python": """\
def main():
    x = 10
    if x > 5:
        print("x is greater than 5")
    else:
        print("x is not greater than 5")
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "For loop",
            "cpp": """\
#include <iostream>

int main() {
    for (int i = 0; i < 5; ++i) {
        std::cout << i << std::endl;
    }
    return 0;
}
""",
            "python": """\
def main():
    for i in range(0, 5):
        print(i)
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "While loop",
            "cpp": """\
#include <iostream>

int main() {
    int i = 0;
    while (i < 5) {
        std::cout << i << std::endl;
        i = i + 1;
    }
    return 0;
}
""",
            "python": """\
def main():
    i = 0
    while i < 5:
        print(i)
        i = i + 1
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "Factorial Function",
            "cpp": """\
#include <iostream>

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    std::cout << factorial(5) << std::endl;
    return 0;
}
""",
            "python": """\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    print(factorial(5))
    return 0

if __name__ == "__main__":
    main()
"""
        },
        {
            "name": "Min/Max and Const",
            "cpp": """\
#include <iostream>
#include <algorithm>

int main() {
    const int a = 10;
    int b = 20;
    std::cout << std::min(a, b) << std::endl;
    std::cout << std::max(a, b) << std::endl;
    return 0;
}
""",
            "python": """\
def main():
    # const
    a = 10
    b = 20
    print(min(a, b))
    print(max(a, b))
    return 0

if __name__ == "__main__":
    main()
"""
        }
    ]

    print("Running translator tests...")
    all_passed = True
    for i, test_case in enumerate(test_cases):
        print(f"--- Test Case {i+1}: {test_case['name']} ---")
        translator = CppToPythonTranslator(test_case["cpp"])
        actual_python = translator.translate()
        expected_python = test_case["python"]

        print("C++ Input:")
        print(test_case["cpp"])
        print("\\nExpected Python Output:")
        print(expected_python)
        print("\\nActual Python Output:")
        print(actual_python)

        if actual_python.strip() == expected_python.strip():
            print("\\nResult: PASSED")
        else:
            print("\\nResult: FAILED")
            all_passed = False
        print("--------------------------------" + "-" * len(test_case['name']))

    print("\\n--- Test Summary ---")
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed.")
    print("--------------------")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_tests()
    else:
        # This part will be for translating a file if needed, but for now, we'll just run tests.
        print("Running tests by default.")
        run_tests()
