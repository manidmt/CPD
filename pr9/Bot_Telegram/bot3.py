from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import command
from icmplib import ping, NameLookupError, ICMPError


def ejecuta_w():
    res = command.run(['ls'])
    print(res.output)
    return str(res.output)

def check_ping(host):
    try:
        return ping(host, privileged=False, count=1).is_alive
    except NameLookupError:
        return "DNS_ERROR"
    except ICMPError:
        return "ICMP_ERROR"
    except Exception:
        return "UNKNOWN_ERROR"
    
# Mensaje de bienvenida
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "*Este es el Bot de Manuel Díaz-Meco creado para la práctica 9 de la asignatura CPD.*\n\n"
        "Estos son los comandos:\n\n"
        "• `/start` - Muestra este mensaje de bienvenida.\n"
        "• `/ping <dirección_ip_o_dominio>` - Realiza un ping al host especificado y comprueba si responde.\n\n"
    )
    await update.message.reply_text(text=welcome_message, parse_mode=ParseMode.MARKDOWN)

async def resp_ls(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(ejecuta_w())
#Para hacer ping
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        message = ("Por favor, proporcionar una dirección IP o dominio después del comando /ping\n\n"
                    "El uso es el siguiente: `/ping <dirección_ip_o_dominio>`")
        await update.message.reply_text(text=message,
        parse_mode=ParseMode.MARKDOWN)
        return

    host = context.args[0]

    result = check_ping(host)

    if result is True:
        await update.message.reply_text(text=f"El host `{host}` está respondiendo", parse_mode=ParseMode.MARKDOWN)
    elif result == "DNS_ERROR":
        await update.message.reply_text(text=f"No se pudo resolver el nombre de dominio: `{host}`", parse_mode=ParseMode.MARKDOWN)
    elif result == "ICMP_ERROR":
        await update.message.reply_text(text=f"Ocurrió un error ICMP al intentar hacer ping a `{host}`", parse_mode=ParseMode.MARKDOWN)
    elif result == "UNKNOWN_ERROR":
        await update.message.reply_text(text=f"Ocurrió un error desconocido al intentar hacer ping a {host}",parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text=f"No se pudo hacer ping al host {host}.", parse_mode=ParseMode.MARKDOWN)
        
#Función para checkar el ping de la ugr
async def check_ugr_ping(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data['chat_id']
    result = check_ping('ugr.es') #Hacemos ping a ugr.es
    if result is True:
        message = "El host `ugr.es` está respondiendo"
    elif result == "DNS_ERROR":
        message = "No se pudo resolver el nombre de dominio: `ugr.es`"
    elif result == "ICMP_ERROR":
        message = "Ocurrió un error ICMP al intentar hacer ping a `ugr.es`"
    elif result == 'UNKNOWN_ERROR':
        message = "Ocurrió un error desconocido al intentar hacer ping a `ugr.es`"
    else:
        message = "No se pudo hacer ping al host `ugr.es`"
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)


#Función para suscribirse al ping a la UGR
async def start_ugr_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.job_queue.run_repeating(check_ugr_ping,
    interval=timedelta(minutes=1), first=10, data={'chat_id': chat_id})
    await update.message.reply_text("Se ha iniciado el monitoreo de ping a `ugr.es`. Recibirás actualizaciones cada minuto.")
#Función para desuscribirse del ping a la UGR
async def stop_ugr_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name('check_ugr_ping')
    job_removed = False
    for job in current_jobs:
        if job.data['chat_id'] == chat_id:
            job.schedule_removal()
            job_removed = True
            break
        if job_removed:
            await update.message.reply_text("Se ha detenido el monitoreo de ping a `ugr.es` para este chat", parse_mode= ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("No se encontró ningún monitoreo activo para este chat")

app = ApplicationBuilder().token("8012205959:AAHTKUKWwEEfKNnRIjetpLkUHbzFaMMDdSI").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ping", ping_command))
app.add_handler(CommandHandler("start_ping_ugr", start_ugr_ping))
app.add_handler(CommandHandler("stop_ugr_ping", stop_ugr_ping))
app.run_polling()