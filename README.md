# Summoners War Monsters & Runes Parser

This tool will parse data captured from the initial Summoners War login data and extract information on the monsters and runes of the user.

This tool was created with a single purpose: Exporting the runes so it can be used with external tools, such as the Rune Optimizer by Redeemer40 available here : http://swrunes.all.my/

## SWProxy
The easiest and safest method is to use the SWProxy application which will run a small proxy server on your machine. You will then need to set the proxy settings in your Android or IOS device to the IP and Port displayed by SWProxy and wait for the data to appear.
In order to get login data, make sure you quit Summoners War and log back in with the proxy enabled.

## SWParser
The SWParser will parse a pcap file containing a network capture of the Summoners War login information.
You will need a pcap file that can be captured either by configuring a proxy (such as Charles or Fiddler) and capturing the pcap file with Wireshark or using a capture application such as tPacketCapture.
Using this method is not recommended, but it's a workaround if it's not possible to setup a proxy with SWProxy for example.

Once you have your pcap capture file, run the SWParser.py with the pcap file as an argument. It will parse the captured data, find the login information and export a few files with all the information on your account.
That's all you need to do.

## Files
<id>.json: This is your login data in its pure JSON format. Read it if you're curious or use it to find data that this tool doesn't export
<id>-info.csv: A CSV file with information about your user
<id>-runes.csv: A CSV file with information about your runes
<id>-monsters.csv: A CSV file with information about your monsters
visit-<id>-monsters.csv: A CSV file with information about the monsters of a user you visited 
visit-<id>.json: The JSON data of the user you visited
<id>-optimizer.json: A json file to use with the Rune optimizer
<id>-swarfarm.json: A json file to use with the Swarfarm import utility.

## CSV Files
The CSV files can be opened as a Spreadsheet with OpenOffice or Microsoft Excel.
The monsters are listed in the same order they would appear in your box if you sort by Grade.
The monsters listed for a visited friend are in the same order as his box as well (which is not actually sorted by grade).

## Visiting friends
You can visit friends (or people from chat, or arena rankings, etc..) and the script will create a visit-<name>-monsters.csv file with all of their monsters and their equipped runes. Note that their monsters that are in storage will also be visible in the CSV file even though the game doesn't show them.

## Optimizer data
The optimizer.json file can be directly loaded on the Rune Optimizer app available here : http://swrunes.all.my/
Simply open the file with a text editor and copy/paste the data into the import section of the web app and press Import.

## Using it on Linux:
All you need to run it is the following dependencies :

* Python 2.x
 * pycrypto
 * dpkt
 * yapsy

You can install python with your package manager and the python dependencies as well, or you can install the python dependencies with :

```sudo pip install -r requirements.txt```

## Using it on a MAC:

Download the latest release source code from here https://github.com/kakaroto/SWParser/releases/latest and extract it in the folder of your choice in your Mac. Open Terminal and browse your folder.
Make sure you have python installed by running `python --version`. It should print something like `Python 2.7.9`.
Install pycrypto by doing the following command: `sudo -H pip install pycrypto dpkt yapsy`. It will ask you to enter your password in order to install the pycrypto dependency. Once you do, it should show a message similar to this :

 	Collecting pycrypto
	  Downloading pycrypto-2.6.1.tar.gz (446kB)
	    100% |████████████████████████████████| 446kB 873kB/s 
	Installing collected packages: pycrypto
	  Running setup.py install for pycrypto
	Successfully installed pycrypto-2.6.1

If you do not have the 'pip' command installed, use 'sudo -H easy_install pycrypt dpkt yapsy' to install pycrypto.

Now you should be able to start the proxy. Simply run the following command: `python SWProxy.py`. If all went fine, you should see the following message:

	SWParser v0.99 - Summoners War Proxy
		Written by KaKaRoTo

	Licensed under LGPLv3 and available at : 
		https://github.com/kakaroto/SWParser

	Running Proxy server at 192.168.x.y on port 8080

## GUI
The optional GUI provided requires the `pyqt` package. 
Instal `pyqt` according to your OS's installation procedures (i.e. `brew install pyqt` on OS X) or you can compile it from source:

[PyQt-x11-gpl-4.11.4.tar.gz](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz) - Linux source

[PyQt-win-gpl-4.11.4.zip](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt-win-gpl-4.11.4.zip) - Windows source

[PyQt-mac-gpl-4.11.4.tar.gz](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt-mac-gpl-4.11.4.tar.gz) - OS X source

After installing `pyqt`, running `python SWProxy.py` will launch the GUI automatically.

## The story of the missing smon_decryptor.py file
The smon_decryptor.py file is not available for now because it contains the decryption key of the protocol. To avoid people abusing the system or creating bots or anything else that is not permitted by the Com2Us terms of service, I have decided not to make that decryption key available publicly.
The binary file smon_decryptor.pyc is provided instead which allows SWProxy and SWParser to still function. That file, as it is only provided as a binary is not licensed under the same terms as the rest of the tool.

## FAQ
### Can I change the port the proxy server runs it
Yes, the first argument of SWProxy is the port number to use.

### For some reason, I can't connect to the internet when I set the proxy settings in my device.
There can be many reasons for that. Here is a list of reasons some people have found caused this problem for them :
* phone was connected to a different router (neighbor's wifi or connected to 3G instead of wifi)
* Windows Firewall had to be disabled
* SWProxy had to be run as administrator
* Antivirus had to be disabled (which sometimes acts as a firewall)
* Router had to be rebooted
* Router had to be updated
* Phone (iOS) had to be updated to the latest version
* PC had to use a wireless dongle because router doesn't let wired and wireless computers communicate with each other

### I can use the internet with the proxy but I can't start the game
The game itself seems to have a bug where it fails to connect to the server at boot (seems to affect everyone, whether using a proxy or not), and I think the proxy just makes that bug more apparent. Some people have reported that it works better if you launch the game without the proxy set, then when the message is "bringing your friend list", then switch to the phone settings and set the proxy before returning to the game. It will usually work when done that way.

### Is there a risk for me to get banned ?
Technically, we're not doing anything wrong, but you can always get banned from the game, so use at your own risks. Some people have been banned in the past simply for having a rooted phone.
The Terms of Service of Com2Us however, only says that you will get banned if you use unauthorized third party application *designed to modify or interfere with or provide automated access* to the service or any software that is used to *abuse the game services*. This application does not modify or interfere in any way with the game, it doesn't act as a bot that automated access to the game and it is not used to abuse any of the game services, so it is not against the ToS.
You can read the full Terms of Services here : http://terms.withhive.com/terms/policy/view/M14

Also, if using the Proxy method, it is virtually undetectable since there is no application installed on the phone, and the Android or iOS operating system is the one that handles the proxy connection transparently. While it might be possible for the game to detect if a proxy is set, many people use proxies everyday (such as in offices), and banning anyone that uses a proxy is not realistic.

### Can you add feature X to the app ?
Whatever the feature is, I'm simply not interested. I've received numerous requests and proposals but this application has a single purpose, it is to export the runes to be used with the rune optimizer apps during free rune removal days. Any extra feature will make the app more and more feature-rich until it becomes something that is against the Terms of Service. I have to draw a line somewhere and I drew a line at "exporting runes and monster information", and I don't want to add anything more to the app.
You are free however to fork the repository and develop your own application with whatever feature you want, but please make sure to read the ToS and not to make anything that can abuse the game services. Also, if you use anything from my app, make sure you read the LICENSE file and respect the license and release your own apps with the same license.
