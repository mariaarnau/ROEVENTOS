<?php
/**
 * Receptor de los formularios de la web (contacto, eventos y CTA de la home).
 * Sin base de datos ni servicios externos: envía un correo desde el propio hosting.
 */
const DESTINO = 'info@roeventos.com';     // ← dónde llegan los mensajes
const REMITENTE = 'info@roeventos.com';    // ← debe ser un correo real del dominio (SPF/DKIM)

function volver(string $origen, string $estado): void {
    // solo rutas internas, nunca URLs externas (evita open redirect)
    if (!preg_match('#^/[A-Za-z0-9/_\-]*$#', $origen)) { $origen = '/contacto/'; }
    header('Location: ' . $origen . '?' . $estado . '=1', true, 303);
    exit;
}
function limpiar(string $s, int $max): string {
    $s = trim(strip_tags($s));
    $s = preg_replace('/[\r\n]+/', ' ', $s);      // sin saltos de línea: evita inyección de cabeceras
    return mb_substr($s, 0, $max);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contacto/', true, 303); exit; }

$origen = $_POST['origen'] ?? '/contacto/';

// anti-spam: campo trampa oculto + el formulario debe llevar >3 s abierto
if (!empty($_POST['web'])) { volver($origen, 'enviado'); }               // robot: finge éxito
$t = (int)($_POST['t'] ?? 0);
if ($t && (time() - $t) < 3) { volver($origen, 'enviado'); }

$nombre   = limpiar($_POST['nombre'] ?? '', 120);
$email    = trim($_POST['email'] ?? '');
$telefono = limpiar($_POST['telefono'] ?? '', 40);
$torneo   = limpiar($_POST['torneo'] ?? '', 120);
$mensaje  = trim(strip_tags($_POST['mensaje'] ?? ''));
$mensaje  = mb_substr($mensaje, 0, 4000);

if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 160) { volver($origen, 'error'); }
if (preg_match_all('#https?://#i', $mensaje) > 2) { volver($origen, 'enviado'); }   // spam con enlaces

$asunto = 'Web roeventos.com — ' . ($torneo !== '' ? $torneo : 'Contacto') . ($nombre !== '' ? " ($nombre)" : '');
$cuerpo = "Nuevo mensaje desde roeventos.com\n"
        . "Página: " . limpiar($origen, 200) . "\n\n"
        . "Nombre:   $nombre\n"
        . "Email:    $email\n"
        . "Teléfono: $telefono\n"
        . "Torneo:   $torneo\n\n"
        . "Mensaje:\n$mensaje\n";

$cabeceras = [
    'From' => 'R&O Eventos Web <' . REMITENTE . '>',
    'Reply-To' => $email,
    'MIME-Version' => '1.0',
    'Content-Type' => 'text/plain; charset=UTF-8',
    'X-Mailer' => 'roeventos-web',
];
$ok = mail(DESTINO, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $cuerpo, $cabeceras, '-f' . REMITENTE);

volver($origen, $ok ? 'enviado' : 'error');
