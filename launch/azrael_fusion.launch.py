from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # azrael_fusion = get_package_share_directory('azrael_fusion')

    target_frame = DeclareLaunchArgument(
        'target_frame',
        default_value='azrael/base_link',
        description='IMU target frame')
    # Here add also parameters for imu bias remover

    imu_transformer_node = Node(
        package='imu_transformer',
        executable='imu_transformer_node',
        name='imu_transformer_node',
        output='screen',
        parameters=[{
         'target_frame': LaunchConfiguration('target_frame')
        }],
        remappings=[("imu_in", "/camera/camera/imu"),
                    ("imu_out", "/azrael_fusion/imu")], # here maybe become /azrael_fusion/imu_biased
        )
      ## imu biase remover
      # IN: /azrael_fusion/imu_biased
      # out  /azrael_fusion/imu
      # replace here to put imu_bias_remover
      # imu_bias_remover = Node(
      #   package='imu_transformer',
      #   executable='imu_transformer_node',
      #   name='imu_transformer_node',
      #   output='screen',
      #   parameters=[{
      #    'target_frame': LaunchConfiguration('target_frame')
      #   }],
      #   remappings=[("imu_in", "/camera/camera/imu"),
      #               ("imu_out", "/azrael_fusion/imu")],
      #   )

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(target_frame)
    ld.add_action(imu_transformer_node)
    # Here add both parameters and node for imu bias remover

    return ld