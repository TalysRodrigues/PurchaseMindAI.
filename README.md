# 🛒 PurchaseMind AI

Assistente inteligente para gestão de compras e controle de entregas, com IA (Claude), Streamlit e Supabase.

Desenvolvido para a **Bovmeat**.

---

## Objetivo

Automatizar e centralizar o processo de gestão de compras — do cadastro à entrega — com apoio de IA para interpretação de linguagem natural, acompanhamento de status e comunicação com fornecedores.

## Funcionalidades

- ✅ **Cadastro manual** de ordens de compra, com **múltiplos itens** por ordem (tabela editável)
- ✅ **Cadastro por linguagem natural** — descreve a compra em texto livre (pode ter vários itens) e a IA interpreta e cadastra
- ✅ **Dashboard** com indicadores por status e notificações
- ✅ **Timeline** de cada ordem de compra, com histórico de mudanças de status
- ✅ **Histórico** completo, filtrável por status
- ✅ **Chat IA** — tira dúvidas sobre o estado atual das compras
- ✅ **Controle de fornecedores**
- ✅ **Notificações automáticas** (nova compra, mudança de status, atraso na entrega, entrega concluída)
- ✅ **Detecção automática de atraso** — compara o prazo de entrega com a data atual
- 🔜 Login individual por usuário (planejado, ainda não implementado)

## Stack

| Camada | Tecnologia |
|---|---|
| Interface | [Streamlit](https://streamlit.io) |
| Banco de dados | [Supabase](https://supabase.com) (PostgreSQL) |
| IA | [Claude](https://www.anthropic.com/claude) (Anthropic API) |
| Hospedagem | [Streamlit Community Cloud](https://streamlit.io/cloud) |

## Estrutura do projeto

```
PurchaseMindAI/
├── app.py                    # Ponto de entrada — inicializa e roteia entre páginas
├── requirements.txt           # Dependências do projeto
├── .env.example                # Modelo de variáveis de ambiente
├── .streamlit/
│   └── config.toml               # Config visual do Streamlit (esconde menus internos)
├── assets/
│   └── logo.png                   # Logo da Bovmeat
├── config/
│   ├── settings.py                 # Lê variáveis de ambiente (.env / Secrets)
│   └── constants.py                # Status de compra, tipos de notificação, limites
├── database/
│   ├── client.py                    # Conexão com o Supabase
│   ├── schema.sql                    # Script de criação das tabelas (instalação nova)
│   ├── migracao_itens.sql             # Migração: adiciona suporte a múltiplos itens
│   ├── compras_repository.py           # CRUD de ordens de compra + itens
│   ├── fornecedores_repository.py       # CRUD de fornecedores
│   └── notificacoes_repository.py        # CRUD de notificações
├── services/
│   ├── compras_service.py            # Validação, transição de status, timeline
│   ├── fornecedores_service.py        # Validação de fornecedores
│   ├── notificacoes_service.py         # Regras de quando notificar
│   └── ia_service.py                    # Integração com a API do Claude
├── components/
│   ├── status_badge.py                # Badge colorido de status
│   ├── compra_card.py                  # Cartão de exibição de uma ordem de compra
│   ├── formulario_compra.py             # Formulário de cadastro (múltiplos itens)
│   └── notificacoes_widget.py            # Lista de notificações
├── pages/
│   ├── dashboard.py, cadastro.py, timeline.py,
│   └── historico.py, chat_ia.py, fornecedores.py
└── utils/
    └── formatters.py                # Formatação de datas, e-mail, texto
```

## Regras de arquitetura

Este projeto segue uma separação estrita de camadas:

1. `app.py` **apenas inicializa** o sistema (config de página, roteamento) — nenhuma regra de negócio aqui.
2. Toda regra de negócio (validação, transição de status, o que notificar) vive em `services/`.
3. Acesso ao banco de dados **somente** em `database/`.
4. `components/` e `pages/` **não acessam o banco diretamente** — sempre passam por `services/`.
5. Qualquer chamada à IA passa pela camada `services/ia_service.py`.

Essa separação existe pra facilitar manutenção: trocar de banco, trocar de provedor de IA, ou redesenhar a interface não deveria exigir reescrever as regras de negócio.

## Modelo de dados

Cada **ordem de compra** (`compras`) pode ter **vários itens** (`compra_itens`), numa relação 1-para-muitos:

```
compras (id, titulo, fornecedor_id, status, prazo_entrega, criado_por, ...)
   └── compra_itens (id, compra_id, descricao, quantidade)
```

O histórico de mudanças de status de cada ordem fica em `compras_historico`, e as notificações do sistema em `notificacoes`.

## Como rodar localmente

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
# preencher .env com as chaves do Supabase e da Anthropic

# 5. Rodar a aplicação
streamlit run app.py
```

## Configuração do banco (Supabase)

**Instalação nova:** rode `database/schema.sql` inteiro no SQL Editor do Supabase.

**Já tem um projeto rodando com a estrutura antiga** (1 item por compra)? Rode `database/migracao_itens.sql` — ele move os dados existentes para o novo formato automaticamente, sem perder nada.

## Variáveis de ambiente necessárias

| Variável | Onde conseguir |
|---|---|
| `SUPABASE_URL` | Supabase → Project Settings → Data API |
| `SUPABASE_KEY` | Supabase → Project Settings → API Keys → **Publishable key** |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → API Keys |

⚠️ Nunca commitar o arquivo `.env` de verdade — ele já está no `.gitignore`. Em produção (Streamlit Cloud), essas variáveis vão em **Secrets** (Manage app → Settings → Secrets), no formato TOML:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "sb_publishable_..."
ANTHROPIC_API_KEY = "sk-ant-..."
```

## Deploy (Streamlit Community Cloud)

1. [share.streamlit.io](https://share.streamlit.io) → login com GitHub
2. **New app** → seleciona o repositório e a branch `main`
3. **Main file path**: `app.py`
4. Em **Advanced settings**, cola os Secrets (formato acima)
5. **Deploy**

## Limitações conhecidas

- **Sem login ainda**: qualquer pessoa com o link acessa o app. Login individual (Supabase Auth) está planejado, mas foi propositalmente adiado.
- **IA depende de créditos**: se a conta da Anthropic ficar sem créditos, o Chat IA e o cadastro por linguagem natural mostram um aviso claro pedindo pra recarregar em [console.anthropic.com](https://console.anthropic.com) → Plans & Billing. O resto do app continua funcionando normalmente.
- **Sessão reseta ao recarregar a página**: isso é uma limitação do próprio Streamlit — nada relacionado ao Supabase.

## Status

🚧 Em desenvolvimento ativo — v0.2.0
