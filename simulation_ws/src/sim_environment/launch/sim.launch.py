import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable,TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    pkg_share = get_package_share_directory('sim_environment')

    world_path = os.path.join(pkg_share, 'worlds', 'default.sdf')
    spawn_launch_path = os.path.join(pkg_share, 'launch', 'spawn_drone.launch.py')

    # Registra o caminho dos modelos para o Gazebo encontrar grass_patch e x500_px4
    models_path = os.path.join(
        pkg_share,
        'models'
    )
    set_gz_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=f"{models_path}:{os.environ.get('GZ_SIM_RESOURCE_PATH', '')}"
    )
    # Executável nativo do Gazebo abrindo o mundo
    gazebo_sim = ExecuteProcess(
        cmd=['gz', 'sim', world_path],
        output='screen'
    )
    # Chama o launch auxiliar de spawn
    spawn_drone = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(spawn_launch_path),
        launch_arguments={
            'drone_name': 'x500_0',
            'x': '0.0',
            'y': '0.0',
            'z': '0.22'
        }.items()
    )

    return LaunchDescription([
        set_gz_path,
        gazebo_sim,
        spawn_drone,
        #delay_spawn
    ])
