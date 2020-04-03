import datetime
from igraph import *

class dEclat:
    def __init__(self, minsupp,db_file,graph_file):
        # initialization
        self.graph = Graph.Read_Edgelist(graph_file,directed=False)
        self.minsupp = minsupp
        self.file = db_file
        file = open(db_file, 'rU')
        self.trans_list = []
        self.maximal = []
        self.freq_count = 0
        self.hashtable = dict()
        for line in file:
            trans = (line.strip()).split(" ")
            indices = [i for i, x in enumerate(trans) if x == "1"]
            if len(indices) >=minsupp:
                self.trans_list.append(indices)

    def doEclat(self,pattern_a,pattern_a_index,patterns_list):
        freq_list = []
        #print "ln the loop"
        for pb_index in range(0,len(patterns_list)):
            if pb_index >  pattern_a_index:
                pattern_ab = pattern_a.extend(patterns_list[pb_index])
                if pattern_ab.supp >= self.minsupp and self.isConnected(pattern_ab.ids_set):
                    self.freq_count = self.freq_count + 1
                    freq_list.append(pattern_ab)
        if len(freq_list) > 0:
            for p in range(0,len(freq_list)):
                self.doEclat(freq_list[p],p,freq_list)
        else:
            self.maximal.append(pattern_a)


    def isConnected(self,ids_set):
        ids_set = [int(x) for x in ids_set]
        subg = self.graph.subgraph(ids_set)
        if len(subg.clusters()) == 1:
            #connected
            return True
        else:
            return False


class Pattern:
    #itemset is a list of items
    def __init__(self,ids_set,prop_list,supp):
        self.ids_set = ids_set
        self.prop_list = set(prop_list)
        self.supp = supp

    def extend(self,pattern_b):
        ab_set = self.ids_set.union(pattern_b.ids_set)
        ab_prop_list = pattern_b.prop_list.intersection(self.prop_list)
        ab_supp = len(ab_prop_list)
        return Pattern(ab_set,ab_prop_list,ab_supp)






def main():
    t1 = datetime.datetime.now()
    print "Started Working"
    #my_eclat = dEclat(4,'data/toyexample.txt')
    my_eclat = dEclat(8,'data/HPRD_GSE4488_binary.txt','data/GSE4488RankHPRDNetwork.txt')

    level_one = []
    for p in range(0,len(my_eclat.trans_list)):
        # at the begining pattern support is the normal support (total len - diffset)
        p_pattern = Pattern(set([p]),set(my_eclat.trans_list[p]),len(my_eclat.trans_list[p]))
        level_one.append(p_pattern)
        my_eclat.hashtable[str(p)] = p_pattern
    print "level one created !",len(level_one)


    for p in range(0,len(level_one)):
        print "working on level ", p
        my_eclat.doEclat(level_one[p],p,level_one)


    t2 = datetime.datetime.now()
    print "Time Diff", t2-t1
    #cnt = 0
    print "################################"
    # for key in my_eclat.hashtable:
    #     print key
    #     cnt = cnt + 1
    print "total number is : ",str(my_eclat.freq_count)
    print "total number of Maximal is : ",str(len(my_eclat.maximal))
    print "Time Diff", t2-t1

if __name__ == "__main__":
    main()