"""Construit les ressources statiques livrées à o2switch."""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"


def minify_css(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{}:;,])\s*", r"\1", text)
    text = re.sub(r";}", "}", text)
    return text.strip()


def build_tailwind() -> None:
    print("== Tailwind CSS ==")
    cli = ROOT / "node_modules" / "@tailwindcss" / "cli" / "dist" / "index.mjs"
    input_css = STATIC / "css" / "tailwind_input.css"
    output_css = STATIC / "css" / "tailwind.css"
    result = subprocess.run(
        ["node", str(cli), "-i", str(input_css), "-o", str(output_css), "-m"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=120,
    )
    print(f"  {output_css.relative_to(ROOT)} ({output_css.stat().st_size:,} octets)")
    if result.stderr.strip():
        print(f"  {result.stderr.strip()}")


def validate_tailwind_output() -> None:
    """Détecte les régressions connues lors d'une mise à jour de Tailwind."""
    output_css = STATIC / "css" / "tailwind.css"
    css = output_css.read_text(encoding="utf-8")

    if "color:var(--fs-" in css:
        raise RuntimeError(
            "Tailwind a interprété un token --fs-* comme une couleur. "
            "Utilisez text-[length:var(--fs-*)] dans les templates."
        )

    required_fragments = {
        "font-size:var(--fs-": "les tailles de texte basées sur les tokens --fs-*",
        ".md\\:translate-x-0": "la remise à zéro de la navigation sur écran large",
    }
    missing = [
        description
        for fragment, description in required_fragments.items()
        if fragment not in css
    ]
    if missing:
        raise RuntimeError(
            "Le CSS Tailwind généré ne contient pas : " + ", ".join(missing) + "."
        )

    print("  Validation Tailwind v4 réussie")


def build_app_css() -> None:
    print("\n== App CSS ==")
    tokens = (STATIC / "css" / "tokens.css").read_text(encoding="utf-8")
    base = (STATIC / "css" / "base.css").read_text(encoding="utf-8")
    print(f"  READ tokens.css ({len(tokens)} caractères)")
    print(f"  READ base.css ({len(base)} caractères)")

    # Les styles sans couche ont priorité sur toutes les utilities Tailwind v4,
    # même lorsqu'une utility possède une spécificité plus forte. Le reset doit
    # donc rejoindre la couche base afin de préserver le design des templates.
    combined = f"{tokens}\n@layer base {{\n{base}\n}}"
    minified = minify_css(combined)
    output = STATIC / "css" / "app.min.css"
    output.write_text(minified, encoding="utf-8")
    print(f"  WROTE app.min.css ({len(minified)} caractères)")


def validate_app_css() -> None:
    """Garantit que le reset ne peut pas écraser les utilities Tailwind."""
    css = (STATIC / "css" / "app.min.css").read_text(encoding="utf-8")
    if "@layer base{" not in css:
        raise RuntimeError(
            "Le reset CSS doit être compilé dans @layer base pour préserver "
            "la priorité des utilities Tailwind."
        )

    print("  Validation des couches CSS réussie")


def _run_esbuild(arguments: list[str], input: str | None = None) -> str:
    """Exécute esbuild (dépendance de développement) pour minifier JS/CSS."""
    cli = ROOT / "node_modules" / "esbuild" / "bin" / "esbuild"
    result = subprocess.run(
        ["node", str(cli), "--minify", "--legal-comments=none", *arguments],
        input=input,
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    return result.stdout


def build_js() -> None:
    print("\n== JS ==")
    sources = ["theme.js", "nav.js", "filters.js", "password.js", "confirm.js"]
    parts = []
    for filename in sources:
        content = (STATIC / "js" / filename).read_text(encoding="utf-8")
        parts.append(f";(function(){{\n{content}\n}})();")
        print(f"  READ {filename} ({len(content)} caractères)")

    combined = "\n".join(parts)
    minified = _run_esbuild(["--target=es2015"], input=combined)
    output = STATIC / "js" / "bundle.min.js"
    output.write_text(minified, encoding="utf-8")
    print(f"  WROTE bundle.min.js ({len(combined)} -> {len(minified)} caractères)")


def build_timeslider() -> None:
    print("\n== Timeslider ==")
    js_source = STATIC / "js" / "timeslider.js"
    js_content = js_source.read_text(encoding="utf-8")
    js_minified = _run_esbuild(["--target=es2015"], input=js_content)
    js_output = STATIC / "js" / "timeslider.min.js"
    js_output.write_text(js_minified, encoding="utf-8")
    print(f"  WROTE timeslider.min.js ({len(js_content)} -> {len(js_minified)} caractères)")

    css_source = STATIC / "css" / "timeslider.css"
    css_content = css_source.read_text(encoding="utf-8")
    css_minified = _run_esbuild(["--loader=css"], input=css_content)
    css_output = STATIC / "css" / "timeslider.min.css"
    css_output.write_text(css_minified, encoding="utf-8")
    print(f"  WROTE timeslider.min.css ({len(css_content)} -> {len(css_minified)} caractères)")


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def build_vendor_assets() -> None:
    print("\n== Vendor ==")
    node_modules = ROOT / "node_modules"
    leaflet_source = node_modules / "leaflet" / "dist"
    leaflet_target = STATIC / "vendor" / "leaflet"
    _copy_file(leaflet_source / "leaflet.css", leaflet_target / "leaflet.css")
    _copy_file(leaflet_source / "leaflet.js", leaflet_target / "leaflet.js")
    shutil.copytree(
        leaflet_source / "images",
        leaflet_target / "images",
        dirs_exist_ok=True,
    )

    marker_source = node_modules / "leaflet.markercluster" / "dist"
    marker_target = STATIC / "vendor" / "leaflet.markercluster"
    _copy_file(marker_source / "MarkerCluster.css", marker_target / "MarkerCluster.css")
    _copy_file(
        marker_source / "leaflet.markercluster.js",
        marker_target / "leaflet.markercluster.js",
    )

    _copy_file(
        node_modules / "chart.js" / "dist" / "chart.umd.js",
        STATIC / "vendor" / "chart.js" / "chart.umd.js",
    )

    inter_source = node_modules / "@fontsource-variable" / "inter"
    inter_target = STATIC / "vendor" / "inter"
    _copy_file(inter_source / "wght.css", inter_target / "inter.css")
    for font_file in (inter_source / "files").glob("*-wght-normal.woff2"):
        _copy_file(font_file, inter_target / "files" / font_file.name)
    print("  Ressources Leaflet, MarkerCluster, Chart.js et Inter copiées")


if __name__ == "__main__":
    build_tailwind()
    validate_tailwind_output()
    build_app_css()
    validate_app_css()
    build_js()
    build_timeslider()
    build_vendor_assets()
    print("\nDone.")
