
# Simulação LEAD - Ambiente de Simulação

Ambiente de simulação puro para desenvolvimento e validação de controle de voo, sensoriamento e missões autônomas com drones utilizando **ROS 2 Humble**, **PX4 SITL (v1.16)** e **Gazebo Sim (Harmonic)**, sem acoplamento a frameworks legados.

---

## Arquitetura do Ambiente

1. **Workspace do Usuário (`simulation_ws/src`)**: Montado como volume compartilhado entre o computador físico e o container Docker. Qualquer código, modelo ou launch alterado no host reflete instantaneamente dentro do container.
2. **Workspace de Dependências (`dependencias_px4`)**: Compilado internamente na imagem Docker com as interfaces oficiais do PX4 (`px4_msgs`, `px4_ros_com`), mantendo o repositório Git leve.
3. **Firmware de Voo (PX4 SITL)**: O código-fonte do **PX4-Autopilot (v1.16)** fica compilado dentro do container em `/home/developer/PX4-Autopilot`.
4. **Ponte de Comunicação (Micro-XRCE-DDS)**: O **MicroXRCEAgent** atua como tradutor de alta frequência entre o middleware DDS do ROS 2 e as mensagens uORB nativas do firmware PX4.

---

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado no seu computador físico (Ubuntu 22.04+):

* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## Instalação e Configuração

### 1. Clonar o Repositório
No terminal do seu **computador real**:
```bash
git clone git@github.com:Larissrocha/Simulation_LEAD.git
cd Simulation_LEAD

```

### 2. Permitir Acesso à Interface Gráfica (X11)

Para que o Gazebo e o RViz consigam abrir janelas gráficas no monitor do seu host, execute no seu **computador real** (necessário após ligar ou reiniciar a máquina):

```bash
xhost +local:root
xhost +local:developer

```

### 3. Construir e Iniciar o Container Docker

Para baixar a imagem base, compilar o MicroXRCEAgent, o PX4 SITL e o workspace de dependências:

```bash
docker compose up -d --build

```

### 4. Acessar o Terminal do Container

Entre no container como o usuário padrão `developer`:

```bash
docker compose exec -it simulation /bin/bash

```

---

## Compilação do Workspace

Na primeira execução (ou após criar/modificar pacotes C++ e mensagens ROS 2), execute a compilação dentro do **Docker**:

```bash
cd /home/developer/simulation_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

> **Nota de Performance:** A flag `--parallel-workers 1` limita o processo de compilação a 1 núcleo por vez para evitar esgotamento de memória RAM da máquina host/VM.

---

## Executar a Simulação

Com o workspace compilado e as permissões de vídeo liberadas, inicie o ambiente de simulação dentro do terminal do **Docker**:

```bash
cd /home/developer/simulation_ws
source install/setup.bash
ros2 launch sim_environment sim.launch.py

```

O comando inicializa os componentes integrados:

* **Gazebo Sim (Harmonic)**: Motor de física e renderização gráfica do mundo default.sdf.
* **Clock Bridge:**: Sincronização do relógio de simulação (/clock) entre o Gazebo e o ecossistema ROS 2.
* **Drone Spawner:** O script auxiliar spawn_drone.launch.py injeta dinamicamente o modelo (x500_px4) na cena.
* **MicroXRCEAgent**: Ponte de dados ROS 2 $\leftrightarrow$ PX4.

---

## Executar Missões em Paralelo

Para interagir com o drone enquanto a simulação está rodando:

1. Abra uma nova aba no terminal da sua **máquina física**:
```bash
docker exec -it -u developer simulation /bin/bash

```


2. Carregue o ambiente e execute seu script de missão:
```bash
cd /home/developer/aerostack2_ws
source install/setup.bash
ros2 run lead_missions simple_mission

