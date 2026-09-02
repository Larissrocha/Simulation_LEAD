import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_share = get_package_share_directory('sim_environment')
    world_path = os.path.join(pkg_share, 'worlds', 'default.sdf')

    # Executável nativo do Gazebo abrindo o mundo
    gazebo_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_path],
        output='screen'
    )

    return LaunchDescription([
        gazebo_sim
    ])
