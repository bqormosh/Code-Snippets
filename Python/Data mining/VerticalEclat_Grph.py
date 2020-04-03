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
        self.maximal = dict()
        self.hashtable = dict()
        self.freq_count = 0
        for line in file:
            trans = (line.strip()).split(" ")
            self.trans_len = len(trans)
            # store the diffset
            indices = [i for i, x in enumerate(trans) if x == "0"]
            if (self.trans_len-len(indices)) >=minsupp:
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
            #print "length of next level : " ,len(freq_list)
            for p in range(0,len(freq_list)):
                self.doEclat(freq_list[p],p,freq_list)
        else:
            hash_str = self.isMaximal(pattern_a.ids_set)
            if hash_str is not None:
                self.maximal[hash_str] = pattern_a


    def isConnected(self,ids_set):
        ids_set = [int(x) for x in ids_set]
        subg = self.graph.subgraph(ids_set)
        if len(subg.clusters()) == 1:
            #connected
            return True
        else:
            return False

    def isMaximal(self,ids_set):
        ids_str = ",".join([str(x) for x in sorted(ids_set)])
        if ids_str not in self.maximal and len(ids_set) >=2:
            for key in self.maximal:
                if ids_set.issubset(set([int(x) for x in key.split(",")])):
                    return None
            return ids_str
        else:
            return None


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





#8,7 ,6 --------------
def main():
    t1 = datetime.datetime.now()
    print "Started Working"
    #my_eclat = dEclat(3,'data/toyexample.txt')
    my_eclat = dEclat(8,'data/HPRD_GSE4488_binary.txt','data/GSE4488RankHPRDNetwork.txt')

    level_one = []
    for p in range(0,len(my_eclat.trans_list)):
        # at the begining pattern support is the normal support (total len - diffset)
        p_supp = my_eclat.trans_len-len(my_eclat.trans_list[p])
        p_pattern = Pattern(set([p]),set(my_eclat.trans_list[p]),p_supp)
        level_one.append(p_pattern)
        my_eclat.freq_count = my_eclat.freq_count + 1
        print p_pattern.ids_set
        #my_eclat.hashtable[str(p)] = p_pattern
    print "level one created !",len(level_one)


    for p in range(0,len(level_one)):
        print "working on level ", p
        my_eclat.doEclat(level_one[p],p,level_one)

    t2 = datetime.datetime.now()
    print "Time Diff", t2-t1
    print "################################"
    print "total number is : ",str(my_eclat.freq_count)
    print "total number of Maximal is : ",str(len(my_eclat.maximal))
    # output = open("output/HPRD_GSE4107_binary_out_grph_11.txt", 'w')
    # for i in my_eclat.maximal:
    #     output.write(i)
    #     output.write("\n")
    # output.close()
    print "Time Diff", t2-t1
if __name__ == "__main__":
    main()