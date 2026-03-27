cmake_policy(SET CMP0078 NEW)
cmake_policy(SET CMP0086 NEW)

find_package(SWIG REQUIRED)
include(UseSWIG)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

set_property(SOURCE pysimulavr.i PROPERTY CPLUSPLUS ON)
set_property(SOURCE pysimulavr.i PROPERTY INCLUDE_DIRECTORIES
  "${CMAKE_SOURCE_DIR}/include"
  "${CMAKE_CURRENT_SOURCE_DIR}")

# Target name matches the SWIG %module name so UseSWIG passes -module pysimulavr,
# producing _pysimulavr.so with single-underscore imports (no Python name-mangling issues).
swig_add_library(pysimulavr TYPE MODULE LANGUAGE python SOURCES pysimulavr.i)

target_include_directories(pysimulavr PRIVATE
  "${CMAKE_SOURCE_DIR}/include"
  "${CMAKE_SOURCE_DIR}/include/elfio"
  "${CMAKE_CURRENT_SOURCE_DIR}")

target_link_libraries(pysimulavr PRIVATE sim_static Python::Module)

install(TARGETS pysimulavr DESTINATION .)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/pysimulavr.py" DESTINATION .)

# EOF
