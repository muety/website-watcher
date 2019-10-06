# 🕵️‍♀️ website-watcher-script

## 🗒 Summary
This script watches a website, saves its contents to a specified text file, compares this file's contents to the website contents at the next visit and sends an e-mail if there are differences.

**Please note:** This will only work for **static** websites, which are completely rendered on the server. To parse dynamic, JavaScript-powered websites, like Single Page Apps, you would need a tool like [Selenium WebDriver](https://www.seleniumhq.org/projects/webdriver/). If you're interested, please refer to my blog article about [_"Building a cloud-native web scraper using 8 different AWS services"_](https://muetsch.io/building-a-cloud-native-web-scraper-using-8-different-aws-services.html).

## 🖊 Description
I made it for the purpose to repeatedly check a specific webpage where university exam results get published so I get notified almost instantly. Another application could be watching on the postal service's shipment tracking or the like.
The script is very simple and works in a way that it visits a website, saves the entire HTML code into a local file and compares its contents to the potentially new page contents at the next visit. If there was a difference you will be notified via an e-mail. You can specify a threshold for saying how many single-character changes you want to actually be considered a change (maybe some webpages will display the current time at the right bottom, which you want to ignore - if time is displayed like `6:45 pm` than a theshold of at least 5 would result in ignoring these changes).
In order to save memory and CPU time in idle (although only very few) the script itself will only run once when executing it and instantly exit after it has finished one website visit. To make it run repeatedly you will have to set up a cron job that simply execute the script.

## ⚙️ Requirements
* Python 3.6 
* A mail server
  * Option 1: sendmail to be installed
  * Option 2: access to an SMTP server
* Cron jobs
  * Or something like [schtasks](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc748993(v=ws.11)?redirectedfrom=MSDN) on Windows

## ▶️ Usage
* Clone project: `git clone https://github.com/n1try/website-watcher-script`
* `sudo pip3 install -r requirements.txt`
* Adjust constants in `watcher.py`, e.g. set the address and credential for your SMTP server, the path to local sendmail, the recipient email address etc.
* `chmod +x watcher.py`
* Create cronjob for your user account: `crontab -e` and add – for instance – `@hourly ~/dev/watcher.py -u https://kit.edu -t 5 -r ferdinand@muetsch.io` for hourly visiting kit.edu and ignoring changes less than 6 characters. See `python3 watcher.py -h` for information on all available parameters.

### 👀 Please note
When running the script for the first time, you will get an e-mail that there where changes, since there is a difference between the empty file and the entire webiste HMTL code.

## 👩‍💻 Contributing
Feel free to contribute! All contributions that add value to the project are welcome. Please check the issues section for bug reports and feature requests.

## 📓 License
MIT @ [Ferdinand Mütsch](https://muetsch.io)