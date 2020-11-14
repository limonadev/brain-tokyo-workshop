import numpy as np
import itertools
from .ind import Ind, getLayer, getNodeOrder


def evolvePop(self):
  """ Evolves new population from existing species.
  Wrapper which calls 'recombine' on every species and combines all offspring 
  into a new population. When speciation is not used, the entire population is
  treated as a single species.
  """  
  newPop = []
  for i in range(len(self.species)):
    children, self.innov = self.recombine(self.species[i],\
                           self.innov, self.gen)
    newPop.append(children)
  self.pop = list(itertools.chain.from_iterable(newPop))   

def recombine(self, species, innov, gen):
  """ Creates next generation of child solutions from a species

  Procedure:
    ) Sort all individuals by rank
    ) Eliminate lower percentage of individuals from breeding pool
    ) Pass upper percentage of individuals to child population unchanged
    ) Select parents by tournament selection
    ) Produce new population through crossover and mutation

  Args:
      species - (Species) -
        .members    - [Ind] - parent population
        .nOffspring - (int) - number of children to produce
      innov   - (np_array)  - innovation record
                [5 X nUniqueGenes]
                [0,:] == Innovation Number
                [1,:] == Source
                [2,:] == Destination
                [3,:] == New Node?
                [4,:] == Generation evolved
      gen     - (int) - current generation

  Returns:
      children - [Ind]      - newly created population
      innov   - (np_array)  - updated innovation record

  """
  p = self.p
  nOffspring = int(species.nOffspring)
  pop = species.members
  children = []
 
  # Sort by rank
  pop.sort(key=lambda x: x.rank)

  # Cull  - eliminate worst individuals from breeding pool
  numberToCull = int(np.floor(p['select_cullRatio'] * len(pop)))
  if numberToCull > 0:
    pop[-numberToCull:] = []     

  # Elitism - keep best individuals unchanged
  nElites = int(np.floor(len(pop)*p['select_eliteRatio']))
  for i in range(nElites):
    children.append(pop[i])
    nOffspring -= 1

  # Get parent pairs via tournament selection
  # -- As individuals are sorted by fitness, index comparison is 
  # enough. In the case of ties the first individual wins
  parentA = np.random.randint(len(pop),size=(nOffspring,p['select_tournSize']))
  parentB = np.random.randint(len(pop),size=(nOffspring,p['select_tournSize']))
  parents = np.vstack( (np.min(parentA,1), np.min(parentB,1) ) )
  parents = np.sort(parents,axis=0) # Higher fitness parent first    

  # Breed child population
  for i in range(nOffspring):  
    if np.random.rand() > p['prob_crossover']:
      # Mutation only: take only highest fit parent
      child = Ind(pop[parents[0,i]].conn,\
                  pop[parents[0,i]].node)
    else:
      #Crossover
      cConn,cNode,innov = self.horizontalCrossover(pop[parents[0,i]], pop[parents[1,i]], innov, gen)
      child = Ind(cConn, cNode)
      #child = self.crossover(pop[parents[0,i]], pop[parents[1,i]])
      #child = self.horizontalCrossover(pop[parents[0,i]], pop[parents[1,i]], innov, gen)
      
    #cconn,cnode,cinnov = self.horizontalCrossover(pop[parents[0,i]], pop[parents[1,i]], innov, gen)
    #kappa = Ind(cconn, cnode)

    child, innov = self.topoMutate(child,innov,gen)    

    child.express()
    children.append(child)      

  return children, innov


# -- Canonical NEAT recombination operators ------------------------------ -- #

