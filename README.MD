# Atlas Workout System - Backend

Backend do Atlas Workout System — uma plataforma para criação de treinos personalizados, registro em tempo real e acompanhamento de progresso.

## 🚀 Funcionalidades

- **Gerenciamento de Exercícios**: Exercícios pré-cadastrados com API exclusiva para administrador  
- **Autenticação de Usuários**: Sistema seguro de registro e login  
- **Pacotes de Treino**: Criação e gerenciamento de rotinas de treino personalizadas  
- **Sessões de Treino**: Registro diário de exercícios com pesos, repetições e dados de cardio  
- **API de Análises**: Monitoramento de progresso e geração de estatísticas  
- **Grupos Competitivos**: Competição entre usuários com comparação de desempenho  

## 🧩 Tecnologias

- **Linguagem**: Python 3.11+  
- **Framework**: FastAPI (Clean Architecture)  
- **Banco de Dados**: MongoDB  
- **ODM**: PyMongo  

## 🧱 Estrutura do Projeto

```
backend/
├── src/
│   ├── core/           # Configuração e banco de dados
│   ├── domain/         # Entidades (modelos de negócio)
│   ├── infrastructure/ # Repositórios (acesso a dados)
│   ├── application/    # Casos de uso (lógica de negócio)
│   └── presentation/   # Rotas da API
└── requirements.txt
```

## ⚙️ Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- MongoDB (local ou em nuvem)
- Ambiente virtual (recomendado)

### Configuração
```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

A API ficará disponível em:  
👉 http://localhost:8000  
👉 Documentação: http://localhost:8000/docs