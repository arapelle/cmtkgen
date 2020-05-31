#!/usr/bin/python3

import os
import shutil
import argparse
import subprocess
import re
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

# python current dir
python_current_dir = os.path.dirname(os.path.realpath(__file__))

#--------------------------------------------------------------------------------

def cancel_project_creation(res = 0):
    print("Project creation canceled.")
    exit(res)

def ask_parameter(label:str, default_value:str):
    return simpledialog.askstring(label, label + ": ", initialvalue=default_value)

def ask_bool_parameter(label:str):
    return messagebox.askyesnocancel(label, label)

def init_parameter(label:str, default_value, check_fn, input_value=None, ask_fn=None):
    parameter_is_bool = type(default_value) == type(True)
    if ask_fn is None:
        if parameter_is_bool:
            ask_fn = lambda: ask_bool_parameter(label)
        else:
            ask_fn = lambda: ask_parameter(label, default_value)
    param = None if parameter_is_bool else default_value.__new__(type(default_value))
    if input_value is not None:
        param = input_value
    while not check_fn(param):
        param = ask_fn()
        if param is None:
            cancel_project_creation()
    print("Parameter '{}': '{}'".format(label, param))
    return param

def init_bool_parameter(label:str, input_value=None):
    check_fn = lambda option: option != None and type(option) == type(True)
    return init_parameter(label, False, check_fn, input_value, lambda: ask_bool_parameter(label))

#--------

# create_project_header_file()
def create_project_header_file(header_file_path:str):
    with open(header_file_path, "w") as header_file:
        content = "#pragma once\n"
        header_file.write(content)
    pass

# create_project_source_file()
def create_project_source_file(project_source_file_path:str):
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

# create_project_cmakelists()
def create_project_cmakelists(project_cmakelists_path:str, project_name:str, cmake_major:str, cmake_minor:str):
    with open(project_cmakelists_path, "w") as project_cmakelists_file:
        content = "cmake_minimum_required(VERSION {cmake_major}.{cmake_minor})\n\
\n\
list(PREPEND CMAKE_MODULE_PATH ${{CMAKE_SOURCE_DIR}}/cmake/)\n\
\n\
# Standard includes\n\
include(CMakePrintHelpers)\n\
# Custom include\n\
include(cmtk/Project)\n\
\n\
#-----\n\
# PROJECT\n\
\n\
set_build_type_if_undefined()\n\
\n\
#-----\n\
# C++ PROJECT\n\
\n\
project({pname}\n\
        LANGUAGES CXX)\n\
\n\
add_executable(${{PROJECT_NAME}} main.cpp main.hpp)\n\n".format(pname=project_name, cmake_major=cmake_major, cmake_minor=cmake_minor)
        project_cmakelists_file.write(content)

#--------------------------------------------------------------------------------

#-----------
# Parse args
#-----------
argparser = argparse.ArgumentParser()
argparser.add_argument('project_name', nargs='?', type=str, help='Project name')
argparser.add_argument('--cmake', metavar='cmake-path', type=str, default="cmake", help='Path or alias to CMake')
pargs = argparser.parse_args()

#---------------
# CMake Metadata
#---------------
if not pargs.cmake or not shutil.which(pargs.cmake):
    messagebox.showerror("CMake not found!", "CMake cannot be found.\nUse option --cmake.\n\n{}".format(argparser.format_usage()))
    exit(-1)
result = subprocess.run("{} -E capabilities".format(pargs.cmake).split(), stdout=subprocess.PIPE)
cmake_metadata = result.stdout.decode('utf-8')
cmake_metadata = json.loads(cmake_metadata)
# print(json.dumps(cmake_metadata, sort_keys=True, indent=2))
cmake_version = cmake_metadata["version"]
cmake_major = cmake_version["major"]
cmake_minor = cmake_version["minor"]
if cmake_major < 3 or cmake_minor < 13:
    messagebox.showerror("Update your CMake!", "Your CMake version is too low: {}.{}.\nUse CMake 3.13 or later!".format(cmake_major, cmake_minor))
#---

#---------------
# Default values
#---------------
default_cpp_version = "17"

#-------------------------
# Check and set parameters
#-------------------------

# hide main window
root = tk.Tk()
root.withdraw()

# Project: 
## Name
project_name = init_parameter("Project name", "", lambda pname: len(pname) > 0, pargs.project_name)

# CMakeLists.txt: 
## C++ version
cml_cpp_version = init_parameter("C++ version", default_cpp_version, lambda version: version in ["11","14","17","20"])

#-----------------
# Create file tree
#-----------------

# If project root directory already exists, remove it
if os.path.exists(project_name):
    print("Remove dir '{}'".format(project_name))
    shutil.rmtree(project_name)
# Create project root directory
print("Create dir '{}'".format(project_name))
os.makedirs(project_name)

# Copy cmtk cmake tools
os.makedirs("{proot}/cmake".format(proot=project_name))
subprocess.run("git init".split(), cwd=project_name)
subprocess.run("git submodule add -b {gitbranch} {gitrepo} cmake/cmtk".format(proot=project_name, \
               gitbranch="master", gitrepo="https://github.com/arapelle/cmtk").split(), \
               cwd=project_name)

# Write project header
header_file_path = "{pname}/main.hpp".format(pname=project_name)
create_project_header_file(header_file_path)

# Write project source
project_source_file_path = "{pname}/main.cpp".format(pname=project_name)
create_project_source_file(project_source_file_path)

# Write project/CMakeLists.txt
project_cmakelists_path = "{proot}/CMakeLists.txt".format(proot=project_name)
create_project_cmakelists(project_cmakelists_path, project_name, cmake_major, cmake_minor)

print("EXIT SUCCESS")
