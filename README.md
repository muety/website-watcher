# website-watcher-script

### Summary
This script will watch a website, save its contents to a specified text file, compares this file's contents to the website contents at the next visit and send an e-mail if there are differences.

### Description
I made it for the purpose to repeatedly check a specific webpage where university exam results get published so I get notified almost instantly. Another application could be watching on the postal service's shipment tracking or the like.
The script is very simple and works in a way that it visits a website, saves the entire HTML code into a local file and compares its contents to the potentially new page contents at the next visit. If there was a difference you will be notified via an e-mail. You can specify a threshold for saying how many single-character changes you want to actually be considered a change (maybe some webpages will display the current time at the right bottom, which you want to ignore - if time is displayed like <code>6:45 pm</code> than a theshold of at least 5 would result in ignoring these changes).
In order to save memory and CPU time in idle (although only very few) the script itself will only run once when executing it and instantly exit after it has finished one website visit. To make it run repeatedly you will have to set up a cron job that simply execute the script.

### Requirements
* Linux based system
* Python 2.7.x to be installed
* __EITHER:__ sendmail to be installed
* __OR:__ access to an SMTP server
* Cron jobs

### Usage
* Clone project: `git clone https://github.com/n1try/website-watcher-script`
* `sudo pip install -r requirements.txt`
* Adjust constants in `watcher.py`, e.g. set the address and credential for your SMTP server, the path to local sendmail, the recipient email address etc.
* Create cronjob for your user account: `crontab -e` and add `@hourly /path/to/script/watcher.py <url> <threshold> <use_smtp>`, e.g. `@hourly ~/dev/watcher.py http://google.com 5 true` for hourly visiting google.com, ignoring changes less than 6 characters and sending notification mail via SMTP

##### NOTE
When running the script for the first time, you will get an e-mail that there where changes, since there is a difference between the empty file and the entire webiste HMTL code.