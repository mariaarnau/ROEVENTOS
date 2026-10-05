#!/usr/bin/env python3
"""Genera produccion/ a partir de docs/ (la maqueta) listo para subir al hosting.

- docs/ se queda como está (maqueta con noindex, publicada en GitHub Pages).
- produccion/ es la versión definitiva: URLs limpias idénticas a las del WordPress
  actual, sin banda de maqueta, SEO completo, formularios reales y redirecciones.

Uso:  python3 migracion/build.py
"""
import csv, datetime, html, os, re, shutil, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "produccion")
SITE = "https://roeventos.com"
EMAIL_DESTINO = "info@roeventos.com"   # <- destino de los formularios (enviar.php)
TODAY = datetime.date.today().isoformat()

# --------------------------------------------------------------------------
# Mapa de páginas: fichero de la maqueta -> ruta pública (URL antigua si existía)
# --------------------------------------------------------------------------
PAGES = {
    "index.html": "/",
    "conocenos.html": "/conocenos/",
    "deportes.html": "/deportes/",
    "eventos.html": "/eventos/",
    "blog.html": "/blog/",
    "contacto.html": "/contacto/",
    # fichas de deporte: misma URL que el WordPress actual
    "portfolio-basket.html": "/portfolio-item/basket/",
    "portfolio-voley.html": "/portfolio-item/volleyball/",
    "portfolio-futbol.html": "/portfolio-item/futbol/",
    "portfolio-futsal.html": "/portfolio-item/futsal/",
    # noticia que ya existía: misma URL exacta que en el WordPress
    "noticia-empren-esport.html":
        "/2022/11/01/valencia-internacional-cup-1er-premio-empren-esport/",
}
for f in sorted(os.listdir(SRC)):
    m = re.fullmatch(r"noticia-(.+)\.html", f)
    if m and f not in PAGES:
        PAGES[f] = f"/blog/{m.group(1)}/"

# Títulos: se mantienen LOS MISMOS que tiene hoy Google en las páginas existentes.
TITLES = {
    "/": "Ro Eventos – Organización de eventos deportivos en la Comunidad Valenciana",
    "/conocenos/": "Conócenos – Ro Eventos",
    "/deportes/": "Deportes – Ro Eventos",
    "/eventos/": "Eventos – Ro Eventos",
    "/blog/": "Blog – Ro Eventos",
    "/contacto/": "Contacto – Ro Eventos",
    "/portfolio-item/basket/": "Basket – Ro Eventos",
    "/portfolio-item/volleyball/": "Volley – Ro Eventos",
    "/portfolio-item/futbol/": "Fútbol – Ro Eventos",
    "/portfolio-item/futsal/": "Futsal – Ro Eventos",
    "/2022/11/01/valencia-internacional-cup-1er-premio-empren-esport/":
        "Valencia Internacional Cup 1er premio Empren Esport – Ro Eventos",
}
# La web antigua no tenía meta description en ninguna página: se añaden.
DESCS = {
    "/": "R&O Eventos organiza torneos y campus deportivos internacionales de baloncesto, fútbol, fútbol sala y vóley en la Comunitat Valenciana. Más de 20 años llevando equipos de todo el mundo a competir en Valencia.",
    "/conocenos/": "Conoce a R&O Eventos Deportivos: más de 20 años organizando torneos internacionales de baloncesto, fútbol, futsal y vóley en Valencia y Cullera.",
    "/deportes/": "Baloncesto, fútbol, fútbol sala y vóley: los deportes de los torneos y campus que organiza R&O Eventos en la Comunitat Valenciana.",
    "/eventos/": "Calendario de torneos 2027: Valencia Basket Cup, International Cup, Summer Cup, Cullera Futsal Cup, Cullera Vóley Cup y Training Stages. Fechas, sedes y dossiers.",
    "/blog/": "Noticias, premios y crónicas de los torneos y campus deportivos de R&O Eventos: Valencia Basket Cup, Futsal Cup, Voley Cup y más.",
    "/contacto/": "Contacta con R&O Eventos Deportivos en Torrent (Valencia): torneos, inscripciones, dossiers y training stages. Te respondemos en menos de 24 h.",
    "/portfolio-item/basket/": "Torneos de baloncesto de R&O Eventos: Valencia Basket Cup, Valencia Basket International Cup y Summer Cup en Valencia.",
    "/portfolio-item/volleyball/": "Torneos de vóley de R&O Eventos: Cullera Vóley Cup, el torneo de final de temporada junto al Mediterráneo.",
    "/portfolio-item/futbol/": "Torneos de fútbol de R&O Eventos: Valencia Soccer Cup, competición internacional de fútbol base en Valencia.",
    "/portfolio-item/futsal/": "Torneos de fútbol sala de R&O Eventos: Cullera Futsal Cup, el torneo de futsal base de final de temporada.",
    "/2022/11/01/valencia-internacional-cup-1er-premio-empren-esport/": "La Valencia International Cup, de R&O Eventos, recibe el 1er premio Empren Esport en la categoría de deporte base.",
}
OG_IMAGES = {
    "/": "images/hero-home.jpg", "/conocenos/": "images/conocenos-hero-team.jpg",
    "/eventos/": "images/eventos-hero-medals.jpg", "/blog/": "images/blog-empren-stage.jpg",
    "/contacto/": "images/contacto-hero-kids.jpg",
}

