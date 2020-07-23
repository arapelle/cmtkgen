#!/usr/bin/python3

from cpp_project import *
import shutil
import argparse
import subprocess
import re
import os
import json

# python current dir
python_current_dir = os.path.dirname(os.path.realpath(__file__))

#--------------------------------------------------------------------------------

# create_test_cmakelists()
def create_test_cmakelists(test_cmakelists_path:str):
    with open(test_cmakelists_path, "w") as test_cmakelists_file:
        content = "\nadd_public_cpp_library_tests(${PROJECT_NAME})\n"
        test_cmakelists_file.write(content)

# create_example_cmakelists()
def create_example_cmakelists(example_cmakelists_path:str):
    with open(example_cmakelists_path, "w") as example_cmakelists_file:
        content = "\nadd_public_cpp_library_examples(${PROJECT_NAME})\n"
        example_cmakelists_file.write(content)

# library_project_cmakelists_contents():
def library_project_cmakelists_contents(project_cmakelists_path:str, project_name:str, project_version:str, \
                                        cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, \
                                        create_version_header:bool, cmake_project_config_type:str,
                                        cpp_version:str):
    contents = project_cmakelists_contents(project_cmakelists_path, project_name, project_version, \
                                           cmake_major, cmake_minor, build_in_tree_allowed)
    create_version_header_code = "    VERSION_HEADER \"version.hpp\"\n" if create_version_header else ""
    return contents + "\
include(CTest)\n\
\n\
add_public_cpp_library(\n\
{create_version_header_code}\
    {cmake_project_config_type}_PACKAGE_CONFIG_FILE\n\
    CXX_STANDARD {cpp_version}\
)\n\
\n\
#-----\n".format(create_version_header_code=create_version_header_code, cmake_project_config_type=cmake_project_config_type, \
                 cpp_version=cpp_version)

# create_project_cmakelists()
def create_project_cmakelists(project_cmakelists_path:str, project_name:str, project_version:str, \
                              cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, \
                              create_version_header:bool, cmake_project_config_type:str,
                              cpp_version:str):
    with open(project_cmakelists_path, "w") as project_cmakelists_file:
        content = library_project_cmakelists_contents(project_cmakelists_path, project_name, project_version, \
                                                      cmake_major, cmake_minor, build_in_tree_allowed, create_version_header, \
                                                      cmake_project_config_type, cpp_version)
        project_cmakelists_file.write(content)

#--------------------------------------------------------------------------------

class Cmtk_library_project_creator(Cmtk_shared_project_creator):
    def __init__(self, cmake_path:str):
        super().__init__(cmake_path)

    def project_include_dir(self):
        return "include/{proot}".format(proot=self._project_name)

    def _init_parameters(self, project_name:str):
        super()._init_parameters(project_name)
        # CMakeLists.txt
        self._cml_create_version_header = init_bool_parameter("Do you want a version header file?")
        default_cmake_project_config_type = "VERBOSE"
        self._cml_cmake_project_config_type = init_parameter("Project config type (BASIC | VERBOSE)", default_cmake_project_config_type, \
                                                             lambda type: type in ["BASIC", "VERBOSE"])
        pass

    def _create_dir_tree(self):
        super()._create_dir_tree()
        for subdir in [self.project_include_dir(), "src", "test", "example"]:
            self._create_subdir(subdir)

    def _create_files(self):
        # Write project header
        header_file_path = "{pname}/{include}/{pname}.hpp".format(include=self.project_include_dir(), pname=self._project_name)
        create_project_header_file(header_file_path)
        # Write project source
        project_source_file_path = "{pname}/src/{pname}.cpp".format(pname=self._project_name)
        create_project_source_file(project_source_file_path, self._project_name)
        # Write project/CMakeLists.txt
        project_cmakelists_path = "{proot}/CMakeLists.txt".format(proot=self._project_name)
        create_project_cmakelists(project_cmakelists_path, self._project_name, self._project_version, \
                                  self._cmake.metadata().major_version(), self._cmake.metadata().minor_version(), \
                                  self._cml_build_in_tree_allowed, self._cml_create_version_header, \
                                  self._cml_cmake_project_config_type, self._cml_cpp_version)
        # Write project/test/CMakeLists.txt
        test_cmakelists_path = "{proot}/{test}/CMakeLists.txt".format(proot=self._project_name, test="test")
        create_test_cmakelists(test_cmakelists_path)
        # Write project/example/CMakeLists.txt
        example_cmakelists_path = "{proot}/{example}/CMakeLists.txt".format(proot=self._project_name, example="example")
        create_example_cmakelists(example_cmakelists_path)
        pass

#-----------
# Parse args
#-----------
argparser = argparse.ArgumentParser()
argparser.add_argument('project_name', nargs='?', type=str, help='Project name')
argparser.add_argument('--cmake', metavar='cmake-path', type=str, default="cmake", help='Path or alias to CMake')
pargs = argparser.parse_args()

cmtkgen = Cmtk_library_project_creator(pargs.cmake)
cmtkgen.cmake().check_version()
cmtkgen.create_project(pargs.project_name)

print("EXIT SUCCESS")
