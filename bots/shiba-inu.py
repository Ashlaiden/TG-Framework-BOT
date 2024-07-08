import os
import sys
# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import sqlite3
import telebot
from core import ProcessThread, Log, DB, manage
# from manage import address
# from typing import Optional, Dict
from telebot import types
from telebot.apihelper import ApiTelegramException
from datetime import datetime, timedelta
import re
from Crypto.Hash import keccak
from peewee import Model, CharField, IntegerField, BooleanField, AutoField, TextField, DateTimeField, IntegrityError

db_name = 'shiba-inu'
db = DB(db_name)

address = manage.address

log_obj = Log(db_name)
log = log_obj.return_logging()
log.critical('Script Restarted!')


# MODELS
class BaseModel(Model):
    class Meta:
        database = db.db


class User(BaseModel):
    id = AutoField(primary_key=True, unique=True)
    uid = IntegerField(null=False, unique=True)
    user_name = CharField(null=False, max_length=150)
    coin = IntegerField(default=0)
    wallet_address = TextField(null=True)
    created = DateTimeField(default=datetime.now)
    last_bonus = DateTimeField(null=True)
    bonus_count = IntegerField(default=0)
    referral_user = IntegerField(default=0)
    agent = IntegerField(null=True)
    request_withdrawal = BooleanField(default=False)
    transaction_amount = IntegerField(default=0)

    def __str__(self):
        return f'{self.uid} - {self.user_name}'


db.add_to_table_list(User)
db.migrate()


# Logic
TOKEN = "Your-bot-token"
bot_username = 'your-bot-user-name'
referral_banner_photo_name = 'referral_banner.jpg'
channels_id = ["@your-channel"]
bot = telebot.TeleBot(token=TOKEN)
# PORT = int(os.environ.get('PORT', 5000))

# Functional Values
exit_flag = False


# Dictionary to store user data during the conversation
user_data = dict()
del_messages_id = dict()
del_msg = list()
is_sub_del = dict()
referral_id = dict()


# DATA MODELS
class ListeningModel:
    def __init__(self):
        self.search = self.SearchingListener()

    class SearchingListener:
        def __init__(self):
            self.process = None
            self.active = False
            self.column = None
            self.min = 0
            self.count = 0
            self.attr_is_bool = False
            self.sameness = False
            self.proc_msg_id = None

        def back_to_default(self):
            if listening.search.process:
                if listening.search.process.active:
                    listening.search.process.terminate()
            self.process = None
            self.active = False
            self.column = None
            self.min = 0
            self.count = 0
            self.attr_is_bool = False
            self.sameness = False


listening = ListeningModel()


# listening: Dict[
#     str,
#     Dict[
#         str,
#         Optional[
#             ProcessThread
#         ] | bool | str | int | int] | Optional[int] | Optional[ProcessThread]
# ] = {
#     'search': {
#         'process': None,
#         'active': False,
#         'column': 'None',
#         'min': 0,
#         'count': 0,
#         'attr_is_bool': False,
#         'sameness': False
#     },
#     'proc_msg_id': None
# }


# --------------Functions-------------------
def is_user_admin(user_id):
    channels = channels_id
    subscribed_channels = 0
    for channel in channels:
        try:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status in ['administrator', 'creator']:
                subscribed_channels += 1
            else:
                return False
        except ApiTelegramException as e:
            log.debug(f'is_user_admin - ApiTelegramException: {e}')
            return False
        except Exception as e:
            log.debug(f'is_user_admin - Exception: {e}')
            return False
    if len(channels) == subscribed_channels:
        return True
    else:
        return False


def is_user_subscribed(user_id):
    channels = channels_id
    subscribed_channels = 0
    for channel in channels:
        try:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status in ['member', 'administrator', 'creator']:
                subscribed_channels += 1
            else:
                return False
        except ApiTelegramException as e:
            log.debug(f'is_user_subscribed - ApiTelegramException: {e}')
            return False
        except Exception as e:
            log.debug(f'is_user_subscribed - Exception: {e}')
            return False
    if len(channels) == subscribed_channels:
        return True
    else:
        return False


def is_valid_address(address):
    if not re.match(r'^(0x)?[0-9a-f]{40}$', address, re.IGNORECASE):
        # Checks if the address has the correct length and characters
        return False
    if address.lower() == address or address.upper() == address:
        # If the address is all lower or upper case, it's valid but not checksummed
        return True
    # Check the EIP-55 checksum
    address = address.replace('0x', '')
    address_hash = keccak.new(digest_bits=256).update(address.lower().encode()).hexdigest()
    for i, char in enumerate(address):
        if int(address_hash[i], 16) > 7 and char.upper() != char:
            return False
        elif int(address_hash[i], 16) <= 7 and char.lower() != char:
            return False
    return True


