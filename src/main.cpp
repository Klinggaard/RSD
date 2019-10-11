//
// Created by kasper on 10/10/19.
// RUNS SERVICE CLIENT TO INTERFACE WITH A PYTHONG MODULE
//

#include <iostream>
#include "ros/ros.h"
#include "robot_system_design/move_robot.h"
#include "URrobot.h"
#include <rw/math/Q.hpp>

bool add(robot_system_design::move_robot::Request &req, robot_system_design::move_robot::Response &res){
    //Move the robot with URRobot.h, NOT TESTED
    URRobot robot;

    rw::math::Q moveRequest(6);
    moveRequest[req.request[0],req.request[1],req.request[2],req.request[3],req.request[4],req.request[5]];

    res.response = robot.setQ(moveRequest);
    return true;
}

int main(int argc, char **argv){
    ros::init(argc, argv, "ur_control");
    ros::NodeHandle n;

    ros::ServiceServer service = n.advertiseService("move_robot",add);
    ROS_INFO("Ready to move robot");
    ros::spin();

    return 0;
}