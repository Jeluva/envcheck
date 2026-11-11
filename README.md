# envcheck

CLI chica en Python para revisar archivos `.env`. Es un proyecto de práctica, no está pensado para producción.

Usa solo la librería estándar (Python 3.8+), no hay nada que instalar.

## Qué hace

- `check [env] [example]`: compara tu `.env` con `.env.example`. Avisa variables que faltan (`FALTA`), que están vacías (`VACIA`) o que sobran (`SOBRA`). Sale con código 1 si falta o está vacía alguna.
- `diff a b`: muestra qué variables se agregaron, sacaron o cambiaron entre dos archivos. Oculta los valores de variables con nombre sensible.
- `redact [env]`: imprime el `.env` con los secretos reemplazados por `***`, útil para pegar en un issue.
- `lint [env]`: detecta líneas inválidas (sin `=`, nombre mal formado) y claves duplicadas.

Un valor se considera secreto si el nombre contiene `SECRET`, `TOKEN`, `PASSWORD`, `PASS`, `KEY`, `PRIVATE` o `CREDENTIAL`.

## Uso

```
python envcheck.py check .env .env.example
python envcheck.py diff .env.staging .env.prod
python envcheck.py redact .env
python envcheck.py lint .env
```

Sin argumentos, `check`, `redact` y `lint` usan `.env` en el directorio actual (y `.env.example` para `check`).

## Límites

El parser es simple: soporta comentarios, `export`, comillas simples/dobles y comentarios al final de línea (` # ...`). No expande variables (`${OTRA}`) ni valores multilínea.

## Tests

```
python -m unittest discover -s tests
```