MESES = {m: i + 1 for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split())}

# --------------------------------------------------------------------------
def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(s)

def url_of(fname):
    return PAGES[fname]

def rewrite_links(s):
    """href/src relativos de la maqueta -> rutas absolutas del sitio final."""
    def page_href(m):
        attr, name, frag = m.group(1), m.group(2), m.group(3) or ""
        return f'{attr}="{url_of(name)}{frag}"'
    s = re.sub(r'(href)="((?:%s))((?:#[^"]*)?)"' % "|".join(map(re.escape, PAGES)), page_href, s)
    # assets: css/js/images/dossiers/favicon -> absolutos
    s = re.sub(r'(href|src|content)="((?:css|js|images|dossiers)/[^"]*|favicon\.ico)"',
               lambda m: f'{m.group(1)}="/{m.group(2)}"', s)
    s = re.sub(r"url\('(images/[^']*)'\)", r"url('/\1')", s)
    return s

def spanish_date(s):
    m = re.search(r"(\d{1,2}) (\w+) (\d{4})", s)
    if not m: return TODAY
    return datetime.date(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))).isoformat()

def esc(s): return html.escape(s, quote=True)

# --------------------------------------------------------------------------
header = read(os.path.join(SRC, "partials/header.html"))
footer = read(os.path.join(SRC, "partials/footer.html"))
# quita la banda de maqueta y la etiqueta "sin publicar"
header = re.sub(r'<div class="preview-banner">.*?</div>\s*', "", header, flags=re.S)
footer = footer.replace('<span class="preview-flag">Maqueta interna · sin publicar</span>', "")
footer = footer.replace("&copy; 2027", f"&copy; {datetime.date.today().year}")
# enlaces sociales muertos (href="#"): fuera hasta tener las URLs reales
footer = re.sub(r'\s*<a href="#" aria-label="(?:Facebook|LinkedIn)">.*?</a>', "", footer, flags=re.S)

ORG_LD = """{
  "@context": "https://schema.org",
  "@type": "SportsOrganization",
  "@id": "%(site)s/#organization",
  "name": "R&O Eventos Deportivos",
  "alternateName": "Ro Eventos",
  "url": "%(site)s/",
  "logo": "%(site)s/images/logo-ro.png",
  "image": "%(site)s/images/hero-home.jpg",
  "email": "info@roeventos.com",
  "telephone": "+34670386418",
  "address": {"@type": "PostalAddress", "streetAddress": "CC Las Américas, Avinguda al Vedat, 180",
              "addressLocality": "Torrent", "addressRegion": "Valencia", "addressCountry": "ES"},
  "sameAs": ["https://www.instagram.com/roeventos_/", "https://www.instagram.com/valenciabasketcup/",
             "https://www.instagram.com/valencia_soccercup/", "https://www.instagram.com/futsal_cup/",
             "https://www.instagram.com/voleycup/"]
}""" % {"site": SITE}

shutil.rmtree(OUT, ignore_errors=True)
sitemap_urls = []
built = {}

