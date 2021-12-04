import telebot
import time
import re
import traceback
from telebot import types
from datetime import datetime

token = '1860559145:AAGQuYWntJXopyuLePGLoZ_Xr9dNI0Pf2oQ'
bot = telebot.TeleBot(token, parse_mode=None)

commands = {  # command description used in the "help" command
	'help' 		: 'Display this menu',
	'new'  	 	: 'Record new spending',
	'show' 	 	: 'Show total spending',
	'clear'		: 'debugger: clear all your records (on development)',
	'delete'	: 'clear selected record (on development)',
	'report'	: 'generate expense tracker report sheet (on development)',
	'feedback'	: 'Yay or Nay? Tell me how I can be better!'
}

global_expense_tracker = {}

date_format = '%d-%b-%Y'
time_format = '%H:%M'


# only used for console output now
def listener(messages):
	"""
	When new messages arrive TeleBot will call this function.
	"""
	for m in messages:
		if m.content_type == 'text':
			# print the sent message to the console
			print("{} name:{} chatid:{} \nmessage: {}\n".format(str(datetime.now() ),str(m.chat.first_name
																),str(m.chat.id ),str(m.text)))


@bot.message_handler(commands=['start', 'help'])
def command_start(message):

	cid = message.chat.id
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	markup.row_width = 2
	help_text = "Welcome! I am your money saver :), how can I help you today?\nThese are available commands: \n\n"
	for key in commands:  # generate help text out of the commands dictionary defined at the top
		help_text += "/" + key + ": "
		help_text += commands[key] + "\n"
		markup.add(commands[key])

	bot.send_message(cid, help_text)


@bot.message_handler(commands=['new'])
def create_new_expense_record(message):
	cid = message.chat.id
	message = bot.send_message(cid, 'How much did you spent? \n(Enter numbers only WITHOUT . for delimiter)')
	bot.register_next_step_handler(message, process_amount_step)


def process_amount_step(message):
	try:
		cid = message.chat.id
		amount_num = validate_amount(message.text)  # validate
		if amount_num == 0:  # cannot be Rp.0 spending
			raise Exception("Amount cannot be Rp.0! or amount is invalid number")

		dt = datetime.today().strftime(date_format + ' ' + time_format)
		input_user_expanses(dt, amount_num, cid)

		dt_text, amt_text = str(dt), str(amount_num)
		bot.send_message(cid, 'Recorded: You spent Rp.{} on {}'.format(amt_text, dt_text))

	except Exception as e:
		bot.reply_to(message, 'Opps! ' + str(e))


def validate_amount(amount_string):
	if 0 < len(amount_string) <= 15:
		if amount_string.isdigit:
			if re.match("^[0-9]*\\.?[0-9]*$", amount_string):
				amount = int(amount_string)
				if amount > 0:
					return str(amount)
	return 0


def input_user_expanses(dt, amount_num, cid):
	global global_expense_tracker

	if cid not in global_expense_tracker:
		global_expense_tracker[cid] = []

	expanse_record = dt + " : Rp." + amount_num
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
		bot.send_message(cid, "There is no expense record for you, please try create a new spending by using /new command")


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
