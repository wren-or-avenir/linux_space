import rclpy
from rclpy.node import Node

# 如果后续需要订阅视觉节点的消息，通常需要导入：
# from gimbal_interfaces.msg import TargetInfo

class PaperControlNode(Node): # 1. 修改类名，建议与文件名对应
    def __init__(self):
        # 2. 修改节点注册名，确保在 ros2 node list 中唯一
        super().__init__('paper_control_node') 
        
        self.get_logger().info('=== Paper Control Node Started! ===')

    # 这里是你未来编写 PID 控制逻辑、订阅话题和驱动云台的地方

def main(args=None):
    rclpy.init(args=args)
    node = PaperControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()