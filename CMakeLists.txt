cmake_minimum_required(VERSION 2.8.3)
project(RSD)

find_package(catkin REQUIRED COMPONENTS message_generation std_msgs)

#add_message_files(DIRECTORY msg FILES Floats.msg HeaderString.msg)
add_service_files(DIRECTORY srv FILES move_robot.srv)

generate_messages(DEPENDENCIES std_msgs)

catkin_package(CATKIN_DEPENDS message_runtime std_msgs)

# do not wildcard install files since the root folder of the package will contain a debian folder for releasing
catkin_install_python(PROGRAMS
  PyURBridge/PyURBridge.py
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/PyURBridge
)