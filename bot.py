import os
import logging
from telegram import LabeledPrice, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
)

# Configurar logs para ver si hay errores en la consola
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Leemos el token de las variables de entorno por seguridad
TOKEN = os.environ.get("TOKEN")
# Coloca aquí el ID de tu grupo o canal privado (ejemplo: -1001234567890)
GROUP_ID = -100XXXXXXXXX 

# 1. Comando para que el usuario pida la factura VIP
async def buy_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # 100 Estrellas (puedes cambiar la cantidad)
    prices = [LabeledPrice("Acceso VIP Mensual", 100)]
    
    await context.bot.send_invoice(
        chat_id=chat_id,
        title="Suscripción VIP Telegram",
        description="Acceso exclusivo al grupo privado por 30 días.",
        payload="vip_subscription_payload",
        provider_token="",  # VACÍO para Telegram Stars
        currency="XTR",     # Moneda oficial de Stars
        prices=prices,
        start_parameter="vip-sub"
    )

# 2. Validación Pre-Checkout obligatoria
async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.payload == "vip_subscription_payload":
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Ha ocurrido un error. Inténtalo de nuevo.")

# 3. Pago Exitoso: Generar enlace único para el grupo
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    try:
        # Generamos un enlace de invitación de un solo uso
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            member_limit=1 
        )
        
        await update.message.reply_text(
            f"¡Pago recibido con éxito! 🎉 Muchas gracias por apoyar con Estrellas.\n\n"
            f"Aquí tienes tu enlace exclusivo de acceso al grupo:\n{invite_link.invite_link}"
        )
    except Exception as e:
        await update.message.reply_text(
            "Pago exitoso, pero hubo un error al generar el enlace automático. Contacta al administrador."
        )

def main():
    if not TOKEN:
        print("Error: No se encontró el TOKEN del bot.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("suscribirse", buy_vip))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    print("Bot iniciado correctamente...")
    app.run_polling()

if __name__ == "__main__":
    main()