# shop.amul_bot

A Python automation script that monitors product availability on shop.amul.com and sends instant push notifications to your phone when an item comes back in stock.



🚀 Features

- Automated Monitoring: periodically checks the stock status of a specific product URL.

- Location Injection: Automatically sets your delivery location (Pincode) to ensure accurate stock data for your area.

- Push Notifications: Uses ntfy.sh to send free, instant alerts to your phone (Android/iOS) or desktop.

- Stealth Mode: Runs in a headless Chrome browser with anti-detection measures.

- Human-like Behavior: Uses randomized check intervals to prevent IP bans.



🛠️ Prerequisites

- Python 3.7+

- Google Chrome installed on your machine.

- An internet connection.
- Install the required Python packages: pip install selenium webdriver-manager requests



⚙️ Configuration

You can configure the bot in two ways: by editing the top of amul_bot.py or by following the interactive prompts when running the script.


- ITEM_URL : The specific product page you want to track (e.g., High Protein Lassi).

- ADDRESS_STRING : Your Pincode (e.g., 500089). This is critical because Amul's stock varies by region.

- NTFY_TOPIC : A unique topic name for notifications (see below).

Setting up Notifications (ntfy.sh)

- This bot uses ntfy.sh for alerts. No sign-up or API key is required.

- Download the Ntfy app on your phone (Android/iOS) or open the website.

- Subscribe to a unique topic name (e.g., my-secret-amul-alert).

- Enter this topic name when the script asks for NTFY_TOPIC.



▶️ Usage

- The script will ask for configuration details. Press Enter to use the defaults set in the code.

- It will launch a headless browser and attempt to set your location/pincode.

- Once the location is verified, it enters a monitoring loop.

- Keep the terminal open. When stock is found, you will get a notification on your subscribed device.



⚠️ Disclaimer

This tool is for educational purposes only. Automated scraping may violate the Terms of Service of the target website. Use responsibly and do not set the check interval too low to avoid overwhelming their servers.