@bot.message_handler(commands=['start'])
def start(message):
    try:
        ref_id = message.text.split(' ')[1]
        referral_id[message.chat.id] = int(ref_id)
    except ValueError:
        pass
    except IndexError:
        pass
    except BaseException:
        pass
    if is_user_admin(message.from_user.id):
        admin_section(message)
    else:
        check_subscription(message)


def home_message(chat_id):
    if is_user_admin(chat_id):
        keyboard = admin_keyboard()
    else:
        keyboard = return_keyboard()
    bot.send_chat_action(chat_id=chat_id, action='typing')
    bot.send_message(chat_id=chat_id, text='🏘🏘', reply_markup=keyboard, protect_content=True)


def check_subscription(message):
    bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    if is_user_subscribed(message.from_user.id):
        # if db.is_user_exist(message.from_user.id):
        if User.get_or_none(User.uid == message.from_user.id) is not None:
            account_callback_handler(message=message)
        else:
            # db.create_user(uid=message.from_user.id, user_name=message.from_user.username)
            try:
                User.create(uid=message.from_user.id, user_name=message.from_user.username)
            except IntegrityError:
                log.info(f'error creating user: {message.from_user.id} - {message.from_user.username}')
            account_callback_handler(message=message)
        is_sub_del[message.from_user.id] = True
        coin = User.get_or_none(User.uid == message.from_user.id).coin
        if coin == 0:
            try:
                is_bot = message.message.from_user.is_bot
            except AttributeError:
                is_bot = False
            except BaseException:
                is_bot = False
            if is_bot:
                get_bonus(chat_id=message.message.chat.id, user_id=message.from_user.id, message=message)
            else:
                get_bonus(chat_id=message.chat.id, user_id=message.from_user.id, message=message)
        active_referral(message)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for channel in channels_id:
            channel_url = f'https://t.me/{channel.lstrip('@')}'
            channel = types.InlineKeyboardButton(text='Join', url=channel_url)
            keyboard.add(channel)
        confirm_button = types.InlineKeyboardButton(text='✅ Confirm ✅', callback_data='confirm_subscription')
        keyboard.add(confirm_button)
        if User.get_or_none(User.uid == message.from_user.id):
            msg1 = bot.send_message(message.chat.id, 'It seems that you don\tt subscribed the channels '
                                                     'anymore!', reply_markup=types.ReplyKeyboardRemove(), protect_content=True)
            msg2 = bot.send_message(message.chat.id, f'Please subscribe these'
                                                     f'channels to continue collecting SHIBA INU.', reply_markup=keyboard, protect_content=True)
        else:
            msg1 = bot.send_message(message.chat.id, 'Welcome to SHIBA INU COLLECTOR BOT!', reply_markup=types.ReplyKeyboardRemove(), protect_content=True)
            msg2 = bot.send_message(message.chat.id, f'Please subscribe these'
                                                     f'channels to join our plan.', reply_markup=keyboard, protect_content=True)
        del_msg.append(msg1.id)
        del_msg.append(msg2.id)
        is_sub_del[message.from_user.id] = False
    try:
        if is_sub_del[message.from_user.id]:
            for msg_id in del_msg:
                try:
                    bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                except ApiTelegramException:
                    log.debug(f'ApiTelegramException occurred while deleting message {msg_id} for user {message.from_user.id}--{message.from_user.username}')
                except TypeError:
                    log.debug(f'TypeError occurred while deleting message {msg_id} for user {message.from_user.id}--{message.from_user.username}')
                except BaseException:
                    log.debug(f'BaseException occurred while deleting message {msg_id} for user {message.from_user.id}--{message.from_user.username}')
            del_msg.clear()
        is_sub_del[message.from_user.id] = False
    except KeyError:
        pass
    except AttributeError:
        pass
    except BaseException:
        pass


def remove_keyboard(message):
    bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    msg = bot.send_message(message.chat.id, 'Processing...', reply_markup=types.ReplyKeyboardRemove(), protect_content=True)
    bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)


def return_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    account = types.KeyboardButton('👤 Account')
    referral_banner = types.KeyboardButton('👬 Referral Banner')
    hourly_bonus = types.KeyboardButton('🎁 Hourly Bonus')
    wallet = types.KeyboardButton('💼 Wallet')
    withdrawal = types.KeyboardButton('📤 Withdrawal')
    keyboard.row(account)
    keyboard.row(referral_banner, hourly_bonus)
    keyboard.row(wallet, withdrawal)
    return keyboard


