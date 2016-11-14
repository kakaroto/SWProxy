import unittest
import SWParser.parser


class ParserCase(unittest.TestCase):
    def test_monster_name(self):
        code_map = {
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
            12211: "AWAKENED Slime (Water)",
            19111: "AWAKENED Fairy Queen (Water)",
        }
        for uid, name in code_map.iteritems():
            self.assertEqual(
                SWParser.parser.monster_name(uid),
                name,
            )


if __name__ == '__main__':
    unittest.main()
