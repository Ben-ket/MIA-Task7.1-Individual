#!/usr/bin/env python3
import os
import select
import sys
import termios
import threading
import tty
from geometry_msgs.msg import Twist, TwistStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from turtlesim.msg import Color


class TurtleController(Node):

    def __init__(self):
        super().__init__('turtle_controller')

        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('color_sensor_topic', '/turtle1/color_sensor')
        self.declare_parameter('dominant_color_topic', '/dominant_color')
        self.declare_parameter('use_stamped_vel', False)






        self.cmd_vel_topic = (
            self.get_parameter('cmd_vel_topic')
            .get_parameter_value()
            .string_value
        )
        self.color_sensor_topic = (
            self.get_parameter('color_sensor_topic')
            .get_parameter_value()
            .string_value
        )
        self.dominant_color_topic = (
            self.get_parameter('dominant_color_topic')
            .get_parameter_value()
            .string_value
        )
        self.use_stamped_vel = (
            self.get_parameter('use_stamped_vel')
            .get_parameter_value()
            .bool_value
        )




        if self.use_stamped_vel:
            self.vel_pub = self.create_publisher(
                TwistStamped, self.cmd_vel_topic, 10
            )
        else:
            self.vel_pub = self.create_publisher(Twist, self.cmd_vel_topic, 10)

        self.color_pub = self.create_publisher(
            String, self.dominant_color_topic, 10
        )
        self.color_sub = self.create_subscription(
            Color, self.color_sensor_topic, self.color_callback, 10
        )

        self.last_dominant_color = None




        self.get_logger().info(f'publishing to topic: {self.cmd_vel_topic}')
        self.get_logger().info(
            'Keep terminal focused and press WASD to drive.'
        )

        self.running = True
        self.key_thread = threading.Thread(target=self.keyboard_loop)
        self.key_thread.daemon = True
        self.key_thread.start()

    def color_callback(self, msg: Color):
        r, g, b = msg.r, msg.g, msg.b
        if r >= g and r >= b:
            major = 'RED'
        elif g >= r and g >= b:
            major = 'GREEN'
        else:
            major = 'BLUE'




        if major != self.last_dominant_color:
            self.last_dominant_color = major
            self.get_logger().info(f'Color Changed -> {major}')
            color_msg = String()
            color_msg.data = major
            self.color_pub.publish(color_msg)

    def publish_velocity(self, linear_x: float, angular_z: float):
        if self.use_stamped_vel:
            stamped_msg = TwistStamped()
            stamped_msg.header.stamp = self.get_clock().now().to_msg()
            stamped_msg.header.frame_id = 'base_link'
            stamped_msg.twist.linear.x = linear_x
            stamped_msg.twist.angular.z = angular_z
            self.vel_pub.publish(stamped_msg)
        else:
            msg = Twist()
            msg.linear.x = linear_x
            msg.angular.z = angular_z

            self.vel_pub.publish(msg)

    def keyboard_loop(self):
        try:
            tty_file = open('/dev/tty', 'r')
            fd = tty_file.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while rclpy.ok() and self.running:
                    if select.select([tty_file], [], [], 0.1)[0]:
                        key = tty_file.read(1).lower()
                        lin, ang = 0.0, 0.0
                        if key == 'w':
                            lin = 2.0
                        elif key == 's':
                            lin = -2.0
                        elif key == 'a':
                            ang = 1.0
                        elif key == 'd':
                            ang = -1.0

                        if lin != 0.0 or ang != 0.0:
                            self.publish_velocity(lin, ang)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                tty_file.close()
        except Exception as e:
            self.get_logger().error(f'Keyboard reader error: {e}')


def main():
    rclpy.init()
    node = TurtleController()
    rclpy.spin(node)
    node.running = False
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()