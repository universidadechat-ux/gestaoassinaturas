#!/usr/bin/env python3
"""Isola a PWA Gestão de Faturas no subdiretório GitHub Pages.
Não altera qualquer aplicação instalada nem a base de dados do utilizador.
Executa-se apenas durante a compilação do ZIP para publicação.
"""
import json
from pathlib import Path

root = Path("webapp")
manifest_path = root / "public" / "manifest.webmanifest"
index_path = root / "index.html"
sw_path = root / "public" / "sw.js"

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["id"] = "/gestaoassinaturas/gestao-faturas-assinaturas-app"
manifest["start_url"] = "/gestaoassinaturas/"
manifest["scope"] = "/gestaoassinaturas/"
manifest["name"] = "Gestão de Faturas | Controlo de Assinaturas"
manifest["short_name"] = "Gestão de Faturas"
assert manifest["id"] != "/"
assert manifest["scope"] != "/"
assert manifest["start_url"].startswith(manifest["scope"])
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

html = index_path.read_text(encoding="utf-8")
# A folha de estilos, as bibliotecas e os dados continuam locais.
# Referências absolutas tornam inequívoca a identidade em Github Pages.
if '<link rel="manifest" href="./manifest.webmanifest" />' not in html:
    raise SystemExit("Não foi encontrado o link de manifesto esperado; publicação interrompida.")
html = html.replace(
    '<link rel="manifest" href="./manifest.webmanifest" />',
    '<link rel="manifest" href="/gestaoassinaturas/manifest.webmanifest" />'
)
old = "navigator.serviceWorker.register('./sw.js', { scope: './' })"
new = "navigator.serviceWorker.register('/gestaoassinaturas/sw.js', { scope: '/gestaoassinaturas/' })"
if old not in html:
    raise SystemExit("Service Worker não tem registo restrito esperado; publicação interrompida.")
html = html.replace(old, new)
index_path.write_text(html, encoding="utf-8")

sw = sw_path.read_text(encoding="utf-8")
if 'const CACHE_NAME = "gestao-faturas-v5";' not in sw:
    raise SystemExit("Falta nome de cache previsto; publicação interrompida.")
sw = sw.replace('const CACHE_NAME = "gestao-faturas-v5";',
                'const CACHE_NAME = "gestao-faturas-assinaturas-pages-v5";')
# O finalizador adiciona o fingerprint da versão compilada.
finalizer_path = root / "scripts" / "finalize-pages.mjs"
finalizer = finalizer_path.read_text(encoding="utf-8")
if "worker.replace('gestao-faturas-v5'" not in finalizer:
    raise SystemExit("Não foi encontrado o finalizador de cache previsto.")
finalizer = finalizer.replace("gestao-faturas-v5", "gestao-faturas-assinaturas-pages-v5")
finalizer_path.write_text(finalizer, encoding="utf-8")

# Esta aplicação só controla pedidos dentro da pasta própria.
sw = sw.replace(
    'if (requestUrl.origin !== self.location.origin) return;',
    "if (requestUrl.origin !== self.location.origin ||"
    " !requestUrl.pathname.startsWith('/gestaoassinaturas/')) return;"
)
# Também impede apagar caches de outra aplicação que use prefixo semelhante.
sw = sw.replace(
    'key.startsWith("gestao-faturas-")',
    'key.startsWith("gestao-faturas-assinaturas-pages-")'
)
sw_path.write_text(sw, encoding="utf-8")
print("Isolamento PWA configurado: identidade, âmbito e cache exclusivos de /gestaoassinaturas/.")