for fname, path in PAGES.items():
    s = read(os.path.join(SRC, fname))
    is_news = path.startswith("/blog/") and path != "/blog/" or path.startswith("/2022/")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    h1txt = html.unescape(re.sub(r"<[^>]+>", "", h1.group(1)).strip()) if h1 else ""

    title = TITLES.get(path) or f"{h1txt} – Ro Eventos"
    lead = re.search(r'<p class="post-lead">(.*?)</p>', s, re.S)
    desc = DESCS.get(path) or (html.unescape(re.sub(r"<[^>]+>", "", lead.group(1))).strip() if lead else "")
    og_img = OG_IMAGES.get(path)
    if not og_img:
        m = re.search(r"class=\"hero hero--inner\" style=\"background-image:url\('(images/[^']+)'\)", s)
        og_img = m.group(1) if m else "images/hero-home.jpg"
    canonical = SITE + path
    date_iso = None
    meta = re.search(r'<span class="eyebrow">[^<]*·\s*(\d{1,2} \w+ \d{4})</span>', s)
    if is_news and meta: date_iso = spanish_date(meta.group(1))

    # --- <head>: fuera comentario de migración, título maqueta y noindex
    s = re.sub(r"(<head>\s*)<!--.*?-->", r"\1", s, count=1, flags=re.S)
    s = re.sub(r"<title>.*?</title>\s*", "", s, flags=re.S)
    s = re.sub(r'<meta name="robots"[^>]*>\s*', "", s)
    s = re.sub(r'<link rel="icon" href="favicon.ico" sizes="any">', '<link rel="icon" href="/favicon.ico" sizes="any">', s)

    ld = [ORG_LD] if path == "/" else []
    if date_iso:
        ld.append("""{
  "@context": "https://schema.org", "@type": "NewsArticle",
  "headline": %s, "datePublished": "%s", "dateModified": "%s",
  "image": "%s/%s", "mainEntityOfPage": "%s",
  "author": {"@type": "Organization", "name": "R&O Eventos Deportivos"},
  "publisher": {"@type": "Organization", "name": "R&O Eventos Deportivos", "logo": {"@type": "ImageObject", "url": "%s/images/logo-ro.png"}}
}""" % (__import__("json").dumps(html.unescape(h1txt), ensure_ascii=False), date_iso, date_iso, SITE, og_img, canonical, SITE))
    ld_html = "".join(f'<script type="application/ld+json">\n{x}\n</script>\n' for x in ld)

    seo = f"""<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{'article' if date_iso else 'website'}">
<meta property="og:site_name" content="R&amp;O Eventos">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/{og_img}">
<meta name="twitter:card" content="summary_large_image">
{ld_html}"""
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + seo, 1)

    # --- header / footer incrustados (sin depender de JavaScript)
    page_id = re.search(r'<body data-page="([^"]+)"', s)
    hdr = header
    if page_id:
        hdr = re.sub(r'(<a href="[^"]*" data-page="%s")' % re.escape(page_id.group(1)),
                     r'\1 class="is-active"', hdr)
    s = s.replace('<div data-include="header"></div>', hdr.strip())
    s = s.replace('<div data-include="footer"></div>', footer.strip())
    s = s.replace('<script src="js/include.js"></script>',
                  "<script>document.addEventListener('DOMContentLoaded',function(){document.dispatchEvent(new CustomEvent('partials:ready'))});</script>")

    # --- formularios reales -> /enviar.php
    def fix_form(m):
        f = m.group(0)
        origen = path
        f = f.replace(" data-preview-form", ' method="post" action="/enviar.php"', 1)
        names = [("¿Tu nombre?*", "nombre"), ("Nombre", "nombre"), ("Nº de teléfono", "telefono"),
                 ("Email*", "email"), ("E-mail", "email"), ("Tu email de contacto", "email"), ("Mensaje", "mensaje")]
        for ph, nm in names:
            f = re.sub(r'(<(?:input|textarea)\b)([^>]*placeholder="%s")' % re.escape(ph), r'\1 name="%s"\2' % nm, f)
        f = f.replace("<select ", '<select name="torneo" aria-label="Torneo de interés" ', 1)
        f = re.sub(r"<option>(Torneo de interés)</option>", r'<option value="">\1</option>', f)
        f = f.replace("</form>",
            f'<input type="hidden" name="origen" value="{origen}">'
            '<input type="text" name="web" value="" tabindex="-1" autocomplete="off" '
            'style="position:absolute;left:-9999px;" aria-hidden="true">'
            '<input type="hidden" name="t" value="" data-ts></form>')
        f = re.sub(r'<div class="form-success">.*?</div>',
                   '<div class="form-success">¡Gracias! Hemos recibido tu mensaje y te responderemos lo antes posible.</div>'
                   '<div class="form-error">No hemos podido enviar el mensaje. Escríbenos a <a href="mailto:info@roeventos.com">info@roeventos.com</a>.</div>', f, flags=re.S)
        return f
    s = re.sub(r"<form\b[^>]*data-preview-form.*?</form>", fix_form, s, flags=re.S)
    # el mensaje de éxito del CTA de la home está fuera del <form>
    s = re.sub(r'(<div class="form-success"[^>]*>)¡Gracias! \(maqueta de demostración[^<]*</div>',
               r'\1¡Gracias! Hemos recibido tu mensaje y te responderemos lo antes posible.</div>', s)
    if 'method="post" action="/enviar.php"' in s:
        s = s.replace("</body>", """<script>
(function(){
  var q=new URLSearchParams(location.search), ok=q.get('enviado')==='1', er=q.get('error')==='1';
  document.querySelectorAll('[data-ts]').forEach(function(i){i.value=Math.floor(Date.now()/1000);});
  if(ok||er){
    document.querySelectorAll('form[action="/enviar.php"]').forEach(function(f){
      var box=f.parentElement.querySelector(ok?'.form-success':'.form-error');
      if(box){box.classList.add('is-visible');box.scrollIntoView({block:'center'});}
    });
  }
})();
</script>
</body>""")

    s = re.sub(r'\s*<a href="#" aria-label="(?:Facebook|LinkedIn)">.*?</a>', '', s, flags=re.S)
    s = rewrite_links(s)
    out_path = os.path.join(OUT, path.lstrip("/"), "index.html")
    built[path] = out_path
    write(out_path, s)
    if not path.startswith("/portfolio-item/") or True:
        sitemap_urls.append((path, date_iso or TODAY))

