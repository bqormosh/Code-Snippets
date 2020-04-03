__author__ = 'Bassam Qormosh'
import os, shutil
import numpy
from igraph import *
import datetime

class BinomialTree:

    def __init__(self,edgelist_path,attrib_path,minth):
        self.graph = Graph.Read_Edgelist(edgelist_path,directed=False)
        for v in self.graph.vs:
            v["name"] = str(v.index)
        # make relationship as key = child , value = parent
        self.relationship_map = {}
        self.visited_list = set()
        self.stack=[]
        self.processed = set()
        self.props_map = {}
        self.rejected = 0
        self.evaluated = 0
        ################3
        self.prop_list = []
        self.minth = minth
        file = open(attrib_path, 'rU')
        line_no = 0
        for line in file:
             line = line.rstrip()
             vector = line.split(" ")
             self.props_map[str(line_no)] = vector
             line_no = line_no + 1
        self.props_map_copy = self.props_map.copy()
        #print self.props_map

    def clear_dir(self,dir_path):
        folder = dir_path
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception, e:
                print e


    def andop(self,a_vector,b_vector):
        a_int_vector = [ int(x) for x in a_vector ]
        b_int_vector = [ int(x) for x in b_vector]

        numbers =  numpy.logical_and(a_int_vector,b_int_vector)
        numbers = [ int(x) for x in numbers ]

        return numbers


    def enumerate(self,tree):
        results = []
        current_node_id = 0
        #ng = tree.neighbors(current_node)
        #ng = tree.vs[ng]["label"]
        current_node_lbl = tree.vs[current_node_id]["label"]
        printed_nodes = set()
        level = [current_node_id]
        enum = current_node_lbl
        prefix_levels = [enum]
        while len(level) > 0:
            level_node = level.pop(0)
            #print "level node",level_node
            #print "node to enum is ",tree.vs[level_node]["name"]

            pre_enum = prefix_levels.pop(0)
            ng = tree.neighbors(level_node)
            #print "node to enum neighbors are",tree.vs[ng]["name"]
            printed_nodes.add(level_node)
            if len(ng) > 0:
                for j in ng:
                        if j not in printed_nodes:
                            enum = pre_enum +"-"+str(tree.vs[j]["label"])
                            level.append(j)
                            prefix_levels.append(enum)
                            printed_nodes.add(j)
                            #print enum
                            results.append(enum)
        #print "results is :",results
        return results

    def copyBranch(self,source_id,tree,dest_node,ancestors_list):
        node_neighbors = tree.neighbors(source_id)
        node_neighbors = tree.vs[node_neighbors]["name"]
        #print "node neighbors being copied",node_neighbors
        node_parent = self.relationship_map[source_id]
        ######################## start by the first node

        # check if dest_node is also a copy
        dest_copied=  False
        #if "," in dest_node:
        #    dest_copied=  True

        ######################################################
        # if self.relationship_map.has_key(source_id):
        #     node_parent = self.relationship_map[source_id]
        # elif self.relationship_map.has_key(int(source_id)):
        #     node_parent =
        if node_parent is not None :
            ancestors_list.append(node_parent)

        for n in node_neighbors:
            if n not in ancestors_list:
                #if dest_node == "1166,347":
                #    print "common", self.getprop(tree,dest_node,copied=True)," and ",self.getprop(tree,n,copied=True)
                common_prop = self.andop(self.getprop(tree,dest_node),self.getprop(tree,n,copied=True))
                v_len = sum(j == 1 for j in common_prop)
                if v_len >= self.minth:
                    tree.add_vertex(name=n+","+dest_node,label=(str(n).split(","))[0])
                    tree.add_edge(dest_node,(n+","+dest_node))
                    new_node_id = tree.vs.find(name=(n+","+dest_node))
                    tree.vs[new_node_id.index]["prop"] = common_prop
                    #print (n+","+dest_node),"copied to",dest_node
                    self.relationship_map[(n+","+dest_node)] = dest_node
                    self.processed.add(n+","+dest_node)
                    self.copyBranch(n,tree,(n+","+dest_node),ancestors_list)


        return True

    def getprop(self,tree,node_name,copied=False):
        if copied:
            if ',' in node_name:
                node_name = (node_name.split(","))[0]
            return self.props_map[node_name]
        else:
            vs_names = tree.vs["name"]
            if node_name in vs_names:
                node_obj = tree.vs.find(name=node_name)
                if node_obj is not None and "prop" in node_obj.attribute_names() and tree.vs[node_obj.index]["prop"] is not None:
                    return tree.vs[node_obj.index]["prop"]
                else:
                    if ',' in node_name:
                        node_name = (node_name.split(","))[0]
                    return self.props_map[node_name]

            else:
                if ',' in node_name:
                    node_name = (node_name.split(","))[0]
                return self.props_map[node_name]

    def getSiblings(self,node_id):

        parent = self.relationship_map[node_id]
        siblings = set()
        for k,v in self.relationship_map.iteritems():
            if v == parent and k != node_id:
                siblings.add(k)

        return siblings.intersection(self.processed)

    def createTree(self,root_id,tree_graph):
        #print "creating tree for node",root_id
        while(len(self.visited_list) > 0):
            current_node = self.stack.pop()
            self.visited_list.remove(current_node)
            self.processed.add(current_node)
            #current_neighbors == Adjv
            current_neighbors = self.graph.neighbors(current_node)
            current_neighbors= set(self.graph.vs[current_neighbors]["name"])
            current_neighbors = current_neighbors - self.visited_list-self.processed
            current_neighbors = sorted(current_neighbors)
            ##################################
            # save the relation so you can know where to add the nodes in the tree
            # you do that so you can tell who is the father of current node
            for i in current_neighbors:
                if not self.relationship_map.has_key(i):
                    self.relationship_map[i] = current_node
            ##################################
            self.stack = self.stack+sorted(current_neighbors,reverse=True)
            # add adjacent in reverse to allow depth first search
            self.visited_list = self.visited_list.union(current_neighbors)
            ##############################################################
            # now add the current node to the tree
            if self.relationship_map.has_key(current_node) and  self.relationship_map[current_node] in tree_graph.vs["name"]:
                parent_node = self.relationship_map[current_node]
                #################### check if extending is allowed here
                common_prop = self.andop(self.getprop(tree_graph,current_node),self.getprop(tree_graph,parent_node))
                v_len = sum(j == 1 for j in common_prop)
                if v_len >= self.minth:
                    tree_graph.add_vertex(name=current_node,label=current_node)
                    tree_graph.add_edge(parent_node,current_node)
                    new_node_id = tree_graph.vs.find(name=current_node)
                    tree_graph.vs[new_node_id.index]["prop"] = common_prop
                    # check if it has a siblings to copy
                    sib_list = self.getSiblings(current_node)
                    #print sib_list,"sib_list for",current_node
                    if len(sib_list) > 0:
                        for sib in sib_list:
                            #check propoerties
                            #current_node_id = tree_graph.vs.find(name=current_node)
                            #sib_id = tree_graph.vs.find(name=sib)
                            common_prop = self.andop(self.getprop(tree_graph,current_node),self.getprop(tree_graph,sib,copied=True))
                            v_len = sum(j == 1 for j in common_prop)
                            #######################################################
                            if v_len >= self.minth:
                                tree_graph.add_vertex(name=sib+","+current_node,label=(str(sib).split(","))[0])
                                tree_graph.add_edge(current_node,(sib+","+current_node))
                                new_node_id = tree_graph.vs.find(name=(sib+","+current_node))
                                tree_graph.vs[new_node_id.index]["prop"] = common_prop
                                #print (sib+","+current_node),"copied to",current_node
                                self.relationship_map[(sib+","+current_node)] = current_node
                                self.processed.add(sib+","+current_node)
                                self.copyBranch(sib,tree_graph,(sib+","+current_node),[parent_node])
                else:
                    self.relationship_map.pop(current_node, None)
                    if current_node != root_id:
                        for c in current_neighbors:
                            self.relationship_map.pop(c, None)
                            if c in self.visited_list:
                                self.visited_list.remove(c)
                            if c in self.stack:
                                self.stack.remove(c)
            else:
                if current_node != root_id:
                    for c in current_neighbors:
                        self.relationship_map.pop(c, None)
                        if c in self.visited_list:
                            self.visited_list.remove(c)
                        if c in self.stack:
                            self.stack.remove(c)





        return tree_graph