def active_referral(message):
    bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    if is_user_subscribed(message.from_user.id):
        if referral_id[message.from_user.id] is not None and str(referral_id[message.from_user.id]).isdigit():
            if len(str(referral_id[message.from_user.id])) >= 9:
                if User.get_or_none(User.uid == referral_id[message.from_user.id]):
                    if referral_id[message.from_user.id]:
                        if referral_id[message.from_user.id] != message.from_user.id:
                            try:
                                if User.get_or_none(User.uid == referral_id[message.from_user.id]).agent == message.from_user.id:
                                    del referral_id[message.from_user.id]
                                else:
                                    re_id = referral_id[message.from_user.id]
                                    user = User.get_or_none(User.uid == message.from_user.id)
                                    user.referral_user += 1
                                    user.agent = re_id
                                    user.save()
                                    text = f'''🎉 Congratulations, a user entered the bot with your Link!\n\n👤 user: {message.from_user.username}\n\n🎁 You received 1500000 (~$15) SHIBA'''
                                    bot.send_message(re_id, text, protect_content=True)
                                    ref_user = User.get_or_none(User.uid == re_id)
                                    ref_user.coin += 1500000
                                    ref_user.save()
                                    del referral_id[message.from_user.id]
                            except sqlite3.ProgrammingError:
                                log.debug(f'sqlite3 error assining user agent and check ref_user: {referral_id[message.from_user.id]}')
                                del referral_id[message.from_user.id]
                            except ValueError:
                                log.debug(f'ValueError error assining user agent and check ref_user: {referral_id[message.from_user.id]}')
                                del referral_id[message.from_user.id]
                            except IndexError:
                                log.debug(f'IndexError error assining user agent and check ref_user: {referral_id[message.from_user.id]}')
                                del referral_id[message.from_user.id]
                            except TypeError:
                                log.debug(f'TypeError error assining user agent and check ref_user: {referral_id[message.from_user.id]}')
                                del referral_id[message.from_user.id]
                            except BaseException:
                                log.debug(f'BaseException error assining user agent and check ref_user: {referral_id[message.from_user.id]}')
                                del referral_id[message.from_user.id]
                        else:
                            del referral_id[message.from_user.id]


@bot.callback_query_handler(func=lambda call: call.data == 'confirm_subscription')
def confirm_subscribed(call):
    bot.send_chat_action(chat_id=call.from_user.id, action='typing')
    if is_user_subscribed(call.from_user.id):
        is_sub_del[call.from_user.id] = True
        if is_sub_del[call.from_user.id]:
            for msg_id in del_msg:
                try:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=msg_id)
                except ApiTelegramException:
                    pass
                except TypeError:
                    pass
                except BaseException:
                    pass
            del_msg.clear()
        is_sub_del[call.from_user.id] = False
        check_subscription(call)
        coin = User.get_or_none(User.uid == call.from_user.id).coin
        if coin == 0:
            get_bonus(chat_id=call.message.chat.id, user_id=call.from_user.id, message=call,
                      user_name=call.from_user.username)
        active_referral(call)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text='please subscribe the channels!', show_alert=True)


def get_bonus(chat_id, user_id, message=None, user_name=None):
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    coin = User.get_or_none(User.uid == user_id).coin
    if coin == 0:
        User.update(coin=(coin + 20000000)).where(User.uid == user_id).execute()
        text = '''🎉 You have successfully joined Collector!\n\n🎁You received 20000000 (~$200) SHIBA Gift\n\n🏠Choose an option from the menu below'''
        bot.send_message(chat_id=chat_id, text=text)
    else:
        if User.get_or_none(User.uid == user_id).last_bonus is not None:
            # If you need to create a new datetime object from the database time
            # and the returned value is a string, you might need to parse it like this:
            # database_time = datetime.strptime(db.get_user_attr(user_id, 'last_bonus'), '%Y-%m-%d %H:%M:%S')
            # Assuming 'database_time' is the datetime object you retrieved from the database
            db_time_default = str(User.get_or_none(User.uid == user_id).last_bonus)
            db_time = datetime.strptime(db_time_default, '%Y-%m-%d %H:%M:%S.%f')
            # Get the current time
            current_time = datetime.now()
            # Calculate the difference between the current time and the database time
            time_difference = current_time - db_time
            # Check if the difference is greater than 6 hours
            if time_difference > timedelta(hours=6):
                User.update(coin=(coin + 500000)).where(User.uid == user_id).execute()
                text = '''🎉 Congratulations 🎉\n\n🎁 You received 500000 (~$5) SHIBA as a gift'''
                bot.send_message(chat_id=chat_id, text=text)
                User.update(last_bonus=datetime.now()).where(User.uid == user_id).execute()
                bonus_count = User.get_or_none(User.uid == user_id).bonus_count
                User.update(bonus_count=(bonus_count + 1)).where(User.uid == user_id).execute()
            else:
                text = '''❌ You already received Hourly Bonus\n\n🎁Every 6 Hours you can get 500000 (~$5) SHIBA as a gift\n\n♻️Come back 6 Hours Later!'''
                bot.send_message(chat_id=chat_id, text=text)
        else:
            if User.get_or_none(User.uid == user_id):
                User.update(coin=(coin + 500000)).where(User.uid == user_id).execute()
                text = '''🎉 Congratulations 🎉\n\n🎁 You received 500000 (~$5) SHIBA as a gift'''
                bot.send_message(chat_id=chat_id, text=text)
                User.update(last_bonus=datetime.now()).where(User.uid == user_id).execute()
                bonus_count = User.get_or_none(User.uid == user_id).bonus_count
                User.update(bonus_count=(bonus_count + 1)).where(User.uid == user_id).execute()
            else:
                check_subscription(message=message)