# --------------------------------------------------------------------------
# Recursos estáticos
for d in ("css", "js", "images", "dossiers"):
    shutil.copytree(os.path.join(SRC, d), os.path.join(OUT, d), dirs_exist_ok=True)
os.remove(os.path.join(OUT, "js/include.js"))
shutil.copy(os.path.join(SRC, "favicon.ico"), os.path.join(OUT, "favicon.ico"))
shutil.copy(os.path.join(ROOT, "migracion/enviar.php"), os.path.join(OUT, "enviar.php"))
# la maqueta de css lleva ?v= para la caché; en producción se mantiene
# CSS: la banda de maqueta (.preview-banner) y el padding extra del body ya no existen
css_p = os.path.join(OUT, "css/style.css")
css = read(css_p)
css = css.replace("body{ padding-top:32px; }", "")
css = css.replace("top:32px; left:0; right:0;\n  z-index: 999;", "top:0; left:0; right:0;\n  z-index: 999;")
css += "\n.form-error{ display:none; background: rgba(227,6,19,.1); border:1px solid rgba(227,6,19,.4); color:#a90410; padding:14px 18px; border-radius:10px; font-size:.9rem; }\n.form-error.is-visible{ display:block; }\n.form-error a{ text-decoration:underline; }\n"
write(css_p, css)

# --------------------------------------------------------------------------
# sitemap.xml y robots.txt
urls = "\n".join(
    f"  <url><loc>{SITE}{p}</loc><lastmod>{d}</lastmod></url>" for p, d in sitemap_urls)
