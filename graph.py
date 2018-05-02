from collections import defaultdict
from heapq import *
import os
import re
from pprint import pprint
import sys
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
class graph(object):
	"""docstring for graph"""
	def __init__(self, filename,ispos=False):
		self.graph = defaultdict(list)
		self.pos = defaultdict()
		# self.G = nx.Graph()
		with open(filename) as file:
			p = re.compile("\d+");
			self.vertices = list(file.readline().replace('\n',''))
			self.nedges = int(file.readline())
			self.edges = []
			for i in range(self.nedges):
				u, v, w = (file.readline()).replace('\n','').split(' ')
				weight = int(w)
				self.graph[u].append((weight,u,v))
				self.graph[v].append((weight,v,u))
				self.edges.append((weight,u,v))
			if ispos:
				for i in self.vertices:
					self.pos[i] = tuple(map(int,file.readline().split(' ')))
		# self.G.add_nodes_from(self.vertices)
		# self.G.add_weighted_edges_from(((e[1],e[2],e[0]) for e in self.edges),label='graph')

	def MST(self):
		nodes = self.vertices
		conn = self.graph
		mst = []
		used = set(nodes[0])
		usable_edges = conn[nodes[0]][:]
		heapify( usable_edges )
		while usable_edges:
			cost, n1, n2 = heappop( usable_edges )
			if n2 not in used:
				used.add( n2 )
				mst.append( ( cost, n1, n2 ) )
				for e in conn[ n2 ]:
					if e[ 2 ] not in used:
						heappush( usable_edges, e )
		return mst
	def convert_graph(self,mst):
		graph = defaultdict(list)
		for edge in mst:
			graph[edge[1]].append(edge[2])
			graph[edge[2]].append(edge[1])
		return graph
	def Add(self,List_of_Trees,tree,k):
		cost = self.compute_mst_cost(tree)
		check = False
		for c , t in List_of_Trees:
			if c==cost:
				chk = True
				for e in tree:
					chk = chk and ( e in t or (e[0],e[2],e[1]) in t)
				check = check or chk
		if not check:
			List_of_Trees.append((cost,list(tree)))
		# if len(List_of_Trees)>k:
		# 	List_of_Trees.pop()
		List_of_Trees.sort()
	def Remove(self,List_of_Trees,tree):
		cost = self.compute_mst_cost(list(tree))
		rtree = []
		for c , t in List_of_Trees:
			if c==cost:
				chk = True
				for e in tree:
					chk = chk and ( e in t or (e[0],e[2],e[1]) in t)
				if chk:
					rtree.append((c,t))
		for t in rtree:
			List_of_Trees.remove(t)



	def main(self,k):
		mst= self.MST()
		i = 1
		List_of_Trees = []
		k_MSTs = []
		k_MSTs.append((self.compute_mst_cost(mst), list(mst)))
		List_of_Trees.append((self.compute_mst_cost(mst),list(mst)))
		# for i in range(1,k+1):
		sys.stdout.write("Generating tree : %d   \r" % (i) )
		sys.stdout.flush()
		while len(List_of_Trees)>0:
			self.Remove( List_of_Trees , mst )
			usable = []
			for edge in self.edges:
				if edge not in mst and (edge[0],edge[2],edge[1]) not in mst:
					usable.append(edge)
			for edge in usable:
				mstd = mst + [edge]
				graph = self.convert_graph(mstd)
				visited = [edge[1],edge[2]]
				result = self.find_cycle(graph,visited)
				cycle_edges = self.make_edges(result[-1])
				cycle_edges.sort()
				if i==1:
					edash = self.find_edash_2(cycle_edges,edge)
				else:
					edash = self.find_edash(cycle_edges,edge)
				for e in edash:
					if e in mstd:
						mstdash = [emst for emst in mstd if emst!=e]
					else:
						mstdash = [emst for emst in mstd if (emst[0],emst[2],emst[1])!=e]
					self.Add(List_of_Trees,list(mstdash),k)
					List_of_Trees.sort()
			if (len(List_of_Trees))==0:
				# print("Generating tree : %d   \r" % (i) )
				break
			mst = List_of_Trees[0][1]
			k_MSTs.append((self.compute_mst_cost(mst), list(mst)))
			i = i +1
			sys.stdout.write("Generating tree : %d   \r" % (i) )
			sys.stdout.flush()
		# print(i)
		return k_MSTs

	def find_edash_2(self,edges,edge):
		check_edge = False
		for e in edges:
			check_edge = check_edge or ( e == edge or (e[0],e[2],e[1])==edge)
		if not check_edge:
			return []
		check = False
		edash = []
		c = 0
		for i in range(len(edges)-1,1,-1):
			if edges[i]==edge or edges[i]==(edge[0],edge[2],edge[1]):
				check = True
				c = edges[i-1][0]
		for e in edges:
			if e[0]==c:
				edash.append(e)
		return edash
	def find_edash(self,edges,edge):
		check_edge = False
		for e in edges:
			check_edge = check_edge or ( e == edge or (e[0],e[2],e[1])==edge)
		if not check_edge:
			return []
		check = False
		edash = []
		c = 0
		for e in edges[::-1]:
			if e[0]<edge[0] and not check:
				check = True
				c = e[0]
			if check and c==e[0]:
				edash.append(e)
		return edash


	def compute_mst_cost(self,mst):
		c = 0
		for cost,_,_ in mst:
			c = c + cost
		return c
	def make_edges(self,cycle):
		edges = []
		for i in range(len(cycle)-1):
			u , v = cycle[i] , cycle[i+1]
			for e in self.graph[u]:
				if e[2]==v:
					edges.append(e)
					break
		return edges


	def find_cycle(self,graph,visited,cycles=[]):
		for nnode in graph[visited[-1]]:
			if nnode==visited[0] or nnode not in visited:
				if len(visited)>2 and nnode==visited[0]:
					cycles.append(list(visited)+[nnode])
					return cycles
				elif nnode not in visited:
					visited.append(nnode)
					result = self.find_cycle(graph,visited)
					visited.remove(nnode)
		return cycles

