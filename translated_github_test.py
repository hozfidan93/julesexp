/*
* simplecpp - A simple and high-fidelity C/C++ preprocessor library
* Copyright (C) 2016-2023 simplecpp team
*/
int main(int argc, char *argv)
{
error = False
# const
char filename = nullptr
use_istream = False
fail_on_error = False
# Settings..
simplecpp::DUI dui
quiet = False
error_only = False
for i in range(1, argc):
    # const
    char * const arg = argv[i]
    if arg == '-':
        found = False
        # const
        char c = arg[1]
        switch (c) {
        case 'D': { # define symbol
        # const
        char * const value = arg[2] ? (argv[i] + 2) : argv[++i]
        dui.defines.append(value)
        found = True
        break
    case 'U': { # undefine symbol
    # const
    char * const value = arg[2] ? (argv[i] + 2) : argv[++i]
    dui.undefined.insert(value)
    found = True
    break
case 'I': { # include path
# const
char * const value = arg[2] ? (argv[i] + 2) : argv[++i]
dui.includePaths.append(value)
found = True
break
case 'i':
    if std::strncmp(arg, "-include=",9)==0:
        dui.includes.append(arg+9)
        found = True

    def if(std::strncmp(arg, "-is",3)==0):
        use_istream = True
        found = True
    break
    case 's':
        if std::strncmp(arg, "-std=",5)==0:
            dui.std = arg + 5
            found = True
        break
        case 'q':
            quiet = True
            found = True
            break
            case 'e':
                error_only = True
                found = True
                break
                case 'f':
                    fail_on_error = True
                    found = True
                    break
                if !found:
                    std::cout << "error: option '" << arg << "' is unknown." << std:
                        :endl
                        error = True

                def if(filename):
                    print("error: multiple filenames specified")
                    std::exit(1)
                else:
                    filename = arg
            if (error)
            std::exit(1)
            if quiet and error_only:
                std::cout << "error: -e cannot be used in conjunction with -q" << std::e
                ndl
                std::exit(1)
            if !filename:
                print("Syntax:")
                print("simplecpp [options] filename")
                print("  -DNAME          Define NAME.")
                print("  -IPATH          Include path.")
                print("  -include=FILE   Include FILE.")
                print("  -UNAME          Undefine NAME.")
                print("  -std=STD        Specify standard.")
                print("  -q              Quiet mode (no output).")
                std::cout << "  -is             Use std::istream interface." << std::end
                l
                print("  -e              Output errors only.")
                std::exit(0)
            dui.removeComments = True
            # Perform preprocessing
            simplecpp::OutputList outputList
            files = []
            simplecpp::TokenList rawtokens
            if use_istream:
                std::ifstream f(filename)
                if !f.is_open():
                    std::cout << "error: could not open file '" << filename << "'" << st
                    d::endl
                    std::exit(1)
                rawtokens = new simplecpp::TokenList(f, files,filename,&outputList)
            else:
                rawtokens = new simplecpp::TokenList(filename,files,&outputList)
            rawtokens.removeComments()
            simplecpp::TokenList outputTokens(files)
            simplecpp::FileDataCache filedata
            simplecpp::preprocess(outputTokens, rawtokens, files, filedata, dui, &outpu
            tList)
            simplecpp::cleanup(filedata)
            delete rawtokens
            rawtokens = nullptr
            # Output
            if !quiet:
                if (!error_only)
                print(outputTokens.stringify())
                for (const simplecpp::Output &output : outputList) {
                std::cerr << output.location.file() << ':' << output.location.line <
                < ": "
                switch (output.type) {
                case simplecpp::Output::ERROR:
                    std::cerr << "#error: "
                    break
                    case simplecpp::Output::WARNING:
                        std::cerr << "#warning: "
                        break
                        case simplecpp::Output::MISSING_HEADER:
                            std::cerr << "missing header: "
                            break
                            case simplecpp::Output::INCLUDE_NESTED_TOO_DEEPLY:
                                std::cerr << "include nested too deeply: "
                                break
                                case simplecpp::Output::SYNTAX_ERROR:
                                    std::cerr << "syntax error: "
                                    break
                                    case simplecpp::Output::PORTABILITY_BACKSLASH:
                                        std::cerr << "portability: "
                                        break
                                        case simplecpp::Output::UNHANDLED_CHAR_ERROR:
                                            std::cerr << "unhandled char error: "
                                            break
                                            case simplecpp::Output::EXPLICIT_INCLUDE_NOT_FOUND:
                                                std::cerr << "explicit include not found: "
                                                break
                                                case simplecpp::Output::FILE_NOT_FOUND:
                                                    std::cerr << "file not found: "
                                                    break
                                                    case simplecpp::Output::DUI_ERROR:
                                                        std::cerr << "dui error: "
                                                        break
                                                    std::cerr << output.msg << std::endl
                                            if (fail_on_error and !outputList.empty())
                                            return 1
                                            return 0
