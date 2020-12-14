
import datetime
import tkinter
import subprocess
import shutil
import json
import re
import os
from tkinter import messagebox
from tkinter import simpledialog

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

# create_readme_file()
def create_readme_file(readme_file_path:str, project_name:str):
    with open(readme_file_path, "w") as readme_file:
        readme_file.write(project_name + "\n")
    pass

# create_cmake_quick_install()
def create_cmake_quick_install(cmake_quick_install_path:str, project_name:str):
    with open(cmake_quick_install_path, "w") as cmake_quick_install_file:
        content="# cmake -P cmake_quick_install.cmake\n\
\n\
function(get_script_args script_args)\n\
    set(sc_args)\n\
    set(start_found False)\n\
    foreach(argi RANGE ${{CMAKE_ARGC}})\n\
        set(arg ${{CMAKE_ARGV${{argi}}}})\n\
        if(start_found)\n\
            list(APPEND sc_args ${{arg}})\n\
        endif()\n\
        if(\"${{arg}}\" STREQUAL \"--\")\n\
            set(start_found True)\n\
        endif()\n\
    endforeach()\n\
    set(${{script_args}} ${{sc_args}} PARENT_SCOPE)\n\
endfunction()\n\
\n\
get_script_args(args)\n\
set(options \"\")\n\
set(params DIR BUILD)\n\
set(lists \"\")\n\
cmake_parse_arguments(ARG \"${{options}}\" \"${{params}}\" \"${{lists}}\" ${{args}})\n\
\n\
set(project \"{project_name}\")\n\
\n\
if(WIN32)\n\
    set(temp_dir $ENV{{TEMP}})\n\
elseif(UNIX)\n\
    set(temp_dir /tmp)\n\
else()\n\
    message(FATAL_ERROR \"No temporary directory found!\")\n\
endif()\n\
\n\
file(TO_NATIVE_PATH \"/\" path_sep)\n\
set(src_dir ${{CMAKE_CURRENT_LIST_DIR}})\n\
set(build_dir ${{temp_dir}}${{path_sep}}${{project}}-build)\n\
set(error_file ${{build_dir}}${{path_sep}}quick_install_error)\n\
\n\
if(EXISTS ${{error_file}})\n\
    message(STATUS \"Previous call to quick_install.cmake failed. Cleaning...\")\n\
    file(REMOVE_RECURSE ${{build_dir}})\n\
endif()\n\
\n\
message(STATUS \"*  CONFIGURATION\")\n\
if(ARG_BUILD)\n\
    list(APPEND conf_args -DCMAKE_BUILD_TYPE=${{ARG_BUILD}})\n\
else()\n\
    list(APPEND conf_args -DCMAKE_BUILD_TYPE=${{CMAKE_BUILD_TYPE}})\n\
endif()\n\
if(ARG_DIR)\n\
    list(APPEND conf_args -DCMAKE_INSTALL_PREFIX=${{ARG_DIR}})\n\
endif()\n\
execute_process(COMMAND ${{CMAKE_COMMAND}} ${{conf_args}} -S ${{src_dir}} -B ${{build_dir}}  RESULT_VARIABLE cmd_res)\n\
if(NOT cmd_res EQUAL 0)\n\
    file(TOUCH ${{error_file}})\n\
    return()\n\
endif()\n\
\n\
message(STATUS \"*  BUILD\")\n\
execute_process(COMMAND ${{CMAKE_COMMAND}} --build ${{build_dir}}  RESULT_VARIABLE cmd_res)\n\
if(NOT cmd_res EQUAL 0)\n\
    file(TOUCH ${{error_file}})\n\
    return()\n\
endif()\n\
\n\
message(STATUS \"*  INSTALL\")\n\
execute_process(COMMAND ${{CMAKE_COMMAND}} --install ${{build_dir}})\n\
if(NOT cmd_res EQUAL 0)\n\
    file(TOUCH ${{error_file}})\n\
endif()\n".format(project_name=project_name)
        cmake_quick_install_file.write(content)

# create_license_file()
def create_license_file(license_file_path:str, license_copyright_holders:str):
    with open(license_file_path, "w") as license_file:
        content = "The MIT License (MIT)\n\
\n\
Copyright (c) {year} {copyright_holders}\n\
\n\
Permission is hereby granted, free of charge, to any person obtaining a copy\n\
of this software and associated documentation files (the \"Software\"), to deal\n\
in the Software without restriction, including without limitation the rights\n\
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n\
copies of the Software, and to permit persons to whom the Software is\n\
furnished to do so, subject to the following conditions:\n\
\n\
The above copyright notice and this permission notice shall be included in\n\
all copies or substantial portions of the Software.\n\
\n\
THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n\
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n\
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n\
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n\
THE SOFTWARE.\n".format(year=datetime.datetime.now().year, copyright_holders=license_copyright_holders)
        license_file.write(content)

