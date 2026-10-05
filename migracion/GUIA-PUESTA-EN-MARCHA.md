# Guía para sustituir la web antigua por la nueva (sin perder SEO)

**Regla de oro:** nada se borra. Todo lo que se quita de la web antigua se mueve a una copia de seguridad, y se puede volver atrás en minutos.

La carpeta que se sube al hosting es **`produccion/`** (se genera con `python3 migracion/build.py` a partir de `docs/`). La maqueta de `docs/` sigue siendo `noindex` y no compite con la web real.

---

## Qué se conserva para el SEO

| Qué | Cómo queda |
|---|---|
| URLs de las 6 páginas principales (`/`, `/conocenos/`, `/deportes/`, `/eventos/`, `/blog/`, `/contacto/`) | **Idénticas**, sin redirección |
| `<title>` de esas páginas | **Idénticos** a los que Google tiene hoy |
| Fichas de deporte `/portfolio-item/{basket,volleyball,futbol,futsal}/` | **Misma URL**, con el diseño nuevo |
| Noticia del premio Empren Esport (2022/11/01/…) | **Misma URL exacta** |
| Las otras 7 noticias antiguas | **301** a la página nueva más relacionada (lista en `urls-antiguas.csv`) |
| Resto de URLs del WordPress (210 en total: demos del tema, partidos, equipos, categorías…) | **301** a su equivalente (`/eventos/`, `/blog/`, `/deportes/`, `/`) |
| Sitemap antiguo `/wp-sitemap.xml` | 301 al nuevo `/sitemap.xml` |
| Imágenes antiguas `/wp-content/uploads/…` | Siguen funcionando **si no se borra esa carpeta** (ver paso 3) |

Mejoras añadidas (la web antigua no las tenía): meta description en todas las páginas, `canonical`, Open Graph (vista previa al compartir), datos estructurados (organización y noticias), `sitemap.xml`, `robots.txt`, página 404 con diseño, HTTPS y dominio sin `www` forzados, compresión y caché.

---

## Paso 1 · Antes de tocar nada (hoy)

1. **Copia de seguridad completa del WordPress** desde el panel del hosting (archivos **y** base de datos). Descárgala a tu ordenador. No sigas sin esto.
2. **Search Console** (search.google.com/search-console):
   - Comprueba que la propiedad `roeventos.com` existe y cómo está verificada (DNS, archivo o etiqueta). Si fue con un **archivo `google….html`** en la raíz, hay que conservarlo (ver paso 3).
   - Exporta: *Rendimiento → páginas y consultas* (últimos 16 meses) y *Páginas → indexadas*. Sirve de referencia para comparar después.
3. Anota qué **correos** (`info@`, `ro@`) existen en el hosting. No se tocan, pero conviene tenerlos a mano.
4. Apunta dónde se envían hoy los mensajes del formulario de Contact Form 7 (ajustes del plugin) y confirma que `e.arnau@roeventos.com` existe como casilla en el hosting (es el destino y el remitente de los avisos). Se cambia en `migracion/enviar.php` (`DESTINO`).

## Paso 2 · Probar en un subdominio (sin riesgo)

1. En el panel: crear el subdominio `nueva.roeventos.com` apuntando a una carpeta vacía.
2. Subir ahí el contenido de `produccion/`, pero **sustituyendo `.htaccess`** por `migracion/htaccess-PRUEBAS.txt` (renombrado a `.htaccess`). Esa versión no redirige al dominio final y añade `noindex`.
3. Revisar a mano: las 6 páginas, una noticia, el menú, el móvil, y **enviar un mensaje real desde cada formulario** (contacto, eventos y la home) comprobando que llega el correo y que sale el aviso verde.
4. Si no llega el correo: mirar spam; comprobar que `REMITENTE` en `enviar.php` es un correo real del dominio; si sigue sin llegar, se cambia a SMTP (se puede preparar).

## Paso 3 · El cambio (elegir un momento de poco tráfico)

