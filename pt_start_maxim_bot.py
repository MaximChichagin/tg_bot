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

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def get_app_list_command(update: Update, context):
    update.message.reply_text('Введите 1, если хотите видеть все установленные пакеты; введите 2, если хотите видеть информацию о конкретном пакете: ')
    user_input = update.message.text
    if user_input == '1':
        return 'get_app_list_all'
    if user_input == '2':
        return 'get_app_list_one'
    update.message.reply_text('Неверный ввод!')



def findPhoneNumbers(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий (или нет) номера телефонов

    phoneNumRegex = re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}') # формат 8 (000) 000-00-00

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_app_list(update: Update, context):


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
    update.message.reply_text(linux('ps -A'))

def get_ss(update: Update, context):
    update.message.reply_text(linux('ss -s'))

def get_services(update: Update, context):
    update.message.reply_text(linux('service --status-all'))

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerAppList = ConversationHandler(
        entry_points=[CommandHandler('get_app_list', get_app_list_command)],
        states={
            'get_app_list_all': [MessageHandler(Filters.text & ~Filters.command, get_app_list_all)],
            'get_app_list_one': [MessageHandler(Filters.text & ~Filters.command, get_app_list_one)],
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
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerAppList)
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
