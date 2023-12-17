import logging
import random
import time
import requests
from telegram import Update
from telegram.ext import CommandHandler, Filters
from telegram.ext import Updater, CommandHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

api_key = 'TVIUM91NNKRRK4797SR65NCUSPS3Q23I8U'
wallet_address = '0x742d3774cBC0Cbd897ddFDA414EA4591c70E784E'
MAX_ENTRIES = 2
GROUP_CHAT_ID = -4000928275
NUMBER_RANGE = 2
lottery_entries = []
entered_users = set()
admin_user_ids = [1814691336, 6171169457]


def generate_target_amount():
    random_xyz = random.randint(100, 999)
    return round(0.050 + random_xyz / 1000000, 7)

# Function to stop the current lottery
def stop_lottery(update, context):
    # Add logic to stop the current lottery (clear entries, reset variables, etc.)
    lottery_entries.clear()
    entered_users.clear()
    context.bot.send_message(update.message.chat_id, "The current lottery has been stopped.")

# Function to reset user statistics
def reset_statistics(update, context):
    # Add logic to reset user statistics (e.g., number of lotteries entered, total winnings, etc.)
    context.bot.send_message(update.message.chat_id, "User statistics have been reset.")

# Function to display a list of participants
def participant_list(update, context):
    participants = [f"@{context.bot.get_chat(user_id).username}" for user_id, _, _ in lottery_entries]
    participants_list = "\n".join(participants)
    context.bot.send_message(update.message.chat_id, f"List of participants:\n{participants_list}")
    


