-- Geraete-Abgleich fuer den Reisebegleiter Suedafrika 2026
-- Liegt im Supabase-Projekt "Pure Lust" (ywpyurlzrexznzlarubm), Region eu-central-2.
-- Isoliert: eigene Tabelle + zwei Funktionen. Entfernen mit:
--   drop function if exists public.suedafrika_sync_put(text,jsonb);
--   drop function if exists public.suedafrika_sync_get(text);
--   drop table if exists public.suedafrika_sync;

create table if not exists public.suedafrika_sync (
  k          text primary key check (char_length(k) between 16 and 64),
  payload    jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.suedafrika_sync enable row level security;   -- absichtlich ohne Policy
revoke all on table public.suedafrika_sync from anon, authenticated;

create or replace function public.suedafrika_sync_get(p_key text)
returns jsonb language plpgsql security definer set search_path = public, pg_temp as $$
declare v jsonb;
begin
  if p_key is null or char_length(p_key) < 16 or char_length(p_key) > 64 then
    raise exception 'ungueltiger schluessel'; end if;
  select payload into v from public.suedafrika_sync where k = p_key;
  return coalesce(v, '{}'::jsonb);
end; $$;

create or replace function public.suedafrika_sync_put(p_key text, p_payload jsonb)
returns jsonb language plpgsql security definer set search_path = public, pg_temp as $$
declare v jsonb;
begin
  if p_key is null or char_length(p_key) < 16 or char_length(p_key) > 64 then
    raise exception 'ungueltiger schluessel'; end if;
  if p_payload is null or jsonb_typeof(p_payload) <> 'object' then
    raise exception 'payload muss ein objekt sein'; end if;
  if pg_column_size(p_payload) > 262144 then
    raise exception 'payload zu gross'; end if;
  insert into public.suedafrika_sync as s (k, payload, updated_at)
  values (p_key, p_payload, now())
  on conflict (k) do update set payload = excluded.payload, updated_at = now()
  returning s.payload into v;
  return v;
end; $$;

revoke all on function public.suedafrika_sync_get(text)        from public;
revoke all on function public.suedafrika_sync_put(text, jsonb) from public;
grant execute on function public.suedafrika_sync_get(text)        to anon, authenticated;
grant execute on function public.suedafrika_sync_put(text, jsonb) to anon, authenticated;
