import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from gimbal_interfaces.msg import TargetInfo 
from cv_bridge import CvBridge
import cv2
import numpy as np

class PaperTrackerNode(Node):
    def __init__(self):
        super().__init__('paper_tracker_node')
        
        # 1. 声明参数
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('b_min', 180)
        self.declare_parameter('b_max', 255)
        self.declare_parameter('g_min', 180)
        self.declare_parameter('g_max', 255)
        self.declare_parameter('r_min', 180)
        self.declare_parameter('r_max', 255)
        # 将默认面积比例调低，增强远距离识别能力
        self.declare_parameter('min_area_ratio', 1.0) 
        self.declare_parameter('debug', True)

        self.bridge = CvBridge()
        image_topic = self.get_parameter('image_topic').value
        
        # 发布者与订阅者
        self.target_pub = self.create_publisher(TargetInfo, '/target_info', 10)
        self.image_sub = self.create_subscription(Image, image_topic, self.image_callback, 10)
        
        self.get_logger().info(f"=== White Rectangle Tracker (Precise Mode) Started! ===")

    def get_intersection(self, p1, p2, p3, p4):
        """计算两直线 (p1-p3) 和 (p2-p4) 的精确几何交点"""
        x1, y1 = p1; x2, y2 = p3
        x3, y3 = p2; x4, y4 = p4
        
        # 直线方程交点公式：L1(p1,p3) 和 L2(p2,p4)
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if abs(denom) < 1e-6:  # 平行或重合处理
            return int((x1 + x2 + x3 + x4) / 4), int((y1 + y2 + y3 + y4) / 4)
            
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        cx = int(x1 + ua * (x2 - x1))
        cy = int(y1 + ua * (y2 - y1))
        return cx, cy

    def image_callback(self, msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Image error: {e}")
            return

        h, w = cv_img.shape[:2]
        total_pixels = h * w

        # 获取动态参数
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

        # 颜色空间掩膜
        mask = cv2.inRange(cv_img, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        info_msg = TargetInfo()
        target_found = False

        if contours:
            # 找到面积最大的轮廓
            max_cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_cnt)
            area_ratio = (area / total_pixels * 10000)

            if area_ratio > min_ratio:
                # 多边形拟合，0.04 是为了在远近变换时更鲁棒
                peri = cv2.arcLength(max_cnt, True)
                approx = cv2.approxPolyDP(max_cnt, 0.04 * peri, True)

                # 只有识别到四边形才进行处理
                if len(approx) == 4:
                    target_found = True
                    pts = approx.reshape(4, 2)
                    
                    # 顶点排序：左上(0), 右上(1), 右下(2), 左下(3)
                    rect = np.zeros((4, 2), dtype="float32")
                    s = pts.sum(axis=1)
                    rect[0] = pts[np.argmin(s)]
                    rect[2] = pts[np.argmax(s)]
                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]
                    rect[3] = pts[np.argmax(diff)]
                    
                    p1, p2, p3, p4 = rect.astype(int)

                    # --- 调用精确交点函数 ---
                    cx, cy = self.get_intersection(p1, p2, p3, p4)

                    # 计算外接矩形宽高（用于发布信息）
                    x_all, y_all = pts[:,0], pts[:,1]
                    rw = np.max(x_all) - np.min(x_all)
                    rh = np.max(y_all) - np.min(y_all)

                    # --- 坐标归一化发布逻辑 ---
                    info_msg.x = float((cx - (w / 2)) / (w / 2))
                    info_msg.y = float((cy - (h / 2)) / (h / 2))
                    info_msg.width = float(rw / w)
                    info_msg.height = float(rh / h)
                    info_msg.confidence = float(min(1.0, area_ratio / 50.0))
                    info_msg.target_type = 0

                    if is_debug:
                        # 1. 绘制绿色四边形边框
                        cv2.drawContours(cv_img, [approx], 0, (0, 255, 0), 2)
                        # 2. 绘制蓝色对角线 (p1-p3, p2-p4)
                        cv2.line(cv_img, tuple(p1), tuple(p3), (255, 0, 0), 1)
                        cv2.line(cv_img, tuple(p2), tuple(p4), (255, 0, 0), 1)
                        # 3. 绘制绿色几何交点圆心
                        cv2.circle(cv_img, (cx, cy), 6, (0, 255, 0), -1)

        if not target_found:
            self.set_lost_target(info_msg)

        self.target_pub.publish(info_msg)

        if is_debug:
            cv2.imshow("White Target Debug", cv_img)
            cv2.waitKey(1)

    def set_lost_target(self, msg):
        msg.x, msg.y, msg.width, msg.height, msg.confidence = 0.0, 0.0, 0.0, 0.0, 0.0
        msg.target_type = 0

def main(args=None):
    rclpy.init(args=args)
    node = PaperTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()