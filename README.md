# Digital Twin Brewing System

## Project Description

This repository contains the implementation of a digital twin for the laboratory brewing system at Hochschule Ruhr West.

The system reads live process data from a Siemens S7-1500 PLC via OPC-UA, stores the data, models the brewing process as a finite state machine, detects rule-based anomalies, and provides the current system state through a REST API.

## Team Roles

| Engineer | Role | Main Folder |
|---|---|---|
| Engineer A | OPC-UA System Analysis | docs/, diagrams/ |
| Engineer B | Data Acquisition | src/opcua_client/, src/storage/ |
| Engineer C | Process Model / FSM | src/process_model/ |
| Engineer D | Anomaly Detection | src/anomaly_detection/ |
| Engineer E | REST API / Integration | src/api/, README.md |

## Repository Structure

```text
src/                 Main source code
docs/                Technical documentation
diagrams/            Architecture and process diagrams
data/                Raw and processed data
tests/               Unit and integration tests
presentation/        Final presentation and demo script
logs/                Runtime logs
```

### Rollen im Repo
```
Engineer A → docs/opcua_nodes_table.md, docs/architecture.md, diagrams/
Engineer B → src/opcua_client/, src/storage/
Engineer C → src/process_model/, diagrams/state_machine_diagram.png
Engineer D → src/anomaly_detection/, docs/anomaly_rules.md, tests/test_anomaly_rules.py
Engineer E → src/api/, README.md, presentation/, docs/api_documentation.md
```

### Installation
```c
git clone https://github.com/YOUR-USERNAME/digital-twin-brewing-system.git
cd digital-twin-brewing-system
```
1. Create and acitvate your python virtual environment
2. Install dependencies
```
pip install -r requirements.txt
```
3. Configure your Environment:
Create a .env file based on -r 

### Git Workflow
To avoid conflicts, nobody works directly on main. Each person should work on their own branch. Examples of names to adopt:
- feature/engineer-a-opcua-analysis
- feature/engineer-b-data-acquisition
- feature/engineer-c-state-machine
- feature/engineer-d-anomaly-detection
- feature/engineer-e-api-integration

#### How to Strart Working
1. First, always update your local repo:
```
git checkout main
git pull origin main
```
2. Create your own branch:
```
git checkout -b feature/engineer<-your-branch-id>
```
3. Work on your files, check status, add your changes, commit your changes and push your branch
```
git status
git add .
git commit -m "your-personal-message"
git push -u origin feature/engineer<-your-branch-id>
```
4. Open a Pull request on Github.

> **Wichtig:** Die echte .env und lokale Datenbank sollten nicht gepusht werden. Nur .env.example gehört ins Repo.
