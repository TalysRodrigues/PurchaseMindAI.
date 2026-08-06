-- =============================================================================
-- PurchaseMind AI - Schema do banco (Supabase / PostgreSQL)
-- =============================================================================
-- Rodar este script no SQL Editor do Supabase para criar as tabelas iniciais.
-- =============================================================================

-- Extensão para gerar UUIDs
create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------------------
-- Fornecedores
-- -----------------------------------------------------------------------------
create table if not exists fornecedores (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    contato text,
    email text,
    telefone text,
    observacoes text,
    criado_em timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Compras (ordens de compra — cada uma pode ter vários itens, ver compra_itens)
-- -----------------------------------------------------------------------------
create table if not exists compras (
    id uuid primary key default gen_random_uuid(),
    titulo text not null,
    fornecedor_id uuid references fornecedores(id) on delete set null,
    status text not null default 'pendente'
        check (status in ('pendente', 'aprovada', 'em_transito', 'entregue', 'cancelada')),
    prazo_entrega date,
    criado_por text,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Itens de cada ordem de compra
-- -----------------------------------------------------------------------------
create table if not exists compra_itens (
    id uuid primary key default gen_random_uuid(),
    compra_id uuid not null references compras(id) on delete cascade,
    descricao text not null,
    quantidade integer not null default 1,
    criado_em timestamptz not null default now()
);

create index if not exists idx_compra_itens_compra on compra_itens(compra_id);


-- -----------------------------------------------------------------------------
-- Histórico de status (timeline de cada compra)
-- -----------------------------------------------------------------------------
create table if not exists compras_historico (
    id uuid primary key default gen_random_uuid(),
    compra_id uuid not null references compras(id) on delete cascade,
    status_anterior text,
    status_novo text not null,
    observacao text,
    criado_em timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Notificações
-- -----------------------------------------------------------------------------
create table if not exists notificacoes (
    id uuid primary key default gen_random_uuid(),
    compra_id uuid references compras(id) on delete cascade,
    tipo text not null,
    mensagem text not null,
    lida boolean not null default false,
    criado_em timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Índices úteis
-- -----------------------------------------------------------------------------
create index if not exists idx_compras_status on compras(status);
create index if not exists idx_compras_fornecedor on compras(fornecedor_id);
create index if not exists idx_historico_compra on compras_historico(compra_id);
create index if not exists idx_notificacoes_compra on notificacoes(compra_id);
create index if not exists idx_notificacoes_lida on notificacoes(lida);

-- -----------------------------------------------------------------------------
-- Trigger: atualizar "atualizado_em" automaticamente
-- -----------------------------------------------------------------------------
create or replace function set_atualizado_em()
returns trigger as $$
begin
    new.atualizado_em = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_compras_atualizado_em on compras;
create trigger trg_compras_atualizado_em
    before update on compras
    for each row
    execute function set_atualizado_em();