def draw_graph( vertices , edges , mst , cost ,k , pos={}):
	G = nx.Graph()
	G.add_nodes_from(vertices)
	G.add_weighted_edges_from(((e[1],e[2],e[0]) for e in mst))
	mst_edges = list(G.edges())
	G.add_weighted_edges_from(((e[1],e[2],e[0]) for e in edges))
	graph_edges = G.edges()
	color = ['red' if e in mst_edges else 'blue' for e in graph_edges]
	style = ['solid' if e in mst_edges else 'dashed' for e in graph_edges]
	if len(pos)==0:
		pos = nx.spring_layout(G)
	else:
		for vertex in vertices:
			G.node[vertex]['pos'] = pos[vertex]
		pos = nx.get_node_attributes(G,'pos')
		print(pos,type(pos))
	# pos = nx.random_layout(G)
	# print(G.nodes,type(G.nodes()))
	nx.draw_networkx(G,pos,node_color='white',width=3,style=style,node_size=600)
	nx.draw_networkx_edges(G,pos,edge_color=color,style=style)
	labels = nx.get_edge_attributes(G,'weight')
	nx.draw_networkx_edge_labels(G,pos,edge_labels=labels,edge_color=color,style=style)
	ax= plt.gca()
	ax.collections[0].set_edgecolor("#000000")
	# size = fig.get_size_inches()*fig.dpi
	# ax.set_title('(a)', y=-size)
	plt.axis('off')
	plt.title("Tree {} has cost = {}".format(k,cost))
	plt.show()
	return G
if __name__=='__main__':
	try:
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		for i in range(len(files)):
			print(str(i+1)+'. '+files[i])
		filename = int(input('Please enter the input file number : '))
		askpos = -1
		while(askpos!=1 and askpos !=0):
			askpos = int(input('Please input 1 if positions are entered in file or 0 : '))
		if askpos:
			ispos = True
		else:
			ispos = False
		g = graph(files[filename-1],ispos)
		msts = g.main(4)
		total = len(msts)
		print('Total number of spanning trees are %d '%total)
		while True:
			k = int(input('Enter any number between %d and %d : '%(1,total)))
			k = k%total
			print(msts[k-1])
			if ispos:
				G = draw_graph(g.vertices,g.edges,msts[k-1][1],msts[k-1][0],k,g.pos)
			else:
				G = draw_graph(g.vertices,g.edges,msts[k-1][1],msts[k-1][0],k)
			G.clear()
	except Exception as e:
		print(e)