@bot.message_handler(func=lambda message: message.text == '👤 Account')
def account_callback_handler(message):
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    try:
        is_bot = message.message.from_user.is_bot
    except AttributeError:
        is_bot = False
    except BaseException:
        is_bot = False
    if is_bot:
        if is_user_subscribed(message.message.chat.id):
            keyboard = return_keyboard()
            user = User.get_or_none(User.uid == message.from_user.ui)
            coin = user.coin
            referral_users = user.referral_users
            wallet_address = user.wallet_address
            text = (f'💰Your Balanced = {coin} SHIBA\n👬Total Referrals : {referral_users} User\n\n💳 Wallet '
                    f'address :\n{wallet_address}\n\n🔰Choose button below to add or change wallet address')
            bot.send_message(message.message.chat.id, text, reply_markup=keyboard, protect_content=True)
        else:
            check_subscription(message)
    else:
        if is_user_subscribed(message.from_user.id):
            keyboard = return_keyboard()
            user = User.get_or_none(User.uid == message.from_user.id)
            coin = user.coin
            referral_users = user.referral_user
            wallet_address = user.wallet_address
            text = (f'💰Your Balanced = {coin} SHIBA\n👬Total Referrals : {referral_users} User\n\n💳 Wallet '
                    f'address :\n{wallet_address}\n\n🔰Choose button below to add or change wallet address')
            bot.send_message(message.chat.id, text, reply_markup=keyboard, protect_content=True)
        else:
            check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '👬 Referral Banner')
def referral_banner_callback_handler(message):
    if is_user_subscribed(message.from_user.id):
        bot.send_chat_action(chat_id=message.chat.id, action='upload_photo')
        caption = f'''🎉 SHIBA INU COLLECTOR has been lunched 🎉\n\n🎁 join now and get 20000000 (~$200) SHIBA as a gift\n\n🔗Join Link:\n👉🏻 https://t.me/{bot_username}?start={message.from_user.id}'''
        try:
            adr = address.assets
            banner_photo = open(f'{adr}/{bot_username}/{referral_banner_photo_name}', 'rb')
            bot.send_photo(message.chat.id, banner_photo, caption=caption, protect_content=False)
        except FileNotFoundError or FileNotFoundError:
            bot.send_chat_action(message.from_user.id, action='typing')
            bot.send_message(message.from_user.id, '❌ Error! Banner Picture File Not Found.', protect_content=True)
            bot.send_chat_action(message.from_user.id, action='typing')
            bot.send_message(message.from_user.id, caption, protect_content=True)
    else:
        check_subscription(message=message)


@bot.message_handler(func=lambda message: message.text == '🎁 Hourly Bonus')
def hourly_bonus_callback_handler(message):
    if is_user_subscribed(message.from_user.id):
        get_bonus(chat_id=message.chat.id, user_id=message.from_user.id, message=message, user_name=message.from_user.username)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '💼 Wallet')
