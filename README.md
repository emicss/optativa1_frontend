# Folio · React + Vite

Prototipo visual de facturación con React, JSX y Vite. Incluye login de demostración, resumen, clientes, catálogo de servicios y creación de borradores.

## Desarrollo

Requiere Node.js 20.19+ o 22.12+ (se verificó con Node 22.14).

```sh
npm install
npm run dev
```

Abre http://127.0.0.1:5173. Vite actualiza las vistas al guardar los archivos JSX. Usa cualquier correo válido y contraseña para entrar. La contraseña no se guarda ni se envía.

Las pantallas usan datos de ejemplo y los borradores se conservan durante la sesión del navegador. No emiten facturas reales ni requieren una conexión con AWS.

## API Flask opcional

Para trabajar con la API existente, inicia otra terminal:

```sh
python -m pip install -r requirements.txt
python app.py
```

Vite redirige las peticiones `/api` a Flask en el puerto 5000. El endpoint existente se configura mediante `AWS_API_URL`; el prototipo visual aún no lo consume.

## Compilar y servir

```sh
npm run build
python app.py
```

Flask sirve `dist/` en http://127.0.0.1:5000. Vuelve a ejecutar `npm run build` después de modificar el frontend. Para revisar únicamente el frontend compilado también puedes usar `npm run preview` (puerto 4173).

## Organización

```text
src/
  App.jsx                 # Selección entre login y espacio de facturación
  main.jsx                # Entrada de React
  pages/                  # Login, inicio, facturas, clientes y servicios
  components/
    ui/                   # Iconos, modal, búsqueda, filtros, estados, métricas
    layout/               # Menú, encabezados y composición de pantallas
    invoices/             # Tabla, formulario, detalle y totales
    clients/              # Tarjeta, identidad y detalle del cliente
    services/             # Tarjeta, características y detalle del servicio
  hooks/                  # Sesión demo, navegación y borradores
  data/                   # Datos de ejemplo y etiquetas de navegación
  utils/                  # Formato, importes y creación de borradores
  styles/                 # Base, login, estructura y facturación
```

React y React DOM son dependencias npm. Los archivos `.jsx` se compilan con Vite; no se utiliza HTM ni se carga React desde un CDN. Las fuentes de Google son opcionales y tienen alternativas locales.

## Verificación

```sh
npm test
npm run build
npm run format:check
```

`npm run format` aplica el formato del proyecto. `dist/`, `node_modules/` y los archivos locales del IDE se excluyen de Git.