En el **Administrador de archivos** del hosting, carpeta `public_html`:

1. **Crea una carpeta fuera de `public_html`** (por ejemplo `/home/USUARIO/wordpress_antiguo_2026-10`) y **mueve** ahí todo lo del WordPress **excepto**:
   - `wp-content/uploads/` → **se queda** (así no se rompen las imágenes antiguas ni los enlaces de otras webs a ellas).
   - Archivos `google….html`, `.well-known/`, `cgi-bin/` y cualquier archivo de verificación → **se quedan**.
   - Mueve también `wp-config.php`, `.htaccess` viejo, `wp-admin/`, `wp-includes/`, `index.php`, `wp-*.php` y el resto de `wp-content/`.
2. **Sube el contenido de `produccion/`** (incluido `.htaccess`, que es un archivo oculto: activa "mostrar archivos ocultos").
3. **Si el hosting es nginx puro y no lee `.htaccess`**, las redirecciones no funcionarán: en su lugar hay que añadir `migracion/nginx-redirecciones.conf` a la configuración del servidor (el hosting puede hacerlo en minutos). El servidor actual responde como `nginx`, así que **confírmalo con el soporte antes del cambio**.

## Paso 4 · Comprobación inmediata (10 minutos)

- `https://roeventos.com/` carga y `http://` y `www.` redirigen a `https://roeventos.com/`.
- Las 6 páginas principales cargan; el menú resalta la página actual.
- Redirecciones: abrir `/2022/09/21/basketball-tryouts-spain/`, `/category/basket/`, `/shop/`, `/wp-sitemap.xml` → deben terminar en la página nueva (no en 404).
- Una URL inventada → página 404 con diseño.
- `https://roeventos.com/sitemap.xml` y `/robots.txt` abren bien.
- Formularios: enviar una prueba real.
- Una imagen antigua, por ejemplo `https://roeventos.com/wp-content/uploads/2022/12/RO-CALIDAD.png` → debe verse.

## Paso 5 · Avisar a Google

1. Search Console → *Sitemaps* → añadir `https://roeventos.com/sitemap.xml` y quitar `wp-sitemap.xml`.
2. *Inspección de URL* de la home y de 2-3 páginas → *Solicitar indexación*.
3. Revisar *Páginas* y *Errores de rastreo* a los 3, 7 y 14 días: no deberían aparecer 404 en URLs que antes posicionaban. Si aparece alguna, se añade su redirección.
4. Comparar clics y posiciones con la exportación del paso 1 durante 4-6 semanas. Es normal una pequeña fluctuación los primeros días.

## Si algo sale mal (volver atrás)

1. Borrar el contenido nuevo de `public_html` (o moverlo a otra carpeta).
2. Devolver a `public_html` los archivos movidos del WordPress, incluido su `.htaccess` original.
3. La web antigua vuelve tal cual estaba. Si hiciera falta, se restaura la copia del paso 1.

**Mantener la copia del WordPress al menos 3 meses y las redirecciones al menos 1 año.**

---

## Cosas que conviene saber

- **Contenido de las páginas:** los títulos y URLs se mantienen, pero los textos de la web nueva son distintos a los antiguos. Si alguna página antigua posicionaba por una frase concreta, el export de Search Console (paso 1) lo muestra y se puede reforzar en la nueva.
- **Redes sociales del footer:** el Facebook y el LinkedIn de la maqueta eran enlaces vacíos (`#`) y los he quitado. Pásame las URLs reales y los pongo.
- **Analítica:** la web antigua no tiene Google Analytics ni etiquetas de seguimiento, así que no se pierde nada; si quieres medir visitas, hay que instalarlo.
- **Noticias con fecha:** las de Futsal Cup y Voley Cup llevan fecha 5 octubre 2026; si prefieres otra, se cambia antes de publicar (la fecha también va a Google).
- **Correo:** `enviar.php` usa `mail()` del hosting. Es lo más simple, pero algunos hosts lo limitan; si los mensajes cayeran en spam se pasa a SMTP.