def main():
    t1 = datetime.datetime.now()
    bt = BinomialTree("HcNetworkN.txt","HcAttrib01-N.txt",4)
    #bt = BinomialTree("edgelist.txt","props",2)
    # clear the output folder to save the output edgelist files in it
    bt.clear_dir("edgelist_binomial/")
    final_results = []
    vcount = bt.graph.vcount()
    i =  0
    file_id = 0
    graph_list = [bt.graph]
    while(len(graph_list) > 0):
        # pop the element from list and assign to bt.graph
        print "processing graph",file_id
        bt.graph = graph_list.pop()
        #print "Graph size ",bt.graph.vcount()
        if bt.graph.vcount() > 1:
            bt.relationship_map = {}
            bt.visited_list = set()
            bt.stack=[]
            bt.processed = set()
            bt.props_map = bt.props_map_copy.copy()
            names_list =  bt.graph.vs["name"]
            i = names_list[0]
            tree_graph= Graph.Full(0,directed=True)
            tree_graph.add_vertex(name=str(i),label=str(i))
            bt.visited_list.add(i)
            bt.stack.append(i)
            tree = bt.createTree(str(i),tree_graph)
            #if i == '25':
                #plot(tree)
            #plot(tree)
            if tree.vcount() > 1:
                #outfile = open('edgelist_binomial/out_edgelist'+str(file_id), 'a')
                rslt = bt.enumerate(tree)
                final_results = final_results + rslt
                file_id = file_id + 1
            bt.graph.delete_vertices(str(i))
            bt_subgraphs = bt.graph.decompose()
            #add them to the list
            graph_list = bt_subgraphs + graph_list


    #tree_graph= Graph.Full(0,directed=True)
    #tree_graph.add_vertex(name=str(0),label=0)
    # visited list and stack will work the same way, I only used stack as list so I can decide what to pop
    # since visited_list is a set which is unoredered
    #bt.visited_list.add("0")
    #bt.stack.append("0")
    #tree = bt.createTree("0",tree_graph)
    #plot(tree)
    #
    #
    # get maxiaml
    t2 = datetime.datetime.now()
    temp_maximal = []
    for c in final_results:
        m = sorted(c.split("-"))
        temp_maximal.append(set(m))
    print temp_maximal

    print "Allcohesive",len(temp_maximal)
    maximal = []
    for m in temp_maximal:
        isMax = True
        for mm in temp_maximal:
            if m.issubset(mm) and m !=mm:
                isMax = False
                break
        if isMax:
            maximal.append(m)
    t3 = datetime.datetime.now()

    print "time to get not maxial is ",t2-t1
    print "time to get maxial is ",t3-t1

    print "Maximal size is :",len(maximal)
    print "Maximal Set is :",maximal
    #print bt.relationship_map
    #print final_results





if __name__ == "__main__":
    main()
