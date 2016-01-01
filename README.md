# Summoners War Monsters & Runes Parser

This tool will parse pcap files captured from the initial Summoners War login data and extract information on the monsters and runes of the user.

This tool was created with a single purpose: Exporting the runes so it can be used with external tools, such as the Rune Optimizer by Redeemer40 available here : http://www.graphactory.eu/sw/

# Data capture
You will need a pcap file that can be captured either by using a proxy (maybe for IOS, it can be done using something like Charles Proxy) or using a capture application such as tPacketCapture.
See https://youtu.be/fimW1n5PSX0 for instructions on how to capture the pcap file on Android.

## Parsing the data
Run the parser.py with the pcap file as an argument. It will parse the captured data, find the login information and export a few files with all the information on your account.
That's all you need to do.

## Files
<id>.json: This is your login data in its pure JSON format. Read it if you're curious or use it to find data that this tool doesn't export
<id>-info.csv: A CSV file with information about your user
<id>-runes.csv: A CSV file with information about your runes
<id>-monsters.csv: A CSV file with information about your monsters
visit-<name>-monsters.csv: A CSV file with information about the monsters of a user you visited 
<id>-optimizer.json: A json file to use with the Rune optimizer
monsters.py: A python dictionary containing all the known monsters by the tool
update_mons.sh: A UNIX script with a list of your monsters (in same order as Grade sorting) to update all their names in the monsters.py dictionary
update_mons.bat: A Windows script with a list of your monsters (in same order as Grade sorting) to update all their names in the monsters.py dictionary

## CSV Files
The CSV files can be opened as a Spreadsheet with OpenOffice or Microsoft Excel.
The monsters are listed in the same order they would appear in your box if you sort by Grade. This can be helpful in figuring out the missing monster names.
The monsters listed for a visited friend are in the same order as his box as well (which is not actually sorted by grade).

## Monster names
Monsters are identified by their ID which is a 5 digit number. The first 3 digits uniquely identify the monster type, for example 101=Fairy, 102=Imp, 103=Pixie, etc.. The 4th digit is set to 1 when the monster is awakened and 0 when it's not, and the 5th digit represents the attribute (1=Water, 2=Fire, 3=Wind, 4=Light, 5=Dark), so for example, 10102=Fire Fairy, 10313=Shannon(Awakened Wind Pixie)

The list of known monsters isn't complete, so if you find a monster without a name, you can either edit the monsters.py file that gets generated, or edit the update_mons.sh or update_mons.bat files (remember, the monsters are listed in the same order as the monsters in the box when sorted by Grade) then run the script to update the monsters.py file for you.
Once the monsters.py has the missing monster names, just run the parser again to update all the files.

If the script finds the monsters.py file, it will load it to override its own list of monsternames.

## Visiting friends
You can visit friends (or people from chat, or arena rankings, etc..) and the script will create a visit-<name>-monsters.csv file with all of their monsters (their equipped runes are also available but they are not exported). Note that their monsters that are in storage will also be visible in the CSV file even though the game doesn't show them.
