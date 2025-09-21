# Dashboard de Tráfego

## Requisitos
- Python 3.10+ (ou 3.12 conforme seu ambiente)
- git

## Como rodar localmente
```bash
git clone <repo-url>
cd <repo-folder>

# criar e ativar venv
python3 -m venv venv
source venv/bin/activate

# instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# rodar o backend
uvicorn main:app --reload --port 8001
