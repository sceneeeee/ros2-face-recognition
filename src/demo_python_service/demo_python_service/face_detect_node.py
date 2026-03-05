import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory # 获取功能包share目录绝对路径
import os
from cv_bridge import CvBridge
import time

class FaceDetectNode(Node):
    def __init__(self):
        super().__init__("face_detect_node")
        self.service_ = self.create_service(FaceDetector, "face_detect", self.face_detect_callback)
        self.bridge = CvBridge()
        self.number_of_times_to_upsample = 1
        self.model = "hog"
        self.defalut_image_path = os.path.join(
            get_package_share_directory('demo_python_service'), "resource/default.jpg")
        self.get_logger().info("FaceDetectNode has been started.")


    def face_detect_callback(self, request, response):
        if request.image.data:
            cv_image = self.bridge.imgmsg_to_cv2(request.image)
        else:
            cv_image = cv2.imread(self.defalut_image_path)
            self.get_logger().warn(
                "No image data received in request, using default image for face detection.")

        # cv_image已经是opencv格式的图像了
        # 可以直接使用face_recognition库进行人脸检测
        start_time = time.time()
        self.get_logger().info("Starting face detection...")

        # 检测人脸位置
        # 返回值是一个列表，每个元素是一个元组，包含人脸的四个坐标（top, right, bottom, left）
        face_locations = face_recognition.face_locations(cv_image,
            number_of_times_to_upsample=self.number_of_times_to_upsample, model=self.model)
        response.use_time = time.time() - start_time
        response.number = len(face_locations)

        for (top, right, bottom, left) in face_locations:
            response.top.append(top)
            response.right.append(right)
            response.bottom.append(bottom)
            response.left.append(left)

        return response # 必须返回response对象，否则服务调用会失败
    

def main():
    rclpy.init()
    node = FaceDetectNode()
    rclpy.spin(node)
    rclpy.shutdown()