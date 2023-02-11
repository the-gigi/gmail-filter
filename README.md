# gmail-filter
The gmail-filter program read emails from your Gmail inbox, filters them based on internal criteria
and move matching emails to two new labels.

# Install from scratch on Windows

To run gmail-filter you need to install git and Python using chocolatey.

## Installing Chocolatey

First install [chocolatey](https://chocolatey.org/install) - a tool to install other tools...

[Open a PowerShell administrative console](https://www.howtogeek.com/194041/how-to-open-the-command-prompt-as-administrator-in-windows-8.1/)

Then type:
```
Set-ExecutionPolicy Bypass -Scope Process
```

Followed by:
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Now, chocolatey should be installed and ready to install the other tools you need. To verify type:
```
choco
```

## Installing git

Git is a tool for version control and management of source code. The gmail-filter code is stored in a git repository, which means you need git to get it.

In the PowerShell administrative console type:
```
choco install git.install
```

Verify git is up and running by typing:
```
git
```

## Installing Python

The gmail-filter program is written in [Python](https://www.python.org), which requires a Python interpreter to run. Note, that you don't need to know Python in order to use gmail-filter.

Install Python using the following command:

```
choco install python
```

Verify Python is installed correctly by typing:
```
python
```

## Cloning the gmail-filter repository

We are to get gmail-filter from [Github](https://github.com) - a git repository that hosts gmail-filter.

In the PowerShell console make a note of your current directory. If you know your way around files and directories you may create or navigate to another diretory (folder).
The following command will create a new directorty called `gmail-filter` under your current directory.

```
git clone https://github.com/the-gigi/gmail-filter.git
```

Verify it was cloned correctly by typing:
```
cd gmail-filter
```

Then type:
```
ls
```

You should see a list of files including a `main.py`

## Troubleshooting

If during the installation process of any tool you run into errors such "command not found" you may need to close and open the PowerShell administrative Window so it picks up the environment.

If you encounter errors similar to "operation is forbidden" male sure you run an administrative console of PowerShell and not a regular one.

If you run into something else... search the internet or ask ChatGPT...

# Using gmail-filter

At this point you should have all the necessary tools and the gmail-filter program should be ready to go. 

NOTE: The gmail-filter application is in testing and only registered users can use it. 

## First time usage

Before running gmail-filter for the first time you need to create the target labels:

- Kneadace
- Kneadace Filtered

Note that when you run gmail-filter for the very first time you will go through an authentication process where you will be asked to give access to your gmail account. Do it!

## Running gmail-filter

Open a PowerShell console (doesn't have to be administrative).
Navigate to the location of the `gmail-filter` 
Type the following command to scan the latest 50 emails in your Gmail inbox (you can pick any number):
```
python main.py 50
```

The gmail-filter program will run and start scanning your gmail inbox. It will scan the latest 50 (or whatever number you provided) emails. 

It will print a snippet from each email to the screen and when it encounters an email that matches the filter it will move it out of your inbox to another label.

After a run review in your web browser (https://gmail.com) the target labels, and your target emails should be in the right place.
If gmail-filter moved an unrelated email you can manually move it back to your inbox and report the problem to the.gigi@gmail.com.

That's it. Enjoy gmail-filter 🎉
