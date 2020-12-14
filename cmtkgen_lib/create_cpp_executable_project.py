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

# create_project_main_file()
def create_project_main_file(project_source_file_path:str, project_name:str):
    with open(project_source_file_path, "w") as source_file:
        content = "#include <{pname}/{pname}.hpp> \n\
#include <iostream>\n\
#include <cstdlib>\n\
\n\
int main()\n\
{{\n\
    std::cout << module_name() << std::endl;\n\
    return EXIT_SUCCESS;\n\
}}\n".format(pname=project_name)
        source_file.write(content)
    pass

# executable_project_cmakelists_contents():
def executable_project_cmakelists_contents(project_cmakelists_path:str, project_name:str, project_version:str, \
                                           cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, \
                                           create_version_header:bool, cpp_version:str):
    contents = project_cmakelists_contents("CppExecutableProject", project_cmakelists_path, project_name, project_version, \
                                           cmake_major, cmake_minor, build_in_tree_allowed)
    create_version_header_code = "    VERSION_HEADER \"version.hpp\"\n" if create_version_header else ""
    return contents + "\
include(CTest)\n\
\n\
# Headers:\n\
set(headers\n\
    include/{pname}/{pname}.hpp\n\
)\n\
\n\
# Sources:\n\
set(sources\n\
    src/{pname}.cpp\n\
    src/main.cpp\n\
)\n\
\n\
# Add C++ library\n\
add_cpp_executable(${{PROJECT_NAME}}\n\
    CXX_STANDARD {cpp_version}\n\
    INCLUDE_DIRECTORIES include\n\
{create_version_header_code}\
    HEADERS ${{headers}}\n\
    SOURCES ${{sources}}\n\
    )\n\
\n\
install(TARGETS ${{PROJECT_NAME}} EXPORT ${{PROJECT_NAME}})\n\
\n\
#-----\n".format(pname=project_name, create_version_header_code=create_version_header_code, cpp_version=cpp_version)

# create_project_cmakelists()
def create_project_cmakelists(project_cmakelists_path:str, project_name:str, project_version:str, \
                              cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, \
                              create_version_header:bool, cpp_version:str):
    with open(project_cmakelists_path, "w") as project_cmakelists_file:
        content = executable_project_cmakelists_contents(project_cmakelists_path, project_name, project_version, \
                                                         cmake_major, cmake_minor, build_in_tree_allowed, create_version_header, \
                                                         cpp_version)
        project_cmakelists_file.write(content)

#--------------------------------------------------------------------------------

class Cmtk_executable_project_creator(Cmtk_shared_project_creator):
    def __init__(self, cmake_path:str):
        super().__init__(cmake_path)

    def project_include_dir(self):
        return "include/{proot}".format(proot=self._project_name)

    def _init_parameters(self, project_name:str):
        super()._init_parameters(project_name)
        # CMakeLists.txt
        self._cml_create_version_header = init_bool_parameter("Do you want a version header file?")
        pass

    def _create_dir_tree(self):
        super()._create_dir_tree()
        for subdir in [self.project_include_dir(), "src"]:
            self._create_subdir(subdir)

    def _create_files(self):
        # Write project header
        header_file_path = "{pname}/{include}/{pname}.hpp".format(include=self.project_include_dir(), pname=self._project_name)
        create_project_header_file(header_file_path)
        # Write project source
        project_source_file_path = "{pname}/src/{pname}.cpp".format(pname=self._project_name)
        create_project_source_file(project_source_file_path, self._project_name)
        project_main_file_path = "{pname}/src/main.cpp".format(pname=self._project_name)
        create_project_main_file(project_main_file_path, self._project_name)
        # Write project/CMakeLists.txt
        project_cmakelists_path = "{proot}/CMakeLists.txt".format(proot=self._project_name)
        create_project_cmakelists(project_cmakelists_path, self._project_name, self._project_version, \
                                  self._cmake.metadata().major_version(), self._cmake.metadata().minor_version(), \
                                  self._cml_build_in_tree_allowed, self._cml_create_version_header, \
                                  self._cml_cpp_version)
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
