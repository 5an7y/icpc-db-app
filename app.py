import json
from pathlib import Path
from flask import Flask, render_template, send_file, abort
import mimetypes

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMAS_FILE = DATA_DIR / "temas.json"
CONCURSOS_FILE = DATA_DIR / "concursos.json"
CONCURSOS_CATEGORIAS_FILE = DATA_DIR / "concursos_categorias.json"
PROBLEMAS_FILE = DATA_DIR / "problemas.json"
CURSOS_FILE = DATA_DIR / "cursos.json"

def cargar_temas():
    if not TEMAS_FILE.exists():
        return []
    with TEMAS_FILE.open("r", encoding="utf-8") as f:
        temas = json.load(f)
    # ordenar por campo 'orden'
    temas.sort(key=lambda t: t.get("orden", 0))
    return temas

def guardar_temas(temas):
    with TEMAS_FILE.open("w", encoding="utf-8") as f:
        json.dump(temas, f, indent=4, ensure_ascii=False)

def obtener_categorias():
    temas = cargar_temas()
    categorias = sorted({t.get("categoria") for t in temas if t.get("categoria")})
    return categorias

def cargar_concursos():
    if not CONCURSOS_FILE.exists():
        return []
    with CONCURSOS_FILE.open("r", encoding="utf-8") as f:
        concursos = json.load(f)
    # ordenar por año descendente y luego por nombre
    concursos.sort(key=lambda c: (-int(c.get("anio", 0)), c.get("nombre", "")))
    return concursos


def guardar_concursos(concursos):
    with CONCURSOS_FILE.open("w", encoding="utf-8") as f:
        json.dump(concursos, f, indent=4, ensure_ascii=False)

def cargar_categorias_concursos():
    # Lee las categorías con orden desde archivo (si existe)
    if CONCURSOS_CATEGORIAS_FILE.exists():
        with CONCURSOS_CATEGORIAS_FILE.open("r", encoding="utf-8") as f:
            categorias = json.load(f)
    else:
        categorias = []

    # Asegurar que todas las categorías presentes en concursos existan aquí
    concursos = cargar_concursos()
    nombres_existentes = {c["nombre"] for c in categorias}
    categorias_en_concursos = set()

    for conc in concursos:
        cat = conc.get("categoria") or "Sin categoría"
        categorias_en_concursos.add(cat)

    # Asignar orden nuevo al final para las categorías que falten
    if categorias:
        max_orden = max(c["orden"] for c in categorias)
    else:
        max_orden = 0

    for cat in sorted(categorias_en_concursos):
        if cat not in nombres_existentes:
            max_orden += 1
            categorias.append({
                "nombre": cat,
                "orden": max_orden
            })

    # Ordenar internamente por 'orden'
    categorias.sort(key=lambda c: c["orden"])

    # Guardar de vuelta por si agregamos nuevas
    guardar_categorias_concursos(categorias)

    return categorias

def guardar_categorias_concursos(categorias):
    with CONCURSOS_CATEGORIAS_FILE.open("w", encoding="utf-8") as f:
        json.dump(categorias, f, indent=4, ensure_ascii=False)

def cargar_problemas():
    if not PROBLEMAS_FILE.exists():
        return []
    with PROBLEMAS_FILE.open("r", encoding="utf-8") as f:
        probs = json.load(f)
    return probs


def guardar_problemas(problemas):
    with PROBLEMAS_FILE.open("w", encoding="utf-8") as f:
        json.dump(problemas, f, indent=4, ensure_ascii=False)

def calcular_tema_principal(problema, temas):
    """
    Devuelve el nombre del 'tema principal' del problema:
    el tema con mayor 'orden' de entre los temas asociados.
    Si no tiene temas, devuelve 'Sin tema principal'.
    """
    nombres_temas_problema = problema.get("temas") or []
    if not nombres_temas_problema:
        return "Sin tema principal"

    orden_por_nombre = {t["nombre"]: t.get("orden", 0) for t in temas}

    # usamos -1 si el tema no existe en la lista de temas
    return max(
        nombres_temas_problema,
        key=lambda nombre: orden_por_nombre.get(nombre, -1)
    )


