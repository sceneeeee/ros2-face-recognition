# ros2-face-recognition

这是一个基于 **ROS2 Python Service** 的人脸检测项目，使用 `face_recognition` 和 `OpenCV` 完成人脸位置检测，并通过自定义服务接口返回检测结果。

项目主要包含以下内容：

- 一个独立的人脸检测学习脚本 `learn_face_detect.py`
- 一个服务端节点 `face_detect_node.py`
- 一个客户端节点 `face_detect_client_node.py`

该项目适合用于学习以下内容：

- ROS2 Python 节点开发
- ROS2 Service 通信机制
- OpenCV 图像读取与显示
- `cv_bridge` 在 ROS 图像消息与 OpenCV 图像之间的转换
- `face_recognition` 的基础使用

---

# 项目功能

本项目实现了一个简单的人脸检测流程：

1. 客户端读取本地图片
2. 客户端将图片转换为 ROS 图像消息并发送给服务端
3. 服务端接收图片后进行人脸检测
4. 服务端将检测到的人脸数量、检测耗时、以及每张人脸的位置坐标返回给客户端
5. 客户端根据返回结果在图像上绘制矩形框，并显示检测结果

---

# 项目结构

```bash
CHAPT4/
├── demo_python_service/
│   ├── demo_python_service/
│   │   ├── face_detect_client_node.py
│   │   ├── face_detect_node.py
│   │   └── learn_face_detect.py
│   ├── resource/
│   │   ├── default.jpg
│   │   └── test1.jpg
│   ├── package.xml
│   ├── setup.py
│   └── ...
├── chapt4_interfaces/
│   ├── srv/
│   │   └── FaceDetector.srv
│   ├── package.xml
│   ├── CMakeLists.txt
│   └── ...
└── README.md
````

---

# 核心文件说明

## 1. `learn_face_detect.py`

这是一个最基础的人脸检测学习脚本，用来直接读取图片并检测人脸位置，不涉及 ROS2 通信。

### 功能

* 从功能包的 `resource/default.jpg` 读取图片
* 使用 `face_recognition.face_locations()` 检测人脸
* 使用 OpenCV 在图像上绘制人脸框
* 弹窗显示检测结果

### 作用

这个脚本适合用来先验证：

* `face_recognition` 是否安装成功
* OpenCV 是否能正常读取和显示图像
* 人脸检测逻辑本身是否正确

---

## 2. `face_detect_node.py`

这是服务端节点，节点名为：

```python
face_detect_node
```

### 功能

* 创建名为 `face_detect` 的服务
* 接收客户端发送的图像消息
* 将 ROS 图像消息转换为 OpenCV 图像
* 使用 `face_recognition` 完成人脸检测
* 返回检测结果，包括：

  * 人脸数量 `number`
  * 检测耗时 `use_time`
  * 每张人脸的位置：

    * `top`
    * `right`
    * `bottom`
    * `left`

### 逻辑说明

如果客户端请求中没有携带图像数据，则服务端会自动使用默认图片：

```python
resource/default.jpg
```

然后进行人脸检测。

### 检测参数

当前服务端使用如下参数：

```python
self.number_of_times_to_upsample = 1
self.model = "hog"
```

说明：

* `number_of_times_to_upsample=1`：对图像放大一次后再检测，有助于识别较小的人脸，但会增加耗时
* `model="hog"`：使用 HOG 模型进行检测，速度较快，适合 CPU 环境

---

## 3. `face_detect_client_node.py`

这是客户端节点，节点名为：

```python
face_detect_client
```

### 功能

* 创建到 `face_detect` 服务的客户端
* 读取本地测试图片 `resource/test1.jpg`
* 将 OpenCV 图像转换为 ROS 图像消息
* 异步调用服务
* 在收到响应后输出检测结果
* 根据返回的人脸坐标在原图中绘制矩形框
* 显示最终检测结果

### 返回结果显示内容

客户端会输出类似信息：

```bash
Number of faces detected: 1, Time taken: 0.15 seconds
```

随后弹出检测结果窗口。

### 异步调用特点

客户端使用的是：

```python
future = self.client.call_async(request)
future.add_done_callback(result_callback)
```

这是一种异步服务调用方式，能够避免直接阻塞在请求阶段，更符合 ROS2 的事件驱动机制。

---

# 自定义服务接口

项目使用了自定义服务：

```bash
chapt4_interfaces/srv/FaceDetector.srv
```

根据你的代码逻辑，这个服务大概率包含以下两部分内容：

## Request

请求部分：

* 一张图像 `image`

## Response

响应部分：

* `number`：检测到的人脸数量
* `use_time`：检测耗时
* `top[]`
* `right[]`
* `bottom[]`
* `left[]`

这些数组分别存储每张人脸框的位置坐标。

---

# 运行原理

整个系统的数据流如下：

```text
本地图片 -> 客户端读取 -> 转换为 ROS 图像消息 -> 调用 face_detect 服务
-> 服务端接收请求 -> 转换为 OpenCV 图像 -> face_recognition 检测人脸
-> 返回人脸数量、耗时、坐标 -> 客户端接收响应 -> OpenCV 绘制方框 -> 显示图像
```

---

# 环境依赖

运行本项目通常需要以下依赖：

## ROS2 相关

* `rclpy`
* `cv_bridge`
* `ament_index_python`

## Python 图像处理与人脸识别

* `opencv-python`
* `face_recognition`

## 其他

* 自定义接口包 `chapt4_interfaces`

---

# 安装与编译

在 ROS2 工作空间下编译项目。

## 1. 进入工作空间

```bash
cd ~/your_ros2_ws
```

## 2. 编译功能包

```bash
colcon build
```

如果只想编译相关包，也可以使用：

```bash
colcon build --packages-select chapt4_interfaces demo_python_service
```

## 3. source 环境

```bash
source install/setup.bash
```

---

# 运行方法

## 1. 启动服务端

打开一个终端：

```bash
source install/setup.bash
ros2 run demo_python_service face_detect_node
```

## 2. 启动客户端

再打开一个终端：

```bash
source install/setup.bash
ros2 run demo_python_service face_detect_client_node
```

---

# 单独测试学习脚本

如果你想先不跑 ROS2 通信，只测试人脸检测功能，可以运行：

```bash
source install/setup.bash
ros2 run demo_python_service learn_face_detect
```

这个脚本会直接读取默认图片并显示检测结果。

---

# 代码设计说明

## 服务端设计

服务端负责真正的人脸检测任务，主要优点：

* 将检测逻辑集中在服务端，结构清晰
* 客户端只负责发送请求和显示结果
* 便于以后扩展成其他客户端调用同一个检测服务

## 客户端设计

客户端主要负责：

* 准备输入图像
* 请求服务
* 接收结果
* 可视化检测结果

这样实现了输入、处理、输出三个环节的分离。

---

# 结果示例

运行成功后，客户端会：

1. 在终端输出检测到的人脸数量和耗时
2. 弹出一个 OpenCV 窗口，显示带有人脸框的图片

例如：

```bash
[INFO] [face_detect_client]: Number of faces detected: 1, Time taken: 0.12 seconds
```

---

# 已知特点与注意事项

## 1. `cv2.waitKey(0)` 会阻塞程序

在客户端的 `show_response()` 中：

```python
cv2.waitKey(0)
```

这会让程序一直等待键盘输入，窗口不关闭时节点也不会继续退出。

## 2. 客户端使用异步调用

虽然请求发送使用了异步方式，但图像显示部分依然可能因为 OpenCV 窗口阻塞而影响程序退出。

## 3. 图片路径依赖功能包资源目录

当前代码中图片路径通过：

```python
get_package_share_directory('demo_python_service')
```

获取，因此运行前需要确保图片资源已经正确安装到功能包中。

## 4. `face_recognition` 依赖环境配置

如果系统中没有正确安装 `dlib` 或 `face_recognition`，程序将无法正常运行。

---

# 可改进方向

这个项目目前已经完成了基础的人脸检测服务通信，后续可以继续扩展：

## 1. 支持实时摄像头图像

当前是读取本地图片，后续可以改为：

* 摄像头采集
* 视频流检测
* ROS2 图像话题订阅

## 2. 支持话题通信

目前使用的是 Service，更适合“请求-响应”模式。
如果想做连续检测，可以改为 Topic 订阅/发布模式。

## 3. 支持更多检测模型

当前使用的是：

```python
model="hog"
```

后续可以尝试：

* `cnn` 模型（更高精度，但更慢）
* GPU 加速

## 4. 增加图像保存功能

客户端在显示结果后，还可以把绘制完的人脸框图片保存到本地。

## 5. 增加异常处理

例如：

* 图片读取失败
* 服务不可用
* 返回结果为空
* OpenCV 窗口异常关闭

---

# 学习收获

通过这个项目，可以练习并掌握以下知识点：

* ROS2 Python 节点编写
* ROS2 Service 服务端与客户端通信
* 自定义 `.srv` 接口设计
* OpenCV 图像处理
* `cv_bridge` 图像格式转换
* `face_recognition` 人脸检测基础流程
* 异步调用与回调处理方式

---

# 总结

这是一个基于 ROS2 的基础人脸检测项目。
项目通过 **客户端发送图片 + 服务端检测 + 客户端显示结果** 的方式，实现了完整的人脸检测服务流程。

它适合作为以下方向的入门项目：

* ROS2 服务通信练习
* Python 机器人视觉项目
* OpenCV 与 ROS2 结合
* 智能感知类课程作业或实验项目

---
