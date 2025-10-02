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
- **wireshark** (https://www.wireshark.org/download.html) -> Para windows
  > baixa e marca a opção de instalar TShark, depois reinicia o computador pras variáveis de ambiente serem aplicadas
  
Opcional (mas recomendado):  
- **Wireshark/tshark** ou permissões de captura de pacotes (`libpcap` no Linux).  
- **Npcap (Windows)** ou **libpcap (Linux)** para captura de pacotes.  

---

## 🐧 Linux

### 1. Clonar o projeto
```bash
git clone https://github.com/TempestaGui/DashboardTrafego
cd DashboardTrafego
```
### 2. Criar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Instalar dependências
```bash
cd backEnd
pip install -r requirements.txt
pip install -r tests_requirements.txt
```
### 4. Testes e Validação

Após instalar as dependências, é importante garantir a qualidade e segurança do código. Os comandos a seguir funcionam tanto no Linux quanto no Windows, desde que você esteja dentro do diretório backEnd com o ambiente virtual ativado.

1. Ativar o Hook de Commit (Obrigatório)
   
Este comando cria o link entre a ferramenta pre-commit e o seu repositório Git. Este é o passo que garante que todas as verificações de segurança (bandit, safety) rodem automaticamente antes de cada git commit para todos os desenvolvedores.
```bash
# Dentro do diretório backEnd com o venv ativado
pre-commit install
> ⚠️ Se tiver problemas, use pre-commit install --install-hooks.
```

2. Testes de Unidade e Integração

Executa todos os arquivos de teste (test_*.py) encontrados no projeto. O flag -v fornece saída detalhada (verbose).
```bash
# Dentro do diretório backEnd com o venv ativado
pytest -v
```
3. Análise de Segurança
   
A. Análise de Vulnerabilidades de Dependências (SCA) com safety

Verifica se as dependências do requirements.txt e tests_requirements.txt possuem vulnerabilidades conhecidas.
```bash
# Executar dentro do venv ativado
safety scan -r
```
B. Análise Estática de Código (SAST) com bandit

Escaneia o código-fonte em busca de problemas de segurança comuns, como senhas hardcoded.
```bash
# Rodar de forma recursiva no diretório atual
bandit -r . --exclude ./tests,./venv
```
### 5. Dar permissão para captura de pacotes
```bash
sudo usermod -aG wireshark $USER
newgrp wireshark
```
### 6. Rodar o back-end
```bash
export SERVER_IP=192.168.0.xxx
export INTERFACE=eth0
# Dentro do venv ativado
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```
> ⚠️ Substitua 192.168.0.xxx pelo IP da sua máquina na rede local e eth0 pela interface correta. Para ver as interfaces disponíveis: ip addr show.

## 🪟 Windows
### 1. Clonar o projeto
```bash
git clone https://github.com/TempestaGui/DashboardTrafego
cd DashboardTrafego
```
### 2. Criar ambiente virtual
```bash
python -m venv venv
.\venv\Scripts\activate
```
### 3. Instalar dependências
```bash
cd backEnd
pip install -r requirements.txt
pip install -r tests_requirements.txt
```
### 4. Testes e Validação

Após instalar as dependências, é importante garantir a qualidade e segurança do código. Os comandos a seguir funcionam tanto no Linux quanto no Windows, desde que você esteja dentro do diretório backEnd com o ambiente virtual ativado.

1. Ativar o Hook de Commit (Obrigatório)
   
Este comando cria o link entre a ferramenta pre-commit e o seu repositório Git. Este é o passo que garante que todas as verificações de segurança (bandit, safety) rodem automaticamente antes de cada git commit para todos os desenvolvedores.
```bash
# Dentro do diretório backEnd com o venv ativado
pre-commit install
> ⚠️ Se tiver problemas, use pre-commit install --install-hooks.
```

2. Testes de Unidade e Integração

Executa todos os arquivos de teste (test_*.py) encontrados no projeto. O flag -v fornece saída detalhada (verbose).
```bash
# Dentro do diretório backEnd com o venv ativado
pytest -v
```
3. Análise de Segurança
   
A. Análise de Vulnerabilidades de Dependências (SCA) com safety

Verifica se as dependências do requirements.txt e tests_requirements.txt possuem vulnerabilidades conhecidas.
```bash
# Executar dentro do venv ativado
safety scan -r
```
B. Análise Estática de Código (SAST) com bandit

Escaneia o código-fonte em busca de problemas de segurança comuns, como senhas hardcoded.
```bash
# Rodar de forma recursiva no diretório atual
bandit -r . --exclude ./tests,./venv
```
### 5. Instalar WinPcap/Npcap
(https://npcap.com/)
### 6. Rodar o back-end
```bash
> caso esteja rodando em um cmd rode esse comando
set SERVER_IP=192.168.0.xxx
set INTERFACE=Ethernet

> caso esteja rodando e um powershell rode esse comando
$env:SERVER_IP="192.168.0.xxx"
$env:INTERFACE="Ethernet"
```

```bash
# Dentro do venv ativado
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
> ⚠️ Se usar setx, será necessário abrir um novo terminal para que as variáveis apareçam na sessão atual.
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

## 🔍 Como descobrir o IP da máquina e o nome da interface (Linux / Windows)
> Abaixo há um bloco com comandos úteis que você pode incluir no checklist antes de executar o 
> backend — mostra como localizar o IP que deve ser usado em SERVER_IP e o nome da interface (ex.: wlx..., eth0, Wi‑Fi, Ethernet).

### Linux
- Mostrar todas as interfaces e IPs:
  ```bash
  ip addr show
  # ou abreviado
  ip a
  ```
### Windows 
- No Prompt (cmd) — mostra adaptadores e IPs:
  ```bash
  ipconfig /all
  ```

## 📌 Observações

Para ver tráfego no drilldown, gere pacotes TCP, UDP, ICMP manualmente.

O front-end atual busca dados em http://127.0.0.1:8001/trafego/....
Se mudar a porta ou host do backend, ajuste no código JS.

Se o gráfico aparecer de uma cor só no drilldown → significa que apenas um protocolo foi capturado.