```
2. Inserir Drones Adicionais / Trocar Modelos
   
   Execute o launch auxiliar especificando outro identificador e novas coordenadas:
```bash
ros2 launch sim_environment spawn_drone.launch.py drone_name:=x500_1 x:=2.0 y:=2.0 z:=0.2
```

---

## Estrutura do Projeto e Organização de Pastas

Abaixo está o detalhamento de cada diretório e componente do repositório:

```text
Simulation_LEAD/
├── docker/
│   └── Dockerfile                   # Receita da imagem com ROS 2 Humble, PX4 SITL e Micro-XRCE-DDS
├── docker-compose.yml               # Mapeamento de volumes, GPU (/dev/dri) e display gráfico
├── README.md                        # Guia operacional do repositório
└── simulation_ws/
    └── src/
        └── sim_environment/          # Pacote ROS 2 com a lógica de simulação
            ├── CMakeLists.txt       # Regras de instalação dos arquivos de share
            ├── package.xml          # Dependências do pacote (ros_gz_sim, ros_gz_bridge)
            ├── launch/
            │   ├── sim.launch.py    # Launch mestre (abre Gazebo, pontes e chama o spawn)
            │   └── spawn_drone.launch.py # Launch modular para injeção dinâmica de drones
            ├── models/              # Modelos 3D locais (grass_patch, x500_px4, marcadores)
            └── worlds/
                └── default.sdf      # Descrição física do mundo (luz sunUTC, chão e atmosfera)

```

### Detalhamento dos Componentes Principais

* **`docker/` e `docker-compose.yml**`: Isolam todo o ecossistema de software de voo (ROS 2 Humble, compilador PX4 e dependências) sem poluir o sistema operacional da máquina física.
* **`sim_environment/`**: Concentra as definições físicas do mundo, modelos de sensores e o orquestrador `launch_sim.bash`, que inicializa simultaneamente a física do Gazebo, o PX4 SITL e as pontes de comunicação.


* **`lead_missions/`**: Área limpa de desenvolvimento do usuário. Contém os nós em Python responsáveis por interagir com os tópicos e ações dos comportamentos do drone.
* **`aerostack2/`**: Estrutura contendo o núcleo de comunicação, dicionários de mensagens (`as2_msgs`), utilitários Python (`as2_python_api`) e os assets e bridges de simulação para o Gazebo (`as2_gazebo_assets`).



```

```

---

## Resumo de Comandos Úteis

| Objetivo | Comando | Onde Executar |
| --- | --- | --- |
| **Liberar display para o Docker** | `xhost +local:root && xhost +local:developer` | Máquina Física |
| **Subir / Recriar Container** | `docker compose up -d --build` | Máquina Física (Raiz) |
| **Entrar no Container** | `docker exec -it -u developer aerostack_lead_2 /bin/bash` | Máquina Física |
| **Derrubar Container** | `docker compose down` | Máquina Física |
| **Compilar Workspace** | `colcon build --symlink-install --parallel-workers 1` | Dentro do Docker |
| **Encerrar Sessão Tmux** | `tmux kill-server` | Dentro do Docker |
| **Forçar Parada do Simulador** | `killall -9 gz-sim-server gz-sim-gui px4 MicroXRCEAgent` | Dentro do Docker |

```

