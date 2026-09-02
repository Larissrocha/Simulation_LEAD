FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV USERNAME=developer
ENV USER_UID=1000
ENV USER_GID=1000

# 1. Repositório oficial do Gazebo Harmonic
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# 2. Instalação do Gazebo Harmonic e dependências completas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gz-harmonic \
    ros-humble-ros-gz \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-interfaces \
    bash-completion \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    tmux \
    tmuxinator \
    nano \
    sudo \
    libxml2-utils \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# 3. Criação do usuário developer
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

# 4. Micro XRCE-DDS Agent
RUN git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git \
    && cd Micro-XRCE-DDS-Agent \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && sudo make install \
    && sudo ldconfig /usr/local/lib/

# 5. PX4-Autopilot com script de setup e compilação do gz_x500
RUN git clone -b release/1.16 https://github.com/PX4/PX4-Autopilot.git \
    && cd PX4-Autopilot \
    && git submodule update --init --recursive \
    && bash ./Tools/setup/ubuntu.sh --no-nuttx --no-sim-tools \
    && DONT_RUN=1 make px4_sitl_default gz_x500

# 6. Pacotes de mensagens ROS 2 / PX4
RUN mkdir -p /home/$USERNAME/dependencias_px4/src \
    && cd /home/$USERNAME/dependencias_px4/src \
    && git clone https://github.com/PX4/px4_msgs.git -b release/1.16 \
    && git clone https://github.com/PX4/px4_ros_com.git -b release/1.16 \
    && cd /home/$USERNAME/dependencias_px4 \
    && /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

# 7. Configurações de ambiente no bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc \
    && echo "source /home/$USERNAME/dependencias_px4/install/setup.bash" >> ~/.bashrc \
    && echo "export GZ_VERSION=harmonic" >> ~/.bashrc

WORKDIR /home/$USERNAME