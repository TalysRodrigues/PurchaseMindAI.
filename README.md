# PurchaseMind AI

Assistente inteligente para gestão de compras e controle de entregas, utilizando IA, Streamlit, GitHub e Supabase.

## Objetivo

Automatizar e centralizar o processo de gestão de compras — do cadastro à entrega — com apoio de IA para interpretação de linguagem natural, acompanhamento de status e comunicação com fornecedores.

## Funcionalidades

- Cadastro por linguagem natural
- Dashboard
- Timeline
- Histórico
- Chat IA
- Controle de fornecedores
- Notificações
- Banco compartilhado

## Stack

- **Frontend/App:** Streamlit
- **Banco de dados:** Supabase
- **IA:** (a definir — Claude / GPT)
- **Versionamento:** GitHub

## Estrutura do projeto

```
PurchaseMindAI/
├── app.py                 # Ponto de entrada — apenas inicializa o sistema
├── requirements.txt        # Dependências do projeto
├── README.md                # Este arquivo
├── CHANGELOG.md             # Histórico de alterações
├── .gitignore
├── .env.example              # Modelo de variáveis de ambiente
├── assets/                   # Imagens, ícones, arquivos estáticos
├── config/                   # Configurações da aplicação
├── database/                 # Toda a comunicação com o banco (Supabase)
├── services/                 # Regras de negócio e lógica da aplicação
├── components/               # Componentes de UI (Streamlit) — não acessam banco
├── pages/                    # Páginas da aplicação
├── utils/                    # Funções utilitárias genéricas
├── docs/                     # Documentação adicional
└── tests/                    # Testes automatizados
```

## Regras de arquitetura

1. `app.py` apenas inicializa o sistema — nenhuma lógica de negócio aqui.
2. Toda regra de negócio fica em `services/`.
3. Acesso ao banco de dados **somente** em `database/`.
4. `components/` não acessam o banco diretamente — sempre passam por `services/`.
5. Qualquer chamada de IA passa pela camada `services/`.

## Ordem de desenvolvimento

1. README.md
2. requirements.txt
3. .env.example
4. config/
5. app.py
6. database/
7. services/
8. components/
9. pages/
10. utils/
11. tests/

## Como rodar (local)

```bash
# 1. Clonar o repositório
git clone <url-do-repo>
cd PurchaseMindAI

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# preencher .env com suas chaves

# 5. Rodar a aplicação
streamlit run app.py
```

## Status

🚧 Projeto em estruturação inicial — código ainda não implementado.
