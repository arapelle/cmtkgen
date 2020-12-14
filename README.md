# Concept

Python scripts which create C++ CMake projects based on [CMTK](https://github.com/arapelle/cmtk) (used as a git submodule).

See the [task board](https://app.gitkraken.com/glo/board/X0RDeiQxbQAR6DqV) for future updates and features.

# Requirements

Binaries:

- CMake 3.16 or later
- git
- python 3.6
- python3-tkinter
# Install

`pip3 install cmtkgen`

# Scripts

Each script creates a C++ project according to the information provided by the user.

### create_cpp_executable_project.py  [*project_name*]

This scripts generates a CMake project with an executable target. This executable can be installed after being successfully built.

<u>Questions asked to generate the project:</u>

- Project name (if not provided on command line)

- Project version (default: 0.1.0)
- Allowing CMake build-in tree? To allow the CMake configuration of the project directly in the source directory or in one of its sub-directory.
- Which C++ version do you want to use? (11, 14, 17, 20)
- Do you want a *.gitignore* file?
- Do you want a License file? Which file name? Who are the copyright holders?
- Do you want a Readme file?Which file name?
- Do you want a version header file? (a version.hpp file will be created by CMTK during CMake configuration.)

<u>Example of a full executable project named `cpp_exec`:</u>

```
cpp_exec/
├── cmake
│   └── cmtk/...
├── include
│   └── cpp_exec
│       └── cpp_exec.hpp
├── src
│   ├── cpp_exec.cpp
│   └── main.cpp
├── CMakeLists.txt
├── cmake_quick_install.cmake
├── .gitignore
├── .gitmodules  # For CMTK
├── LICENSE.md
└── README.md
```

To configure, build and install such a project use [cmake_quick_install.cmake](#About cmake_quick_install.cmake) or execute the following commands:

```
cmake -S cpp_exec/ -B build
cmake --build build/
cmake --install build/
```

### create_cpp_lib_project.py  [*project_name*]

<u>Questions asked to generate the project:</u>

- Project name (if not provided on command line)

- Project version (default: 0.1.0)
- Allowing CMake build-in tree? To allow the CMake configuration of the project directly in the source directory or in one of its sub-directory.
- Which C++ version do you want to use? (11, 14, 17, 20)
- Do you want a *.gitignore* file?
- Do you want a License file? Which file name? Who are the copyright holders?
- Do you want a Readme file?Which file name?
- Do you want a version header file? (a version.hpp file will be created by CMTK during CMake configuration.)

- Which type of package-config file do you want for your project, BASIC or VERBOSE? (a *package*-config.cmake will be created by CMTK during CMake configuration.)

<u>Example of a full executable project named `cpp_lib`:</u>

```
cpp_lib/
├── cmake
│   └── cmtk/...
├── example
│   ├── CMakeLists.txt
│   └── cpp_lib_example.cpp
├── include
│   └── cpp_lib
│       └── cpp_lib.hpp
├── src
│   └── cpp_lib.cpp
├── test
│   ├── CMakeLists.txt
│   └── cpp_lib_tests.cpp
├── CMakeLists.txt
├── cmake_quick_install.cmake
├── .gitignore
├── .gitmodules  # For CMTK
├── LICENSE.md
└── README.md
```

To configure, build and install such a project use [cmake_quick_install.cmake](#About cmake_quick_install.cmake) or execute the following commands:

```
cmake -S cpp_lib/ -B build
cmake --build build/
cmake --install build/
```

### create_cpp_honly_lib_project.py  [*project_name*]

<u>Questions asked to generate the project:</u>

- Project name (if not provided on command line)

- Project version (default: 0.1.0)
- Allowing CMake build-in tree? To allow the CMake configuration of the project directly in the source directory or in one of its sub-directory.
- Which C++ version do you want to use? (11, 14, 17, 20)
- Do you want a *.gitignore* file?
- Do you want a License file? Which file name? Who are the copyright holders?
- Do you want a Readme file?Which file name?
- Do you want a version header file? (a version.hpp file will be created by CMTK during CMake configuration.)

- Which type of package-config file do you want for your project, BASIC or VERBOSE? (a *package*-config.cmake will be created by CMTK during CMake configuration.)

<u>Example of a full executable project named `cpp_honly`:</u>

```
cpp_honly/
├── cmake
│   └── cmtk/...
├── example
│   ├── CMakeLists.txt
│   └── cpp_honly_example.cpp
├── include
│   └── cpp_honly
│       └── cpp_honly.hpp
├── test
│   ├── CMakeLists.txt
│   └── cpp_honly_tests.cpp
├── CMakeLists.txt
├── cmake_quick_install.cmake
├── .gitignore
├── .gitmodules  # For CMTK
├── LICENSE.md
└── README.md
```

To configure, build and install such a project use [cmake_quick_install.cmake](#About cmake_quick_install.cmake) or execute the following commands:

```
cmake -S cpp_honly/ -B build
cmake --build build/
cmake --install build/
```

### create_cpp_hello_world.py  [*project_name*]

<u>Questions asked to generate the project:</u>

- Project name (if not provided on command line)

- Which C++ version do you want to use? (11, 14, 17, 20)

<u>Example of a full executable project named `cpp_hello_world`:</u>

```
cpp_hello_world/
├── cmake
│   └── cmtk/...
├── CMakeLists.txt
├── .gitmodules  # For CMTK
├── main.cpp
└── main.hpp
```

To configure and build such a project execute use the following commands:

```
cmake -S cpp_hello_world/ -B build
cmake --build build/
```

### About cmake_quick_install.cmake

Executable and library projects have a cmake_quick_install.cmake script. It can be called with CMake like this:

`cmake -P cmake_quick_install.cmake`

It has optional parameters:

- DIR: 	The install prefix directory.
- BUILD: 	The build type. (default: Release)

Some examples:

```
cmake -P cmake_quick_install.cmake -- DIR ~/local/
cmake -P cmake_quick_install.cmake -- BUILD Debug
cmake -P cmake_quick_install.cmake -- DIR ~/local/ BUILD Debug
```

# License

[MIT License](./LICENSE.md) © cmtkgen