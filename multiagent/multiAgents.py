# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
import math

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        #return successorGameState.getScore()

        # given state and action, try to decrease food num and avoid ghost
        if newFood.count() == 0:
            return 0

        # parameters
        GHOST_DANGER_DISTANCE = 4
        GHOST_SCARED_TIME_THRED = 4

        # find the distance to the nearest food
        walls = currentGameState.getWalls()
        distToFood = 0
        visited = []
        frontier = util.Queue()
        frontier.push((newPos, 0))

        distToGhost = []
        ghostPos = []
        ghostCount = len(newGhostStates)
        for ghostState in newGhostStates:
            if ghostState.scaredTimer < GHOST_SCARED_TIME_THRED:
                ghostPos.append(ghostState.getPosition())

        while not frontier.isEmpty():
            pos, level = frontier.pop()
            if pos in visited:
                continue
            visited.append(pos)

            x = pos[0]
            y = pos[1]
            if newFood[x][y] and distToFood == 0:
                distToFood = level
            if pos in ghostPos:
                distToGhost.append(level)
            if distToFood > 0 and (len(distToGhost) == ghostCount or level > GHOST_DANGER_DISTANCE):
                #print "level ", level, ", distFood ", distToFood, ", ghostNum", len(distToGhost)
                break

            if not walls[x + 1][y] and (x + 1, y) not in visited:
                frontier.push(((x + 1, y), level + 1))
            if not walls[x - 1][y] and (x - 1, y) not in visited:
                frontier.push(((x - 1, y), level + 1))
            if not walls[x][y + 1] and (x, y + 1) not in visited:
                frontier.push(((x, y + 1), level + 1))
            if not walls[x][y - 1] and (x, y - 1) not in visited:
                frontier.push(((x, y - 1), level + 1))


        # penalty if inside ghost's range, maze distance instead of manh
        penalty = 0
        #for ghostState in newGhostStates:
        #    if ghostState.scaredTimer < GHOST_SCARED_TIME_THRED:
        #        manDis = manhattanDistance(ghostState.getPosition(), newPos)
        #        if manDis < GHOST_DANGER_DISTANCE:
        #            penalty += math.pow(3, (GHOST_DANGER_DISTANCE - manDis))
        for mazeDist in distToGhost:
            penalty += math.pow(3, (GHOST_DANGER_DISTANCE - mazeDist))

        # last two food issue
        currentFoodCnt = currentGameState.getFood().count()
        if newFood.count() < currentFoodCnt:   # this action will eat a food
            distToFood = 0

        # smaller food count, smaller distance, smaller penalty, the better
        evaluation = -newFood.count() - distToFood * 0.1 - penalty
        #print "Action ", action, ", Evaluation ", evaluation
        return evaluation

        # TODO eat scared ghost
        # TODO corner location issue
        #penaltyForStop = 0
        #if action == Directions.STOP:
        #    penaltyForStop = 10

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()

        # legalActions = gameState.getLegalActions(0)
        # pacmanState = gameState.generateSuccessor(0, legalActions[0])
        if debug: print "Agent Num: ", gameState.getNumAgents()
        if debug: print "DEPTH: ", self.depth
        if debug: print "Evaluation: ", self.evaluationFunction(gameState)

        v, action = self.maxValue(gameState, 0)
        if debug: print v, " ", action
        return action

    def maxValue(self, gameState, curDepth):
        # Termination case 1
        if curDepth == self.depth:                      # Leaf is always max node
            return self.evaluationFunction(gameState), Directions.STOP
        # Termination case 2: pacman don't have legal moves
        legalActions = gameState.getLegalActions(0)
        if debug: print "pacman actions: ", legalActions
        if len(legalActions) == 0:
            return self.minValue(gameState, curDepth, 1), Directions.STOP

        v = float("-inf")
        maxAction = Directions.STOP
        for action in legalActions:
            successorState = gameState.generateSuccessor(0, action)
            sv = self.minValue(successorState, curDepth, 1)         # index 1 for the first ghost
            if debug: print "max: depth ", curDepth, " action ", action, " sv ", sv, " v ", v
            if sv > v:
                v = sv
                maxAction = action
        return v, maxAction

    def minValue(self, gameState, curDepth, ghostId):
        agentNum = gameState.getNumAgents()
        # Termination case 1
        if ghostId == agentNum:
            v, action = self.maxValue(gameState, curDepth + 1)      # increase depth
            return v
        # Termination case 2: ghost doesn't have legal moves, try next ghost
        legalActions = gameState.getLegalActions(ghostId)
        if debug: print "ghost actions: ", legalActions
        if len(legalActions) == 0:
            return self.minValue(gameState, curDepth, ghostId + 1)

        v = float("inf")
        for action in legalActions:
            successorState = gameState.generateSuccessor(ghostId, action)
            sv = self.minValue(successorState, curDepth, ghostId + 1)   # find min for next ghost
            if debug: print "min: depth ", curDepth, " action ", action, " sv ", sv, " v ", v
            if sv < v:
                v = sv
        return v

debug = False


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()

        # ===========================================
        # below implementation is almost the same as MinimaxAgent,
        # only difference is two extra parameters, and value update
        # ===========================================
        # legalActions = gameState.getLegalActions(0)
        # pacmanState = gameState.generateSuccessor(0, legalActions[0])
        if debug: print "Agent Num: ", gameState.getNumAgents()
        if debug: print "DEPTH: ", self.depth
        if debug: print "Evaluation: ", self.evaluationFunction(gameState)

        v, action = self.maxValue(gameState, 0, float("-inf"), float("inf"))
        if debug: print v, " ", action
        return action

    def maxValue(self, gameState, curDepth, alpha, beta):
        # Termination case 1
        if curDepth == self.depth:                      # Leaf is always max node
            return self.evaluationFunction(gameState), Directions.STOP
        # Termination case 2: pacman don't have legal moves
        legalActions = gameState.getLegalActions(0)
        if debug: print "pacman actions: ", legalActions
        if len(legalActions) == 0:
            return self.minValue(gameState, curDepth, 1, alpha, beta), Directions.STOP

        v = float("-inf")
        maxAction = Directions.STOP
        for action in legalActions:
            successorState = gameState.generateSuccessor(0, action)
            sv = self.minValue(successorState, curDepth, 1, alpha, beta)         # index 1 for the first ghost
            if debug: print "max: depth ", curDepth, " action ", action, " sv ", sv, " v ", v
            if sv > v:
                v = sv
                maxAction = action
            # ==alpha-beta pruning==
            if v > beta:
                return v, maxAction
            if v > alpha:
                alpha = v
        return v, maxAction

    def minValue(self, gameState, curDepth, ghostId, alpha, beta):
        agentNum = gameState.getNumAgents()
        # Termination case 1
        if ghostId == agentNum:
            v, action = self.maxValue(gameState, curDepth + 1, alpha, beta)      # increase depth
            return v
        # Termination case 2: ghost doesn't have legal moves, try next ghost
        legalActions = gameState.getLegalActions(ghostId)
        if debug: print "ghost actions: ", legalActions
        if len(legalActions) == 0:
            return self.minValue(gameState, curDepth, ghostId + 1, alpha, beta)

        v = float("inf")
        for action in legalActions:
            successorState = gameState.generateSuccessor(ghostId, action)
            sv = self.minValue(successorState, curDepth, ghostId + 1, alpha, beta)   # find min for next ghost
            if debug: print "min: depth ", curDepth, " action ", action, " sv ", sv, " v ", v
            if sv < v:
                v = sv
            # ==alpha-beta pruning==
            if v < alpha:
                return v
            if v < beta:
                beta = v
        return v

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

