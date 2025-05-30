# swiss-knive-telegram
A simple script that can be deployed anywhere and used for any purpose you need.
Its monolithic structure makes it easy to add your own features.
Overall, it can significantly enhance your Telegram surfing experience.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
📦 Installation
Make sure you have Python 3.8+ installed
Install dependencies:
 
       pip install telethon

    
 Clone the repository
              
      git clone https://github.com/Sava234/swiss-knive-telegram.git

🚀  Quick Start

 Run the script:

    python main.py

Enter your API ID, API Hash, and phone number when you first launch the app.
This data will be saved in tg_tools_config.json, and the session will be saved in session_name.session.
After connecting, you will see the main menu:
   
     1. Clear correspondence (including media)
     2. Set up an auto-responder
     3. Mass mailing
     4. Delete authorization data
     5. Log out

🧰 Features

🔁 Answering machine
Responds to keywords or all messages.
Supports sending media files.
Anti-spam: fixed, progressive, or random delay.

🧹 Cleaning chats
Delete all messages or just yours.
Delete by time (for example, only the last 10 minutes).
You can leave media files or delete them along with the messages.

📢 Mass messaging
Send text or media to multiple chats.
You can specify chats by ID or name.

🔐 Data management
 Delete configuration and Telegram sessions at will.

📝 Notes
The script does not use bots; it works through the Telegram API as a full-fledged user.
Your data is stored locally and is not transferred to third parties.
Use the script responsibly and follow Telegram's rules.
