#!/usr/bin/python3

from cmtkgen_lib.cpp_project import *
import shutil
import argparse
import subprocess
import re
import os
import json

# python current dir    
python_current_dir = os.path.dirname(os.path.realpath(__file__))

#--------------------------------------------------------------------------------

# create_project_header_main_file()
def create_project_header_main_file(header_file_path:str):
    with open(header_file_path, "w") as header_file:
        content = "#pragma once\n"
        header_file.write(content)
    pass

# create_project_source_main_file()
def create_project_source_main_file(project_source_file_path:str):
    with open(project_source_file_path, "w") as source_file:
        content = "#include \"main.hpp\"\n\
#include <iostream>\n\
\n\
int main(int argc, char** argv)\n\
{\n\
    std::cout << \"EXIT SUCCESS\" << std::endl;\n\
    return EXIT_SUCCESS;\n\
}\n\n"
        source_file.write(content)
    pass

# hello_world_project_cmakelists_contents():
def hello_world_project_cmakelists_contents(project_cmakelists_path:str, project_name:str, project_version, \
                                           cmake_major:str, cmake_minor:str, build_in_tree_allowed, cpp_version:str):
    contents = project_cmakelists_contents("Project", project_cmakelists_path, project_name, project_version, \
                                           cmake_major, cmake_minor, build_in_tree_allowed)
    return contents + "add_executable(${{PROJECT_NAME}} main.cpp main.hpp)\n\
target_compile_features(${{PROJECT_NAME}} PUBLIC cxx_std_{cpp_version})\n\
#-----\n".format(cpp_version=cpp_version)

# create_project_cmakelists()
def create_project_cmakelists(project_cmakelists_path:str, project_name:str, project_version, \
                              cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, cpp_version:str):
    with open(project_cmakelists_path, "w") as project_cmakelists_file:
        content = hello_world_project_cmakelists_contents(project_cmakelists_path, project_name, project_version, \
                                                          cmake_major, cmake_minor, build_in_tree_allowed, cpp_version)
        project_cmakelists_file.write(content)

#--------------------------------------------------------------------------------

class Cmtk_executable_project_creator(Cmtk_project_creator):
    def __init__(self, cmake_path:str):
        super().__init__(cmake_path)
        self._project_version = False
        self._cml_build_in_tree_allowed = True

    def _create_files(self):
        # Write project header/source files
        project_header_main_file_path = "{pname}/main.hpp".format(pname=self._project_name)
        create_project_header_main_file(project_header_main_file_path)
        project_source_main_file_path = "{pname}/main.cpp".format(pname=self._project_name)
        create_project_source_main_file(project_source_main_file_path)
        # Write project/CMakeLists.txt
        project_cmakelists_path = "{proot}/CMakeLists.txt".format(proot=self._project_name)
        create_project_cmakelists(project_cmakelists_path, self._project_name, self._project_version, \
                                  self._cmake.metadata().major_version(), self._cmake.metadata().minor_version(), \
                                  self._cml_build_in_tree_allowed, self._cml_cpp_version)
        super()._create_files()
        pass

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('project_name', nargs='?', type=str, help='Project name')
    argparser.add_argument('--cmake', metavar='cmake-path', type=str, default="cmake", help='Path or alias to CMake')
    pargs = argparser.parse_args()

    cmtkgen = Cmtk_executable_project_creator(pargs.cmake)
    cmtkgen.cmake().check_version()
    cmtkgen.create_project(pargs.project_name)

    print("EXIT SUCCESS")
