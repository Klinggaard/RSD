cmake_minimum_required(VERSION 2.8.3)
project(RSD)

## Add support for C++11, supported in ROS Kinetic and newer
set (CMAKE_CXX_STANDARD 11)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
        roscpp
        rospy
        roslib
        caros_common_msgs
        caros_control_msgs
        caros_common
        caros_control
        std_msgs
        message_generation
        )

add_service_files(
        FILES
        move_robot.srv
)

generate_messages(
        DEPENDENCIES
        std_msgs
)

###################################
##         RobWork setup         ##
###################################
# Set the RobWork root (edit in .bashrc if necessary)
SET(RW_ROOT $ENV{RW_ROOT})

# Use RobWork
MESSAGE("-- RobWork root: " ${RW_ROOT})
SET(RobWork_DIR ${RW_ROOT}/cmake)
FIND_PACKAGE(RobWork REQUIRED)
INCLUDE_DIRECTORIES( ${ROBWORK_INCLUDE_DIRS} )
LINK_DIRECTORIES( ${ROBWORK_LIBRARY_DIRS} )


###################################
## catkin specific configuration ##
###################################
catkin_package(
        CATKIN_DEPENDS message_runtime
        #  INCLUDE_DIRS include
        #  LIBRARIES rovi2_rob
        #  CATKIN_DEPENDS roscpp
        #  DEPENDS system_lib
)

###########
## Build ##
###########

include_directories(include/
        ${catkin_INCLUDE_DIRS}
        )

add_executable(ur_control src/URrobot.cpp src/main.cpp)
target_link_libraries(ur_control ${catkin_LIBRARIES} ${ROBWORK_LIBRARIES} ${ROS_LIBRARIES})
add_dependencies(ur_control caros_common_msgs caros_control_msgs caros_control ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})