write(os.path.join(OUT, "sitemap.xml"),
      f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
write(os.path.join(OUT, "robots.txt"),
      f"User-agent: *\nAllow: /\nDisallow: /enviar.php\n\nSitemap: {SITE}/sitemap.xml\n")

# --------------------------------------------------------------------------
# 404 con el diseño de la web
s404 = read(os.path.join(SRC, "contacto.html"))
page404 = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Página no encontrada – Ro Eventos</title><meta name="robots" content="noindex, follow">
<link rel="icon" href="/favicon.ico" sizes="any">
<link href="{re.search(r'<link href="(https://fonts.googleapis.com/css2[^"]+)"', s404).group(1)}" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css"></head>
<body data-page="404">
{header.strip()}
<section class="hero hero--inner" style="background-image:url('/images/hero-home.jpg')"><div class="container hero-content">
<span class="eyebrow">Error 404</span><h1>Página no encontrada</h1>
<p class="lead">La página que buscas ya no existe o ha cambiado de dirección.</p>
<p style="margin-top:24px"><a class="btn btn-primary" href="/">Volver al inicio</a> <a class="btn btn-outline" href="/blog/">Ir al blog</a></p>
</div></section>
{footer.strip()}
<script src="/js/main.js"></script>
<script>document.addEventListener('DOMContentLoaded',function(){{document.dispatchEvent(new CustomEvent('partials:ready'))}});</script>
</body></html>"""
write(os.path.join(OUT, "404.html"), rewrite_links(page404))

print(f"OK: {len(built)} páginas en produccion/")
for p in sorted(built): print("  ", p)

# --------------------------------------------------------------------------
# .htaccess: HTTPS, sin www, páginas servidas y 301 de TODAS las URLs antiguas
rules = []
seen = set()
with open(os.path.join(ROOT, "migracion/urls-antiguas.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["accion_final"] != "301": continue
        src = urllib.parse.urlparse(r["url_antigua"]).path
        if src in seen: continue
        seen.add(src)
        rules.append((src.strip("/"), r["destino"]))
rules.sort()
exact = "\n".join(f"RewriteRule ^{re.escape(s)}/?$ {d} [R=301,L,NE]" for s, d in rules if s)
htaccess = f"""# R&O Eventos — producción (generado por migracion/build.py)
Options -Indexes
DirectoryIndex index.html index.php
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
RewriteEngine On

# 1) HTTPS y sin www (la web antigua ya canonicaliza a https://roeventos.com/)
RewriteCond %{{HTTPS}} !=on
RewriteCond %{{HTTP:X-Forwarded-Proto}} !https
RewriteRule ^ https://roeventos.com%{{REQUEST_URI}} [R=301,L]
RewriteCond %{{HTTP_HOST}} ^www\\. [NC]
RewriteRule ^ https://roeventos.com%{{REQUEST_URI}} [R=301,L]

# 2) Si el archivo o carpeta existe en la web nueva, se sirve tal cual
RewriteCond %{{DOCUMENT_ROOT}}%{{REQUEST_URI}} -f [OR]
RewriteCond %{{DOCUMENT_ROOT}}%{{REQUEST_URI}} -d
RewriteRule ^ - [L]

# 3) URLs antiguas del WordPress -> destino equivalente (301)
{exact}

# 4) Familias del WordPress sin ficha propia en la web nueva
RewriteRule ^wp-sitemap[^/]*\\.xml$ /sitemap.xml [R=301,L]
RewriteRule ^(category|tag|author|feed|comments)(/|$) /blog/ [R=301,L]
RewriteRule ^(event|team|calendar|events|events_category)/ /eventos/ [R=301,L]
RewriteRule ^portfolio-item/ /deportes/ [R=301,L]
RewriteRule ^(portfolio|elements|shop|cart|checkout|my-account)(/|$) / [R=301,L]
</IfModule>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>

<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
ExpiresByType image/x-icon "access plus 1 year"
ExpiresByType text/css "access plus 1 month"
ExpiresByType application/javascript "access plus 1 month"
ExpiresByType application/pdf "access plus 1 month"
</IfModule>

<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
"""
write(os.path.join(OUT, ".htaccess"), htaccess)
print(f".htaccess: {len(rules)} redirecciones 301 exactas + familias")

# --------------------------------------------------------------------------
# Variantes: .htaccess para un subdominio de pruebas y reglas equivalentes para nginx
pruebas = htaccess.replace(
    htaccess[htaccess.index("# 1) HTTPS"):htaccess.index("# 2) Si el archivo")],
    "# (pruebas) sin redirección a https/dominio final\n"
    "<IfModule mod_headers.c>\nHeader set X-Robots-Tag \"noindex, nofollow\"\n</IfModule>\n\n")
write(os.path.join(ROOT, "migracion/htaccess-PRUEBAS.txt"), pruebas)

ng = ["# R&O Eventos — reglas nginx (solo si el hosting NO usa .htaccess). Generado por build.py",
      "# Pegar dentro del bloque server { } de roeventos.com", "",
      "error_page 404 /404.html;", "location / { try_files $uri $uri/ =404; }", ""]
ng += [f"rewrite ^/{re.escape(s)}/?$ {d} permanent;" for s, d in rules if s]
ng += ["", "rewrite ^/wp-sitemap[^/]*\\.xml$ /sitemap.xml permanent;",
       "rewrite ^/(category|tag|author|feed|comments)(/|$) /blog/ permanent;",
       "rewrite ^/(event|team|calendar|events|events_category)/ /eventos/ permanent;",
       "rewrite ^/portfolio-item/(?!(basket|volleyball|futbol|futsal)(/|$)) /deportes/ permanent;",
       "rewrite ^/(portfolio|elements|shop|cart|checkout|my-account)(/|$) / permanent;",
       "location = /enviar.php { include fastcgi_params; fastcgi_param SCRIPT_FILENAME $document_root/enviar.php; fastcgi_pass unix:/run/php/php-fpm.sock; }"]
write(os.path.join(ROOT, "migracion/nginx-redirecciones.conf"), "\n".join(ng) + "\n")
