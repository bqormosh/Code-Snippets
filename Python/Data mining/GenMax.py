__author__ = 'Bassam Qormosh'
import os.path

class Genmax:
    def __init__(self, minsupp):
        # initialization
        self.minsupp = minsupp
        # initialize transaction id with 1 and increment when vertical database is created
        self.tid = 1
        # vertical database
        self.vertical_db = dict()
        # list of maximal itemsets
        self.maximal = []

    def doGenmax(self, prefix_eq):
        # First Check
        pattern_y = Pattern(set(),set())
        for patterns in prefix_eq:
            pattern_y = pattern_y.union(patterns)
        for pattern_z in self.maximal:
            if (pattern_y.itemset).issubset(pattern_z.itemset):
                return
        #########################
        for pattern_a in prefix_eq:
            prefix_eq_a = []
            for pattern_b in prefix_eq:
                if prefix_eq.index(pattern_b) > prefix_eq.index(pattern_a):
                    pattern_ab = pattern_a.union(pattern_b)
                    if len(pattern_ab.tids) >= self.minsupp:
                       prefix_eq_a.append(pattern_ab)
            if len(prefix_eq_a) > 0:
                self.doGenmax(prefix_eq_a)
            else:
                ########## Second Check
                found = False
                for pattern_z in self.maximal:
                    if (pattern_a.itemset).issubset(pattern_z.itemset):
                        found = True
                if found == False :
                    self.maximal.append(pattern_a)



    def createDb(self, path):
        if os.path.isfile(path):
            try:
                file = open(path, 'rU')
                for line in file:
                    items_objects = line.split(" ")
                    for i in items_objects:
                        # usage of (forzentset) because they are hashable and can be used as dictionary keys
                        itemset_v = frozenset([i.strip()])
                        if itemset_v in self.vertical_db:
                            temp_set = self.vertical_db[itemset_v]
                            temp_set.update([self.tid])
                            self.vertical_db[itemset_v] = temp_set
                        else:
                            self.vertical_db[itemset_v] = set()
                            tempo_set = set()
                            tempo_set.update([self.tid])
                            self.vertical_db[itemset_v] = tempo_set
                    self.tid = self.tid + 1
                file.close()
            except IOError:
                print 'Error reading File'
        else:
            print "File not found"
    def cleanDb(self):
        initial_prefix_eq = []
        self.maximal = []
        if len(self.vertical_db) > 0:
            for key in self.vertical_db:
                if len(self.vertical_db[key]) >= self.minsupp:
                    initial_prefix_eq.append(Pattern(set(key),set(self.vertical_db[key])))
        return initial_prefix_eq

class Pattern:
    #itemset is a list of items
    def __init__(self, itemset, tids):
        self.itemset = itemset
        self.tids = tids

    def union(self,other_pattern):
        #items union
        new_itemset = (self.itemset).union(other_pattern.itemset)
        #transactions ids intersection
        new_tids = (self.tids).intersection(other_pattern.tids)

        return Pattern(new_itemset,new_tids)



def main():
    my_genmax = Genmax(4000)
    # path for the file where the database is stored
    # need to be changed according to user
    my_genmax.createDb('mushroom.txt')
    initial_prefix_eq = my_genmax.cleanDb()
    my_genmax.doGenmax(initial_prefix_eq)
    print len(my_genmax.maximal)
    # for p in my_genmax.maximal:
    #     print p.itemset
    #     print p.tids


if __name__ == "__main__":
    main()



