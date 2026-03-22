from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. 相机节点：必须把分辨率和设备号传给它！
        Node(
            package='usb_camera', # 确认你的驱动包名
            executable='usb_camera_node',
            name='usb_camera',
            parameters=[{
                'video_device': '/dev/video4', # 强制和自瞄包一样用 video4
                'image_width': 640,            # 显式给驱动下指令
                'image_height': 480,
                'pixel_format': 'mjpeg'
            }],
            output='screen'
        ),

        # 2. 识别节点：只需接收图像并处理
        Node(
            package='target_tracking_pkg',
            executable='paper_tracker',
            name='paper_tracker_node',
            parameters=[{
                'debug': True,
                'image_topic': '/image_raw'
            }],
            output='screen'
        ),

        # 3. 控制节点
        Node(
            package='target_tracking_pkg',
            executable='paper_controller',
            name='paper_control_node',
            output='screen'
        )
    ])