def crossover(self,parentA, parentB):
  """Combine genes of two individuals to produce new individual

    Procedure:
    ) Inherit all nodes and connections from most fit parent
    ) Identify matching connection genes in parentA and parentB
    ) Replace weights with parentB weights with some probability

    Args:
      parentA  - (Ind) - Fittest parent
        .conns - (np_array) - connection genes
                 [5 X nUniqueGenes]
                 [0,:] == Innovation Number (unique Id)
                 [1,:] == Source Node Id
                 [2,:] == Destination Node Id
                 [3,:] == Weight Value
                 [4,:] == Enabled?             
      parentB - (Ind) - Less fit parent

  Returns:
      child   - (Ind) - newly created individual

  """  
  # Inherit all nodes and connections from most fit parent
  child = Ind(parentA.conn, parentA.node)
  
  # Identify matching connection genes in ParentA and ParentB
  aConn = np.copy(parentA.conn[0,:])
  bConn = np.copy(parentB.conn[0,:])
  matching, IA, IB = np.intersect1d(aConn,bConn,return_indices=True)
  
  # Replace weights with parentB weights with some probability
  bProb = 0.5
  bGenes = np.random.rand(1,len(matching))<bProb
  child.conn[3,IA[bGenes[0]]] = parentB.conn[3,IB[bGenes[0]]]
  
  return child


def horizontalCrossover(self, parentA, parentB, innov, gen):
  #print('Horizontal Crossover')

  base, addition = np.random.permutation([parentA, parentB])

  path = _getPath(addition)

  if len(path) < 2:
    return parentA.conn, parentA.node, innov

  print('Horizontal Crossover')

  nConn = np.shape(base.conn)[1]
  connG = np.copy(base.conn)
  nodeG = np.copy(base.node)

  possibleIndexes = np.where(nodeG[1,:] == 1)[0]
  initialIndex = np.random.choice(possibleIndexes)
  initialNode = nodeG[:,initialIndex]

  prev = initialNode

  for node in path:
    newNodeId = int(max(innov[2,:])+1)
    newNode = np.array([[newNodeId, node[1], node[2]]]).T

    nodeG = np.hstack((nodeG, newNode))

    connNew = np.empty((5,1))
    connNew[0] = innov[0,-1]+1
    connNew[1] = prev[0]
    connNew[2] = newNodeId
    connNew[3] = 1
    connNew[4] = 1 #TODO: change if the original conn was enabled/disabled

    connG = np.c_[connG, connNew]

    newInnov = np.hstack((connNew[0:3].flatten(), -1, gen))
    innov = np.hstack((innov,newInnov[:,None]))

    prev = newNode

  possibleIndexes = np.where(nodeG[1,:] == 2)[0]
  lastIndex = np.random.choice(possibleIndexes)
  lastNode = nodeG[:,lastIndex]

  connNew = np.empty((5,1))
  connNew[0] = innov[0,-1]+1
  connNew[1] = prev[0]
  connNew[2] = lastNode[0]
  connNew[3] = 1
  connNew[4] = 1 #TODO: change if the original conn was enabled/disabled

  connG = np.c_[connG, connNew]

  newInnov = np.hstack((connNew[0:3].flatten(), -1, gen))
  innov = np.hstack((innov,newInnov[:,None]))

  return connG, nodeG, innov

  '''path = []

  nConn = np.shape(parentA.conn)[1]
  connG = np.copy(parentA.conn)
  nodeG = np.copy(parentA.node)

  possibleIndexes = np.where(nodeG[1,:] == 1)[0]
  initialIndex = np.random.choice(possibleIndexes)
  
  initialNode = nodeG[:,initialIndex]

  currentNode = initialNode
  currentOutputConnIndexes = np.where(connG[1,:] == currentNode[0])[0]

  while len(currentOutputConnIndexes) > 0:
    path.append(currentNode)

    nextConnIndex = np.random.choice(currentOutputConnIndexes)
    nextConn = connG[:, nextConnIndex]
    nextNodeId = nextConn[2]

    currentNodeIndex = np.where(nodeG[0,:] == nextNodeId)[0][0]
    currentNode = nodeG[:, currentNodeIndex]

    currentOutputConnIndexes = np.where(connG[1,:] == currentNode[0])[0]

  if len(path) > 1:
    print('Horizontal Crossover')
    print(connG)
    print(nodeG)
    print(path)'''