def agrupar_problemas_por_tema_principal(problemas, temas):
    """
    Regresa una lista de grupos:
    [
      {
        "nombre": "Segment Tree",
        "problemas": [ ... lista de problemas ... ]
      },
      ...
    ]
    Los grupos se ordenan por el 'orden' del Tema.
    Dentro de cada grupo:
      - primero los etiquetados como Introductorios,
      - luego el resto en el orden original.
    """
    # por si queremos usar el orden original como tie-breaker
    for idx, p in enumerate(problemas):
        p["_idx"] = idx

    grupos_dict = {}  # nombre_tema_principal -> lista de problemas

    for p in problemas:
        tema_principal = calcular_tema_principal(p, temas)
        p["_tema_principal"] = tema_principal
        grupos_dict.setdefault(tema_principal, []).append(p)

    # Orden de grupos: primero los temas en su orden, luego extra, luego 'Sin tema principal'
    nombres_grupos_ordenados = []

    nombres_temas = [t["nombre"] for t in temas]
    for nombre in nombres_temas:
        if nombre in grupos_dict:
            nombres_grupos_ordenados.append(nombre)

    otros = [
        nombre for nombre in grupos_dict.keys()
        if nombre not in nombres_grupos_ordenados
        and nombre != "Sin tema principal"
    ]
    otros.sort()
    nombres_grupos_ordenados.extend(otros)

    if "Sin tema principal" in grupos_dict:
        nombres_grupos_ordenados.append("Sin tema principal")

    grupos = []
    for nombre in nombres_grupos_ordenados:
        lista = grupos_dict[nombre]

        # Introductorios primero (etiqueta == 'introductorio', case-insensitive)
        def es_introductorio(p):
            return (p.get("etiqueta", "") or "").strip().lower() == "introductorio"

        lista.sort(key=lambda p: (not es_introductorio(p), p["_idx"]))

        grupos.append({
            "nombre": nombre,
            "problemas": lista,
        })

    return grupos

def cargar_cursos():
    if not CURSOS_FILE.exists():
        return []
    with CURSOS_FILE.open("r", encoding="utf-8") as f:
        cursos = json.load(f)
    # ordenar por nombre alfabéticamente
    cursos.sort(key=lambda c: c.get("nombre", ""))
    return cursos

def guardar_cursos(cursos):
    with CURSOS_FILE.open("w", encoding="utf-8") as f:
        json.dump(cursos, f, indent=4, ensure_ascii=False)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/temas")
def lista_temas():
    temas = cargar_temas()
    return render_template("temas_list.html", temas=temas)

from flask import request, redirect, url_for


@app.route("/temas/nuevo", methods=["GET", "POST"])
def nuevo_tema():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        categoria_existente = request.form.get("categoria_existente", "").strip()
        categoria_nueva = request.form.get("categoria_nueva", "").strip()
        categoria = categoria_nueva or categoria_existente  # prioriza nueva si se escribió
        ruta = request.form["ruta"].strip()

        temas = cargar_temas()
        nuevo_orden = (temas[-1]["orden"] + 1) if temas else 1

        temas.append({
            "nombre": nombre,
            "categoria": categoria,
            "orden": nuevo_orden,
            "ruta": ruta
        })

        guardar_temas(temas)
        return redirect(url_for("lista_temas"))

    return render_template("temas_form.html", modo="nuevo", tema=None, categorias=obtener_categorias())

@app.route("/temas/editar/<nombre>", methods=["GET", "POST"])
def editar_tema(nombre):
    temas = cargar_temas()
    tema = next((t for t in temas if t["nombre"] == nombre), None)

    if not tema:
        return "Tema no encontrado", 404

    if request.method == "POST":
        nuevo_nombre = request.form["nombre"].strip()
        categoria_existente = request.form.get("categoria_existente", "").strip()
        categoria_nueva = request.form.get("categoria_nueva", "").strip()
        categoria = categoria_nueva or categoria_existente
        ruta = request.form["ruta"].strip()

        tema["nombre"] = nuevo_nombre
        tema["categoria"] = categoria
        tema["ruta"] = ruta

        guardar_temas(temas)
        return redirect(url_for("lista_temas"))

    return render_template("temas_form.html", modo="editar", tema=tema, categorias=obtener_categorias())

@app.route("/temas/eliminar/<nombre>", methods=["POST"])
def eliminar_tema(nombre):
    temas = cargar_temas()
    nuevos = [t for t in temas if t["nombre"] != nombre]

    guardar_temas(nuevos)
    return redirect(url_for("lista_temas"))

