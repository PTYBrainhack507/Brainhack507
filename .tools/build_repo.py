#!/usr/bin/env python3
"""
Build script for the Brainhack Kodi repository fork.

What it does:
1. Re-zips the modified plugin.video.umbrella into omega/zips/plugin.video.umbrella/.
2. Refreshes the icon.png + fanart.jpg copies that live alongside the zip
   (Kodi pulls thumbnails from there, not from inside the zip).
3. Creates the repository.brainhack addon (XML + assets), zips it, and writes
   the zip into omega/zips/repository.brainhack/ AND into the repo root
   (root copy is the bootstrap zip users install via "Install from zip file").
4. Regenerates omega/zips/addons.xml so it includes:
   - the bumped plugin.video.umbrella entry
   - the new repository.brainhack entry
   - all the unchanged dependency entries that were already there
5. Regenerates omega/zips/addons.xml.md5.

Re-run this any time you bump plugin version or touch repository metadata.
"""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OMEGA = ROOT / "omega"
ZIPS = OMEGA / "zips"

GH_USER = "PTYBrainhack507"
GH_REPO = "Brainhack507"
PAGES_BASE = f"https://ptybrainhack507.github.io/{GH_REPO}"
RAW_BASE = f"https://raw.githubusercontent.com/{GH_USER}/{GH_REPO}/main"

REPO_ADDON_ID = "repository.brainhack"
REPO_ADDON_VERSION = "1.0.0"


def read_addon_version(addon_xml: Path) -> tuple[str, str]:
    root = ET.parse(addon_xml).getroot()
    return root.attrib["id"], root.attrib["version"]


def zip_addon(src_dir: Path, dest_zip: Path) -> None:
    """Zip src_dir as <addon_id>/ inside dest_zip (Kodi convention)."""
    addon_id = src_dir.name
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    if dest_zip.exists():
        dest_zip.unlink()
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src_dir.rglob("*")):
            if path.is_file():
                arc = Path(addon_id) / path.relative_to(src_dir)
                zf.write(path, arc.as_posix())
    print(f"  zipped {src_dir.name} → {dest_zip.relative_to(ROOT)}  ({dest_zip.stat().st_size:,} bytes)")


def build_repository_addon() -> Path:
    """Create the repository.brainhack source tree under .build/, return its path."""
    build_root = ROOT / ".build" / REPO_ADDON_ID
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True)

    addon_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="{REPO_ADDON_ID}" name="Brainhack Repository" version="{REPO_ADDON_VERSION}" provider-name="Brainhack507">
    <extension point="xbmc.addon.repository" name="Brainhack Repository">
        <dir minversion="20.90.0">
            <info compressed="false">{PAGES_BASE}/omega/zips/addons.xml</info>
            <checksum>{PAGES_BASE}/omega/zips/addons.xml.md5</checksum>
            <datadir zip="true">{PAGES_BASE}/omega/zips/</datadir>
        </dir>
        <dir minversion="19.8.0" maxversion="20.89.0">
            <info compressed="false">{PAGES_BASE}/nexus/zips/addons.xml</info>
            <checksum>{PAGES_BASE}/nexus/zips/addons.xml.md5</checksum>
            <datadir zip="true">{PAGES_BASE}/nexus/zips/</datadir>
        </dir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary>Brainhack Repository</summary>
        <description>Fork personal del repo Umbrella mantenido por Brainhack507.</description>
        <disclaimer></disclaimer>
        <platform>all</platform>
        <assets>
            <icon>icon.png</icon>
            <fanart>fanart.jpg</fanart>
        </assets>
    </extension>
</addon>
"""
    (build_root / "addon.xml").write_text(addon_xml)
    # Reuse the plugin's icon/fanart so the repository looks consistent.
    plugin_dir = OMEGA / "plugin.video.umbrella"
    shutil.copy(plugin_dir / "icon.png", build_root / "icon.png")
    shutil.copy(plugin_dir / "fanart.jpg", build_root / "fanart.jpg")
    return build_root


def rebuild_addons_xml() -> None:
    """Walk omega/zips/<addon>/addon.xml entries and produce omega/zips/addons.xml + md5."""
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]
    for child in sorted(ZIPS.iterdir()):
        if not child.is_dir():
            continue
        addon_xml = child / "addon.xml"
        if not addon_xml.exists():
            continue
        # Inline the addon.xml body (everything after the XML declaration).
        text = addon_xml.read_text().lstrip()
        if text.startswith("<?xml"):
            text = text.split("?>", 1)[1].lstrip()
        out.append(text.rstrip())
    out.append("</addons>")
    addons_xml = ZIPS / "addons.xml"
    addons_xml.write_text("\n".join(out) + "\n")

    md5 = hashlib.md5(addons_xml.read_bytes()).hexdigest()
    (ZIPS / "addons.xml.md5").write_text(md5 + "\n")
    print(f"  wrote {addons_xml.relative_to(ROOT)} and md5={md5}")


def main() -> None:
    print("== 1. Re-zipping plugin.video.umbrella ==")
    plugin_dir = OMEGA / "plugin.video.umbrella"
    plugin_id, plugin_ver = read_addon_version(plugin_dir / "addon.xml")
    plugin_zip_dir = ZIPS / plugin_id
    # Clean old zips for this addon so stale versions don't linger.
    for old in plugin_zip_dir.glob(f"{plugin_id}-*.zip"):
        old.unlink()
    zip_addon(plugin_dir, plugin_zip_dir / f"{plugin_id}-{plugin_ver}.zip")
    # Refresh sidecar assets + addon.xml that live next to the zip.
    shutil.copy(plugin_dir / "addon.xml", plugin_zip_dir / "addon.xml")
    shutil.copy(plugin_dir / "icon.png", plugin_zip_dir / "icon.png")
    shutil.copy(plugin_dir / "fanart.jpg", plugin_zip_dir / "fanart.jpg")

    print("== 2. Building repository.brainhack addon ==")
    repo_dir = build_repository_addon()
    repo_zip_target_dir = ZIPS / REPO_ADDON_ID
    if repo_zip_target_dir.exists():
        shutil.rmtree(repo_zip_target_dir)
    repo_zip_target_dir.mkdir(parents=True)
    repo_zip_path = repo_zip_target_dir / f"{REPO_ADDON_ID}-{REPO_ADDON_VERSION}.zip"
    zip_addon(repo_dir, repo_zip_path)
    shutil.copy(repo_dir / "addon.xml", repo_zip_target_dir / "addon.xml")
    shutil.copy(repo_dir / "icon.png", repo_zip_target_dir / "icon.png")
    shutil.copy(repo_dir / "fanart.jpg", repo_zip_target_dir / "fanart.jpg")
    # Root-level bootstrap zip — users install this first.
    root_bootstrap = ROOT / f"{REPO_ADDON_ID}-{REPO_ADDON_VERSION}.zip"
    shutil.copy(repo_zip_path, root_bootstrap)
    print(f"  bootstrap zip at {root_bootstrap.relative_to(ROOT)}")

    print("== 3. Regenerating addons.xml + md5 ==")
    rebuild_addons_xml()

    print("\nDone.")


if __name__ == "__main__":
    main()
