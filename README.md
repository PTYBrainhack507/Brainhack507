# Brainhack — fork personal de Umbrella para Kodi

Fork personal del addon [Umbrella](https://github.com/umbrellaplug/umbrellaplug.github.io) mantenido por [@PTYBrainhack507](https://github.com/PTYBrainhack507).

- **Plugin**: `plugin.video.umbrella` — visible en Kodi como **Brainhack** (v6.7.75.1, basado en upstream 6.7.75)
- **Repositorio**: `repository.brainhack` v1.0.0 — apunta a este repo vía GitHub Pages
- **Compatibilidad**: Kodi 21 (Omega). Carpetas `matrix/`, `nexus/`, `piers/` heredadas del upstream y disponibles, pero el foco activo es Omega.

## Instalación en Kodi 21 (Omega)

1. **Permitir orígenes desconocidos**: Ajustes → Sistema → Add-ons → activar *Orígenes desconocidos*.
2. **Añadir la fuente**: Ajustes → Administrador de archivos → Añadir fuente.
   - Ruta: `https://ptybrainhack507.github.io/Brainhack507/`
   - Nombre: `brainhack`
3. **Instalar el repositorio**: Add-ons → Instalar desde archivo zip → `brainhack` → `repository.brainhack-1.0.0.zip`.
4. **Instalar el plugin**: Add-ons → Instalar desde repositorio → *Brainhack Repository* → *Add-ons de vídeo* → *Brainhack* → Instalar.

A partir de acá Kodi descargará automáticamente las actualizaciones que publiques en este repo.

## Setup mínimo del addon

Brainhack necesita al menos un servicio externo (debrid o cloud) para funcionar — viene del comportamiento upstream de Umbrella. Soportado:

- **Debrid**: Real-Debrid, All-Debrid, Premiumize, TorBox, OffCloud
- **Cloud / otros**: Easynews, Plex, Google Drive
- **Trakt** (opcional, recomendado para listas y sincronización)

Configurá en *Tools → Settings → Accounts* dentro del addon.

## Estructura del repo

```
.
├── repository.brainhack-1.0.0.zip   ← bootstrap zip (instalación inicial)
├── omega/                            ← addons para Kodi 21
│   ├── plugin.video.umbrella/        ← código fuente del plugin (editable)
│   └── zips/                         ← zips + addons.xml servidos al repo
│       ├── addons.xml
│       ├── addons.xml.md5
│       ├── plugin.video.umbrella/
│       └── repository.brainhack/
├── nexus/, matrix/, piers/           ← heredado del upstream, sin tocar
└── .tools/build_repo.py              ← script de empaquetado (uv run --python 3.12)
```

## Workflow de cambios

```bash
# 1. Editás lo que quieras en omega/plugin.video.umbrella/
# 2. Bumpeás <version> en omega/plugin.video.umbrella/addon.xml
# 3. Regenerás zips + addons.xml + md5
uv run --python 3.12 .tools/build_repo.py
# 4. Commit + push — Kodi verá la nueva versión en la próxima sync (24h o forzada)
git add -A && git commit -m "..." && git push
```

Para forzar update en Kodi: Add-ons → Mis Add-ons → Brainhack → Actualizar.

## Créditos

- [Umbrella](https://github.com/umbrellaplug/umbrellaplug.github.io) — upstream.
- [Estuary](https://github.com/xbmc/xbmc) — base del skin Umbrestuary.
- Licencia: GPL v3 (heredada).
