from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_recuperacion(destinatario, asunto, codigo):
    """
    Envía un correo con un código de recuperación usando HTML personalizado.
    """
    mensaje_texto = f'Tu código de recuperación es: {codigo}'

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px; border: 1px solid #ddd;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/474x/3f/12/a1/3f12a1195c99b8453369d31060be4a9f.jpg" alt="Recuperación de contraseña" style="max-width: 150px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #333; text-align: center;">🔐 Recuperación de contraseña</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hemos recibido una solicitud para restablecer tu contraseña en <strong>Mi App</strong>.
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <p style="font-size: 18px; color: #333;">Tu código es:</p>
            <p style="font-size: 32px; font-weight: bold; color: #4A154B; letter-spacing: 2px;">{codigo}</p>
        </div>
        <p style="font-size: 14px; color: #777; text-align: center;">
            Este código expirará en 10 minutos. Si no solicitaste este código, puedes ignorar este correo.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="#" style="background-color:rgb(65, 41, 65); color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">🌐 Ir a Mi App</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def enviar_correo_registro(destinatario, nombre_usuario):
    """
    Envía un correo de bienvenida tras el registro del cliente.
    """
    asunto = "Bienvenido a CandyNails 💅"
    mensaje_texto = f"Hola {nombre_usuario}, gracias por registrarte en CandyNails. 🎉"

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/564x/0e/ae/64/0eae64ff82b0e63b91ef3b91e46d52a3.jpg" alt="Bienvenida" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">🎉 ¡Bienvenida a CandyNails!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_usuario}</strong>, gracias por unirte a nuestra comunidad.
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            En CandyNails estamos felices de tenerte aquí. Agenda tus citas fácilmente y descubre nuestros servicios.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="#" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">💅 Explora CandyNails</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de registro: {e}")
        return False

def enviar_correo_cambio_password(destinatario, nombre_usuario):
    """
    Envía un correo notificando que la contraseña fue cambiada exitosamente.
    """
    asunto = "🔐 Contraseña actualizada con éxito"
    mensaje_texto = f"Hola {nombre_usuario}, tu contraseña en CandyNails ha sido cambiada correctamente."

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #f1f9f9; border-radius: 10px; border: 1px solid #d1ecf1;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/564x/7e/f4/42/7ef44226d5df65a76509be26de79d7ea.jpg" alt="Cambio de contraseña" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #0c5460; text-align: center;">🔐 Cambio de contraseña exitoso</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_usuario}</strong>, tu contraseña ha sido actualizada correctamente en <strong>CandyNails</strong>.
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            Si no fuiste tú quien realizó este cambio, por favor contacta con el soporte inmediatamente.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="#" style="background-color:#117a8b; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">🔐 Ir a CandyNails</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de cambio de contraseña: {e}")
        return False

def enviar_correo_confirmacion(destinatario, nombre_cliente, fecha, hora, servicios=None):
    """
    Envía un correo confirmando que la cita fue registrada exitosamente, con detalle de servicios.
    """
    asunto = "📅 Cita registrada en CandyNails"
    mensaje_texto = f"Hola {nombre_cliente}, tu cita ha sido registrada para el día {fecha} a las {hora}."

    # Construir la tabla HTML de servicios
    servicios_html = ""
    total = 0

    if servicios:
        filas = ""
        for s in servicios:
            filas += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ccc;">{s['nombre']}</td>
                <td style="padding: 8px; border: 1px solid #ccc; text-align: right;">${s['subtotal']:.2f}</td>
            </tr>
            """
            total += s['subtotal']

        servicios_html = f"""
        <h3 style="color: #a44a3f;">🧾 Detalles de tu cita</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <thead>
                <tr>
                    <th style="padding: 8px; background-color: #fdd; border: 1px solid #ccc;">Servicio</th>
                    <th style="padding: 8px; background-color: #fdd; border: 1px solid #ccc; text-align: right;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {filas}
                <tr>
                    <td style="padding: 8px; border: 1px solid #ccc; font-weight: bold;">Total</td>
                    <td style="padding: 8px; border: 1px solid #ccc; font-weight: bold; text-align: right;">${total:.2f}</td>
                </tr>
            </tbody>
        </table>
        """

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fef9f5; border-radius: 10px; border: 1px solid #ffe5d0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/564x/27/f0/ef/27f0ef723c6f89eaf1ee00eec3ef68d0.jpg" alt="Cita confirmada" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #a44a3f; text-align: center;">📅 ¡Cita confirmada!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_cliente}</strong>, tu cita ha sido registrada exitosamente para el <strong>{fecha}</strong> a las <strong>{hora}</strong>.
        </p>
        {servicios_html}
        <p style="font-size: 15px; color: #777; text-align: center;">
            Si deseas reprogramar o cancelar tu cita, comunícate con nosotros con anticipación.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="#" style="background-color:#d9480f; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">💅 Ir a CandyNails</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de confirmación de cita: {e}")
        return False
