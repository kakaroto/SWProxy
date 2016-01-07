#rune: {u'occupied_type': 1, u'sell_value': 17514, u'pri_eff': [4, 63], u'prefix_eff': [0, 0], u'slot_no': 6, u'rank': 5, u'occupied_id': 1180433153, u'sec_eff': [[11, 6, 0, 0], [1, 323, 0, 0], [9, 5, 0, 0], [2, 5, 0, 0]], u'wizard_id': 53120, u'upgrade_curr': 15, u'rune_id': 5941249, u'base_value': 350285, u'class': 6, u'set_id': 8, u'upgrade_limit': 15}


def rune_addition(runes, stat, basevalue):
    addition = 0

    #print basevalue
    
    if stat == 'atk':
        multiplicitiveType = 4
        additiveType = 3
    if stat == 'def':
        multiplicitiveType = 6
        additiveType = 5
    if stat == 'con':
        multiplicitiveType = 2
        additiveType = 1
    if stat == 'spd':
        multiplicitiveType = 0
        additiveType = 8
    if stat == 'critical_rate':
        multiplicitiveType = 0
        additiveType = 9
    if stat == 'critical_damage':
        multiplicitiveType = 0
        additiveType = 10       
    if stat == 'resist':
        multiplicitiveType = 0
        additiveType = 11
    if stat == 'accuracy':
        multiplicitiveType = 0
        additiveType = 12

#    if len(runes) > 0:
#        print "rune 1 ", runes[0], "substats ", len(runes[0]['sec_eff']), "\n"
#        print "rune 2 ", runes[1], "substats ", len(runes[1]['sec_eff']),  "\n"
#        print "rune 3 ", runes[2], "substats ", len(runes[2]['sec_eff']), "\n" 
#        print "rune 4 ", runes[3], "substats ", len(runes[3]['sec_eff']),  "\n"
#        print "rune 5 ", runes[4], "substats ", len(runes[4]['sec_eff']),  "\n"
#        print "rune 6 ", runes[5], "substats ", len(runes[5]['sec_eff']),  "\n"
    
    #print "mval = ", multiplicitiveType, " aval = ", additiveType
    for rune in runes:
        if stat == 'spd' or stat == 'critical_rate' or stat == 'critical_damage' or stat == 'resist' or stat == 'accuracy':
            if rune['pri_eff'][0] == additiveType:
                addition += rune['pri_eff'][1]
            if rune['prefix_eff'][0] == additiveType:
                addition += rune['prefix_eff'][1]
            for sec_eff in rune['sec_eff']:            
                if sec_eff[0] == additiveType:
                    addition += sec_eff[1]

        if stat == 'atk' or stat == 'def' or stat == 'con':
            if rune['pri_eff'][0] == multiplicitiveType:
                #print "pri_eff ", basevalue * .01 * rune['pri_eff'][1]
                addition += basevalue * .01 * rune['pri_eff'][1] 
            if rune['pri_eff'][0] == additiveType:
                #print "pri_eff ", rune['pri_eff'][1]
                addition += rune['pri_eff'][1]
            if rune['prefix_eff'][0] == multiplicitiveType:
                #print "prefix_eff ", basevalue * .01 * rune['prefix_eff'][1] 
                addition += basevalue * .01 * rune['prefix_eff'][1] 
            if rune['prefix_eff'][0] == additiveType:
                #print "prefix_eff ", rune['prefix_eff'][1] 
                addition += rune['prefix_eff'][1]
            for sec_eff in rune['sec_eff']:            
                if sec_eff[0] == multiplicitiveType:
                    #print sec_eff
                    #print "sec_eff ", basevalue * .01 * sec_eff[1]
                    addition += basevalue * .01 * sec_eff[1]
                if sec_eff[0] == additiveType:
                    #print sec_eff
                    #print "sec_eff ", sec_eff[1]
                    addition += sec_eff[1]

#    if len(runes) > 0:                
#        print "rune_addition(runes", ", ", stat, ", ", basevalue, ") = ", int(addition)
    return int(addition)

def get_rune_sets(runes):
    from parser import rune_set_id
    
#                    1  2  3  4  5  6  7  8  9  A  B  C  D  E  F 11 12
    rune_sets_min = [2, 2, 4, 2, 4, 2, 2, 4, 6, 4, 4, 6, 2, 2, 2, 2, 2]
    rune_sets = [0] * 18

    if len(runes) == 0:
        return rune_sets
    
    for rune in runes:
        #print rune_set_id(rune['set_id'])
        rune_sets[rune['set_id'] - 1] += 1

    for x in range(0, 17):
        rune_sets[x] = rune_sets[x] / rune_sets_min[x];
        
    return rune_sets

