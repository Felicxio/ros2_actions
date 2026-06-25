#!/usr/bin/env python3
import rclpy
import time
import threading
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle
from my_robot2_interfaces.action import CountUtil
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup


class CountUntilServerNode(Node): 
    def __init__(self):
        super().__init__("count_until_server") 
        self.goal_handle_:ServerGoalHandle = None
        self.goal_lock_ = threading.Lock()
        self.count_until_server_ = ActionServer(self, CountUtil, "count_until",
                                                goal_callback= self.goal_callback,
                                                cancel_callback=self.cancel_callback,
                                                execute_callback=self.execute_callback,
                                                callback_group=ReentrantCallbackGroup())
        self.get_logger().info("Action Server has been started!")


    def goal_callback(self, goal_request: CountUtil.Goal):
        self.get_logger().info("Received a goal")
        #Policy:Refuse new goal if the current goal is still active
        # with self.goal_lock_:
        #     if self.goal_handle_ is not None and self.goal_handle_.is_active:
        #         self.get_logger().info("Goal is already active...rejecting new goal...")
        #         return GoalResponse.REJECT
        
        #Validate the goal request
        if goal_request.target_number <= 0:
            self.get_logger().info("Rejecting the goal...")
            return GoalResponse.REJECT
        
        # Policy: Preempt existing goal when receiveing a new goal...
        with self.goal_lock_:
            if self.goal_handle_ is not None and self.goal_handle_.is_active:
                self.get_logger().info("Abort current goal and accept new goal...")
                self.goal_handle_.abort()

        self.get_logger().info("Goal Accepted...")
        return GoalResponse.ACCEPT


    def cancel_callback(self, goal_handle:ServerGoalHandle):
        self.get_logger().info("Received a cancel request...")
        return CancelResponse.ACCEPT #or reject

    def execute_callback(self, goal_handle: ServerGoalHandle):
        with self.goal_lock_:
            self.goal_handle_ = goal_handle
        #Get request from goal
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        #execute the action
        self.get_logger().info("Executing the goal...")
        feedback = CountUtil.Feedback()
        result = CountUtil.Result()
        counter = 0
        for i in range(target_number):
            if not goal_handle.is_active:
                result.reached_number = counter
                return result
            if goal_handle.is_cancel_requested:
                self.get_logger().info("Canceling the goal...")
                goal_handle.canceled()
                result.reached_number = counter
                return result
            counter +=1
            self.get_logger().info(str(counter))
            feedback.current_number = counter
            goal_handle.publish_feedback(feedback)
            time.sleep(period)

        #once done, set the goal final state
        goal_handle.succeed()

        #and send the result
    
        result.reached_number = counter
        return result


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServerNode() 
    rclpy.spin(node, MultiThreadedExecutor())
    rclpy.shutdown()


if __name__ == "__main__":
    main()