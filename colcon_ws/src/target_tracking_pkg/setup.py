from setuptools import setup
from glob import glob
import os

package_name = 'target_tracking_pkg'

setup(
    name=package_name,
    version='0.1.0',
    # 确保这些路径下都有 __init__.py 文件
    packages=[
        package_name, 
        package_name + '.driver',
        package_name + '.scripts',
    ],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 安装 launch 和 config 文件夹
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='avenir',
    maintainer_email='your_email@example.com',
    description='Target tracking system for competition',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 格式：'可执行程序名 = 包名.文件名:入口函数'
            'paper_tracker_node = target_tracking_pkg.paper_tracker_node:main',
            'paper_controller_node = target_tracking_pkg.paper_control_node:main',
            'calibrate_color = target_tracking_pkg.scripts.calibrate_color:main',
        ],
    },
)