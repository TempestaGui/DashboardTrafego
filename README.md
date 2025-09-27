# 📊 Dashboard de Tráfego de Rede

Este projeto exibe em tempo real o tráfego de rede capturado na máquina local.  
Ele possui dois componentes principais:  

- **Back-end**: API em **FastAPI (Python)** que coleta e expõe os dados de tráfego.  
- **Front-end**: Interface em **HTML/JavaScript** que exibe gráficos com Chart.js.  

---

## 🚀 Pré-requisitos

- **Python 3.9+**  
- **pip** (gerenciador de pacotes do Python)  
- **git** (para clonar o projeto)  

Opcional (mas recomendado):  
- **Wireshark/tshark** ou permissões de captura de pacotes (`libpcap` no Linux).  
- **Npcap (Windows)** ou **libpcap (Linux)** para captura de pacotes.  

---

## 🐧 Linux

### 1. Clonar o projeto
```bash
git clone https://github.com/TempestaGui/testeTrabalhoRedes
cd testeTrabalhoRedes/backEnd
```
### 2. Criar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Instalar dependências
```bash
pip install -r requirements.txt
```
### 4. Dar permissão para captura de pacotes
```bash
sudo usermod -aG wireshark $USER
newgrp wireshark
```
### 5. Rodar o back-end
```bash
export SERVER_IP=192.168.0.xxx
export INTERFACE=eth0
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 🪟 Windows
### 1. Clonar o projeto
```bash
git clone https://github.com/TempestaGui/testeTrabalhoRedes
cd testeTrabalhoRedes/backEnd
```
### 2. Criar ambiente virtual
```bash
python -m venv venv
.\venv\Scripts\activate
```
### 3. Instalar dependências
```bash
pip install -r requirements.txt
```
### 4. Instalar WinPcap/Npcap
```bash
https://npcap.com/
```
### 5. Rodar o back-end
```bash
setx SERVER_IP "192.168.0.xxx"
setx INTERFACE "Ethernet"
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 🔎 Testando com ICMP e UDP
### Linux
```bash
ping 8.8.8.8
```
### Windows
```bash
ping 8.8.8.8
```

## Testar UDP (com nping)
### Linux
```bash
sudo apt install nmap -y
sudo nping --udp -p 53 8.8.8.8
```
### Windows
```bash
nping --udp -p 53 8.8.8.8
```

## 📌 Observações

Para ver tráfego no drilldown, gere pacotes TCP, UDP, ICMP manualmente.

O front-end atual busca dados em http://127.0.0.1:8001/trafego/....
Se mudar a porta ou host do backend, ajuste no código JS.

Se o gráfico aparecer de uma cor só no drilldown → significa que apenas um protocolo foi capturado.
