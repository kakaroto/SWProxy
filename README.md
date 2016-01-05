# Summoners War Monsters & Runes Parser

This tool will parse data captured from the initial Summoners War login data and extract information on the monsters and runes of the user.

This tool was created with a single purpose: Exporting the runes so it can be used with external tools, such as the Rune Optimizer by Redeemer40 available here : http://www.graphactory.eu/sw/

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
The optimizer.json file can be directly loaded on the Rune Optimizer app available here : http://www.graphactory.eu/sw/
Simply open the file with a text editor and copy/paste the data into the import section of the web app and press Import.
