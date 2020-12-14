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

# create_test_cmakelists()
def create_test_cmakelists(project_name:str, test_cmakelists_path:str):
    with open(test_cmakelists_path, "w") as test_cmakelists_file:
        content = "\
add_cpp_library_tests(SHARED ${{PROJECT_NAME}}\n\
                      STATIC ${{PROJECT_NAME}}-static\n\
                      SOURCES {pname}_tests.cpp)\n".format(pname=project_name)
        test_cmakelists_file.write(content)

# create_example_cmakelists()
def create_example_cmakelists(project_name:str, example_cmakelists_path:str):
    with open(example_cmakelists_path, "w") as example_cmakelists_file:
        content = "\
add_cpp_library_examples(SHARED ${{PROJECT_NAME}}\n\
                         STATIC ${{PROJECT_NAME}}-static\n\
                         SOURCES {pname}_example.cpp)\n".format(pname=project_name)
        example_cmakelists_file.write(content)

# library_project_cmakelists_contents():
def library_project_cmakelists_contents(project_cmakelists_path:str, project_name:str, project_version:str, \
                                        cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, \
                                        create_version_header:bool, cmake_project_config_type:str, cmake_project_config_file:str, \
                                        cpp_version:str):
    contents = project_cmakelists_contents("CppLibraryProject", project_cmakelists_path, project_name, project_version, \
                                           cmake_major, cmake_minor, build_in_tree_allowed)
    create_version_header_code = "    OUTPUT_VERSION_HEADER \"version.hpp\"\n" if create_version_header else ""
    package_config_code = cmake_project_config_type + "_PACKAGE_CONFIG_FILE"
    if cmake_project_config_type:
        package_config_code += " " + cmake_project_config_file
    return contents + "\
include(CTest)\n\
\n\
# Project options\n\
library_build_options(${{PROJECT_NAME}} STATIC SHARED EXAMPLE TEST)\n\
\n\
# Headers:\n\
set(headers\n\
include/{pname}/{pname}.hpp\n\
)\n\
\n\
# Sources:\n\
set(sources\n\
src/{pname}.cpp\n\
)\n\
\n\
# Add C++ library\n\
add_cpp_library(${{PROJECT_NAME}} ${{PROJECT_NAME}}_BUILD_SHARED_LIB ${{PROJECT_NAME}}_BUILD_STATIC_LIB\n\
    SHARED ${{PROJECT_NAME}}\n\
    STATIC ${{PROJECT_NAME}}-static\n\
    CXX_STANDARD {cpp_version}\n\
    INCLUDE_DIRECTORIES include\n\
{create_version_header_code}\
    HEADERS ${{headers}}\n\
    SOURCES ${{sources}}\n\
    BUILT_TARGETS project_targets\n\
    )\n\
\n\
# Install C++ library\n\
install_cpp_library_targets(${{PROJECT_NAME}}\n\
                            TARGETS ${{project_targets}}\n\
                            INCLUDE_DIRECTORIES \"include/${{PROJECT_NAME}}\"\n\
                            )\n\
\n\
# Link targets:\n\
# find_package(TBB 2018 REQUIRED CONFIG)\n\
# cpp_library_targets_link_libraries(${{PROJECT_NAME}} PUBLIC TBB::tbb)\n\
\n\
# Install package\n\
install_package(${{PROJECT_NAME}}\n\
                {package_config_code}\n\
                EXPORT_NAMES ${{PROJECT_NAME}})\n\
\n\
if(${{PROJECT_NAME}}_BUILD_EXAMPLES)\n\
    add_subdirectory(example)\n\
endif()\n\
\n\
if(${{PROJECT_NAME}}_BUILD_TESTS AND BUILD_TESTING)\n\
    add_subdirectory(test)\n\
endif()\n\
\n\
#-----\n".format(create_version_header_code=create_version_header_code, package_config_code=package_config_code, \
                 cpp_version=cpp_version, pname=project_name)

