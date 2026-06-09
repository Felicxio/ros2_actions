#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse
from rclpy.action.server import ServerGoalHandle
from my_robot2_interfaces.action import CountUtil


class CountUntilServerNode(Node): 
    def __init__(self):
        super().__init__("count_until_server") 
        self.count_until_server_ = ActionServer(self, CountUtil, "count_until",
                                                goal_callback= self.goal_callback,
                                                execute_callback=self.execute_callback)
        self.get_logger().info("Action Server has been started!")


    def goal_callback(self, goal_request: CountUtil.Goal):
        self.get_logger().info("Received a goal")
        #Validate the goal request
        if goal_request.target_number <= 0:
            self.get_logger().info("Rejecting the goal...")
            return GoalResponse.REJECT
        self.get_logger().info("Goal Accepted...")
        return GoalResponse.ACCEPT




    def execute_callback(self, goal_handle: ServerGoalHandle):
        #Get request from goal
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        #execute the action
        self.get_logger().info("Executing the goal...")
        counter = 0
        for i in range(target_number):
            counter +=1
            self.get_logger().info(str(counter))
            time.sleep(period)

        #once done, set the goal final state
        goal_handle.succeed()

        #and send the result
        result = CountUtil.Result()
        result.reached_number = counter
        return result


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServerNode() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()