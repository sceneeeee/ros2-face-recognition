import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory # 获取功能包share目录绝对路径
import os
from cv_bridge import CvBridge
import time

class FaceDetectClient(Node):
    def __init__(self):
        super().__init__("face_detect_client")
        self.bridge = CvBridge()
        self.defalut_image_path = os.path.join(
            get_package_share_directory('demo_python_service'), "resource/test1.jpg")
        self.get_logger().info("FaceDetectClient has been started.")
        self.client = self.create_client(FaceDetector, "face_detect")
        self.image = cv2.imread(self.defalut_image_path)

    def send_request(self):
        # 判断服务是否可用
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for service to be available...")

        # 构建Request对象
        request = FaceDetector.Request() 
        request.image = self.bridge.cv2_to_imgmsg(self.image)

        # 发送请求并等待响应
        future = self.client.call_async(request) # 现在future里面没有有响应结果，要等待服务端处理完请求并返回结果
        # while future.done() == False:
        #     time.sleep(1.0) # 等待服务端处理请求的时间，避免占用过多CPU资源,但是会导致当前节点在等待服务端响应的过程中无法处理其他事件，比如接收新的请求或者执行其他任务
        
        # rclpy.spin_until_future_complete(self, future) # 让当前节点在等待服务端响应的过程中仍然能够处理其他事件，比如接收新的请求或者执行其他任务，直到future对象完成，即服务端处理完请求并返回结果
        def result_callback(result_future):
            response = result_future.result() # 获取服务端返回的结果
            self.get_logger().info(f"Number of faces detected: {response.number}, Time taken: {response.use_time:.2f} seconds") 
            self.show_response(response)

        future.add_done_callback(result_callback) # 当future对象完成时，调用result_callback函数来处理结果

        
        # future.add_done_callback(self.result_callback) # 当future对象完成时，调用result_callback函数来处理结果
        

        

    def show_response(self, response):
        # 在图像上绘制检测到的人脸位置
        for i in range(response.number):
            top = response.top[i]
            right = response.right[i]
            bottom = response.bottom[i]
            left = response.left[i]
            cv2.rectangle(self.image, (left, top), (right, bottom), (255, 0, 0), 4)

        # 显示结果图像
        cv2.imshow("Face Detection Result", self.image)
        cv2.waitKey(0) # 也会导致当前节点在等待用户按键的过程中无法处理其他事件，比如接收新的请求或者执行其他任务

def main():
    rclpy.init()
    node = FaceDetectClient()
    node.send_request()
    rclpy.spin(node)
    rclpy.shutdown()