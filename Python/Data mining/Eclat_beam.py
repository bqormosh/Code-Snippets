__author__ = 'Bassam Qormosh'
import os.path
import datetime
class Eclat_beam:
    def __init__(self, minsupp):
        # initialization
        self.minsupp = minsupp
        # initialize transaction id with 1 and increment when vertical database is created
        self.tid = 1
        # vertical database
        self.vertical_db = dict()
        # list of frequent itemsets
        self.frequents = []

    def doEclat_beam(self,pattern_a,prefix_eq,current_index):
        self.frequents.append(pattern_a)
        # prefix_eq_a = []
        for pattern_b in prefix_eq:
            #for pattern_b in prefix_eq[current_index+1:]:
            if prefix_eq.index(pattern_b) > current_index:
                # union will make union on itemsets and intersection on tids
                pattern_ab = pattern_a.union(pattern_b)
                if len(pattern_ab.tids) >= self.minsupp:
                    self.doEclat_beam(pattern_ab,prefix_eq,prefix_eq.index(pattern_b))

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
    t1 = datetime.datetime.now()
    my_eclat_beam = Eclat_beam(2000)
    my_eclat_beam.createDb('mushroom.txt')
    initial_prefix_eq = my_eclat_beam.cleanDb()

    print len(initial_prefix_eq)

    for items in initial_prefix_eq:
        my_eclat_beam.doEclat_beam(items,initial_prefix_eq,initial_prefix_eq.index(items))
    ############## Print the result
    t2 = datetime.datetime.now()
    print t2 - t1
    print len(my_eclat_beam.frequents)
    # for items in my_eclat_beam.frequents:
    #     print(items.itemset)
    #     print(items.tids)

if __name__ == "__main__":
    main()



