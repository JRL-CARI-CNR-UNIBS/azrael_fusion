from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # azrael_fusion = get_package_share_directory('azrael_fusion')

    target_frame = DeclareLaunchArgument(
        'target_frame',
        default_value='imu_enu',
        description='IMU target frame')
    # Here add also parameters for imu bias remover

    static_transform_imu_enu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_imu_enu',
        output='screen',
        arguments=[
            '--frame-id', 'azrael/base_link', #'azrael/base_link' in azrael, 'base_footprint' in gazebo
            '--child-frame-id', 'imu_enu',
            '--x', '-0.0198132',
            '--y', '0.252878',
            '--z', '0.0375784',
            '--qx', '0.0',
            '--qy', '0.0',
            '--qz', '0.0',
            '--qw', '1.0'
            #'--roll', '0.0',
            #'--pitch', '0.0',
            #'--yaw', '0.0',
        ]
    )

    imu_transformer_node = Node(
        package='imu_transformer',
        executable='imu_transformer_node',
        name='imu_transformer_node',
        output='screen',
        parameters=[{
         'target_frame': LaunchConfiguration('target_frame'),
         'use_sim_time': True # per forzare time rosbag
        }],
        remappings=[("imu_in", "/camera/camera/imu"), #"/camera/camera/imu" in azrael, "/sensor/imu/data" in gazebo
                    ("imu_out", "/imu_enu_biased")], # here maybe become /azrael_fusion/imu_enu_biased
        )

      
      # replace here to put imu_bias_remover
    imu_bias_remover_node = Node(
        package='azrael_fusion',
        executable='imu_bias_remover.py',
        name='imu_bias_remover_node',
        output='screen',
        parameters=[
            {
                'use_sim_time': True # per forzare time rosbag
            }
        ],
        remappings=[("imu_in", "/imu_enu_biased"), # in: /azrael_fusion/imu_biased
                    ("imu_out", "/imu_enu")], # out  /azrael_fusion/imu
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(target_frame)
    ld.add_action(static_transform_imu_enu)
    ld.add_action(imu_transformer_node)
    ld.add_action(imu_bias_remover_node)
    # Here add both parameters and node for imu bias remover

    return ld