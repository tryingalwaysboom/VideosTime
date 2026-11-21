"""Oficina Pinti: dashboard en vivo del equipo de agentes (Railway + PostgreSQL).

Los agentes escriben su estado real en pinti-organico/oficina/ del repo (GitHub).
Esta app lo sincroniza a PostgreSQL (webhook de GitHub al instante + comprobación periódica)
y sirve la oficina 3D, que consulta /api/estado cada pocos segundos.
"""
import hashlib
import hmac
import json
import os
import threading
import time

import psycopg
import requests
import io
from flask import Flask, send_file, Response, abort, jsonify, render_template, request
from psycopg.types.json import Jsonb

DATABASE_URL = os.environ["DATABASE_URL"]
GITHUB_REPO = os.environ.get("GITHUB_REPO", "tryingalwaysboom/VideosTime")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
GITHUB_PATH = os.environ.get("GITHUB_PATH", "pinti-organico/oficina")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
OFICINA_TOKEN = os.environ.get("OFICINA_TOKEN", "")
OFICINA_PASS = os.environ.get("OFICINA_PASS", "")
SYNC_SECONDS = int(os.environ.get("SYNC_SECONDS", "60"))
SYNC_GITHUB = os.environ.get("SYNC_GITHUB", "0") == "1"  # el equipo en Railway escribe directo en la base de datos

app = Flask(__name__)
_wake = threading.Event()
_estado_sync = {"ultimo": None, "error": None}


def db():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def init_db():
    with db() as c:
        c.execute("""
            create table if not exists agentes (id text primary key, datos jsonb not null, actualizado timestamptz default now());
            create table if not exists eventos (id text primary key, datos jsonb not null, ts text not null default '');
            create table if not exists hallazgos (id text primary key, datos jsonb not null, ts text not null default '');
            create table if not exists meta (k text primary key, v text not null);
            insert into meta (k, v) values ('rev', '0') on conflict do nothing;
            create table if not exists tandas (id serial primary key, n int not null default 3, tema text not null default '',
                estado text not null default 'pendiente', nota text not null default '', coste_usd numeric not null default 0,
                creada timestamptz default now(), actualizada timestamptz default now());
            create table if not exists acciones (id bigserial primary key, agente text not null, tipo text not null,
                titulo text not null, contenido text not null default '', ts timestamptz default now());
            create index if not exists acciones_ag on acciones (agente, id);
            create table if not exists aprobaciones (id serial primary key, tanda_id int, tipo text not null, titulo text not null,
                detalle jsonb not null default '{}', creditos int not null default 0, estado text not null default 'pendiente',
                creada timestamptz default now(), respondida timestamptz);
            create table if not exists videos (nombre text primary key, titulo text not null default '', detalle text not null default '',
                datos bytea not null, creada timestamptz default now());
        """)


def bump(c):
    c.execute("update meta set v = (v::bigint + 1)::text where k = 'rev'")


def upsert_agentes(c, datos):
    cambios = 0
    for aid, d in datos.items():
        if not isinstance(d, dict):
            continue
        r = c.execute(
            "insert into agentes (id, datos) values (%s, %s) on conflict (id) do update set datos = excluded.datos, "
            "actualizado = now() where agentes.datos is distinct from excluded.datos", (aid, Jsonb(d)))
        cambios += r.rowcount
    return cambios


def upsert_filas(c, tabla, filas):
    cambios = 0
    for f in filas:
        if not isinstance(f, dict) or not f.get("id"):
            continue
        r = c.execute(
            f"insert into {tabla} (id, datos, ts) values (%s, %s, %s) on conflict (id) do update set "
            f"datos = excluded.datos, ts = excluded.ts where {tabla}.datos is distinct from excluded.datos",
            (f["id"], Jsonb(f), f.get("ts", "")))
        cambios += r.rowcount
    return cambios


