#!/usr/bin/env python3
"""Reporta el estado real del equipo Pinti a la Oficina (Railway lee estos archivos desde GitHub).

Uso:
  python3 pinti-organico/oficina/reportar.py agente guionista --estado trabajando --tarea "Escribiendo guion b/d" --episodio pinti_org_01_b_d
  python3 pinti-organico/oficina/reportar.py evento guionista "Guion b/d listo" --a pedagoga --episodio pinti_org_01_b_d [--archivo URL]
  python3 pinti-organico/oficina/reportar.py hallazgo creativo referencia "Creador · TikTok" --detalle "..." --enlace URL [--metricas "..."] [--episodio ...]
  Añade --no-push para solo escribir los archivos (luego haz commit y push tú).
Solo estados reales: nunca simular actividad.
"""
import argparse, datetime, json, os, subprocess, sys

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(DIR, "..", ".."))
IDS = ["productor", "creativo", "estratega", "guionista", "pedagoga", "critico", "arte",
       "sonido", "animador", "montaje", "publicador", "community", "analista"]
ESTADOS = ["trabajando", "revisando", "esperando", "devuelto", "listo", "error", "libre"]
TIPOS = ["referencia", "idea", "guion", "audio", "video"]


def ahora():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(nombre, fila):
    with open(os.path.join(DIR, nombre), "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def push(msg):
    rel = os.path.relpath(DIR, REPO)
    run = lambda *a: subprocess.run(["git", "-C", REPO, *a], check=False, capture_output=True, text=True)
    run("add", rel)
    if run("diff", "--cached", "--quiet").returncode == 0:
        return
    run("commit", "-m", f"Oficina: {msg}")
    for _ in range(3):
        run("fetch", "-q", "origin", "main")
        run("rebase", "-q", "origin/main")
        if run("push", "-q", "origin", "HEAD:main").returncode == 0:
            return
    print("Aviso: no se pudo hacer push; los cambios quedan en local.", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("agente"); a.add_argument("id", choices=IDS)
    a.add_argument("--estado", choices=ESTADOS); a.add_argument("--tarea"); a.add_argument("--episodio")
    a.add_argument("--nota", type=float); a.add_argument("--archivo")
    e = sub.add_parser("evento"); e.add_argument("agente", choices=IDS); e.add_argument("texto")
    e.add_argument("--a", choices=IDS); e.add_argument("--episodio"); e.add_argument("--archivo")
    h = sub.add_parser("hallazgo"); h.add_argument("agente", choices=IDS); h.add_argument("tipo", choices=TIPOS)
    h.add_argument("titulo"); h.add_argument("--detalle"); h.add_argument("--enlace"); h.add_argument("--metricas")
    h.add_argument("--episodio")
    for s in (a, e, h):
        s.add_argument("--no-push", action="store_true")
    o = p.parse_args()
    ts = ahora()
    if o.cmd == "agente":
        ruta = os.path.join(DIR, "agentes.json")
        datos = json.load(open(ruta, encoding="utf-8"))
        d = datos.setdefault(o.id, {})
        for k in ("estado", "tarea", "episodio", "nota", "archivo"):
            v = getattr(o, k)
            if v is not None:
                d[k] = v
        if o.estado == "libre":
            d["tarea"] = o.tarea or ""
            d.pop("nota", None)
        d["actualizado"] = ts
        json.dump(datos, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        msg = f"{o.id} {d.get('estado', '')}"
    elif o.cmd == "evento":
        fila = {"id": f"e-{ts[:10].replace('-', '')}-{ts[11:19].replace(':', '')}-{o.agente}", "agente": o.agente,
                "texto": o.texto, "ts": ts}
        for k in ("a", "episodio", "archivo"):
            if getattr(o, k):
                fila[k] = getattr(o, k)
        append("eventos.jsonl", fila)
        msg = f"evento {o.agente}"
    else:
        fila = {"id": f"{o.tipo[0]}-{ts.replace('-', '').replace(':', '')}-{o.agente}", "agente": o.agente,
                "tipo": o.tipo, "titulo": o.titulo, "ts": ts}
        for k in ("detalle", "enlace", "metricas", "episodio"):
            if getattr(o, k):
                fila[k] = getattr(o, k)
        if fila.get("enlace") and not fila["enlace"].startswith("https://"):
            sys.exit("El enlace debe ser una URL https real.")
        append("hallazgos.jsonl", fila)
        msg = f"hallazgo {o.agente}"
    if not o.no_push:
        push(msg)
    print("ok")


if __name__ == "__main__":
    main()
