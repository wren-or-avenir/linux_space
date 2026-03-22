from setuptools import setup
from glob import glob
import os

package_name = 'vision_pkg_py'

setup(
    name=package_name,
    version='0.1.0',
    packages=[
        package_name, 
        package_name + '.driver',
        package_name + '.scripts',  # ✅ 新增
    ],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Your Name',
    author_email='your_email@example.com',
    description='Gimbal tracking system with ROS2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_node = vision_pkg_py.vision_node:main',
            'control_node = vision_pkg_py.control_node:main',
            'calibrate_color = vision_pkg_py.scripts.calibrate_color:main',
        ],
    },
)