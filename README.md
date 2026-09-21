```markdown
# Simulation LEAD - Ambiente de Simulação Nativo

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
No terminal da sua **máquina física**:
```bash
git clone git@github.com:Larissrocha/Simulation_LEAD.git
cd Simulation_LEAD

```

### 2. Permitir Acesso à Interface Gráfica (X11) e GPU

Para que o Gazebo abra a janela de renderização 3D na tela do host (execute após ligar ou reiniciar a máquina):

```bash
xhost +local:root
xhost +local:developer
sudo chmod -R a+rw /dev/dri/

```

### 3. Construir e Iniciar o Container Docker

Para compilar a imagem com Gazebo Harmonic, MicroXRCEAgent e PX4 SITL:

```bash
docker compose up -d --build

```

### 4. Acessar o Terminal do Container

Entre no container em execução utilizando o usuário padrão `developer`:

```bash
docker compose exec -it simulation /bin/bash

```

*(Ou diretamente via Docker CLI: `docker exec -it -u developer lead_simulation /bin/bash`)*

---

## Compilação do Workspace

Ao entrar no container pela primeira vez (ou após modificar arquivos no workspace):

```bash
cd /home/developer/simulation_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash

```

---

## Executar a Simulação

Com o workspace compilado e as permissões gráficas liberadas, inicie o ambiente de simulação dentro do container:

```bash
cd /home/developer/simulation_ws
source install/setup.bash
ros2 launch sim_environment sim.launch.py

```

O comando inicializa os componentes integrados:

* **Gazebo Sim (Harmonic)**: Motor de física ODE e renderização gráfica do mundo `default.sdf`.


* **Drone Spawner**: O script auxiliar `spawn_drone.launch.py` injeta dinamicamente o modelo (`x500_px4`) na cena.

---

## Executar Missões em Paralelo

Para interagir com o drone enquanto a simulação está rodando:

1. Abra uma nova aba no terminal da sua **máquina física**:

```bash
docker compose exec -it simulation /bin/bash

```

2. Carregue o ambiente e execute seu script de missão:

```bash
cd /home/developer/simulation_ws
source install/setup.bash
ros2 run lead_missions simple_mission

```

3. **Inserir Drones Adicionais / Trocar Modelos (Opcional):**
Execute o launch auxiliar especificando outro identificador e novas coordenadas:



```bash
ros2 launch sim_environment spawn_drone.launch.py drone_name:=x500_1 x:=2.0 y:=2.0 z:=0.22

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
        ├── sim_environment/          # Pacote de simulação e modelos 3D
        │   ├── CMakeLists.txt       # Regras de instalação dos arquivos de share
        │   ├── package.xml          # Dependências do pacote (ros_gz_sim, ros_gz_bridge)
        │   ├── launch/
        │   │   ├── sim.launch.py    # Launch principal (inicia Gazebo e dispara o spawn)
        │   │   └── spawn_drone.launch.py # Launch modular para injeção dinâmica de drones
        │   ├── models/              # Modelos 3D locais (grass_patch, x500_px4, ariel_marker)
        │   └── worlds/
        │       └── default.sdf      # Descrição física do mundo (física ODE, sol, piso e marcador)
        └── lead_missions/           # Pacote Python de controle e missões autônomas
            ├── package.xml          # Dependências de mensagens e execução ROS 2
            ├── setup.py             # Registro de entry points dos nós
            └── lead_missions/
                ├── base_mission.py  # Gerenciador de contexto do ciclo de voo
                └── simple_mission.py# Script sequencial de decolagem, voo e pouso

```

### Detalhamento dos Componentes Principais

* **`docker/` e `docker-compose.yml**`: Isolam o ecossistema de software de voo (ROS 2 Humble, compilador PX4 e dependências) sem modificar as bibliotecas do sistema hospedeiro.


* **`sim_environment/`**: Concentra as definições físicas do mundo, modelos dos veículos e arquivos de launch do Gazebo Sim.


* **`lead_missions/`**: Área de desenvolvimento da aplicação. Contém os scripts em Python que publicam setpoints e gerenciam as rotinas de voo sobre os tópicos da FMU.



---

## Resumo de Comandos Úteis

| Objetivo | Comando | Onde Executar |
| --- | --- | --- |
| **Liberar display e GPU para o Docker** | `xhost +local:root && xhost +local:developer && sudo chmod -R a+rw /dev/dri/` | Máquina Física

 |
| **Subir / Recriar Container** | `docker compose up -d --build` | Máquina Física (Raiz)

 |
| **Entrar no Container** | `docker compose exec -it simulation /bin/bash` | Máquina Física

 |
| **Derrubar Container** | `docker compose down` | Máquina Física

 |
| **Compilar Workspace** | `colcon build --symlink-install` | Dentro do Docker

 |
| **Iniciar Simulação** | `ros2 launch sim_environment sim.launch.py` | Dentro do Docker

 |
| **Forçar Parada de Processos** | `killall -9 gz-sim-server gz-sim-gui px4 MicroXRCEAgent 2>/dev/null || true` | Dentro do Docker

 |

```

```