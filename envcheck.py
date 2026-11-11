#!/usr/bin/env python3
"""envcheck: herramientas chicas para archivos .env (solo libreria estandar)."""
import argparse
import re
import sys

KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SECRET_HINTS = ("SECRET", "TOKEN", "PASSWORD", "PASS", "KEY", "PRIVATE", "CREDENTIAL")


def parse(text):
    """Devuelve (valores, problemas, duplicadas).

    valores: dict clave -> valor (la ultima aparicion gana).
    problemas: lista de (nro_linea, mensaje).
    duplicadas: lista de (clave, nro_linea).
    """
    values, problems, dups = {}, [], []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            problems.append((n, "linea sin '='"))
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if not KEY_RE.match(key):
            problems.append((n, f"nombre de variable invalido: {key!r}"))
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        elif " #" in val:
            val = val.split(" #", 1)[0].rstrip()
        if key in values:
            dups.append((key, n))
        values[key] = val
    return values, problems, dups


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return parse(f.read())
    except OSError as e:
        sys.exit(f"error: no pude leer {path}: {e.strerror}")


def is_secret(key):
    return any(h in key.upper() for h in SECRET_HINTS)


def mask(key, val):
    if not val:
        return ""
    return "***" if is_secret(key) else val


def cmd_check(args):
    """Compara un .env contra su plantilla (.env.example)."""
    env, _, _ = load(args.env)
    tpl, _, _ = load(args.example)
    missing = sorted(set(tpl) - set(env))
    extra = sorted(set(env) - set(tpl))
    empty = sorted(k for k in tpl if k in env and not env[k] and tpl[k] == "")
    for k in missing:
        print(f"FALTA   {k}")
    for k in empty:
        print(f"VACIA   {k}")
    for k in extra:
        print(f"SOBRA   {k}")
    ok = not missing and not empty
    print("OK" if ok else f"{len(missing)} faltan, {len(empty)} vacias, {len(extra)} sobran")
    return 0 if ok else 1


def cmd_diff(args):
    """Muestra que cambia entre dos .env (valores de secretos ocultos)."""
    a, _, _ = load(args.a)
    b, _, _ = load(args.b)
    changes = 0
    for k in sorted(set(a) | set(b)):
        if k not in b:
            print(f"- {k}={mask(k, a[k])}")
        elif k not in a:
            print(f"+ {k}={mask(k, b[k])}")
        elif a[k] != b[k]:
            print(f"~ {k}: {mask(k, a[k])!r} -> {mask(k, b[k])!r}")
        else:
            continue
        changes += 1
    if not changes:
        print("sin diferencias")
    return 1 if changes else 0


def cmd_redact(args):
    """Imprime el .env con los valores de secretos reemplazados por ***."""
    env, _, _ = load(args.env)
    for k, v in env.items():
        print(f"{k}={mask(k, v)}")
    return 0


def cmd_lint(args):
    """Detecta lineas invalidas y claves duplicadas."""
    _, problems, dups = load(args.env)
    for n, msg in problems:
        print(f"linea {n}: {msg}")
    for k, n in dups:
        print(f"linea {n}: clave duplicada {k}")
    if not problems and not dups:
        print("OK")
    return 1 if problems or dups else 0


def build_parser():
    p = argparse.ArgumentParser(prog="envcheck", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help=cmd_check.__doc__)
    c.add_argument("env", nargs="?", default=".env")
    c.add_argument("example", nargs="?", default=".env.example")
    c.set_defaults(fn=cmd_check)
    d = sub.add_parser("diff", help=cmd_diff.__doc__)
    d.add_argument("a")
    d.add_argument("b")
    d.set_defaults(fn=cmd_diff)
    r = sub.add_parser("redact", help=cmd_redact.__doc__)
    r.add_argument("env", nargs="?", default=".env")
    r.set_defaults(fn=cmd_redact)
    l = sub.add_parser("lint", help=cmd_lint.__doc__)
    l.add_argument("env", nargs="?", default=".env")
    l.set_defaults(fn=cmd_lint)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
