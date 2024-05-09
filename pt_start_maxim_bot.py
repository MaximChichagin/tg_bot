import logging
import re
import paramiko
import os
import psycopg2

from psycopg2 import Error
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()

token = os.getenv('TOKEN')

host_sys_mon = os.getenv('HOST_SYS_MON')
port_sys_mon = os.getenv('PORT_SYS_MON')
username_sys_mon = os.getenv('USER_SYS_MON')
password_sys_mon = os.getenv('PASSWORD_SYS_MON')

host_repl = os.getenv('HOST_REPL')
port_repl = os.getenv('PORT_REPL')
username_repl = os.getenv('USER_REPL')
password_repl = os.getenv('PASSWORD_REPL')

username_db = os.getenv('USER_DB')
password_db = os.getenv('PASSWORD_DB')
host_db = os.getenv('HOST_DB')
port_db = os.getenv('PORT_DB')
database_db = os.getenv('DATABASE_DB')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
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
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END 

    emails = ''
    for i, email in enumerate(emailList):
        emails += f'{i+1}. {email}\n'
    
    update.message.reply_text(emails)

    update.message.reply_text('Хотите сохранить найденные email-адреса в базе данных? (да/нет)')
    context.user_data['emails'] = emailList
    return 'saveEmails'

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

    update.message.reply_text('Хотите сохранить найденные номера телефонов в базе данных? (да/нет)')
    context.user_data['phone_numbers'] = phoneNumberList

    return 'savePhoneNumbers'

def saveEmails(update: Update, context):
    user_response = update.message.text.lower()
    emailList = context.user_data.get('emails', [])

    if user_response == 'да':
        for email in enumerate(emailList):
            answer = db("INSERT INTO email_table (email) VALUES ('" + str(email[1]) + "');", username_db, password_db, host_db, port_db, database_db, 'insert')
            
            update.message.reply_text(answer)
            if answer == "Ошибка при работе с PostgreSQL":
                    return ConversationHandler.END
        update.message.reply_text('Email-адреса успешно сохранены в базе данных')
    else:
        update.message.reply_text('Email-адреса не будут сохранены в базе данных')

    return ConversationHandler.END

def savePhoneNumbers(update: Update, context):
    user_response = update.message.text.lower()
    phoneNumberList = context.user_data.get('phone_numbers', [])

    if user_response == 'да':
        for phoneNumber in enumerate(phoneNumberList):
            answer = db("INSERT INTO phone_table (phone_number) VALUES ('" + str(phoneNumber[1]) + "');", username_db, password_db, host_db, port_db, database_db, 'insert')
            
            update.message.reply_text(answer)
            if answer == "Ошибка при работе с PostgreSQL":
                    return ConversationHandler.END
        update.message.reply_text('Номера телефонов успешно сохранены в базе данных')
    else:
        update.message.reply_text('Номера телефонов не будут сохранены в базе данных')

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

def linux(command: str, host: str, username: str, password: str, port: str):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        logging.info("Команда успешно выполнена")
        return data
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с Linux: %s", error)
        return "Не удалось установить соединение"

def db(command: str, username: str, password: str, host: str, port: str, database: str, type: str):
    connection = None
    result = ''

    try:
        connection = psycopg2.connect(user=username, password=password, host=host, port=port, database=database)
        cursor = connection.cursor()
        cursor.execute(command)
        if type == 'select':
            data = cursor.fetchall()
            for row in data:
                result += str(row[0]) + ' ' + str(row[1]) + '\n'
        elif type == 'insert':
            connection.commit()
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        return "Ошибка при работе с PostgreSQL"
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        if result:
            return result
        return "Ошибка при работе с PostgreSQL"

def get_emails(update: Update, context):
    update.message.reply_text(db('SELECT * FROM email_table;', username_db, password_db, host_db, port_db, database_db, 'select'))

def get_phone_numbers(update: Update, context):
    update.message.reply_text(db('SELECT * FROM phone_table;', username_db, password_db, host_db, port_db, database_db, 'select'))

def get_release(update: Update, context):
    update.message.reply_text(linux('cat /proc/version', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_uname(update: Update, context):
    update.message.reply_text(linux('uname -o -n -r -v -p', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_uptime(update: Update, context):
    update.message.reply_text(linux('uptime', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_df(update: Update, context):
    update.message.reply_text(linux('df -a -h', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_free(update: Update, context):
    update.message.reply_text(linux('free -h', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_mpstat(update: Update, context):
    update.message.reply_text(linux('mpstat -P ALL', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_w(update: Update, context):
    update.message.reply_text(linux('w', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_auths(update: Update, context):
    update.message.reply_text(linux('last -n 10', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_critical(update: Update, context):
    update.message.reply_text(linux('journalctl -p crit -n 5', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_ps(update: Update, context):
    update.message.reply_text(linux('ps -A | head -n 11', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_ss(update: Update, context):
    update.message.reply_text(linux('ss -s', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_services(update: Update, context):
    update.message.reply_text(linux('service --status-all', host_sys_mon, username_sys_mon, password_sys_mon, port_sys_mon))

def get_repl_logs(update: Update, context):
    update.message.reply_text(linux('cat /var/log/postgresql/postgresql-15-main.log | grep repl_user | tail -n 10', host_repl, username_repl, password_repl, port_repl))

def main():
    updater = Updater(token, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчики диалога
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'saveEmails': [MessageHandler(Filters.text & ~Filters.command, saveEmails)]
        },
        fallbacks=[]
    )

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'savePhoneNumbers':  [MessageHandler(Filters.text & ~Filters.command, savePhoneNumbers)]
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
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
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