# create_project_cmakelists()
def create_project_cmakelists(project_cmakelists_path:str, project_name:str, project_version:str, \
                              cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool, \
                              create_version_header:bool, cmake_project_config_type:str, cmake_project_config_file:str, \
                              cpp_version:str):
    with open(project_cmakelists_path, "w") as project_cmakelists_file:
        content = library_project_cmakelists_contents(project_cmakelists_path, project_name, project_version, \
                                                      cmake_major, cmake_minor, build_in_tree_allowed, create_version_header, \
                                                      cmake_project_config_type, cmake_project_config_file, cpp_version)
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
        self._cml_cmake_project_config_type = init_parameter("Project config type (BASIC | VERBOSE | INPUT)", default_cmake_project_config_type, \
                                                             lambda type: type in ["BASIC", "VERBOSE", "INPUT"])
        self._cmake_project_config_file = ""
        if self._cml_cmake_project_config_type == "INPUT":
            default_cmake_package_config_file = "CMake-package-config.cmake.in"
            self._cmake_project_config_file = init_parameter("Input package config file name?", default_cmake_package_config_file, \
                                                                lambda filename: len(filename) > 0)
        pass

    def _create_dir_tree(self):
        super()._create_dir_tree()
        for subdir in [self.project_include_dir(), "src", "test", "example", "example/basic_cmake_project"]:
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
                                  self._cml_cmake_project_config_type, self._cmake_project_config_file, \
                                  self._cml_cpp_version)
        # Write project input CMake package config, if needed:
        if self._cml_cmake_project_config_type == "INPUT":
            input_cmake_package_config_path = "{proot}/{filename}".format(proot=self._project_name, filename=self._cmake_project_config_file)
            self.__create_input_cmake_package_config_file(input_cmake_package_config_path)
        # Write project/test/CMakeLists.txt
        test_source_path = "{proot}/{test}/{proot}_tests.cpp".format(proot=self._project_name, test="test")
        self.__create_test_file(test_source_path)
        test_cmakelists_path = "{proot}/{test}/CMakeLists.txt".format(proot=self._project_name, test="test")
        create_test_cmakelists(self._project_name, test_cmakelists_path)
        # Write project/example/CMakeLists.txt
        example_source_path = "{proot}/{example}/{proot}_example.cpp".format(proot=self._project_name, example="example")
        self.__create_example_file(example_source_path)
        example_cmakelists_path = "{proot}/{example}/CMakeLists.txt".format(proot=self._project_name, example="example")
        create_example_cmakelists(self._project_name, example_cmakelists_path)
        # Write project/example/basic_cmake_project/CMakeLists.txt
        cmake_example_source_path = "{proot}/{example}/main.cpp".format(proot=self._project_name, example="example/basic_cmake_project")
        self.__create_cmake_example_file(cmake_example_source_path)
        cmake_example_cmakelists_path = "{proot}/{example}/CMakeLists.txt".format(proot=self._project_name, example="example/basic_cmake_project")
        self.__create_cmake_example_cmakelists(cmake_example_cmakelists_path)
        super()._create_files()
        pass

    def __create_input_cmake_package_config_file(self, input_cmake_package_config_path:str):
        with open(input_cmake_package_config_path, "w") as input_cmake_package_config_file:
            content = """
@PACKAGE_INIT@

# include(CMakeFindDependencyMacro)
# find_dependency(TBB 2018 CONFIG)

include(${CMAKE_CURRENT_LIST_DIR}/@PROJECT_NAME@.cmake)
check_required_components(@PROJECT_NAME@)

message(STATUS "Found package @PROJECT_NAME@ @PROJECT_VERSION@")
"""
            input_cmake_package_config_file.write(content)
        pass

    def __create_test_file(self, test_source_path:str):
        with open(test_source_path, "w") as test_source_file:
            content = "\
#include <{pname}/{pname}.hpp>\n\
#include <gtest/gtest.h>\n\
#include <cstdlib>\n\
\n\
TEST({pname}_tests, basic_test)\n\
{{\n\
    ASSERT_EQ(module_name(), \"{pname}\");\n\
}}\n\
\n\
int main(int argc, char** argv)\n\
{{\n\
    ::testing::InitGoogleTest(&argc, argv);\n\
    return RUN_ALL_TESTS();\n\
}}\n".format(pname=self._project_name)
            test_source_file.write(content)
        pass

    def __create_example_file(self, example_source_path:str):
        with open(example_source_path, "w") as example_source_file:
            content = "\
#include <iostream>\n\
#include <{pname}/{pname}.hpp>\n\
\n\
int main()\n\
{{\n\
    std::cout << module_name() << std::endl;\n\
    return EXIT_SUCCESS;\n\
}}\n".format(pname=self._project_name)
            example_source_file.write(content)
        pass

    def __create_cmake_example_file(self, example_source_path:str):
        self.__create_example_file(example_source_path)
        pass

    def __create_cmake_example_cmakelists(self, example_cmakelists_path:str):
        with open(example_cmakelists_path, "w") as example_cmakelists_file:
            content = "cmake_minimum_required(VERSION {cmake_version_major}.{cmake_version_minor})\n\
\n\
project(basic_cmake_project)\n\
\n\
add_executable(${{PROJECT_NAME}} main.cpp)\n\
# Find package {pname}:\n\
find_package({pname} {pversion} CONFIG REQUIRED)\n\
# Use {pname} release shared target:\n\
target_link_libraries(${{PROJECT_NAME}} PRIVATE {pname})\n\
# Use {pname} release static target:\n\
#target_link_libraries(${{PROJECT_NAME}} PRIVATE {pname}-static)\n\
\n".format(pname=self._project_name, pversion=self._project_version, \
           cmake_version_major=self._cmake.metadata().major_version(), \
           cmake_version_minor=self._cmake.metadata().minor_version())
            example_cmakelists_file.write(content)
        pass

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('project_name', nargs='?', type=str, help='Project name')
    argparser.add_argument('--cmake', metavar='cmake-path', type=str, default="cmake", help='Path or alias to CMake')
    pargs = argparser.parse_args()

    cmtkgen = Cmtk_library_project_creator(pargs.cmake)
    cmtkgen.cmake().check_version()
    cmtkgen.create_project(pargs.project_name)

    print("EXIT SUCCESS")
