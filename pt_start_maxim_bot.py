import logging
import re

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


TOKEN = "7098871610:AAE-ucrsjqPLk0Y6ed-VYUfSK9YaDpEw4iU"


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


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

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


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


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
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
