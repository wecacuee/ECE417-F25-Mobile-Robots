# ECE417: Making your own ROS nodes 

## ROS client libraries 

### Using colcon to build packages 

Colcon is a build management system. What is a build management system?

You have used gcc to compile (build) \*.c files. When projects get big, there are too many gcc commands to run and too many gcc flags to keep track of. To keep track of dependencies and gcc flags, we use build management systems. Colcon sits on top of a hierarchy of build management systems. Makefiles and CMake are used to build C++ projects, while python setuptools are used to build python projects. Colcon allows you to compile multiple ROS projects while figuring out inter project dependencies.

What follows is mostly a copy of ROS beginners tutorial : [https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html) Please make sure you go through all the [beginner tutorials](https://docs.ros.org/en/humble/Tutorials.html) on your own.

Make sure colcon in installed on the laptop. It is already installed in the jetbot docker container.

```shell
laptop:~/ece417$ sudo apt install python3-colcon-common-extensions |
```

A ROS workspace is a directory with a particular structure. Commonly there is a `src` subdirectory. Inside that subdirectory is where the source code of ROS packages will be located. Typically the directory starts otherwise empty.

colcon does out of source builds. By default it will create the following directories as peers of the `src` directory:

1. The `build` directory will be where intermediate files are stored. For each package a subfolder will be created in which e.g. CMake is being invoked.  
2. The `install` directory is where each package will be installed to. By default each package will be installed into a separate subdirectory.  
3. The `log` directory contains various logging information about each colcon invocation.

### Create a workspace 

First, create a directory (`ws`) on the jetbot to contain our workspace

```shell
jetbot@nano-4gb-jp45:~/ece417$ mkdir -p ws/src
jetbot@nano-4gb-jp45:~/ece417$ cd ws
```

### Add some sources 

Let’s clone [jetbot\_ros](https://github.com/dusty-nv/jetbot_ros) repository into the `src` directory of the workspace:

```shell
jetbot@nano-4gb-jp45:~/ece417$ cd ws/src 
jetbot@nano-4gb-jp45:~/.../src$ git clone https://github.com/dusty-nv/jetbot_ros -b master
```

### Source an underlay 

It is important that we have sourced the environment for an existing ROS 2 installation that will provide our workspace with the necessary build dependencies for the example packages. This is achieved by sourcing the setup script provided by a binary installation or a source installation, ie. another colcon workspace (see [Installation](https://docs.ros.org/en/foxy/Installation.html)). We call this environment an **underlay**.

Our workspace, `ws`, will be an **overlay** on top of the existing ROS 2 installation. In general, it is recommended to use an overlay when you plan to iterate on a small number of packages, rather than putting all of your packages into the same workspace.

### Build the workspace 

In the root of the workspace, run `colcon build`. Since build types such as `ament_cmake` do not support the concept of the `devel` space and require the package to be installed, colcon supports the option `--symlink-install`. This allows the installed files to be changed by changing the files in the `source` space (e.g. Python files or other non-compiled resources) for faster iteration.

Since our ROS installation is a docker image, we will need to run a docker container and enter in it first. We will pull a new docker image on jetbot. Also, we will be using docker a lot, we need to avoid sudo. Add jetbot user to the docker group. Exit the ssh and ssh to jetbot again.

```shell
jetbot@nano-4gb-jp45:~/ece417$ sudo adduser jetbot docker
jetbot@nano-4gb-jp45:~/ece417$ <Press Ctrl+D>
logout
Connection to 141.114.195.160 closed.
laptop:~$ ssh jetbot@10.0.0.2
jetbot@nano-4gb-jp45:~/$ cd ece417
jetbot@nano-4gb-jp45:~/ece417$
```

Pull a new docker image called vdhiman86/ros:humble-pytorch-l4t-r32.7.1.

```shell
jetbot@nano-4gb-jp45:~/ece417$ docker pull vdhiman86/ros:humble-pytorch-l4t-r32.7.1 |
```

Create a new docker container from this image. Note that some flags have changed since we created the last docker container.

```shell
jetbot@nano-4gb-jp45:~/ece417$ docker container rm ros-humble
jetbot@nano-4gb-jp45:~/ece417$ docker run -it \
	--runtime nvidia \
	--network host \
	--privileged \
	--device /dev/video* \
	-v /dev/bus/usb:/dev/bus/usb \
	-v /tmp/argus_socket:/tmp/argus_socket \
	-v /home/jetbot:/home/jetbot \
	--workdir /home/jetbot/ece417 \
	--name=ros-humble \
	vdhiman86/ros:humble-pytorch-l4t-r32.7.1
sourcing   /opt/ros/humble/install/setup.bash
ROS_ROOT   /opt/ros/humble
ROS_DISTRO humble
root@nano-4gb-jp45:~/ece417$
```

It is recommended that you add this command to a file and call it rundocker.sh.

:::{code} bash
:filename: jetbot:~/ece417/rundocker.sh
docker run -it \
	--runtime nvidia \
	--network host \
	--privileged \
	--device /dev/video* \
	-v /dev/bus/usb:/dev/bus/usb \
	-v /tmp/argus_socket:/tmp/argus_socket \
	-v /home/jetbot:/home/jetbot \
	--workdir /home/jetbot/ece417 \
	--name=ros-humble \
	vdhiman86/ros:humble-pytorch-l4t-r32.7.1
:::

Now change directory to ws and run colcon build.

:::{code} shell
:caption: Context: on jetbot, inside docker container
root@nano-4gb-jp45:~/ece417$ cd ws
root@nano-4gb-jp45:~/ece417/ws$ colcon build --symlink-install
:::

After the build is finished, we should see the `build`, `install`, and `log` directories:

### Source the environment 

When colcon has completed building successfully, the output will be in the `install` directory. Before you can use any of the installed executables or libraries, you will need to add them to your path and library paths. colcon will have generated bash/bat files in the `install` directory to help set up the environment. These files will add all of the required elements to your path and library paths as well as provide any bash or shell commands exported by packages.

:::{code} shell
:caption: Context: on jetbot, inside docker container
root@nano-4gb-jp45:~/ece417/ws$ source install/setup.bash
:::

After sourcing the environment, the compiled packages should be part of ros2 pkg list


:::{code} shell
:caption: Context: on jetbot, inside docker container
root@nano-4gb-jp45:~/ece417/ws$ ros2 pkg list | grep -E 'jetbot_ros'
jetbot_ros
:::

The new `install/setup.bash` is a replacement of /opt/ros/humble/install/setup.bash. Modify the ~/ece417/setup.bash that we created last time, to source install/setup.bash instead of /opt/ros/humble/install/setup.bash. The new setup.bash should look like this:

:::{code} bash
:filename: jetbot:~/ece417/setup.bash
source ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="file://$(pwd)/cyclonedds.xml"
alias rosenv='printenv | grep -E "ROS|RMW_IMPLEMENTATION|AMENT|CYCLONEDDS_URI"'
:::

Source the new setup.bash and check the environment variables

:::{code} shell
:caption: Context: on jetbot, inside docker container
root@nano-4gb-jp45:~/ece417/ws$ cd ..
root@nano-4gb-jp45:~/ece417$ source setup.bash
root@nano-4gb-jp45:~/ece417$ rosenv
AMENT_PREFIX_PATH=/home/jetbot/ece417/ws/install/jetbot_ros:/opt/ros/humble/install
CYCLONEDDS_URI=file:///home/jetbot/ece417/cyclonedds.xml
ROS_ROOT=/opt/ros/humble
ROS_VERSION=2
ROS_LOCALHOST_ONLY=0
ROS_PYTHON_VERSION=3
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ROS_DISTRO=humble
:::

Install the Adafruit\_MotorHAT package from inside the  docker container. 

:::{code} shell
:caption: Context: on jetbot, inside docker container
root@nano-4gb-jp45:~/ece417$ pip3 install Adafruit_MotorHAT
:::

### Try a demo 

With the environment sourced, we can run executables built by colcon. Let’s run the motor\_waveshare node from jetbot\_ros. 

:::{code} shell
:caption: Context: on jetbot, inside docker container
root@nano-4gb-jp45:~/ece417$ ros2 run jetbot_ros motors_waveshare
:::

In another terminal on the laptop, let’s run a publisher node (don’t forget to source the setup script).

:::{code} shell
:caption: Context: on laptop
laptop:~/ece417$ source setup.bash
laptop:~/$ rosenv
ROS_VERSION=2
ROS_PYTHON_VERSION=3
AMENT_PREFIX_PATH=/opt/ros/humble
ROS_LOCALHOST_ONLY=0
CYCLONEDDS_URI=file:///home/vdhiman/wrk/teaching/ece417/website/docs/labnotes/09-22/cyclonedds/cyclonedds.xml
ROS_DISTRO=humble
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
:::

Introspect the running ros nodes and expected topics.

```shell
:caption: Context: on laptop
laptop:~/ece417$ ros2 node list
/jetbot/motors
laptop:~/ece417$ ros2 topic list
/jetbot/cmd_vel
/parameter_events
/rosout
```

Then run a keyboard teleop node **(Attn: Make sure you either lift the robot or decrease the speed below 0.07 before pressing a move button)**

```shell
laptop:~/ece417$ ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/jetbot/cmd_vel
This node takes keypresses from the keyboard and publishes them
as Twist messages. It works best with a US keyboard layout.
---------------------------
Moving around:
   u	i	o
   j	k	l
   m	,	.

For Holonomic mode (strafing), hold down the shift key:
---------------------------
   U	I	O
   J	K	L
   M	<	>

t : up (+z)
b : down (-z)

anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit

```

Visualize the connected nodes in the RQT graph. In another terminal, source setup.bash and launch rqt\_graph  
![][image1]  
Top stop, press Ctrl+C in all the three terminals for rqt\_graph, teleop\_twist\_keyboard, and motors\_waveshare on jetbot.

### Create your own package  

#### What is a ROS 2 package? 

A package is an organizational unit for your ROS 2 code. If you want to be able to install your code or share it with others, then you’ll need it organized in a package. With packages, you can release your ROS 2 work and allow others to build and use it easily.

Package creation in ROS 2 uses ament as its build system and colcon as its build tool. You can create a package using either CMake or Python, which are officially supported, though other build types do exist.

#### What makes up a ROS 2 package? 

ROS 2 Python and CMake packages each have their own minimum required contents:

##### CMake 

* `CMakeLists.txt` file that describes how to build the code within the package  
* `include/<package_name>` directory containing the public headers for the package  
* `package.xml` file containing meta information about the package  
* `src` directory containing the source code for the package

##### Python 

* `package.xml` file containing meta information about the package  
* `resource/<package_name>` marker file for the package  
* `setup.cfg` is required when a package has executables, so `ros2 run` can find them  
* `setup.py` containing instructions for how to install the package  
* `<package_name>` \- a directory with the same name as your package, used by ROS 2 tools to find your package, contains `__init__.py`

The simplest possible package may have a file structure that looks like:

CMake  
my\_package/  
     CMakeLists.txt  
     include/my\_package/  
     package.xml  
     src/

##### Python 

my\_package/  
      package.xml  
      resource/my\_package  
      setup.cfg  
      setup.py  
      my\_package/

### Create a Python package 

The command syntax for creating a new package in ROS 2 is:

```shell
root@nano-4gb-jp45:~/ece417/ws/src$ ros2 pkg create --build-type ament_python py_pubsub
going to create a new package
package name: py_pubsub
destination directory: /home/jetbot/ece417/ws/src
package format: 3
version: 0.0.0
description: TODO: Package description
maintainer: ['root <root@todo.todo>']
licenses: ['TODO: License declaration']
build type: ament_python
dependencies: []
creating folder ./py_pubsub
creating ./py_pubsub/package.xml
creating source folder
creating folder ./py_pubsub/py_pubsub
creating ./py_pubsub/setup.py
creating ./py_pubsub/setup.cfg
creating folder ./py_pubsub/resource
creating ./py_pubsub/resource/py_pubsub
creating ./py_pubsub/py_pubsub/__init__.py
creating folder ./py_pubsub/test
creating ./py_pubsub/test/test_copyright.py
creating ./py_pubsub/test/test_flake8.py
creating ./py_pubsub/test/test_pep257.py
```

### Write the publisher node 

In a file `ws/src/py_pubsub/py_pubsub/publisher_member_function.py` write:

:::{code} python
:filename: jetbot:~/ece417/ws/src/py_pubsub/py_pubsub/publisher_member_function.py
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalPublisher(Node):
    def __init__(self):
    	super().__init__('minimal_publisher')
    	self.publisher_ = self.create_publisher(String, 'topic', 10)
    	timer_period = 0.5  # seconds
    	self.timer = self.create_timer(timer_period, self.timer_callback)
    	self.i = 0

    def timer_callback(self):
    	msg = String()
    	msg.data = 'Hello World: %d' % self.i
    	self.publisher_.publish(msg)
    	self.get_logger().info('Publishing: "%s"' % msg.data)
    	self.i += 1


def main(args=None):
	rclpy.init(args=args)

	minimal_publisher = MinimalPublisher()

	rclpy.spin(minimal_publisher)

	# Destroy the node explicitly
	# (optional - otherwise it will be done automatically
	# when the garbage collector destroys the node object)
	minimal_publisher.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()
:::

Edit package.xml to add dependencies.


:::{code} xml
:filename: edit jetbot:~/ece417/ws/src/py_pubsub/package.xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
:::

Edit the `setup.py` file to add the following line within the `console_scripts` brackets of the `entry_points` field:

:::{code} python
:filename: edit jetbot:~/ece417/ws/src/py_pubsub/setup.py
:emphasize-lines: 3
entry_points={
        'console_scripts': [
                'talker = py_pubsub.publisher_member_function:main',
        ],
},
:::

Verify setup.cfg looks like this

:::{code} ini
:filename: jetbot:~/ece417/ws/src/py_pubsub/setup.cfg
[develop]
script-dir=$base/lib/py_pubsub
[install]
install-scripts=$base/lib/py_pubsub
:::

### Write the subscriber node 

In a file `ws/src/py_pubsub/py_pubsub/subscriber_member_function.py` write:

:::{code} python
:filename: ws/src/py_pubsub/py_pubsub/subscriber_member_function.py
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
    	super().__init__('minimal_subscriber')
    	self.subscription = self.create_subscription(
        	String,
        	'topic',
        	self.listener_callback,
        	10)
    	self.subscription  # prevent unused variable warning
    def listener_callback(self, msg):
    	self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
	rclpy.init(args=args)

	minimal_subscriber = MinimalSubscriber()

	rclpy.spin(minimal_subscriber)

	# Destroy the node explicitly
	# (optional - otherwise it will be done automatically
	# when the garbage collector destroys the node object)
	minimal_subscriber.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()
:::

Edit setup.py to add the `listener = ..` line to the `console_scripts`, next to the talker script:

:::{code} python
:filename: edit jetbot:~/ece417/ws/src/py_pubsub/setup.py
:emphasize-lines: 4,
entry_points={
        'console_scripts': [
                'talker = py_pubsub.publisher_member_function:main',
                'listener = py_pubsub.subscriber_member_function:main'
        ],
},
:::

#### Build and run 

:::{code} shell
:caption: Context: on jetbot, in docker container
:emphasize-lines: 5
root@nano-4gb-jp45:~/ece417/ws$ rosdep install -i --from-path src --rosdistro humble -y
root@nano-4gb-jp45:~/ece417/ws$ colcon build --packages-select py_pubsub
root@nano-4gb-jp45:~/ece417/ws$ source install/setup.bash
root@nano-4gb-jp45:~/ece417/ws$ ros2 run py_pubsub talker
<Press Ctrl+p Ctrl+q> to detach from docker container without stopping it
:::

You can start another docker terminal in the same docker container using docker exec. Make sure the docker container is still running.

```shell
jetbot@nano-4gb-jp45:~/ece417/ws$ docker container ls -a
```

Start a new terminal inside the docker container ros-humble

```shell
jetbot@nano-4gb-jp45:~/ece417$ docker container exec -it ros-humble bash
root@nano-4gb-jp45:~/ece417$ source setup.bash
root@nano-4gb-jp45:~/ece417$ ros2 run py_pubsub listener
```

You can stop the listener by pressing Ctrl+C and Ctrl+D to quit the session in the container. To reattach to the detached session type 

```shell
jetbot@nano-4gb-jp45:~/ece417/ws$ docker container attach ros-humble
```

Now you can press Ctrl+C to stop the talker and Ctrl+D to quit the session and stop the container.

You can start a stopped docker container and attach to it by:

```shell
jetbot@nano-4gb-jp45:~/ece417/ws$ docker container start -ia ros-humble
```

For learning more about docker, please go through [https://docs.docker.com/get-started/overview/](https://docs.docker.com/get-started/overview/) 

[image1]: <data:image/png;base64,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>
