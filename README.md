# 🕵️‍♀️ website-watcher

![License](https://badges.fw-web.space/github/license/muety/website-watcher)
![Coding Activity](https://badges.fw-web.space/endpoint?url=https://wakapi.dev/api/compat/shields/v1/n1try/interval:any/project:website-watcher&color=blue)
![GitHub code size in bytes](https://badges.fw-web.space/github/languages/code-size/muety/website-watcher)
![GitHub issues](https://badges.fw-web.space/github/issues/muety/website-watcher)
![GitHub last commit](https://badges.fw-web.space/github/last-commit/muety/website-watcher)
[![Say thanks](https://badges.fw-web.space/badge/SayThanks.io-%E2%98%BC-1EAEDB.svg)](https://saythanks.io/to/n1try)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=muety_website-watcher&metric=security_rating)](https://sonarcloud.io/dashboard?id=muety_website-watcher)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=muety_website-watcher&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=muety_website-watcher)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=muety_website-watcher&metric=sqale_index)](https://sonarcloud.io/dashboard?id=muety_website-watcher)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=muety_website-watcher&metric=ncloc)](https://sonarcloud.io/dashboard?id=muety_website-watcher)

## 🗒 Summary
This script watches a website, saves its contents to a specified text file, compares this file's contents to the website contents at the next visit and sends an e-mail if there are differences.

**Please note:** This will only work for **static** websites, which are completely rendered on the server. To parse dynamic, JavaScript-powered websites, like Single Page Apps, you would need a tool like [Selenium WebDriver](https://www.seleniumhq.org/projects/webdriver/). If you're interested, please refer to my blog article about [_"Building a cloud-native web scraper using 8 different AWS services"_](https://muetsch.io/building-a-cloud-native-web-scraper-using-8-different-aws-services.html).

## 🖊 Description
I made it for the purpose to repeatedly check a specific webpage where university exam results get published so I get notified almost instantly. Another application could be watching on the postal service's shipment tracking or the like.
The script is very simple and works in a way that it visits a website, saves the entire HTML code into a local file and compares its contents to the potentially new page contents at the next visit. If there was a difference you will be notified via an e-mail. You can specify a threshold for saying how many single-character changes you want to actually be considered a change (maybe some webpages will display the current time at the right bottom, which you want to ignore - if time is displayed like `6:45 pm` than a theshold of at least 5 would result in ignoring these changes).
In order to save memory and CPU time in idle (although only very few) the script itself will only run once when executing it and instantly exit after it has finished one website visit. To make it run repeatedly you will have to set up a cron job that simply execute the script.

## ⚙️ Requirements
* Python >= 3.6
  * Currently not working with Python 3.9
* Cron jobs
  * Or something like [schtasks](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc748993(v=ws.11)?redirectedfrom=MSDN) on Windows

## ▶️ Usage
* Clone project: `git clone https://github.com/n1try/website-watcher-script`
* `sudo pip3 install -r requirements.txt`
* `chmod +x watcher.py`
* Create cronjob for your user account with `crontab -e` and add – for instance – `@hourly ~/dev/watcher.py -u https://kit.edu -t 5 --adapter email -r ferdinand@muetsch.io`. This will hourly visit kit.edu and send an e-mail in case of changes, while ignoring changes less than 6 characters.
* See `python3 watcher.py -h` for information on all available parameters.

### Options
* `-u URL` (`required`): URL of the website to watch
* `-t TOLERANCE`: Tolerance in characters, i.e. changes with a difference of less than or equal to `TOLERANCE` characters will be ignored and not trigger a notification
* `-x XPATH`: An [XPath](https://developer.mozilla.org/en-US/docs/Web/XPath) query to restrict watching to certain parts of a website. Only child elements of the element matching the query will be considered while watching
* `--adapter ADAPTER`: Which sending adapter to use (see below)

### 👀 Please note
When running the script for the first time, you will get an e-mail that there where changes, since there is a difference between the empty file and the entire webiste HMTL code.

## 🔌 Adapters
Multiple **send methods** are supported in the form of _adapters_. To choose one, supply `--adapter` (e.g. `--adapter email`) as a an argument to `watcher.py`

To write your **own adapter**, you need to implement abstract `SendAdapter` class. See [adapters/email.py](adapters/email.py) for an example.

### E-Mail (`email`)
This adapter, which is also the default one, will send an e-mail to notify about changes. It either uses local _sendmail_ or a specified SMTP server.

#### Options
```
  -r RECIPIENT_ADDRESS          – Recipient e-mail address (required)
  -s SENDER_ADDRESS             – Sender e-mail address
  --subject SUBJECT             – E-Mail subject
  --sendmail_path SENDMAIL_PATH – Path to Sendmail binary
  --smtp                        – If set, SMTP is used instead of local Sendmail.
  --smtp_host SMTP_HOST         – SMTP server host name to send mails with – only required of "--smtp" is set to true
  --smtp_port SMTP_PORT         – SMTP server port – only required of "--smtp" is set to true
  --smtp_username SMTP_USERNAME – SMTP server login username – only required of "--smtp" is set to true
  --smtp_password SMTP_PASSWORD – SMTP server login password – only required of "--smtp" is set to true
  --disable_tls                 – If set, SMTP connection is unencrypted (TLS disabled) – only required of "--smtp" is set to true

```

### Webhook2Telegram (`webhook2telegram`)
This adapter will send an push notification via [Telegram](https://telegram.org) using [Webhook2Telegram](https://github.com/muety/webhook2telegram).
You have to register for the bot first to get an token. To do so, send a message to [@MiddlemanBot](https://t.me/@MiddlemanBot) (Webhook2Telegram was formerly called MiddlemanBot).

#### Options
```
  -r RECIPIENT_TOKEN            – Recipient token (required)
  -s SENDER                     – Sender name
  --webhook_url WEBHOOK_URL     – URL of the Webhook2Telegram bot instance
```

### Gotify (`gotify`)
This adapter will send an push notification via [Gotify](https://gotify.net).
First, you have to register a new app in Gotify and gets its key as an authorization token.

#### Options
```
  --gotify_key GOTIFY_KEY       – Gotify app key / token
  --gotify_url GOTIFY_URL       – Gotify server instance address
```

### WebSub (`websub`)
This adapter will send a ping to a [WebSub Hub](https://w3c.github.io/websub) (e.g. [pubsubhubbub.superfeedr.com](http://pubsubhubbub.superfeedr.com/) as a hosted service or [Switchboard](https://switchboard.p3k.io/) as a self-hosted hub). However, a check whether the target resource is actually a publisher for that hub is skipped. You should verify that yourself.

#### Options
```
  --hub_url HUB_URL       – URL of the WebSub hub to publish to
```

## 👩‍💻 Contributing
Feel free to contribute! All contributions that add value to the project are welcome. Please check the issues section for bug reports and feature requests.

## 📓 License
MIT @ [Ferdinand Mütsch](https://muetsch.io)
