cmake_minimum_required(VERSION 3.8)
project(gimbal_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# 生成消息接口
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/TargetInfo.msg"
  DEPENDENCIES std_msgs
)

# 确保消息生成在编译时可用
ament_export_dependencies(rosidl_default_runtime)

ament_package()

