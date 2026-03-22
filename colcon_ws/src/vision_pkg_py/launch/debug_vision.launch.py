from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # ✅ 正确方式：使用 get_package_share_directory 获取包路径
    pkg_share = get_package_share_directory('vision_pkg_py')
    
    # ✅ 正确方式：使用 os.path.join 构建文件路径
    params_file = os.path.join(pkg_share, 'config', 'params.yaml')
    
    return LaunchDescription([
        Node(
            package='vision_pkg_py',
            executable='vision_node',
            name='vision_node',
            parameters=[params_file],  # ✅ 传递参数文件路径
            output='screen'
        )
    ])