def _getPath(genome):
  path = []

  nConn = np.shape(genome.conn)[1]
  connG = np.copy(genome.conn)
  nodeG = np.copy(genome.node)

  possibleIndexes = np.where(nodeG[1,:] == 1)[0]
  initialIndex = np.random.choice(possibleIndexes)
  
  initialNode = nodeG[:,initialIndex]

  currentNode = initialNode
  currentOutputConnIndexes = np.where(connG[1,:] == currentNode[0])[0]

  while len(currentOutputConnIndexes) > 0:
    path.append(currentNode)

    nextConnIndex = np.random.choice(currentOutputConnIndexes)
    nextConn = connG[:, nextConnIndex]
    nextNodeId = nextConn[2]

    currentNodeIndex = np.where(nodeG[0,:] == nextNodeId)[0][0]
    currentNode = nodeG[:, currentNodeIndex]

    currentOutputConnIndexes = np.where(connG[1,:] == currentNode[0])[0]
  
  return path[1:]

def verticalCrossover(self, parentA, parentB, innov):
  pass


def mutAddNode(self, connG, nodeG, innov, gen):
  """Add new node to genome

  Args:
    connG    - (np_array) - connection genes
               [5 X nUniqueGenes] 
               [0,:] == Innovation Number (unique Id)
               [1,:] == Source Node Id
               [2,:] == Destination Node Id
               [3,:] == Weight Value
               [4,:] == Enabled?  
    nodeG    - (np_array) - node genes
               [3 X nUniqueGenes]
               [0,:] == Node Id
               [1,:] == Type (1=input, 2=output 3=hidden 4=bias)
               [2,:] == Activation function (as int)
    innov    - (np_array) - innovation record
               [5 X nUniqueGenes]
               [0,:] == Innovation Number
               [1,:] == Source
               [2,:] == Destination
               [3,:] == New Node?
               [4,:] == Generation evolved
    gen      - (int) - current generation

  Returns:
    connG    - (np_array) - updated connection genes
    nodeG    - (np_array) - updated node genes
    innov    - (np_array) - updated innovation record

  """
  p = self.p
  nextInnovNum = innov[0,-1]+1
     
  # Choose connection to split
  connActive = np.where(connG[4,:] == 1)[0]
  if len(connActive) < 1:
    return connG, nodeG, innov # No active connections, nothing to split
  connSplit  = connActive[np.random.randint(len(connActive))]
  
  # Create new node
  newActivation = p['ann_actRange'][np.random.randint(len(p['ann_actRange']))]
  newNodeId = int(max(innov[2,:])+1) # next node id is a running counter
  newNode = np.array([[newNodeId, 3, newActivation]]).T
  
  # Add connections to and from new node
  # -- Effort is taken to minimize disruption from node addition:
  # The weight to the node is set to 1, the weight from is set to the original 
  # weight. With a near linear activation function the change in performance 
  # should be minimal.

  connTo    = connG[:,connSplit].copy()
  connTo[0] = nextInnovNum
  connTo[2] = newNodeId
  connTo[3] = 1 # weight set to 1
    
  connFrom    = connG[:,connSplit].copy()
  connFrom[0] = nextInnovNum + 1
  connFrom[1] = newNodeId
  connFrom[3] = connG[3,connSplit] # weight set previous weight value   
      
  newConns = np.vstack((connTo,connFrom)).T
      
  # Disable original connection
  connG[4,connSplit] = 0
      
  # Record innovations
  newInnov = np.empty((5,2))
  newInnov[:,0] = np.hstack((connTo[0:3], newNodeId, gen))   
  newInnov[:,1] = np.hstack((connFrom[0:3], -1, gen)) 
  innov = np.hstack((innov,newInnov))
  
  # Add new structures to genome
  nodeG = np.hstack((nodeG,newNode))
  connG = np.hstack((connG,newConns))
  
  return connG, nodeG, innov

