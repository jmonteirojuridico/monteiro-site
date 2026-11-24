#!/usr/bin/env python3
"""Gera as páginas do site a partir de _build/content/*.html.

Cada arquivo de conteúdo começa com uma linha de metadados:
  <!-- {"title": "...", "description": "...", "path": "/pasta/", "nav": "id-do-menu"} -->
e depois traz só o miolo da página (o que fica dentro de <main>).
Cabeçalho, menu, rodapé e ícones ficam aqui, num lugar só.

Uso (na raiz do repositório):  python3 _build/build.py
A pasta _build não é publicada pelo GitHub Pages.
"""
import hashlib
import json
import pathlib
import re
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "_build" / "content"
SITE = "https://monteirojuridico.adv.br"

WHATSAPP_JULIA = "5511999103182"


def agende(area=None):
    """Link do botão "Agende sua consulta".
    Enquanto a página de agendamento não existe, abre o WhatsApp da Júlia."""
    msg = "Olá! Gostaria de agendar uma consulta"
    msg += f" na área {area}." if area else "."
    return f"https://wa.me/{WHATSAPP_JULIA}?text={quote(msg)}"


NAV = [
    ("inicio", "/", "Início"),
    ("escritorio", "/o-escritorio/", "O escritório"),
    ("equipe", "/equipe/", "Equipe"),
    ("areas", "/areas-de-atuacao/", "Áreas de atuação"),
    ("atendimento", "/formas-de-atendimento/", "Formas de atendimento"),
    ("contato", "/contato/", "Contato"),
]

ICONS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11.5a8 8 0 0 1-11.6 7.1L4 20l1.4-4.2A8 8 0 1 1 20 11.5Z"/><path d="M9 10h6M9 13.5h4"/></symbol>
  <symbol id="i-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h3.5l1.7 4.3-2.2 1.4a11 11 0 0 0 6.3 6.3l1.4-2.2L20 15.5V19a1.5 1.5 0 0 1-1.6 1.5A16 16 0 0 1 3.5 5.6 1.5 1.5 0 0 1 5 4Z"/></symbol>
  <symbol id="i-mail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="m3.5 6 8.5 7 8.5-7"/></symbol>
  <symbol id="i-insta" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="0.6" fill="currentColor"/></symbol>
  <symbol id="i-calendar" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></symbol>
  <symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
</svg>"""

JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LegalService",
  "name": "Monteiro Advogados",
  "url": "https://monteirojuridico.adv.br/",
  "telephone": "+55-11-98953-1221",
  "email": "central.monteirogfr@gmail.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Rua XV de Novembro, 597, Centro",
    "addressLocality": "Jundiaí",
    "addressRegion": "SP",
    "postalCode": "13201-005",
    "addressCountry": "BR"
  },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "08:00",
    "closes": "18:00"
  }],
  "sameAs": ["https://www.instagram.com/advmonteirojur/"]
}
</script>
"""

LAYOUT = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{canonical}<meta name="theme-color" content="#151416">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/montserrat.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css?v={css_version}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Monteiro Advogados">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
{og_url}{robots}{jsonld}</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>

{icons}

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Monteiro Advogados, página inicial">
      <img src="/assets/img/monograma-ma.svg" alt="" width="1020" height="615">
      <span>Monteiro Advogados</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu">
      <span class="nav-toggle-bars" aria-hidden="true"></span>
      Menu
    </button>
    <nav class="site-nav" id="menu" aria-label="Principal">
      <ul>
{nav}
        <li class="nav-cta-item"><a class="nav-cta" href="{agende}">Agende sua consulta</a></li>
      </ul>
    </nav>
  </div>
</header>

<main id="conteudo">
{body}
</main>

<footer class="site-footer">
  <div class="wrap">
    <p class="footer-name">Monteiro Advogados</p>
    <p>Rua XV de Novembro, 597, Centro, Jundiaí/SP</p>
    <p>Responsável técnico: Dr. Nivaldo Monteiro, OAB/SP 261.752</p>
    <p class="footer-links">
      <a href="/politica-de-privacidade/">Política de Privacidade</a>
      <a href="https://www.instagram.com/advmonteirojur/">Instagram</a>
    </p>
  </div>
</footer>

<script>
  (function () {{
    var b = document.querySelector(".nav-toggle");
    var h = document.querySelector(".site-header");
    b.addEventListener("click", function () {{
      var open = b.getAttribute("aria-expanded") !== "true";
      b.setAttribute("aria-expanded", String(open));
      h.classList.toggle("nav-open", open);
    }});
  }})();
</script>
{scripts}</body>
</html>
"""


# Muda sempre que o style.css muda: obriga o navegador a baixar o estilo novo
# em vez de usar a cópia antiga guardada (cache).
CSS_VERSION = hashlib.sha1((ROOT / "assets" / "css" / "style.css").read_bytes()).hexdigest()[:8]


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def build_page(src):
    text = src.read_text(encoding="utf-8")
    first, body = text.split("\n", 1)
    meta = json.loads(re.fullmatch(r"<!--\s*(\{.*\})\s*-->", first.strip()).group(1))

    # Scripts da própria página vão para o fim do <body>.
    scripts = "".join(re.findall(r"<script>.*?</script>\n?", body, re.S))
    body = re.sub(r"<script>.*?</script>\n?", "", body, flags=re.S).rstrip("\n")

    area = meta.get("area")
    body = body.replace("{{AGENDE}}", esc(agende(area)))

    nav = "\n".join(
        '        <li><a href="{}"{}>{}</a></li>'.format(
            href, ' aria-current="page"' if key == meta.get("nav") else "", label
        )
        for key, href, label in NAV
    )
    path = meta.get("path")
    html = LAYOUT.format(
        title=esc(meta["title"]),
        og_title=esc(meta.get("og_title", meta["title"])),
        description=esc(meta["description"]),
        canonical=f'<link rel="canonical" href="{SITE}{path}">\n' if path else "",
        og_url=f'<meta property="og:url" content="{SITE}{path}">\n' if path else "",
        robots='<meta name="robots" content="noindex">\n' if meta.get("noindex") else "",
        jsonld=JSONLD if meta.get("jsonld") else "",
        icons=ICONS,
        nav=nav,
        agende=esc(agende(area)),
        body=body,
        scripts=scripts,
        css_version=CSS_VERSION,
    )
    out = ROOT / meta["out"] if "out" in meta else ROOT / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return path, meta.get("noindex", False)


def main():
    urls = []
    for src in sorted(CONTENT.glob("*.html")):
        path, noindex = build_page(src)
        print("ok", src.name, "->", path or "(fora do sitemap)")
        if path and not noindex:
            urls.append(path)
    urls.sort(key=lambda p: (p != "/", p))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{SITE}{p}</loc></url>" for p in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