# create_gitignore_file()
def create_gitignore_file(gitignore_file_path):
    with open(gitignore_file_path, "w") as gitignore_file:
        content = "CMakeLists.txt.user\n\
build/\n\
*.pro.user\n"
        gitignore_file.write(content)

# create_project_header_file()
def create_project_header_file(header_file_path:str, project_name:str="", honly:str=False):
    with open(header_file_path, "w") as header_file:
        content = "#pragma once \n\
\n\
#include <string>\n\
\n"
        if honly:
            content += "inline std::string module_name() {{ return \"{pname}\"; }}\n".format(pname=project_name)
        else:
            content += "std::string module_name();\n"
        header_file.write(content)
    pass

# create_project_source_file()
def create_project_source_file(project_source_file_path:str, project_name:str):
    with open(project_source_file_path, "w") as source_file:
        content = "#include <{pname}/{pname}.hpp> \n\
\n\
std::string module_name()\n\
{{\n\
    return \"{pname}\";\n\
}}\n".format(pname=project_name)
        source_file.write(content)
    pass

# project_cmakelists_contents():
def project_cmakelists_contents(cmtk_include:str, project_cmakelists_path:str, project_name:str, project_version:str, \
                                cmake_major:str, cmake_minor:str, build_in_tree_allowed:bool):
    check_cmake_binary_dir_code = "check_cmake_binary_dir()\n" if not build_in_tree_allowed else ""
    project_version_code = "        VERSION " + project_version if project_version else '#        VERSION "0.1.0"'
    return "\
cmake_minimum_required(VERSION {cmake_major}.{cmake_minor})\n\
\n\
list(PREPEND CMAKE_MODULE_PATH ${{CMAKE_SOURCE_DIR}}/cmake/)\n\
\n\
include(CMakePrintHelpers)\n\
include(cmtk/{cmtk_include})\n\
\n\
#-----\n\
# PROJECT\n\
\n\
{check_cmake_binary_dir_code}\
set_build_type_if_undefined()\n\
\n\
#-----\n\
# C++ PROJECT\n\
\n\
project({pname}\n\
{pversion_code}\n\
#        DESCRIPTION \"\"\n\
#        HOMEPAGE_URL \"\"\n\
        LANGUAGES CXX)\n\
\n\
message(STATUS \"BUILD   : ${{CMAKE_BUILD_TYPE}}\")\n\
message(STATUS \"CPPCOMP : ${{CMAKE_CXX_COMPILER}} ${{CMAKE_CXX_COMPILER_VERSION}}\")\n\
message(STATUS \"PROJECT : ${{PROJECT_NAME}} ${{PROJECT_VERSION}}\")\n\
\n\
#-----\n".format(cmtk_include=cmtk_include, pname=project_name, pversion_code=project_version_code, 
                 cmake_major=cmake_major, cmake_minor=cmake_minor, \
                 check_cmake_binary_dir_code=check_cmake_binary_dir_code)

#--------

# CMake_metadata:
class CMake_metadata:
    def __init__(self, json_data):
        self.__json_data = json_data
    def version(self):
        return self.__json_data["version"]
    def major_version(self):
        return self.__json_data["version"]["major"]
    def minor_version(self):
        return self.__json_data["version"]["minor"]

# CMake:
class CMake:
    def __init__(self, cmake_path:str):
        self.__path = cmake_path
        result = subprocess.run("{} -E capabilities".format(self.__path).split(), stdout=subprocess.PIPE)
        metadata = result.stdout.decode('utf-8')
        self.__metadata = CMake_metadata(json.loads(metadata))
    def path(self):
        return self.__path
    def metadata(self):
        return self.__metadata
    def check_version(self):
        major = self.metadata().major_version()
        minor = self.metadata().minor_version()
        if major < 3 or minor < 13:
            error_msg = str("Update your CMake!", "Your CMake version is too low: {}.{}.\nUse CMake 3.13 or later!")
            messagebox.showerror(error_msg.format(major, minor))
            exit(-1)

def check_project_version(project_version):
    regexp = re.compile('[0-9]+.[0-9]+.[0-9]+')
    return regexp.fullmatch(project_version) != None

