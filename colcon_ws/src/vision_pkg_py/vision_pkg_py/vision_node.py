import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from gimbal_interfaces.msg import TargetInfo 
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        
        # 1. 声明参数
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('b_min', 0)
        self.declare_parameter('b_max', 50)
        self.declare_parameter('g_min', 0)
        self.declare_parameter('g_max', 50)
        self.declare_parameter('r_min', 150)
        self.declare_parameter('r_max', 255)
        self.declare_parameter('min_area_ratio', 5.0)
        self.declare_parameter('debug', True)

        self.bridge = CvBridge()
        image_topic = self.get_parameter('image_topic').value
        
        # 发布者
        self.target_pub = self.create_publisher(TargetInfo, '/target_info', 10)
        
        self.image_sub = self.create_subscription(
            Image, 
            image_topic, 
            self.image_callback, 
            10
        )
        
        self.get_logger().info(f"=== Vision Node Started! Targeting {image_topic} ===")

    def image_callback(self, msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Image convert error: {e}")
            return

        h, w = cv_img.shape[:2]
        total_pixels = h * w

        # 获取参数
        lower = np.array([
            self.get_parameter('b_min').value,
            self.get_parameter('g_min').value,
            self.get_parameter('r_min').value
        ])
        upper = np.array([
            self.get_parameter('b_max').value,
            self.get_parameter('g_max').value,
            self.get_parameter('r_max').value
        ])
        min_ratio = self.get_parameter('min_area_ratio').value
        is_debug = self.get_parameter('debug').value

        # 颜色过滤与轮廓提取
        mask = cv2.inRange(cv_img, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        info_msg = TargetInfo()

        if contours:
            max_cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_cnt)
            # 这里的 area_ratio 是为了和参数 min_ratio 匹配
            area_ratio = (area / total_pixels * 10000)

            if area_ratio > min_ratio:
                # 获取最小外接矩形
                rect = cv2.minAreaRect(max_cnt)
                cx, cy = rect[0]
                rw, rh = rect[1] # 目标的像素宽高
                
                # 符合 TargetInfo.msg 定义的字段
                # 1. 坐标归一化 (-1.0 ~ 1.0)
                info_msg.x = float((cx - (w / 2)) / (w / 2))
                info_msg.y = float((cy - (h / 2)) / (h / 2))
                
                # 2. 宽高归一化 (0.0 ~ 1.0)
                info_msg.width = float(rw / w)
                info_msg.height = float(rh / h)
                
                # 3. 置信度 (使用面积占比计算，确保 > 0.1)
                info_msg.confidence = float(min(1.0, area_ratio / 50.0))
                if info_msg.confidence < 0.1: info_msg.confidence = 0.11
                
                # 4. 目标类型 (0=色块)
                info_msg.target_type = 0 

                if is_debug:
                    box = np.intp(cv2.boxPoints(rect))
                    cv2.drawContours(cv_img, [box], 0, (0, 255, 0), 2)
                    cv2.circle(cv_img, (int(cx), int(cy)), 5, (0, 0, 255), -1)
            else:
                self.set_lost_target(info_msg)
        else:
            self.set_lost_target(info_msg)

        # 发布数据
        self.target_pub.publish(info_msg)

        if is_debug:
            cv2.imshow("Vision Debug View", cv_img)
            cv2.waitKey(1)

    def set_lost_target(self, msg):
        """当丢失目标时，重置消息字段"""
        msg.x = 0.0
        msg.y = 0.0
        msg.width = 0.0
        msg.height = 0.0
        msg.confidence = 0.0  # 符合你定义的 0.0=丢失
        msg.target_type = 0

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()
