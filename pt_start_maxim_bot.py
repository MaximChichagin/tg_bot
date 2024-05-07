import logging
import re
import paramiko

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


TOKEN = "7098871610:AAE-ucrsjqPLk0Y6ed-VYUfSK9YaDpEw4iU"

host = '192.168.88.182'
port = '22'
username = 'kali'
password = 'kali'

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Инициализируем нужные функции
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'findEmails'

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности: ')
    return 'verifyPassword'

def findEmails(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b') # регулярное выражение для поиска email-адресов
    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END 

    emails = ''
    for i, email in enumerate(emailList):
        emails += f'{i+1}. {email}\n'
    
    update.message.reply_text(emails)
    return ConversationHandler.END

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END 

    phoneNumbers = ''
    for i, phoneNumber in enumerate(phoneNumberList):
        phoneNumbers += f'{i+1}. {phoneNumber}\n'
    
    update.message.reply_text(phoneNumbers)
    return ConversationHandler.END

def verifyPassword(update: Update, context):
    user_input = update.message.text
    passwordRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')
    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END

def get_app_list_all(update: Update, context):
    update.message.reply_text(linux('dpkg -l | head -n 11'))
    return ConversationHandler.END

def get_app_list_one(update: Update, context):
    update.message.reply_text('Введите название пакета для поиска информации: ')
    return 'get_app_info'

def get_app_info(update: Update, context):
    package_name = update.message.text.strip()
    app_info = linux(f'dpkg -s {package_name}')
    update.message.reply_text(app_info)
    return ConversationHandler.END

def get_app_list_command(update: Update, context):
    update.message.reply_text('Введите 1, если хотите видеть информацию о первых 10 установленных пакетах; введите 2, если хотите видеть информацию о конкретном пакете: ')
    return 'get_app_list_choice'

def get_app_list_choice(update: Update, context):
    user_input = update.message.text
    if user_input == '1':
        return get_app_list_all(update, context)
    elif user_input == '2':
        return get_app_list_one(update, context)
    update.message.reply_text('Неверный ввод')
    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def linux(command: str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

def get_release(update: Update, context):
    update.message.reply_text(linux('cat /proc/version'))

def get_uname(update: Update, context):
    update.message.reply_text(linux('uname -o -n -r -v -p'))

def get_uptime(update: Update, context):
    update.message.reply_text(linux('uptime'))

def get_df(update: Update, context):
    update.message.reply_text(linux('df -a -h'))

def get_free(update: Update, context):
    update.message.reply_text(linux('free -h'))

def get_mpstat(update: Update, context):
    update.message.reply_text(linux('mpstat -P ALL'))

def get_w(update: Update, context):
    update.message.reply_text(linux('w'))

def get_auths(update: Update, context):
    update.message.reply_text(linux('last -n 10'))

def get_critical(update: Update, context):
    update.message.reply_text(linux('journalctl -p crit -n 5'))

def get_ps(update: Update, context):
    update.message.reply_text(linux('ps -A | head -n 11'))

def get_ss(update: Update, context):
    update.message.reply_text(linux('ss -s'))

def get_services(update: Update, context):
    update.message.reply_text(linux('service --status-all'))

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчики диалога
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
        },
        fallbacks=[]
    )

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerAppList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_app_list_command)],
        states={
            'get_app_list_choice': [MessageHandler(Filters.text & ~Filters.command, get_app_list_choice)],
            'get_app_info': [MessageHandler(Filters.text & ~Filters.command, get_app_info)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerAppList)
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()