def mutAddConn(self, connG, nodeG, innov, gen):
  """Add new connection to genome.
  To avoid creating recurrent connections all nodes are first sorted into
  layers, connections are then only created from nodes to nodes of the same or
  later layers.


  Todo: check for preexisting innovations to avoid duplicates in same gen

  Args:
    connG    - (np_array) - connection genes
               [5 X nUniqueGenes] 
               [0,:] == Innovation Number (unique Id)
               [1,:] == Source Node Id
               [2,:] == Destination Node Id
               [3,:] == Weight Value
               [4,:] == Enabled?  
    nodeG    - (np_array) - node genes
               [3 X nUniqueGenes]
               [0,:] == Node Id
               [1,:] == Type (1=input, 2=output 3=hidden 4=bias)
               [2,:] == Activation function (as int)
    innov    - (np_array) - innovation record
               [5 X nUniqueGenes]
               [0,:] == Innovation Number
               [1,:] == Source
               [2,:] == Destination
               [3,:] == New Node?
               [4,:] == Generation evolved
    gen      - (int) - current generation


  Returns:
    connG    - (np_array) - updated connection genes
    innov    - (np_array) - updated innovation record

  """
  nIns = len(nodeG[0,nodeG[1,:] == 1]) + len(nodeG[0,nodeG[1,:] == 4])
  nOuts = len(nodeG[0,nodeG[1,:] == 2])
  order, wMat = getNodeOrder(nodeG, connG)   # Topological Sort of Network
  hMat = wMat[nIns:-nOuts,nIns:-nOuts]
  hLay = getLayer(hMat)+1

  # To avoid recurrent connections nodes are sorted into layers, and 
  # connections are only allowed from lower to higher layers
  if len(hLay) > 0:
    lastLayer = max(hLay)+1
  else:
    lastLayer = 1
  L = np.r_[np.zeros(nIns), hLay, np.full((nOuts),lastLayer) ]
  nodeKey = np.c_[nodeG[0,order], L] # Assign Layers

  sources = np.random.permutation(len(nodeKey))
  for src in sources:
    srcLayer = nodeKey[src,1]
    dest = np.where(nodeKey[:,1] > srcLayer)[0]
    
    # Finding already existing connections:
    #   take all connection genes with this source (connG[1,:])
    #   take the destination of those genes (connG[2,:])
    #   convert to nodeKey index (gotta be a better way in numpy...)   
    srcIndx = np.where(connG[1,:]==nodeKey[src,0])[0]
    exist = connG[2,srcIndx]
    existKey = []
    for iExist in exist:
      existKey.append(np.where(nodeKey[:,0]==iExist)[0])
    dest = np.setdiff1d(dest,existKey) # Remove existing connections
    
    # Add a random valid connection
    np.random.shuffle(dest)
    if len(dest)>0:  # (if there is one)
      connNew = np.empty((5,1))
      connNew[0] = innov[0,-1]+1 # Increment innovation counter
      connNew[1] = nodeKey[src,0]
      connNew[2] = nodeKey[dest[0],0]
      connNew[3] = 1
      connNew[4] = 1
      connG = np.c_[connG,connNew]

      # Record innovation
      newInnov = np.hstack((connNew[0:3].flatten(), -1, gen))
      innov = np.hstack((innov,newInnov[:,None]))
      break;

  return connG, innov

def mutDelNode(self, connG, nodeG, innov, gen):
  #print('I deleted a node')
  hiddenIndexes = np.where(nodeG[1,:] == 3)[0]

  if len(hiddenIndexes) == 0:
    return connG, nodeG, innov

  indexToDelete = np.random.choice(hiddenIndexes)
  nodeToDelete = nodeG[:,indexToDelete]

  outputConnIndexes = np.where(connG[1,:] == nodeToDelete[0])[0]
  inputConnIndexes = np.where(connG[2,:] == nodeToDelete[0])[0]
  
  updatedNodeG = np.delete(nodeG, indexToDelete, 1)

  connIndexes = np.concatenate((outputConnIndexes, inputConnIndexes))
  updatedConnG = np.delete(connG, connIndexes, 1)
  for sourceIndex in inputConnIndexes:
    sourceNodeId = connG[:,sourceIndex][1]
    #print('SOURCE NODE CONN: ', connG[:,sourceIndex])
    otherDestinies = np.where(updatedConnG[1,:] == sourceNodeId)[0]
    if len(otherDestinies) != 0:
      continue
    for destinyIndex in outputConnIndexes:
      destinyNodeId = connG[:,destinyIndex][2]
      #print('DESTINY NODE CONN: ', connG[:,destinyIndex])
      connNew = np.empty((5,1))
      connNew[0] = innov[0,-1]+1 # Increment innovation counter
      connNew[1] = sourceNodeId
      connNew[2] = destinyNodeId
      connNew[3] = 1
      connNew[4] = 1 if connG[:,sourceIndex][4] == 1 and connG[:,destinyIndex][4] == 1 else 0
      updatedConnG = np.c_[updatedConnG,connNew]

      # Record innovation
      newInnov = np.hstack((connNew[0:3].flatten(), -1, gen))
      innov = np.hstack((innov,newInnov[:,None]))
  
  '''print('HERE ARE THE RESULTS')
  print(updatedConnG)
  print(updatedNodeG)'''
  return updatedConnG, updatedNodeG, innov

