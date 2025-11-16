# ICPC Database App

Aplicación local para gestionar una base de datos personal de entrenamiento ICPC.  
Permite administrar **Temas**, **Problemas**, **Concursos** y **Cursos/Ciclos de entrenamiento**, todo desde una interfaz web moderna y almacenado en archivos JSON locales.  

El proyecto está diseñado para ejecutarse **completamente en tu computadora**, sin servidor remoto y sin necesidad de internet (excepto para cargar Bootstrap/Chart.js desde CDN).

---

## 🚀 Tecnologías utilizadas

- **Python 3**
- **Flask** (backend y plantillas)
- **HTML + Bootstrap 5** (interfaz moderna)
- **JSON** como base de datos local
- **Jinja2** para rendering de plantillas

No requiere base de datos externa, Docker, ni servicios en la nube.

---

## 🔧 Instalación y configuración

Sigue estos pasos para ejecutar la aplicación localmente.

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/icpc-db-app.git
cd icpc-db-app
```

### 2. Crear y activar el entorno virtual

MacOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

pip install flask

---

## ▶️ Cómo ejecutar la aplicación

Desde la raíz del proyecto (y con el entorno virtual activo):

```bash
python app.py
```

La aplicación correrá en:

```
http://localhost:5000
```

---

## 📁 Estructura del proyecto

```pgsql
icpc-db-app/
│
├── app.py
├── README.md
├── .gitignore
│
├── data/                 # "Base de datos" local (JSON)
│   ├── temas.json
│   ├── concursos.json
│   ├── problemas.json
│   └── cursos.json
│
├── templates/            # Todas las plantillas HTML (Jinja2)
│   ├── base.html
│   ├── home.html
│   ├── temas_list.html
│   ├── temas_form.html
│   ├── concursos_list.html
│   ├── concursos_form.html
│   ├── problemas_list.html
│   ├── problemas_form.html
│   ├── cursos_list.html
│   ├── cursos_form.html
│   └── curso_usos.html
│
└── static/               # CSS, imágenes, JS adicional (si lo necesitas)
```

---

## ⚠️ Notas importantes

- Todos los datos se guardan en la carpeta `data/` en formato JSON.
Puedes versionarlos en GitHub o ignorarlos según tus necesidades.
- La app funciona completamente offline.
- Puedes abrir y editar los archivos `.md` de soluciones o temas desde tu editor preferido.
- El entorno virtual (`.venv/`) no debe subirse al repositorio.