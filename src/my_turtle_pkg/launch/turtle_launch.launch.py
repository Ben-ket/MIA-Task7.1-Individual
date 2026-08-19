from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'cmd_vel_topic',
                default_value='/turtle1/cmd_vel',
                description='Command velocity topic name',
            ),
            DeclareLaunchArgument(
                'color_sensor_topic',
                default_value='/turtle1/color_sensor',
                description='Color sensor topic name',
            ),
            DeclareLaunchArgument(
                'use_stamped_vel',
                default_value='false',
                description='Use TwistStamped instead of Twist',
            ),
            Node(
                package='turtlesim',
                executable='turtlesim_node',
                name='turtlesim',
                output='screen',
            ),
            Node(
                package='my_turtle_pkg',
                executable='turtle_controller',
                name='turtle_controller',
                output='screen',
                emulate_tty=True,
                parameters=[
                    {
                        'cmd_vel_topic': LaunchConfiguration('cmd_vel_topic'),
                        'color_sensor_topic': LaunchConfiguration(
                            'color_sensor_topic'
                        ),
                        'use_stamped_vel': LaunchConfiguration(
                            'use_stamped_vel'
                        ),
                    }
                ],
            ),
        ]
    )