@app.route("/temas/mover/<nombre>/<direccion>", methods=["POST"])
def mover_tema(nombre, direccion):
    temas = cargar_temas()  # ya viene ordenado por 'orden'
    idx = next((i for i, t in enumerate(temas) if t["nombre"] == nombre), None)

    if idx is None:
        return "Tema no encontrado", 404

    if direccion == "up" and idx > 0:
        # intercambiar orden con el de arriba
        temas[idx]["orden"], temas[idx - 1]["orden"] = temas[idx - 1]["orden"], temas[idx]["orden"]
    elif direccion == "down" and idx < len(temas) - 1:
        # intercambiar orden con el de abajo
        temas[idx]["orden"], temas[idx + 1]["orden"] = temas[idx + 1]["orden"], temas[idx]["orden"]

    guardar_temas(temas)
    return redirect(url_for("lista_temas"))

@app.route("/temas/ver/<nombre>")
def ver_tema(nombre):
    temas = cargar_temas()
    tema = next((t for t in temas if t["nombre"] == nombre), None)

    if not tema or not tema.get("ruta"):
        return "No hay archivo asociado a este tema.", 404

    # Interpretar la ruta como relativa al directorio del proyecto
    file_path = (BASE_DIR / tema["ruta"]).resolve()

    if not file_path.exists():
        return f"Archivo no encontrado: {file_path}", 404

    mime_type, _ = mimetypes.guess_type(str(file_path))
    # send_file se encarga de mostrar pdf en el navegador, txt/md como descarga o texto
    return send_file(file_path, mimetype=mime_type or "application/octet-stream")

@app.route("/concursos")
def lista_concursos():
    concursos = cargar_concursos()
    categorias = cargar_categorias_concursos()

    # Agrupar concursos por categoría
    concursos_por_categoria = {}
    for conc in concursos:
        cat = conc.get("categoria") or "Sin categoría"
        concursos_por_categoria.setdefault(cat, []).append(conc)

    # Ordenar los concursos de cada categoría por año (desc) y nombre
    for cat, lista in concursos_por_categoria.items():
        lista.sort(key=lambda c: (-(c["anio"] or 0), c["nombre"]))

    return render_template(
        "concursos_list.html",
        categorias=categorias,
        concursos_por_categoria=concursos_por_categoria,
    )


@app.route("/concursos/nuevo", methods=["GET", "POST"])
def nuevo_concurso():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        anio_raw = request.form["anio"].strip()
        categoria_existente = request.form.get("categoria_existente", "").strip()
        categoria_nueva = request.form.get("categoria_nueva", "").strip()
        categoria = categoria_nueva or categoria_existente  # prioriza nueva si existe

        try:
            anio = int(anio_raw) if anio_raw else None
        except ValueError:
            anio = None

        concursos = cargar_concursos()

        if any(c["nombre"] == nombre for c in concursos):
            return "Ya existe un concurso con ese nombre", 400

        concursos.append({
            "nombre": nombre,
            "anio": anio,
            "categoria": categoria
        })
        guardar_concursos(concursos)

        # actualizar categorías (por si se creó una nueva)
        cargar_categorias_concursos()

        return redirect(url_for("lista_concursos"))

    categorias = cargar_categorias_concursos()
    return render_template("concursos_form.html", modo="nuevo", concurso=None, categorias=categorias)


@app.route("/concursos/editar/<nombre>", methods=["GET", "POST"])
def editar_concurso(nombre):
    concursos = cargar_concursos()
    concurso = next((c for c in concursos if c["nombre"] == nombre), None)

    if not concurso:
        return "Concurso no encontrado", 404

    if request.method == "POST":
        nuevo_nombre = request.form["nombre"].strip()
        anio_raw = request.form["anio"].strip()
        categoria_existente = request.form.get("categoria_existente", "").strip()
        categoria_nueva = request.form.get("categoria_nueva", "").strip()
        categoria = categoria_nueva or categoria_existente

        try:
            anio = int(anio_raw) if anio_raw else None
        except ValueError:
            anio = None

        concurso["nombre"] = nuevo_nombre
        concurso["anio"] = anio
        concurso["categoria"] = categoria

        guardar_concursos(concursos)
        cargar_categorias_concursos()  # por si aparece una nueva categoría

        return redirect(url_for("lista_concursos"))

    categorias = cargar_categorias_concursos()
    return render_template("concursos_form.html", modo="editar", concurso=concurso, categorias=categorias)



