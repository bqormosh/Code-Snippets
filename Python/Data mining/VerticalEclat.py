import datetime

class dEclat:
    def __init__(self, minsupp,db_file):
        # initialization
        self.minsupp = minsupp
        self.file = db_file
        file = open(db_file, 'rU')
        self.trans_list = []
        self.all_freq_list = []
        self.hashtable = dict()
        for line in file:
            trans = (line.strip()).split(" ")
            self.trans_len = len(trans)
            # store the diffset
            indices = [i for i, x in enumerate(trans) if x == "0"]
            if (self.trans_len-len(indices)) >=minsupp:
                self.trans_list.append(indices)

    def doEclat(self,pattern_a,pattern_a_index,patterns_list):
        freq_list = []
        print "ln the loop"
        for pb_index in range(0,len(patterns_list)):
            if pb_index >  pattern_a_index:
                pattern_ab = pattern_a.extend(patterns_list[pb_index])
                if pattern_ab.supp >= self.minsupp:
                    freq_list.append(pattern_ab)
                    print pattern_ab.ids_set," ,,, ",pattern_ab.supp
        if len(freq_list) > 0:
            for p in range(0,len(freq_list)):
                self.doEclat(freq_list[p],p,freq_list)
        else:
            self.all_freq_list.append(patterns_list)




class Pattern:
    #itemset is a list of items
    def __init__(self,ids_set,diff_list,supp):
        self.ids_set = ids_set
        self.diff_list = diff_list
        self.supp = supp
    def extend(self,pattern_b):
        ab_set = self.ids_set.union(pattern_b.ids_set)
        ab_diff_list = pattern_b.diff_list - self.diff_list
        ab_supp = self.supp-len(ab_diff_list)
        return Pattern(ab_set,ab_diff_list,ab_supp)






def main():
    t1 = datetime.datetime.now()
    print "Started Working"
    my_eclat = dEclat(3,'data/toyexample.txt')
    #my_eclat = dEclat(11,'data/HPRD_GSE4107_binary_notTransposed.txt')

    level_one = []
    for p in range(0,len(my_eclat.trans_list)):
        # at the begining pattern support is the normal support (total len - diffset)
        p_supp = my_eclat.trans_len-len(my_eclat.trans_list[p])
        p_pattern = Pattern(set([p]),set(my_eclat.trans_list[p]),p_supp)
        level_one.append(p_pattern)
    print "level one created !",len(level_one)


    for p in range(0,len(level_one)):
        my_eclat.doEclat(level_one[p],p,level_one)

    t2 = datetime.datetime.now()
    print "Time Diff", t2-t1
    print "################################"
    cnt = 0
    for l in my_eclat.all_freq_list:
        for p in l:
            print p.ids_set
            cnt = cnt + 1
    print "total number is : ",str(cnt)
if __name__ == "__main__":
    main()