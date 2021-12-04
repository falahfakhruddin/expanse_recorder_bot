import telebot
import time
import re
import traceback
from telebot import types
from datetime import datetime

token = '<BOT TOKEN>'
bot = telebot.TeleBot(token, parse_mode=None)

commands = {  # command description used in the "help" command
	'help' 		: 'Display this menu',
	'new'  	 	: 'Record new spending',
	'show' 	 	: 'Show spending history',
	'clear'		: 'Clear all your records (on development)',
	'report'	: 'generate expense tracker report sheet (on development)',
	'feedback'	: 'Yay or Nay? Tell me how I can be better!'
}

global_expense_tracker = {}

date_format = '%d-%b-%Y'
time_format = '%H:%M'

CATEGORIES = ['Food', 'Groceries', 'Transport', 'Shopping', 'Others']


@bot.message_handler(commands=['start', 'help'])
def command_start(message):

	cid = message.chat.id
	help_text = "Welcome! I am your money saver :), how can I help you today?\nThese are commands which available: \n\n"
	for key in commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + key + ": "
		help_text += commands[key] + "\n"

	bot.send_message(cid, help_text)


@bot.message_handler(commands=['new'])
def create_new_expense_record(message):
	cid = message.chat.id
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	for cat in CATEGORIES:
		markup.add(cat)
	message = bot.send_message(cid, 'Please select spending category ', reply_markup=markup)
	bot.register_next_step_handler(message, process_spending_message)


def process_spending_message(message):
	cid = message.chat.id
	category = message.text
	message = bot.send_message(cid, 'How much did you spent and what is it for? \n'
									'(Using , as delimiter of amount and note ex: "120000, shopping in indomaret")')
	bot.register_next_step_handler(message, process_amount_step, category)


def process_amount_step(message, category):
	try:
		cid = message.chat.id
		amount_num, note = parsing_amount(message.text)  # validate
		if not amount_num.isdecimal():  # cannot be Rp.0 spending
			raise Exception("Amount is invalid number")

		dt = datetime.today().strftime(date_format + ' ' + time_format)
		input_user_expanses(dt, amount_num, cid, note, category)

		bot.send_message(cid, 'Recorded: You spent Rp.{} in {} category on {}\nnote: {}'.format(amount_num, category, dt, note))

	except Exception as e:
		bot.reply_to(message, 'Opps! ' + str(e))


def parsing_amount(spending):
	try:
		spending_detail = spending.split(',', 1)
		spending_amount = re.sub(r"[^0-9]", "", spending_detail[0])
		if len(spending_detail) > 1:
			spending_note = spending_detail[1].strip()
		else:
			spending_note = ""
		return spending_amount, spending_note

	except Exception as e:
		traceback.print_exc()
		raise Exception


def input_user_expanses(dt, amount_num, cid, note, category):
	global global_expense_tracker

	if cid not in global_expense_tracker:
		global_expense_tracker[cid] = []

	expanse_record = dt + " : Rp." + amount_num + " for: " + note + " category: " + category
	global_expense_tracker[cid].append(expanse_record)


@bot.message_handler(commands=['show'])
def show_total_expenses(message):
	global global_expense_tracker
	cid = message.chat.id
	if cid in global_expense_tracker:
		record = global_expense_tracker[cid]
		print(record)
		record_msg = ''
		for data in record:
			record_msg = record_msg + data + "\n"
		bot.send_message(cid, record_msg)
	else:
		bot.send_message(cid, "There is no expense record for you, please try create a new in using /new command")


@bot.message_handler(commands=['feedback'])
def feedback_command(message):
	cid = message.chat.id
	msg = bot.send_message(cid, "Any suggestion to improve my function for you?")
	bot.register_next_step_handler(msg, process_feedback)


def process_feedback(m):
	print("{} name:{} chatid:{} \nmessage: {}\n".format(str(datetime.now()), str(m.chat.first_name),
														str(m.chat.id), str(m.text)))


@bot.message_handler(commands=['my_id'])
def get_chat_id_command(message):
	cid = message.chat.id
	bot.reply_to(message, "Here is your chat id: {}".format(cid))


# default handler for every other text
@bot.message_handler(func=lambda message: True)
def command_default(m):
	# this is the standard reply to a normal message
	bot.send_message(m.chat.id, "I can't understand with  \"" + m.text + "\"\nMaybe try the help page at /help")


def main():
	while True:
		try:
			bot.polling(none_stop=True)

		except Exception as e:
			traceback.print_exc()
			time.sleep(15)


if __name__ == '__main__':
	main()