# Cmtk_project_creator:
class Cmtk_project_creator:
    def __init__(self, cmake_path:str):
        self._cmake = CMake(cmake_path)
        # project
        self._project_name = ""
        self._project_version = None
        # CMakeLists.txt
        self._cml_build_in_tree_allowed = None
        self._cml_cpp_version = ""
        pass

    def cmake(self):
        return self._cmake

    def create_project(self, project_name:str):
        gui = tkinter.Tk()
        gui.withdraw()
        self._init_parameters(project_name)
        self._create_dir_tree()
        self._create_files()
        pass

    def _init_parameters(self, project_name:str):
        # Init parameters
        ## Project:
        self._project_name = init_parameter("Project name", "", lambda pname: len(pname) > 0, project_name)
        if self._project_version is None:
            default_project_version = "0.1.0"
            self._project_version = init_parameter("Project version", default_project_version, check_project_version)
        ## CMakeLists.txt:
        if self._cml_build_in_tree_allowed is None:
            default_cmake_build_in_tree = False
            self._cml_build_in_tree_allowed = init_parameter("Allowing build-in tree", default_cmake_build_in_tree, lambda option: option != None)
        default_cpp_version = "17"
        self._cml_cpp_version = init_parameter("C++ version", default_cpp_version, lambda version: version in ["11","14","17","20"])
        pass

    def _create_dir_tree(self):
        # Remove existing project root directory
        if os.path.exists(self._project_name):
            print("Remove dir '{}'".format(self._project_name))
            shutil.rmtree(self._project_name)
        # Create project root directory
        print("Create dir '{}'".format(self._project_name))
        os.makedirs(self._project_name)
        # Init git
        self.__init_git()
        pass

    def _create_files(self):
        pass

    def _create_subdir(self, subdir:str):
        path = "{proot}/{sub}".format(proot=self._project_name, sub=subdir)
        print("Create dir '{}'".format(path))
        os.makedirs(path)
        pass

    def __init_git(self):
        cmtk_version = "0.4.4"
        os.makedirs("{proot}/cmake".format(proot=self._project_name))
        subprocess.run("git init".split(), cwd=self._project_name)
        # Copy cmtk cmake tools
        subprocess.run("git submodule add -b {gitbranch} {gitrepo} cmake/cmtk".format(proot=self._project_name, \
                    gitbranch="release/{}".format(cmtk_version), gitrepo="https://github.com/arapelle/cmtk").split(), \
                    cwd=self._project_name)
        pass

# Cmtk_shared_project_creator:
class Cmtk_shared_project_creator(Cmtk_project_creator):
    def __init__(self, cmake_path:str):
        super().__init__(cmake_path)
        #  Git
        self._git_create_gitignore = False
        # License
        self._license_create_license_file = False
        self._license_file_name = ""
        self._license_copyright_holders = ""
        # Readme
        self._readme_create_readme_file = ""
        self._readme_file_name = ""
        pass

    def _init_parameters(self, project_name:str):
        super()._init_parameters(project_name)
        # Init parameters
        ## Git:
        self._git_create_gitignore = init_bool_parameter("Do you want a .gitignore file?")
        ## License:
        self._license_create_license_file = init_bool_parameter("Do you want a license file?")
        if self._license_create_license_file:
            self._license_file_name = init_parameter("License file name?", "LICENSE.md", lambda pname: len(pname) > 0)
            self._license_copyright_holders = init_parameter("Who are the copyright holders?", "", lambda pname: len(pname) > 0)
        ## Readme:
        self._readme_create_readme_file = init_bool_parameter("Do you want a readme file?")
        if self._readme_create_readme_file:
            self._readme_file_name = init_parameter("Readme file name?", "README.md", lambda pname: len(pname) > 0)
        pass

    def _create_files(self):
        # Write .gitignore file
        if self._git_create_gitignore:
            gitignore_file_path = "{pname}/.gitignore".format(pname=self._project_name)
            create_gitignore_file(gitignore_file_path)
        # Write license file
        if self._license_create_license_file:
            license_file_path = "{pname}/{license}".format(pname=self._project_name, license=self._license_file_name)
            create_license_file(license_file_path, self._license_copyright_holders)
        # Write readme file
        if self._readme_create_readme_file:
            readme_file_path = "{pname}/{readme}".format(pname=self._project_name, readme=self._readme_file_name)
            create_readme_file(readme_file_path, self._project_name)
        # Write cmake_quick_install.cmake
        cmake_quick_install_path = "{}/cmake_quick_install.cmake".format(self._project_name)
        create_cmake_quick_install(cmake_quick_install_path, self._project_name)
        pass    
