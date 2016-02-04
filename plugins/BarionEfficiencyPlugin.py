import SWPlugin

class BarionEfficiencyPlugin(SWPlugin.SWPlugin):
    def process_csv_row(self, csv_type, data_type, data):
        if csv_type not in ['monsters', 'visit', 'runes']:
            return

        if data_type == 'header':
            ids, headers = data
            ids.append('barion')
            headers['barion'] = "Barion's Rune Efficiency"
            return
        if data_type == 'rune':
            rune, row = data
            row['barion'] = "%.2f %%" % (rune_efficiency(rune) * 100)

def rune_efficiency(rune):
    sum = 0
    for eff in [rune['prefix_eff']] + rune['sec_eff']:
        typ = eff[0]
        value = eff[1]
        max = 0
        if typ in [2, 4, 6, 11, 12]:
            max = 40.0
        elif typ == 8 or typ == 9:
            max = 30.0
        elif typ == 10:
            max = 35.0
        if max > 0:
            sum += (value / max)
    sum += 1 if rune['class'] == 6 else 0.85
    return sum / 2.8
