import unittest
import SWParser.parser


class ParserCase(unittest.TestCase):
    def test_monster_name_full(self):
        code_map = {
            0: "???[0] (???[0])",
            10100: "Fairy (???[0])",
            10101: "Fairy (Water)",
            10102: "Fairy (Fire)",
            10103: "Fairy (Wind)",
            10104: "Fairy (Light)",
            10105: "Fairy (Dark)",
            10106: "Fairy (???[6])",
            10111: "Elucia",
            10112: "Iselia",
            10113: "Aeilene",
            10114: "Neal",
            10115: "Sorin",
            10000: "???[100] (???[0])",
            10001: "???[100] (Water)",
            12211: "AWAKENED Slime (Water)",
            19111: "AWAKENED Fairy Queen (Water)",
            1000111: "Homunculus (Water)",
        }
        for uid, name in code_map.iteritems():
            self.assertEqual(
                SWParser.parser.monster_name(uid),
                name,
            )

    def test_monster_name_short(self):
        code_map = {
            0: "???[0]",
            10100: "Fairy",
            10101: "Fairy",
            10102: "Fairy",
            10103: "Fairy",
            10104: "Fairy",
            10105: "Fairy",
            10106: "Fairy",
            10111: "Elucia",
            10112: "Iselia",
            10113: "Aeilene",
            10114: "Neal",
            10115: "Sorin",
            10000: "???[100]",
            10001: "???[100]",
            12211: "???[122]",
            19111: "???[191]",
            1000111: "Homunculus (Water)",
        }
        for uid, name in code_map.iteritems():
            self.assertEqual(
                SWParser.parser.monster_name(uid, full=False),
                name,
            )

if __name__ == '__main__':
    unittest.main()
