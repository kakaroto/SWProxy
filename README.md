# Summoners War Monsters & Runes Parser

This tool will parse data captured from the initial Summoners War login data and extract information on the monsters and runes of the user.

This tool was created with a single purpose: Exporting the runes so it can be used with external tools, such as the Rune Optimizer by Redeemer40 available here : http://swrunes.all.my/

## SWProxy
The easiest and safest method is to use the SWProxy application which will run a small proxy server on your machine. You will then need to set the proxy settings in your Android or IOS device to the IP and Port displayed by SWProxy and wait for the data to appear.
In order to get login data, make sure you quit Summoners War and log back in with the proxy enabled.

## SWParser
The SWParser will parse a pcap file containing a network capture of the Summoners War login information.
You will need a pcap file that can be captured either by configuring a proxy (such as Charles or Fiddler) and capturing the pcap file with Wireshark or using a capture application such as tPacketCapture.
See https://www.reddit.com/r/summonerswar/comments/3yzb02/releasing_the_sw_monsters_runes_extractor/cyi2adn for instructions on how to capture the pcap file on IOS or Android using a proxy and wireshark.
See https://youtu.be/fimW1n5PSX0 for instructions on how to capture the pcap file on Android using tPacketCapture.

### Parsing the data
Run the SWParser.py with the pcap file as an argument. It will parse the captured data, find the login information and export a few files with all the information on your account.
That's all you need to do.

## Files
<id>.json: This is your login data in its pure JSON format. Read it if you're curious or use it to find data that this tool doesn't export
<id>-info.csv: A CSV file with information about your user
<id>-runes.csv: A CSV file with information about your runes
<id>-monsters.csv: A CSV file with information about your monsters
visit-<id>-monsters.csv: A CSV file with information about the monsters of a user you visited 
visit-<id>.json: The JSON data of the user you visited
<id>-optimizer.json: A json file to use with the Rune optimizer

## CSV Files
The CSV files can be opened as a Spreadsheet with OpenOffice or Microsoft Excel.
The monsters are listed in the same order they would appear in your box if you sort by Grade.
The monsters listed for a visited friend are in the same order as his box as well (which is not actually sorted by grade).

## Visiting friends
You can visit friends (or people from chat, or arena rankings, etc..) and the script will create a visit-<name>-monsters.csv file with all of their monsters and their equipped runes. Note that their monsters that are in storage will also be visible in the CSV file even though the game doesn't show them.

## Optimizer data
The optimizer.json file can be directly loaded on the Rune Optimizer app available here : http://swrunes.all.my/
Simply open the file with a text editor and copy/paste the data into the import section of the web app and press Import.

--

## Installing and using it (MAC):

Download the repo's zip and extract in the folder of your choice in your Mac. Open Terminal and browse your folder.
Make sure you have python installed by running `python --version`. It should print something like `Python 2.7.9`. If you don't have, install it with Brew.
Install pycrypto by doing the following command: `sudo -H pip install pycrypto`. It should appear the following message:

 	Collecting pycrypto
	  Downloading pycrypto-2.6.1.tar.gz (446kB)
	    100% |████████████████████████████████| 446kB 873kB/s 
	Installing collected packages: pycrypto
	  Running setup.py install for pycrypto
	Successfully installed pycrypto-2.6.1

Now run `setup.py install` to install SWParser. It should appear the following message:

	/usr/local/Cellar/python/2.7.9/Frameworks/Python.framework/Versions/2.7/lib/python2.7/distutils/dist.py:267: UserWarning: Unknown distribution option: 'console'
	  warnings.warn(msg)
	running install
	running build
	running build_py
	creating build
	creating build/lib
	creating build/lib/SWParser
	copying SWParser/__init__.py -> build/lib/SWParser
	copying SWParser/monsters.py -> build/lib/SWParser
	copying SWParser/parser.py -> build/lib/SWParser
	copying SWParser/setup.py -> build/lib/SWParser
	running install_lib
	creating /usr/local/lib/python2.7/site-packages/SWParser
	copying build/lib/SWParser/__init__.py -> /usr/local/lib/python2.7/site-packages/SWParser
	copying build/lib/SWParser/monsters.py -> /usr/local/lib/python2.7/site-packages/SWParser
	copying build/lib/SWParser/parser.py -> /usr/local/lib/python2.7/site-packages/SWParser
	copying build/lib/SWParser/setup.py -> /usr/local/lib/python2.7/site-packages/SWParser
	byte-compiling /usr/local/lib/python2.7/site-packages/SWParser/__init__.py to __init__.pyc
	byte-compiling /usr/local/lib/python2.7/site-packages/SWParser/monsters.py to monsters.pyc
	byte-compiling /usr/local/lib/python2.7/site-packages/SWParser/parser.py to parser.pyc
	byte-compiling /usr/local/lib/python2.7/site-packages/SWParser/setup.py to setup.pyc
	running install_egg_info
	Writing /usr/local/lib/python2.7/site-packages/SWParser-1.0-py2.7.egg-info
	
Now to start proxy, run the following command: `SWProxy.py`. If by any chance you get `ImportError: No module named Crypto.Cipher`, run `python SWProxy.py` instead. If all went fine, you should see the following message:

	SWParser v0.95 - Summoners War Proxy
		Written by KaKaRoTo

	Licensed under GPLv3 and available at : 
		https://github.com/kakaroto/SWParser

	Running Proxy server at 192.168.0.78 on port 8080
