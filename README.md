# px4_t265_drone


# 无人机调试笔记

## 环境配置
基于Ubuntu20.04 x86架构工控机
t265相机

### ROS Noetic


### mavros

### QGC
QGroundControl

### Realsense t265


```bash
dpkg -l | grep "realsense" | cut -d " " -f 3 | xargs sudo dpkg --purge\n

sudo apt-get update
sudo apt-get install librealsense2-udev-rules:amd64=2.53.1-0~realsense0.8250
sudo apt-get install librealsense2-dkms=1.3.17-0ubuntu1
sudo apt-get install librealsense2=2.53.1-0~realsense0.8250
sudo apt-get install librealsense2-gl=2.53.1-0~realsense0.8250
sudo apt-get install librealsense2-net=2.53.1-0~realsense0.8250
sudo apt-get install librealsense2-utils=2.53.1-0~realsense0.8250
sudo apt-get install librealsense2-dev=2.53.1-0~realsense0.8250
sudo apt-get install librealsense2-dbg=2.53.1-0~realsense0.8250
realsense-viewer
sudo apt install ros-noetic-realsense2-camera
roslaunch realsense2_camera demo_t265.launch
source /opt/ros/noetic/setup.zsh
roslaunch realsense2_camera demo_t265.launch

```



https://zhuanlan.zhihu.com/p/626664186?utm_id=0&wd=&eqid=cd50a7d70000d592000000066469c664

### ddynamic-reconfigure

error like this:
```bash
Failed to load nodelet [/camera/realsense2_camera] of type [realsense2_camera
```


安装ddynamic
```bash
sudo apt-get install ros-noetic-ddynamic-reconfigure
```



### QGC配置

修改gcs_url
```yaml
gcs_url:=udp-b://@

or

gcs_url:=udp://@<IP>:<PORT>
example:
gcs_url:=udp://@192.168.0.105:14550

```