# -- 'Single Weight Network' topological mutation ------------------------ -- #

def topoMutate(self,child,innov,gen):
  """Randomly alter topology of individual
  Note: This operator forces precisely ONE topological change 

  Args:
    child    - (Ind) - individual to be mutated
      .conns - (np_array) - connection genes
               [5 X nUniqueGenes] 
               [0,:] == Innovation Number (unique Id)
               [1,:] == Source Node Id
               [2,:] == Destination Node Id
               [3,:] == Weight Value
               [4,:] == Enabled?  
      .nodes - (np_array) - node genes
               [3 X nUniqueGenes]
               [0,:] == Node Id
               [1,:] == Type (1=input, 2=output 3=hidden 4=bias)
               [2,:] == Activation function (as int)
    innov    - (np_array) - innovation record
               [5 X nUniqueGenes]
               [0,:] == Innovation Number
               [1,:] == Source
               [2,:] == Destination
               [3,:] == New Node?
               [4,:] == Generation evolved

  Returns:
      child   - (Ind)      - newly created individual
      innov   - (np_array) - innovation record

  """

  # Readability
  p = self.p  
  nConn = np.shape(child.conn)[1]
  connG = np.copy(child.conn)
  nodeG = np.copy(child.node)

  # Choose topological mutation
  topoRoulette = np.array((p['prob_addConn'], p['prob_addNode'], \
                           p['prob_enable'] , p['prob_mutAct'], \
                           p['prob_delNode']))

  spin = np.random.rand()*np.sum(topoRoulette)
  slot = topoRoulette[0]
  choice = topoRoulette.size
  for i in range(1,topoRoulette.size):
    if spin < slot:
      choice = i
      break
    else:
      slot += topoRoulette[i]

  # Add Connection
  if choice is 1:
    connG, innov = self.mutAddConn(connG, nodeG, innov, gen)  

  # Add Node
  elif choice is 2:
    connG, nodeG, innov = self.mutAddNode(connG, nodeG, innov, gen)

  # Enable Connection
  elif choice is 3:
    disabled = np.where(connG[4,:] == 0)[0]
    if len(disabled) > 0:
      enable = np.random.randint(len(disabled))
      connG[4,disabled[enable]] = 1

  # Mutate Activation
  elif choice is 4:
    start = 1+child.nInput + child.nOutput
    end = nodeG.shape[1]           
    if start != end:
      mutNode = np.random.randint(start,end)
      newActPool = listXor([int(nodeG[2,mutNode])], list(p['ann_actRange']))
      nodeG[2,mutNode] = int(newActPool[np.random.randint(len(newActPool))])

  # Delete Node
  elif choice is 5:
    connG, nodeG, innov = self.mutDelNode(connG, nodeG, innov, gen)

  child.conn = connG
  child.node = nodeG
  child.birth = gen

  return child, innov

# -- Utilties ------------------------------------------------------------ -- #
def listXor(b,c):
  """Returns elements in lists b and c that they don't share"""
  A = [a for a in b+c if (a not in b) or (a not in c)]
  return A
