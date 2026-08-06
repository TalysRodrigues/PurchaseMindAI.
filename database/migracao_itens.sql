-- =============================================================================
-- PurchaseMind AI - Migração: múltiplos itens por ordem de compra
-- =============================================================================
-- Rodar no SQL Editor do Supabase. Essa migração transforma cada "compra"
-- em uma ORDEM DE COMPRA que pode ter vários itens dentro.
--
-- ⚠️ Se você já tem compras cadastradas, os dados de descrição/quantidade
-- antigos serão movidos automaticamente para a nova tabela compra_itens,
-- então nada se perde.
-- =============================================================================

-- 1) Renomeia "descricao" para "titulo" (agora é o título da ordem, não do item)
alter table compras rename column descricao to titulo;

-- 2) Cria a tabela de itens
create table if not exists compra_itens (
    id uuid primary key default gen_random_uuid(),
    compra_id uuid not null references compras(id) on delete cascade,
    descricao text not null,
    quantidade integer not null default 1,
    criado_em timestamptz not null default now()
);

create index if not exists idx_compra_itens_compra on compra_itens(compra_id);

-- 3) Migra os dados existentes: cada compra antiga vira 1 item na tabela nova
insert into compra_itens (compra_id, descricao, quantidade)
select id, titulo, quantidade
from compras
where not exists (
    select 1 from compra_itens where compra_itens.compra_id = compras.id
);

-- 4) Remove a coluna "quantidade" de compras (agora vive em compra_itens)
alter table compras drop column if exists quantidade;

-- =============================================================================
-- Fim da migração
-- =============================================================================
