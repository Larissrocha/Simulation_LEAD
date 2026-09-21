import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('sim_environment')

    drone_name_arg = DeclareLaunchArgument(
        'drone_name',
        default_value='x500_0',
        description='Nome da entidade no Gazebo'
    )
    x_arg = DeclareLaunchArgument('x', default_value='0.0', description='Posicao X')
    y_arg = DeclareLaunchArgument('y', default_value='0.0', description='Posicao Y')
    z_arg = DeclareLaunchArgument('z', default_value='0.22', description='Posicao Z')

    drone_name = LaunchConfiguration('drone_name')
    pos_x = LaunchConfiguration('x')
    pos_y = LaunchConfiguration('y')
    pos_z = LaunchConfiguration('z')

    drone_sdf_path = os.path.join(pkg_share, 'models', 'x500_px4', 'x500_px4.sdf')

    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'default',
            '-name', drone_name,
            '-file', drone_sdf_path,
            '-x', pos_x,
            '-y', pos_y,
            '-z', pos_z,
            '--timeout', '15.0'
        ],
        output='screen'
    )
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/x500_0/pose@geometry_msgs/msg/Pose[gz.msgs.Pose',
            '/x500_0/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/x500_0/enable@std_msgs/msg/Bool]gz.msgs.Boolean',
        ],
        output='screen'
    )
    return LaunchDescription([
        drone_name_arg,
        x_arg,
        y_arg,
        z_arg,
        spawn_node,
        bridge_node
    ])