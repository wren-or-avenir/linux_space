import cv2
import numpy as np
import sys

def nothing(x):
    pass

def main(args=None):
    # 初始化摄像头
    cap = cv2.VideoCapture(4)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        sys.exit(1)

    # 创建窗口
    cv2.namedWindow('BGR Calibration')
    
    # 创建 Trackbar
    # Blue
    cv2.createTrackbar('B Min', 'BGR Calibration', 0, 255, nothing)
    cv2.createTrackbar('B Max', 'BGR Calibration', 255, 255, nothing)
    # Green
    cv2.createTrackbar('G Min', 'BGR Calibration', 0, 255, nothing)
    cv2.createTrackbar('G Max', 'BGR Calibration', 255, 255, nothing)
    # Red
    cv2.createTrackbar('R Min', 'BGR Calibration', 0, 255, nothing)
    cv2.createTrackbar('R Max', 'BGR Calibration', 255, 255, nothing)

    print("=== BGR 颜色校准工具启动 ===")
    print("调整滑动条直到只选中目标色块")
    print("按 's' 保存参数到终端，按 'q' 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        bgr = frame 

        # 获取当前滑动条位置
        b_min = cv2.getTrackbarPos('B Min', 'BGR Calibration')
        b_max = cv2.getTrackbarPos('B Max', 'BGR Calibration')
        g_min = cv2.getTrackbarPos('G Min', 'BGR Calibration')
        g_max = cv2.getTrackbarPos('G Max', 'BGR Calibration')
        r_min = cv2.getTrackbarPos('R Min', 'BGR Calibration')
        r_max = cv2.getTrackbarPos('R Max', 'BGR Calibration')

        # 创建掩膜 
        lower_bound = np.array([b_min, g_min, r_min])
        upper_bound = np.array([b_max, g_max, r_max])
        mask = cv2.inRange(bgr, lower_bound, upper_bound)

        # 显示原图和掩膜
        cv2.imshow('Original', frame)
        cv2.imshow('Mask', mask)

        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            print("\n=== 保存参数 ===")
            print(f"b_min: {b_min}, b_max: {b_max}")
            print(f"g_min: {g_min}, g_max: {g_max}")
            print(f"r_min: {r_min}, r_max: {r_max}")
            print("请将上述值复制到 config/params.yaml 中\n")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()