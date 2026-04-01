import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER     = os.getenv("GMAIL_USER", "copia1bedoya@gmail.com")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")


def send_confirmation_email(nombre: str, apellido: str, email_destino: str) -> None:
    """
    Envía un correo de confirmación de registro al paciente.
    Se llama justo después de crear el usuario en la base de datos.
    """

    subject = "¡Bienvenido a Clínica Boris Viafara! Tu cuenta fue creada"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">

      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0"
                   style="background:#ffffff;border-radius:16px;overflow:hidden;
                          box-shadow:0 4px 24px rgba(0,0,0,0.08);">

              <!-- HEADER -->
              <tr>
                <td style="background:linear-gradient(135deg,#0d2b1d 0%,#1a7a4a 100%);
                           padding:40px 40px 32px;text-align:center;">
                  <p style="margin:0 0 8px;font-size:13px;font-weight:600;
                             letter-spacing:0.15em;text-transform:uppercase;
                             color:rgba(255,255,255,0.6);">Portal de Pacientes</p>
                  <h1 style="margin:0;font-size:26px;font-weight:700;color:#ffffff;">
                    Dr. Boris Viafara
                  </h1>
                  <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.7);
                             font-style:italic;">Cirugía de Alta Especialidad</p>
                </td>
              </tr>

              <!-- ÍCONO CHECK -->
              <tr>
                <td align="center" style="padding:36px 40px 0;">
                  <div style="width:72px;height:72px;background:#1a7a4a;border-radius:50%;
                              display:inline-flex;align-items:center;justify-content:center;
                              margin:0 auto;">
                    <span style="font-size:36px;color:#ffffff;line-height:1;">✓</span>
                  </div>
                </td>
              </tr>

              <!-- CUERPO -->
              <tr>
                <td style="padding:28px 40px 0;text-align:center;">
                  <h2 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#0d2b1d;">
                    ¡Registro exitoso, {nombre}!
                  </h2>
                  <p style="margin:0 0 24px;font-size:15px;color:#4a7060;line-height:1.7;">
                    Tu cuenta de paciente en el portal del <strong>Dr. Boris Viafara</strong>
                    ha sido creada correctamente. Ya puedes iniciar sesión y agendar
                    tus citas médicas.
                  </p>
                </td>
              </tr>

              <!-- DATOS -->
              <tr>
                <td style="padding:0 40px;">
                  <table width="100%" cellpadding="0" cellspacing="0"
                         style="background:#f0faf4;border:1px solid #d1f0e0;
                                border-radius:12px;padding:20px;">
                    <tr>
                      <td style="padding:8px 16px;">
                        <p style="margin:0;font-size:13px;color:#4a7060;">Nombre registrado</p>
                        <p style="margin:4px 0 0;font-size:15px;font-weight:600;color:#0d2b1d;">
                          {nombre} {apellido}
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:8px 16px;">
                        <p style="margin:0;font-size:13px;color:#4a7060;">Correo electrónico</p>
                        <p style="margin:4px 0 0;font-size:15px;font-weight:600;color:#0d2b1d;">
                          {email_destino}
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- BOTÓN -->
              <tr>
                <td align="center" style="padding:32px 40px;">
                  <a href="http://localhost:8000/login"
                     style="display:inline-block;background:#1a7a4a;color:#ffffff;
                            text-decoration:none;font-size:15px;font-weight:700;
                            padding:14px 36px;border-radius:10px;
                            box-shadow:0 4px 16px rgba(26,122,74,0.35);">
                    Iniciar sesión
                  </a>
                </td>
              </tr>

              <!-- AVISO -->
              <tr>
                <td style="padding:0 40px 16px;text-align:center;">
                  <p style="margin:0;font-size:13px;color:#9eb8a8;line-height:1.6;">
                    Si no creaste esta cuenta, puedes ignorar este correo.
                    Nadie más puede acceder sin tu contraseña.
                  </p>
                </td>
              </tr>

              <!-- FOOTER -->
              <tr>
                <td style="background:#f8fbf9;border-top:1px solid #d1e5d9;
                           padding:20px 40px;text-align:center;">
                  <p style="margin:0;font-size:12px;color:#9eb8a8;">
                    © 2026 Dr. Boris Viafara · Cirugía de Alta Especialidad
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>

    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Clínica Boris Viafara <{GMAIL_USER}>"
    msg["To"]      = email_destino

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, email_destino, msg.as_string())