def check_transactions(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        if 'target_amount' not in context.user_data:
            context.user_data['target_amount'] = generate_target_amount()

        target_amount = context.user_data['target_amount']

        # BSCScan API endpoint for getting the latest transactions of an address
        api_url = f'https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}'

        # Make a GET request to the BSCScan API
        response = requests.get(api_url)
        data = response.json()

        # Check if the request was successful
        if data['status'] == '1':
            # Check if there is any transaction with the correct value within the last 600 seconds
            recent_transactions = [
                tx for tx in data['result']
                if float(tx['value']) / 10**18 == target_amount and
                (int(time.time()) - int(tx['timeStamp']) <= 300)
            ]

            if recent_transactions:
                context.bot.send_message(update.message.chat_id, f"Received {target_amount} BNB ✅. You are now entered into the lottery.")
                context.user_data[user_id]['paid'] = True

                # Assign a unique number
               # assigned_number = assign_unique_number()

                # Add the user to the set of entered users
                

                #update.message.reply_text(f"You've been assigned the number <b>{assigned_number}</b>. Good luck 🤞", parse_mode='HTML')

                if len(entered_users) == MAX_ENTRIES:
                    send_winner_messages(context)

                context.user_data['target_amount'] = generate_target_amount()  # Generate a new target amount for the next transaction
            else:
                context.bot.send_message(update.message.chat_id, f"{target_amount} BNB not received. Please try again. Incase of any transaction error, please contact @samcomanaria")
        else:
            context.bot.send_message(update.message.chat_id, f"API request failed. Error message: {data['message']}")
    except Exception as e:
        context.bot.send_message(update.message.chat_id, f"An error occurred: {e}")


def entry(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # Explicitly call check_transactions to handle payment status
    check_transactions(update, context)

    if user_id not in context.user_data:
        context.user_data[user_id] = {'paid': False}

    if context.user_data[user_id]['paid']:
        if 'address' not in context.user_data[user_id]:
            update.message.reply_text("Please set your BNB wallet address using the /setaddress command before entering the lottery.")
            return

        if user_id not in entered_users and len(lottery_entries) < MAX_ENTRIES:
            # Display a waiting message
            context.bot.send_message(chat_id, "⌛ Please wait, our system will randomly assign you a number...")

            # Wait for 3-4 seconds
            time.sleep(random.uniform(3, 4))

            assigned_number = assign_unique_number()
            lottery_entries.append((user_id, chat_id, assigned_number))
            entered_users.add(user_id)  # Add the user to the set of entered users

            # Send an entry message to the group chat
            entry_message = f"@{context.bot.get_chat(user_id).username} paid {context.user_data['target_amount']} BNB with wallet address {context.user_data[user_id]['address']} has entered the lottery."
            context.bot.send_message(GROUP_CHAT_ID, entry_message)

            update.message.reply_text(f"You've been assigned the number <b>{assigned_number}</b>. Good luck 🤞. The results will be announced soon ⏰", parse_mode='HTML')

            # Reset the paid status for all participants

            # Check if the maximum number of entries is reached
            if len(lottery_entries) == MAX_ENTRIES:
                send_winner_messages(context)

        elif user_id in entered_users:
            update.message.reply_text("You've already entered the lottery.")

        else:
            update.message.reply_text("The lottery is full. Try again next time.")

    else:
        update.message.reply_text("Please make the payment first to enter the lottery. Type /start to get payment details.")




def assign_unique_number() -> int:
    assigned_number = random.randint(1, NUMBER_RANGE)
    while any(number == assigned_number for (_, _, number) in lottery_entries):
        assigned_number = random.randint(1, NUMBER_RANGE)
    return assigned_number


def send_winner_messages(context):
  try:  
    print("Before shuffling:", lottery_entries)
    if lottery_entries:
          # Convert to list to avoid modifying the original set
        #random.shuffle(shuffled_entries)
        #print("After shuffling:", shuffled_entries)
         
      
        '''
        winner_user_id, winner_chat_id, winner_number = random.choice(
            [(u_id, c_id, num) for u_id, c_id, num in lottery_entries if context.user_data.get(u_id, {}).get('paid', False)]
        )
        '''
        #winner_user_id, winner_chat_id, winner_number = lottery_entries[0]
        #winner_user_id, winner_chat_id, winner_number = random.choice(lottery_entries)
        winner_user_id, winner_chat_id, winner_number = random.choice(lottery_entries)
        
        # Check if the user has paid
        print(f"Winner: User ID: {winner_user_id}, Chat ID: {winner_chat_id}, Number: {winner_number}")
        if context.user_data.get(winner_user_id, {}).get('paid', True):
            

            winner_user_id_str = str(winner_user_id)
            winner_wallet_address = context.user_data.get(winner_user_id, {}).get('address', 'N/A')

            winner_message_individual = (
                f"🎉 <b>Congratulations</b> to @{context.bot.get_chat(winner_user_id).username} for winning the lottery with the lucky number <b>{winner_number}</b>! 🌟. The winner will soon receive the winning amount to the wallet address: <code>{winner_wallet_address}</code>."
                "\n\n🥳 <b>Thank you</b> to all participants! <b>Better luck next time!</b> 🍀"
            )

            winner_message_group = "🏆 <b>Lottery Results:</b>\n\n"
            for user_id, _, assigned_number in lottery_entries:
                username = context.bot.get_chat(user_id).username
                user_wallet_address = context.user_data.get(user_id, {}).get('address', 'N/A')
                winner_message_group += f"@{username} - Number: <b>{assigned_number}</b> - Wallet: <code>{user_wallet_address}</code>\n"

            time.sleep(random.uniform(180, 220))

            for _, chat_id, _ in lottery_entries:
                context.bot.send_message(chat_id, winner_message_individual, parse_mode='HTML')

            additional_group_chat_id = -4000928275
            context.bot.send_message(additional_group_chat_id, winner_message_individual, parse_mode='HTML')
            context.bot.send_message(additional_group_chat_id, winner_message_group, parse_mode='HTML')

            lottery_entries.clear()
            entered_users.clear()
  except Exception as e:
        logging.error(f"An error occurred in send_winner_messages: {e}")          


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if 'target_amount' not in context.user_data:
        context.user_data['target_amount'] = generate_target_amount()

    target_amount = context.user_data['target_amount']

    if user_id not in context.user_data:
        context.user_data[user_id] = {'paid': False}

    context.bot.send_message(
        user_id,
        f"Welcome to the lottery bot! To enter the lottery, send exact <b>{target_amount} BNB </b> to the provided address:\n\n"
        f"<code>{wallet_address}</code>\n\n"
        f"Once the payment is confirmed, please wait for 20-30 seconds and type /entry to join the lottery.\n\n"
        f"Before sending the amount, please provide your BNB wallet address to receive the winning amount using the /setaddress command. eg. <code>/setaddress 0x.... </code>",
        parse_mode='HTML'
    )

def set_address(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if 'address' in context.user_data[user_id]:
        update.message.reply_text("Your wallet address is already set.")
    else:
        # Get the provided wallet address from the user's message
        user_address = update.message.text.replace('/setaddress', '').strip()
        
        # Validate the wallet address (you may want to add more sophisticated validation)
        if user_address.startswith('0x') and len(user_address) == 42:
            context.user_data[user_id]['address'] = user_address
            update.message.reply_text(f"Wallet address set to: {user_address}")
        else:
            update.message.reply_text("Invalid wallet address. Please provide a valid BNB wallet address.")


def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused an error {context.error}")


def main() -> None:
    updater = Updater("6662143941:AAFzXOvVor6vXZRfH6F7CQ1o8w7Bo9B6lQM")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("entry", entry))
    dp.add_handler(CommandHandler("setaddress", set_address))
    # Register the admin commands with the dispatcher
    dp.add_handler(CommandHandler("stoplottery", stop_lottery, filters=Filters.user(admin_user_ids)))
    dp.add_handler(CommandHandler("resetstatistics", reset_statistics, filters=Filters.user(admin_user_ids)))
    dp.add_handler(CommandHandler("participants", participant_list, filters=Filters.user(admin_user_ids)))

    dp.add_error_handler(error_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