@app.route("/concursos/eliminar/<nombre>", methods=["POST"])
def eliminar_concurso(nombre):
    concursos = cargar_concursos()
    nuevos = [c for c in concursos if c["nombre"] != nombre]
    guardar_concursos(nuevos)
    return redirect(url_for("lista_concursos"))

@app.route("/concursos/categorias/mover/<nombre>/<direccion>", methods=["POST"])
def mover_categoria_concurso(nombre, direccion):
    categorias = cargar_categorias_concursos()
    idx = next((i for i, c in enumerate(categorias) if c["nombre"] == nombre), None)

    if idx is None:
        return "Categoría no encontrada", 404

    if direccion == "up" and idx > 0:
        categorias[idx]["orden"], categorias[idx - 1]["orden"] = categorias[idx - 1]["orden"], categorias[idx]["orden"]
    elif direccion == "down" and idx < len(categorias) - 1:
        categorias[idx]["orden"], categorias[idx + 1]["orden"] = categorias[idx + 1]["orden"], categorias[idx]["orden"]

    guardar_categorias_concursos(categorias)
    return redirect(url_for("lista_concursos"))

@app.route("/problemas")
def lista_problemas():
    problemas = cargar_problemas()
    temas = cargar_temas()
    grupos = agrupar_problemas_por_tema_principal(problemas, temas)
    return render_template("problemas_list.html", grupos=grupos)


@app.route("/problemas/nuevo", methods=["GET", "POST"])
def nuevo_problema():
    temas = cargar_temas()
    concursos = cargar_concursos()

    if request.method == "POST":
        problema_id = request.form["id"].strip()
        url_p = request.form["url"].strip()
        concurso = request.form.get("concurso", "").strip()
        temas_seleccionados = request.form.getlist("temas")
        ruta_solucion = request.form["ruta_solucion"].strip()
        etiqueta = request.form["etiqueta"].strip()

        problemas = cargar_problemas()
        if any(p["id"] == problema_id for p in problemas):
            return "Ya existe un problema con ese ID", 400

        problemas.append({
            "id": problema_id,
            "url": url_p,
            "concurso": concurso,
            "temas": temas_seleccionados,
            "ruta_solucion": ruta_solucion,
            "etiqueta": etiqueta,
        })
        guardar_problemas(problemas)
        return redirect(url_for("lista_problemas"))

    return render_template(
        "problemas_form.html",
        modo="nuevo",
        problema=None,
        temas=temas,
        concursos=concursos,
    )

@app.route("/problemas/editar/<problema_id>", methods=["GET", "POST"])
def editar_problema(problema_id):
    temas = cargar_temas()
    concursos = cargar_concursos()
    problemas = cargar_problemas()

    problema = next((p for p in problemas if p["id"] == problema_id), None)
    if not problema:
        return "Problema no encontrado", 404

    if request.method == "POST":
        nuevo_id = request.form["id"].strip()
        url_p = request.form["url"].strip()
        concurso = request.form.get("concurso", "").strip()
        temas_seleccionados = request.form.getlist("temas")
        ruta_solucion = request.form["ruta_solucion"].strip()
        etiqueta = request.form["etiqueta"].strip()

        # validar que el nuevo ID no choque con otro problema distinto
        if nuevo_id != problema_id and any(p["id"] == nuevo_id for p in problemas):
            return "Ya existe otro problema con ese ID", 400

        problema["id"] = nuevo_id
        problema["url"] = url_p
        problema["concurso"] = concurso
        problema["temas"] = temas_seleccionados
        problema["ruta_solucion"] = ruta_solucion
        problema["etiqueta"] = etiqueta


        guardar_problemas(problemas)
        return redirect(url_for("lista_problemas"))

    return render_template(
        "problemas_form.html",
        modo="editar",
        problema=problema,
        temas=temas,
        concursos=concursos,
    )

@app.route("/problemas/eliminar/<problema_id>", methods=["POST"])
def eliminar_problema(problema_id):
    problemas = cargar_problemas()
    nuevos = [p for p in problemas if p["id"] != problema_id]
    guardar_problemas(nuevos)
    return redirect(url_for("lista_problemas"))