def fetch(nombre, c):
    """Descarga un archivo del repo con ETag; devuelve el texto o None si no cambió."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{nombre}?ref={GITHUB_BRANCH}"
    h = {"Accept": "application/vnd.github.raw", "User-Agent": "oficina-pinti"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    fila = c.execute("select v from meta where k = %s", (f"etag:{nombre}",)).fetchone()
    if fila:
        h["If-None-Match"] = fila[0]
    r = requests.get(url, headers=h, timeout=20)
    if r.status_code == 304:
        return None
    r.raise_for_status()
    if r.headers.get("ETag"):
        c.execute("insert into meta (k, v) values (%s, %s) on conflict (k) do update set v = excluded.v",
                  (f"etag:{nombre}", r.headers["ETag"]))
    return r.text


def sync():
    with db() as c:
        cambios = 0
        txt = fetch("agentes.json", c)
        if txt is not None:
            cambios += upsert_agentes(c, json.loads(txt))
        for nombre, tabla in (("eventos.jsonl", "eventos"), ("hallazgos.jsonl", "hallazgos")):
            txt = fetch(nombre, c)
            if txt is not None:
                filas = [json.loads(l) for l in txt.splitlines() if l.strip()]
                cambios += upsert_filas(c, tabla, filas)
        if cambios:
            bump(c)
    _estado_sync["ultimo"] = time.time()


def bucle():
    while True:
        try:
            sync()
            _estado_sync["error"] = None
        except Exception as ex:  # noqa: BLE001 - se informa en /health y se reintenta
            _estado_sync["error"] = str(ex)[:300]
        _wake.wait(SYNC_SECONDS)
        _wake.clear()


init_db()
if SYNC_GITHUB:
    threading.Thread(target=bucle, daemon=True).start()


@app.before_request
def proteger():
    if not OFICINA_PASS or request.path in ("/health", "/webhook/github") or request.path.startswith("/api/escribir"):
        return None
    a = request.authorization
    if a and hmac.compare_digest(a.password or "", OFICINA_PASS):
        return None
    return Response("Acceso a la Oficina Pinti", 401, {"WWW-Authenticate": 'Basic realm="Oficina Pinti"'})


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/estado")
def estado():
    with db() as c:
        rev = c.execute("select v from meta where k = 'rev'").fetchone()[0]
        if request.args.get("rev") == rev:
            return jsonify(rev=rev, sin_cambios=True)
        agentes = {r[0]: r[1] for r in c.execute("select id, datos from agentes")}
        eventos = [r[0] for r in c.execute("select datos from eventos order by ts desc, id desc limit 60")]
        hallazgos = [r[0] for r in c.execute("select datos from hallazgos order by ts desc, id desc limit 150")]
        tandas = [dict(id=r[0], n=r[1], tema=r[2], estado=r[3], nota=r[4], coste_usd=float(r[5]))
                  for r in c.execute("select id, n, tema, estado, nota, coste_usd from tandas order by id desc limit 5")]
        aprob = [dict(id=r[0], tanda_id=r[1], titulo=r[2], detalle=r[3], creditos=r[4], estado=r[5])
                 for r in c.execute("select id, tanda_id, titulo, detalle, creditos, estado from aprobaciones "
                                    "order by id desc limit 5")]
    return jsonify(rev=rev, agentes=agentes, eventos=eventos, hallazgos=hallazgos, tandas=tandas, aprobaciones=aprob)


@app.get("/api/pantalla/<aid>")
def pantalla(aid):
    desde = request.args.get("desde", type=int)
    with db() as c:
        if desde:
            filas = c.execute("select id, tipo, titulo, contenido, ts from acciones where agente = %s and id > %s "
                              "order by id limit 60", (aid, desde)).fetchall()
        else:
            filas = list(reversed(c.execute("select id, tipo, titulo, contenido, ts from acciones where agente = %s "
                                            "order by id desc limit 25", (aid,)).fetchall()))
    return jsonify([dict(id=r[0], tipo=r[1], titulo=r[2], contenido=r[3], ts=r[4].isoformat()) for r in filas])


@app.get("/api/videos")
def videos():
    with db() as c:
        return jsonify([dict(nombre=r[0], titulo=r[1], detalle=r[2], creada=r[3].isoformat(), mb=round(r[4] / 1e6, 1))
                        for r in c.execute("select nombre, titulo, detalle, creada, length(datos) from videos "
                                           "order by creada desc limit 100")])


@app.get("/video/<nombre>.mp4")
def video(nombre):
    with db() as c:
        f = c.execute("select datos from videos where nombre = %s", (nombre,)).fetchone()
    if not f:
        abort(404)
    return send_file(io.BytesIO(bytes(f[0])), mimetype="video/mp4", conditional=True, as_attachment=bool(request.args.get("dl")),
                     download_name=f"{nombre}.mp4")


@app.post("/api/tanda")
def nueva_tanda():
    p = request.get_json(force=True, silent=True) or {}
    n = max(1, min(int(p.get("n") or 3), 6))
    tema = str(p.get("tema") or "")[:200]
    with db() as c:
        if c.execute("select 1 from tandas where estado in ('pendiente','en_curso')").fetchone():
            return jsonify(error="Ya hay una tanda en marcha"), 409
        tid = c.execute("insert into tandas (n, tema) values (%s, %s) returning id", (n, tema)).fetchone()[0]
        bump(c)
    return jsonify(id=tid)


@app.post("/api/tanda/<int:tid>/cancelar")
def cancelar_tanda(tid):
    with db() as c:
        c.execute("update tandas set estado = 'cancelada' where id = %s and estado in ('pendiente','en_curso')", (tid,))
        c.execute("update aprobaciones set estado = 'rechazada', respondida = now() where tanda_id = %s and estado = 'pendiente'", (tid,))
        bump(c)
    return jsonify(ok=True)


@app.post("/api/aprobar/<int:aid>")
def aprobar(aid):
    p = request.get_json(force=True, silent=True) or {}
    nuevo = "aprobada" if p.get("ok") else "rechazada"
    with db() as c:
        c.execute("update aprobaciones set estado = %s, respondida = now() where id = %s and estado = 'pendiente'", (nuevo, aid))
        bump(c)
    return jsonify(estado=nuevo)


@app.post("/webhook/github")
def webhook():
    if GITHUB_WEBHOOK_SECRET:
        firma = request.headers.get("X-Hub-Signature-256", "")
        esperada = "sha256=" + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), request.get_data(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(firma, esperada):
            abort(401)
    _wake.set()
    return ("", 202)


def autorizado():
    if not OFICINA_TOKEN:
        abort(503, "Falta OFICINA_TOKEN")
    if not hmac.compare_digest(request.headers.get("Authorization", ""), f"Bearer {OFICINA_TOKEN}"):
        abort(401)


@app.post("/api/escribir")
def escribir():
    """Escritura directa (para agentes que corran fuera de esta nube): {agentes:{}, eventos:[], hallazgos:[]}."""
    autorizado()
    p = request.get_json(force=True, silent=True) or {}
    with db() as c:
        n = upsert_agentes(c, p.get("agentes") or {})
        n += upsert_filas(c, "eventos", p.get("eventos") or [])
        n += upsert_filas(c, "hallazgos", p.get("hallazgos") or [])
        if n:
            bump(c)
    return jsonify(cambios=n)


@app.get("/health")
def health():
    return jsonify(ok=True, ultimo_sync=_estado_sync["ultimo"], error_sync=_estado_sync["error"])