```
Markdown# Simulation LEAD - Ambiente de Simulação Nativo

Ambiente de simulação puro para desenvolvimento e validação de controle de voo, sensoriamento e missões autônomas com drones utilizando **ROS 2 Humble**, **PX4 SITL (v1.16)** e **Gazebo Sim (Harmonic)**, sem acoplamento a frameworks legados.

---

## Arquitetura do Ambiente

1. **Workspace do Usuário (`simulation_ws/src`)**: Montado como volume compartilhado entre o computador físico e o container Docker. Qualquer código, modelo ou launch alterado no host reflete instantaneamente dentro do container.
2. **Workspace de Dependências (`dependencias_px4`)**: Compilado internamente na imagem Docker com as interfaces oficiais do PX4 (`px4_msgs`, `px4_ros_com`), mantendo o repositório Git leve.
3. **Firmware de Voo (PX4 SITL)**: O código-fonte do **PX4-Autopilot (v1.16)** fica compilado dentro do container em `/home/developer/PX4-Autopilot`.
4. **Ponte de Comunicação (Micro-XRCE-DDS)**: O **MicroXRCEAgent** atua como tradutor de alta frequência entre o middleware DDS do ROS 2 e as mensagens uORB nativas do firmware PX4.

---

## Pré-requisitos

Instale no seu sistema operacional host (Ubuntu 22.04 LTS):

* [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
* [Docker Compose Plugin](https://docs.docker.com/compose/install/)

---

## Instalação e Configuração

### 1. Clonar o Repositório
No terminal da sua máquina física:
```bash
git clone git@github.com:Larissrocha/Simulation_LEAD.git
cd Simulation_LEAD
2. Permitir Acesso à Interface Gráfica (X11)Para que o Gazebo abra a janela de renderização 3D na tela do host (execute sempre que ligar ou reiniciar a máquina):Bashxhost +local:root
xhost +local:developer
3. Construir e Iniciar o Container DockerPara compilar a imagem com Gazebo Harmonic, MicroXRCEAgent e PX4 SITL:Bashdocker compose up -d --build
4. Acessar o Terminal do ContainerEntre no container em execução utilizando o usuário não-root developer:Bashdocker compose exec -it simulation /bin/bash
(Ou diretamente via Docker CLI: docker exec -it -u developer lead_simulation /bin/bash)Compilação do WorkspaceAo entrar no container pela primeira vez (ou após modificar arquivos do workspace):Bashcd /home/developer/simulation_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
Executar a SimulaçãoCom o workspace compilado e as permissões de vídeo liberadas, inicie o ambiente de simulação:Bashcd /home/developer/simulation_ws
source install/setup.bash
ros2 launch sim_environment sim.launch.py
O comando inicializa os componentes integrados:Gazebo Sim (Harmonic): Motor de física e renderização gráfica do mundo default.sdf.Clock Bridge: Sincronização do relógio de simulação (/clock) entre o Gazebo e o ecossistema ROS 2.Drone Spawner: O script auxiliar spawn_drone.launch.py injeta dinamicamente o modelo (x500_px4) na cena.MicroXRCEAgent: Gerenciamento de transporte UDP (porta 8888) para a controladora PX4.Inserir Drones Adicionais / Trocar ModelosPara injetar outro drone com a simulação já aberta, abra um segundo terminal no host e rode:Bashdocker compose exec -it simulation /bin/bash
E execute o launch auxiliar especificando outro identificador e novas coordenadas:Bashros2 launch sim_environment spawn_drone.launch.py drone_name:=x500_1 x:=2.0 y:=2.0 z:=0.2
Estrutura do Projeto e Organização de PastasPlaintextSimulation_LEAD/
├── docker/
│   └── Dockerfile                   # Receita da imagem com ROS 2 Humble, PX4 SITL e Micro-XRCE-DDS
├── docker-compose.yml               # Mapeamento de volumes, GPU (/dev/dri) e display gráfico
├── README.md                        # Guia operacional do repositório
└── simulation_ws/
    └── src/
        └── sim_environment/          # Pacote ROS 2 com a lógica de simulação
            ├── CMakeLists.txt       # Regras de instalação dos arquivos de share
            ├── package.xml          # Dependências do pacote (ros_gz_sim, ros_gz_bridge)
            ├── launch/
            │   ├── sim.launch.py    # Launch mestre (abre Gazebo, pontes e chama o spawn)
            │   └── spawn_drone.launch.py # Launch modular para injeção dinâmica de drones
            ├── models/              # Modelos 3D locais (grass_patch, x500_px4, marcadores)
            └── worlds/
                └── default.sdf      # Descrição física do mundo (luz sunUTC, chão e atmosfera)
Resumo de Comandos ÚteisObjetivoComandoOnde ExecutarLiberar display para o Dockerxhost +local:root && xhost +local:developerMáquina FísicaLiberar acesso à aceleração gráficasudo chmod -R a+rw /dev/dri/Máquina FísicaSubir / Recriar Containerdocker compose up -d --buildMáquina Física (Raiz)Entrar no Containerdocker compose exec -it simulation /bin/bashMáquina FísicaDerrubar Containerdocker compose downMáquina FísicaCompilar Pacote de Simulaçãocolcon build --packages-select sim_environment --symlink-installDentro do DockerIniciar Simulaçãoros2 launch sim_environment sim.launch.pyDentro do DockerForçar Parada de Processos`killall -9 gz-sim-server gz-sim-gui px4 MicroXRCEAgent 2>/dev/null