def wallet_callback_handler(message):
    if is_user_subscribed(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        wallet_address = User.get_or_none(User.uid == message.from_user.id).wallet_address
        text = f'💳 Wallet address :\n{wallet_address}\n\n🔰Choose button below to add or change wallet address'
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        change_wallet_btn = types.InlineKeyboardButton(text='💳 Wallet Address', callback_data='update_wallet_address')
        keyboard.add(change_wallet_btn)
        bot.send_message(message.chat.id, text, reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.callback_query_handler(func=lambda call: call.data == 'update_wallet_address')
def wallet_callback_handler(call):
    if is_user_subscribed(call.from_user.id):
        bot.send_chat_action(chat_id=call.from_user.id, action='typing')
        bot.send_chat_action(chat_id=call.message.chat.id, action='typing')
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        cancel_btn = types.KeyboardButton(text='❌ Cancel')
        keyboard.add(cancel_btn)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, '📝 Please send SHIBA INU wallet Address(we will send SHIBA to this '
                                          'address):', reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(call)


@bot.message_handler(func=lambda message: message.text == '❌ Cancel')
def cancel_callback_handler(message, done=False):
    if is_user_subscribed(message.from_user.id):
        if done:
            if listening.search.process is not None:
                if listening.search.process.active:
                    listening.search.process.terminate()
                listening.search.back_to_default()
            # if listening['proc_msg_id'] is not None:
            #     print('*' * 20)
            #     bot.delete_message(chat_id=message.from_user.id, message_id=listening['proc_msg_id'])
            return
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        if is_user_admin(message.from_user.id):
            keyboard = admin_keyboard()
            if listening.search.active:
                if listening.search.process is not None:
                    if listening.search.process.active:
                        listening.search.process.terminate()
                listening.search.back_to_default()
        else:
            keyboard = return_keyboard()
        bot.send_message(message.chat.id, '❌ Task Cancelled', reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '📤 Withdrawal')
def withdrawal_callback_handler(message):
    if is_user_subscribed(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        withdrawal_btn = types.InlineKeyboardButton(text='📤 Withdrawal', callback_data='withdrawal')
        keyboard.add(withdrawal_btn)
        coin = User.get_or_none(User.uid == message.from_user.id).coin
        text = f'''⚠️ The minimum Withdrawal is 100000000 SHIBA\n\n💰 Your Balance is: {coin} SHIBA\n\n🔰 Click the Withdrawal button to continue Withdrawal'''
        bot.send_message(message.chat.id, text, reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.callback_query_handler(func=lambda call: call.data == 'withdrawal')
def withdrawal_callback_handler(call):
    if is_user_subscribed(call.from_user.id):
        bot.send_chat_action(chat_id=call.from_user.id, action='typing')
        user = User.get_or_none(User.uid == call.from_user.id)
        if user.coin > 100000000:
            if user.wallet_address is not None:
                keyboard = types.ReplyKeyboardMarkup(row_width=2)
                cancel_btn = types.KeyboardButton(text='❌ Cancel')
                confirm_withdrawal_btn = types.KeyboardButton(text='✅ Confirm Withdrawal')
                keyboard.add(cancel_btn)
                keyboard.add(confirm_withdrawal_btn)
                coin = user.coin
                wallet_address = user.wallet_address
                text = f'''‼️ Are You sure do you want to Withdrawal all Your Balance?\n\n💰Your Balance is: {coin} SHIBA\n\n💳Your Wallet address is:\n👉🏻 {wallet_address}\n\n🔰Click confirm to done transaction or click Cancel to terminate Task.'''
                bot.send_message(call.from_user.id, text, reply_markup=keyboard, protect_content=True)
            else:
                wallet_callback_handler(call)
        else:
            text = '⛔️ Your Balancer is fewer than minimum requirement of Withdrawal'
            bot.send_message(call.from_user.id, text, protect_content=True)
    else:
        check_subscription(call)


@bot.message_handler(func=lambda message: message.text == '✅ Confirm Withdrawal')
def confirm_withdrawal_task(message):
    if is_user_subscribed(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        keyboard = return_keyboard()
        text = f'''✅ OK, Withdrawal confirmed.\n\n👥This transaction will be done after checking by admins.\n\n🔰We will send you a notification when the transaction is completed.'''
        bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
        user = User.get_or_none(User.uid == message.from_user.id)
        coin = user.coin
        user.request_withdrawal = True
        user.transaction_amount += user.coin
        user.coin = 0
        user.save()
    else:
        check_subscription(message)


# ---------------------------------ADMIN-SECTION-------------------------------------------------
# -----------------Functions------------------------
def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    cancel_btn = types.KeyboardButton(text='❌ Cancel')
    keyboard.add(cancel_btn)
    return keyboard


def admin_search_in_db(message, search_data):
    if is_user_admin(message.from_user.id):
        if search_data.active:
            bot.send_chat_action(chat_id=message.from_user.id, action='typing')
            keyboard = admin_keyboard()
            column = search_data.column
            minimum = search_data.min
            count_of = search_data.count
            data_count = User.select().where(column <= minimum).count()
            data = User.select().where(column <= minimum).limit(count_of)
            user_text = f''''''
            for user in data:
                base_user_text = f'''👤 ID: {user.uid}\n➖User Name: @{user.user_name}\n➖Bonus Count: {user.bonus_count}\n➖Last Bonus: {user.last_bonus}\n➖Coin: {user.coin}\n➖Invited Users: {user.referral_user}\n➖Date Joined: {user.created}\n\n'''
                user_text += base_user_text
            data_empty = '\n❌ 404 ❌ No User Found! ❌\n'
            if user_text == '':
                text = f'''📊 Count of users with this search setting: {data_count}\n\n🔰 Users 🔰\n''' + data_empty
            else:
                text = f'''📊 Count of users with this search setting: {data_count}\n\n🔰 Users 🔰\n''' + user_text
            if search_data.proc_msg_id is not None:
                try:
                    bot.delete_message(chat_id=message.from_user.id, message_id=search_data.proc_msg_id)
                except ApiTelegramException:
                    pass
            bot.send_message(message.from_user.id, text, reply_markup=keyboard)
            cancel_callback_handler(message, done=True)
        else:
            cancel_callback_handler(message)
    else:
        check_subscription(message)


# -----------------Handler------------------------
@bot.message_handler(commands=['admin'])
def admin_section(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        keyboard = admin_keyboard()
        text = f'''👋🏻 Hi admin {message.from_user.username}\n\n🔰Welcome to Your BOT'''
        bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
        if listening.search.active:
            listening.search.back_to_default()
    else:
        check_subscription(message)


def admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    get_user_count = types.KeyboardButton(text='👬 Users Count')
    hardworking_users = types.KeyboardButton(text='📝 Active users')
    requests_withdrawal_users = types.KeyboardButton(text='💳 Request Transaction Users')
    most_invited = types.KeyboardButton(text='🔗 Most Invited')
    not_in_channels = types.KeyboardButton(text='📵 Not in Channels')
    log_options = types.KeyboardButton(text='📝 Log Option')
    back_up_db = types.KeyboardButton(text='📤 Backup Database')
    keyboard.row(get_user_count, hardworking_users)
    keyboard.row(requests_withdrawal_users, most_invited, not_in_channels)
    keyboard.row(log_options, back_up_db)
    return keyboard


# ----------Log-Option-------------------
def return_log_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    archive_log = types.KeyboardButton(text='🗄 Archive Current Log')
    if log_obj.daily_archive:
        change_daily_archive = types.KeyboardButton(text='💢 Turn off Daily Archive')
    else:
        change_daily_archive = types.KeyboardButton(text='✳️ Turn on Daily Archive')
    get_all_archived = types.KeyboardButton(text='🗂 Get All Archived')
    get_log_file = types.KeyboardButton(text='📥 Get Log File')
    cancel_btn = types.KeyboardButton(text='❌ Cancel')
    keyboard.row(archive_log, change_daily_archive)
    keyboard.row(get_all_archived, get_log_file)
    keyboard.row(cancel_btn)
    return keyboard


@bot.message_handler(func=lambda message: message.text == '📝 Log Option')
def admin_log_options(message):
    if is_user_admin(message.from_user.id):
        keyboard = return_log_keyboard()
        text = '''🔰 Select Next Step\n\n⭕️ Press Cancel button to terminate task'''
        bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '🗄 Archive Current Log')
def admin_archive_log(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        log_obj.archive_log_file()
        log.info(f'log archived by admin: {message.from_user.id} - {message.from_user.username}')
        keyboard = return_log_keyboard()
        bot.send_message(message.from_user.id, f'✅ Log archived at: {datetime.now().strftime("%Y-%m-%d--%H:%M:%S")}', reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '💢 Turn off Daily Archive')
def admin_disable_auto_log_archive(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        log_obj.daily_archive = False
        log.info(f'daily archive disabled by admin: {message.from_user.id} - {message.from_user.username}')
        keyboard = return_log_keyboard()
        bot.send_message(message.from_user.id, f'💢 Daily archive disabled until next server restart.', reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '✳️ Turn on Daily Archive')
def admin_enable_daily_archive_log(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        log_obj.daily_archive = True
        log.info(f'daily archive disabled by admin: {message.from_user.id} - {message.from_user.username}')
        keyboard = return_log_keyboard()
        bot.send_message(message.from_user.id, f'✳️ Daily archive enabled (backed to normal), restart server does not affect on this.', reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '🗂 Get All Archived')
def admin_get_all_archived_logs(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='upload_document')
        d_path = log_obj.get_archives_in_zip(save_zip=True)
        keyboard = admin_keyboard()
        if d_path is not None:
            d_file = open(d_path, 'rb')
            log.info(f'Archive - Log Files Archived and sent to admin: {message.from_user.id} - {message.from_user.username}')
            bot.send_document(message.from_user.id, d_file, reply_markup=keyboard, caption=f'🗂 All Archived Log Files', visible_file_name=f'Archives-until--{datetime.now().strftime("%Y-%m-%d")}.zip')
        else:
            log.info(f'404 - Archive -  Log Files Archived and sent to admin: {message.from_user.id} - {message.from_user.username}')
            bot.send_message(message.from_user.id, f'❌ 404 ❌ No Archive Found ‼️', reply_markup=keyboard)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '📥 Get Log File')
def admin_get_current_log_file(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='upload_document')
        d_path = log_obj.log_file_path()
        keyboard = admin_keyboard()
        if d_path is not None:
            d_file = open(d_path, 'rb')
            log.info(f'Log File sent to admin: {message.from_user.id} - {message.from_user.username}')
            bot.send_document(message.from_user.id, d_file, reply_markup=keyboard, caption=f'🗂 Log Files\n\n📍 Time: {datetime.now().strftime("%Y-%m-%d  %H:%M")}', visible_file_name=f'Log--{datetime.now().strftime("%Y-%m-%d")}.log')
        else:
            log.info(f'404 - Log File Not Found for sent to admin: {message.from_user.id} - {message.from_user.username}')
            bot.send_message(message.from_user.id, f'❌ 404 ❌ No Archive Found ‼️', reply_markup=keyboard)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '👬 Users Count')
def admin_get_user_count(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        count = User.select().count()
        first = User.select().order_by(User.created).first()
        last = User.select().order_by(User.created.desc()).first()
        if first and last:
            text = f'''🔰 User Count: {count}\n\n🟢 Newest User: @{first.user_name}\n   ➖ Joined: {first.created}\n\n🔴 Oldest User: @{last.user_name}\n   ➖ Joined: {last.created}\n'''
        else:
            text = f'''🔰 User Count: {count}\n\n🟢 Newest User: ❌ 404 ❌\n🔴 Oldest User: ❌ 404 ❌'''
        bot.send_message(message.from_user.id, text, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '📝 Active users')
def admin_get_most_active_users(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        default_button = types.KeyboardButton(text='📊 Default Search Settings')
        cancel_btn = types.KeyboardButton(text='❌ Cancel')
        bonus_count_btn = types.KeyboardButton(text='🟢 Bonus Count')
        coin_btn = types.KeyboardButton(text='🟢 Coin')
        invited_user_btn = types.KeyboardButton(text='🟢 Invited Users')
        keyboard.row(bonus_count_btn, coin_btn, invited_user_btn)
        keyboard.row(default_button)
        keyboard.row(cancel_btn)
        text = '''📜 Please send your Values to do search based on the values you performed\n\n✅ Select Your Column\n\n🔰 Press Default button to do search based on default setting:\n📊 Bonus Count Should be 10 or more\n\n❌ Press the cancel button to Terminate Task.'''
        bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
        listening.search.back_to_default()
        listening.search.active = True
        listening.search.proc_msg_id = None
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '📊 Default Search Settings')
def admin_default_search_most_active_user_handler(message):
    if is_user_admin(message.from_user.id):
        processing_message(message)
        default_search_settings(message)
    else:
        check_subscription(message)


def processing_message(message):
    bot.send_chat_action(message.from_user.id, action='typing')
    keyboard = cancel_keyboard()
    text = f'''🔰 Processing...\n\n⚠️ Click Cancel button to terminate task'''
    msg = bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
    listening.search.proc_msg_id = msg.message_id


def default_search_settings(message):
    if listening.search.active:
        assign_and_lunch_search_settings(message=message, column=User.bonus_count, minimum=10, count=5, lunch=True)
    else:
        home_message(message.from_user.id)


def assign_and_lunch_search_settings(message, column, minimum, count, attr_is_bool=False, sameness=False, lunch=True):
    if listening.search.active:
        listening.search.column = column
        listening.search.min = minimum
        listening.search.count = count
        listening.search.attr_is_bool = attr_is_bool
        listening.search.sameness = sameness
        if lunch is True:
            lunch_search_process(message)
    else:
        home_message(message.from_user.id)


def lunch_search_process(message):
    if listening.search.process is None:
        listening.search.process = ProcessThread(admin_search_in_db, message, listening.search)
        listening.search.process.start()
    else:
        if listening.search.process.active:
            listening.search.process.terminate()
        listening.search.process = None
        listening.search.process = ProcessThread(admin_search_in_db, message, listening.search)
        listening.search.process.start()


@bot.message_handler(func=lambda message: message.text == '🟢 Bonus Count')
def search_by_bonus_count(message):
    if is_user_admin(message.from_user.id):
        if listening.search.active:
            bot.send_chat_action(chat_id=message.from_user.id, action='typing')
            keyboard = cancel_keyboard()
            text = f'''✏️ Please write your minimum value for this column'''
            bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
            listening.search.column = User.bonus_count
        else:
            home_message(message.from_user.id)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '🟢 Coin')
def search_by_bonus_count(message):
    if is_user_admin(message.from_user.id):
        if listening.search.active:
            bot.send_chat_action(chat_id=message.from_user.id, action='typing')
            keyboard = cancel_keyboard()
            text = f'''✏️ Please write your minimum value for this column'''
            bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
            listening.search.column = User.coin
        else:
            home_message(message.from_user.id)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '🟢 Invited Users')
def search_by_bonus_count(message):
    if is_user_admin(message.from_user.id):
        if listening.search.active:
            bot.send_chat_action(chat_id=message.from_user.id, action='typing')
            keyboard = cancel_keyboard()
            text = f'''✏️ Please write your minimum value for this column'''
            bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
            listening.search.column = User.referral_user
        else:
            home_message(message.from_user.id)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '💳 Request Transaction Users')
def admin_request_transaction_users(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        listening.search.active = True
        assign_and_lunch_search_settings(
            message=message,
            column=User.request_withdrawal,
            minimum=True,
            count=5,
            attr_is_bool=True,
            sameness=True,
            lunch=True
        )
        # count = User.select().where(User.request_withdrawal == True)
        # bot.send_message(message.from_user.id, f'count = {len(count)}')
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '🔗 Most Invited')
def admin_get_most_invited_users(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        listening.search.active = True
        assign_and_lunch_search_settings(
            message=message,
            column=User.referral_user,
            minimum=10,
            count=5,
            attr_is_bool=False,
            sameness=False,
            lunch=True
        )
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '📵 Not in Channels')
def admin_get_not_in_channel_users(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        confirm_btn = types.KeyboardButton(text='⚠️ OK, I Understand ⚠️')
        cancel_btn = types.KeyboardButton(text='❌ Cancel')
        keyboard.row(confirm_btn)
        keyboard.row(cancel_btn)
        text = f'''⚠️ Warning!\n\n🔰 This Process can Take a few minutes and take some processing resource to be Done!\n\n❌ Press Cancel button to terminate Task.'''
        bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message)


@bot.message_handler(func=lambda message: message.text == '⚠️ OK, I Understand ⚠️')
def admin_get_not_in_channel_users_finally(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        processing_message(message)
        proc_msg_id = listening.search.proc_msg_id
        users = User.select()
        listening.search.process = ProcessThread(check_users_is_subscribed, message, users, proc_msg_id)
        listening.search.process.start()
    else:
        check_subscription(message)


def check_users_is_subscribed(message, users, proc_msg_id):
    not_subscribed = []
    not_subscribed_count = 0
    last_user = None
    try:
        for user in users:
            last_user = user
            if is_user_subscribed(user.uid):
                pass
            else:
                not_subscribed.append(user)
                not_subscribed_count += 1
    except BaseException:
        log.debug(f'Check all Users Subscription BaseException Error: {last_user.uid}--{last_user.user_name}')
    keyboard = admin_keyboard()
    user_text = f''''''
    for user in not_subscribed:
        base_user_text = f'''👤 ID: {user.uid}\n➖User Name: @{user.user_name}\n➖Bonus Count: {user.bonus_count}\n➖Last Bonus: {user.last_bonus}\n➖Coin: {user.coin}\n➖Invited Users: {user.referral_user}\n➖Date Joined: {user.created}\n\n'''
        user_text += base_user_text
    data_empty = '\n❌ 404 ❌ No User Found! ❌\n'
    if user_text == '':
        text = f'''📊 Count of users with this search setting: {not_subscribed_count}\n\n🔰 Users 🔰\n''' + data_empty
    else:
        text = f'''📊 Count of users with this search setting: {not_subscribed_count}\n\n🔰 Users 🔰\n''' + user_text
    if proc_msg_id is not None:
        try:
            bot.delete_message(chat_id=message.from_user.id, message_id=proc_msg_id)
        except ApiTelegramException:
            log.debug(f'ApiTelegramException error deleting message {proc_msg_id}, for user {message.from_user.id}')
    bot.send_message(message.from_user.id, text, reply_markup=keyboard)
    cancel_callback_handler(message, done=True)


@bot.message_handler(func=lambda message: message.text == '📤 Backup Database')
def admin_get_backup_database(message):
    if is_user_admin(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='upload_document')
        try:
            adr = address.db
            db_file = open(f'{adr}/{db_name}.db', 'rb')
            bot.send_document(
                message.from_user.id,
                db_file,
                caption=f'''\n📥Database Backup\n🔰BOT: {bot_username}\n📍Date: {datetime.now().strftime("%Y/%m/%d (%H:%M)")}''',
                visible_file_name='DataBase.db',
                allow_sending_without_reply=True
            )
        except FileNotFoundError or FileExistsError:
            log.warn(f'Database Backup File Not Found: ./db/{db_name}.db')
            bot.send_chat_action(message.from_user.id, action='typing')
            text = f'''❌ Error! Database File Not Found.'''
            bot.send_message(message.from_user.id, text, protect_content=True)
    else:
        check_subscription(message)


# -----------------------------------Echo-ALL-Message------------------------------
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    if is_user_subscribed(message.from_user.id):
        bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        if is_user_admin(message.from_user.id):
            if listening.search.active:
                keyboard = cancel_keyboard()
                data_str = str(message.text)
                if data_str.isdigit():
                    data_int = int(data_str)
                    if listening.search.column is not None and listening.search.min == 0:
                        text = f'''✏️ Please Write How many users would you like to receive'''
                        bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
                        listening.search.min = data_int
                    elif listening.search.column is not None and listening.search.count == 0:
                        listening.search.count = data_int
                        processing_message(message)
                        lunch_search_process(message)
                    else:
                        lunch_search_process(message)
                else:
                    text = f'''🚫 Unexpected value 🚫'''
                    bot.send_message(message.from_user.id, text, reply_markup=keyboard, protect_content=True)
            else:
                home_message(chat_id=message.from_user.id)
        else:
            keyboard = return_keyboard()
            if is_valid_address(message.text):
                user = User.get_or_none(User.uid == message.from_user.id)
                user.wallet_address = message.text
                user.save()
                text = '✅ Your Wallet Address is successfully updated!'
                bot.send_message(message.chat.id, text, reply_markup=keyboard, protect_content=True)
            else:
                text = '''❌ Error ❌\n⭕️ error during submit your wallet address healthy\n\n🔴 Use a valid address or another address\n🟡 if you are sure about your address healthy, it can be a internal error!\n\n🔄 please try again later.'''
                bot.send_message(message.chat.id, text, reply_markup=keyboard, protect_content=True)
    else:
        check_subscription(message=message)


# Run the application
if __name__ == '__main__':
    bot.infinity_polling()