@app.route("/problemas/ver_solucion/<problema_id>")
def ver_solucion_problema(problema_id):
    problemas = cargar_problemas()
    problema = next((p for p in problemas if p["id"] == problema_id), None)

    if not problema or not problema.get("ruta_solucion"):
        return "No hay archivo de solución asociado a este problema.", 404

    file_path = (BASE_DIR / problema["ruta_solucion"]).resolve()

    if not file_path.exists():
        return f"Archivo no encontrado: {file_path}", 404

    mime_type, _ = mimetypes.guess_type(str(file_path))
    return send_file(file_path, mimetype=mime_type or "application/octet-stream")

@app.route("/problemas/mover/<problema_id>/<direccion>", methods=["POST"])
def mover_problema(problema_id, direccion):
    problemas = cargar_problemas()
    temas = cargar_temas()

    idx = next((i for i, p in enumerate(problemas) if p["id"] == problema_id), None)
    if idx is None:
        return "Problema no encontrado", 404

    tema_main = calcular_tema_principal(problemas[idx], temas)

    # Índices de todos los problemas con el mismo tema principal
    indices_grupo = [
        i for i, p in enumerate(problemas)
        if calcular_tema_principal(p, temas) == tema_main
    ]

    pos = indices_grupo.index(idx)

    if direccion == "up" and pos > 0:
        other_idx = indices_grupo[pos - 1]
        problemas[idx], problemas[other_idx] = problemas[other_idx], problemas[idx]
    elif direccion == "down" and pos < len(indices_grupo) - 1:
        other_idx = indices_grupo[pos + 1]
        problemas[idx], problemas[other_idx] = problemas[other_idx], problemas[idx]

    guardar_problemas(problemas)
    return redirect(url_for("lista_problemas"))


@app.route("/cursos")
def lista_cursos():
    cursos = cargar_cursos()
    return render_template("cursos_list.html", cursos=cursos)

@app.route("/cursos/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form["descripcion"].strip()

        cursos = cargar_cursos()
        if any(c["nombre"] == nombre for c in cursos):
            return "Ya existe un curso con ese nombre", 400

        cursos.append({
            "nombre": nombre,
            "descripcion": descripcion,
            "usados_problemas": [],
            "usados_temas": [],
            "usados_concursos": []
        })
        guardar_cursos(cursos)
        return redirect(url_for("lista_cursos"))

    return render_template("cursos_form.html", modo="nuevo", curso=None)

@app.route("/cursos/editar/<nombre>", methods=["GET", "POST"])
def editar_curso(nombre):
    cursos = cargar_cursos()
    curso = next((c for c in cursos if c["nombre"] == nombre), None)

    if not curso:
        return "Curso no encontrado", 404

    if request.method == "POST":
        nuevo_nombre = request.form["nombre"].strip()
        descripcion = request.form["descripcion"].strip()

        # evitar duplicado de nombre (con otro curso)
        if nuevo_nombre != nombre and any(c["nombre"] == nuevo_nombre for c in cursos):
            return "Ya existe otro curso con ese nombre", 400

        curso["nombre"] = nuevo_nombre
        curso["descripcion"] = descripcion

        guardar_cursos(cursos)
        return redirect(url_for("lista_cursos"))

    return render_template("cursos_form.html", modo="editar", curso=curso)

@app.route("/cursos/eliminar/<nombre>", methods=["POST"])
def eliminar_curso(nombre):
    cursos = cargar_cursos()
    nuevos = [c for c in cursos if c["nombre"] != nombre]
    guardar_cursos(nuevos)
    return redirect(url_for("lista_cursos"))

@app.route("/cursos/gestionar/<nombre>", methods=["GET", "POST"])
def gestionar_curso(nombre):
    cursos = cargar_cursos()
    curso = next((c for c in cursos if c["nombre"] == nombre), None)
    if not curso:
        return "Curso no encontrado", 404

    temas = cargar_temas()
    concursos = cargar_concursos()
    problemas = cargar_problemas()

    if request.method == "POST":
        usados_problemas = request.form.getlist("usados_problemas")
        usados_temas = request.form.getlist("usados_temas")
        usados_concursos = request.form.getlist("usados_concursos")

        curso["usados_problemas"] = usados_problemas
        curso["usados_temas"] = usados_temas
        curso["usados_concursos"] = usados_concursos

        guardar_cursos(cursos)
        return redirect(url_for("gestionar_curso", nombre=curso["nombre"]))

    return render_template(
        "curso_usos.html",
        curso=curso,
        temas=temas,
        concursos=concursos,
        problemas=problemas,
    )

if __name__ == "__main__":
    app.run(debug=True)
