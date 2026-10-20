import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression

from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

from launch_ros.actions import Node


from launch import Action
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node as rclpyNode
import threading
import time
from typing import List



def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='shesnar' #<--- CHANGE ME
   
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )


    default_world = os.path.join(
            get_package_share_directory(package_name),
            'worlds',
            'complete_world.world'
            )    
       
    world = LaunchConfiguration('world')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='World to load'
        )

    # Include the Gazebo launch file, provided by the ros_gz_sim package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
                    # launch_arguments={'gz_args': ['-r --render-engine ogre -v4 ', world], 'on_exit_shutdown': 'true'}.items()
                    launch_arguments={'gz_args': ['-r -v4 ', world], 'on_exit_shutdown': 'true'}.items()
             )

    # Run the spawner node from the ros_gz_sim package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-topic', 'robot_description',
                                #    '-name', 'my_bot', "-z", '0.111' , "-y", '-1.1', "-x", '0.75' ],
                                            '-name', 'my_bot', "-z", '0.111' , "-y", '-0.3', "-x", '1.0' ],
                        output='screen')

    bridge_params = os.path.join(get_package_share_directory(package_name),'config','gz_bridge.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ]        
    )

    move_control = Node(
        package="cpp_omnidrive_gazebo_controller",
        executable="omni_gz_con",
        arguments=[
 
        ],
        parameters = [{'use_sim_time': True}]
    )



    # Launch them all!
    return LaunchDescription([     
        world_arg,   
        rsp,        
        gazebo,
        ros_gz_bridge,
        spawn_entity,
        move_control
    ])