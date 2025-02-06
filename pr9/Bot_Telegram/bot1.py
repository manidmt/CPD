from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import command

def ejecuta_w():
    res = command.run(['ls'])
    print(res.output)
    return str(res.output)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(f'Hello {update.effective_user.first_name}')
async def resp_ls(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(ejecuta_w())

app = ApplicationBuilder().token("**************************zFaMMDdSI").build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("ls", resp_ls))
app.run_polling()
