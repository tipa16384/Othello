// Tree node class to represent a state in the Monte Carlo Tree Search
class TreeNode {
    constructor(boardState, parent, move) {
        this.boardState = boardState;
        this.parent = parent;
        this.children = [];
        this.wins = 0;
        this.visits = 0;
        this.untriedMoves = getLegalMoves(boardState);
        this.move = move;
        this.passed = false;
    }
}

function choose_mcts(boardState) {

    // get current time
    const startTime = Date.now();

    // Create a tree node for the current state
    rootNode = getRootNode(boardState);

    // Perform Monte Carlo Tree Search for five seconds
    while (Date.now() - startTime < 7000) {

        let selectedNode = rootNode;

        while (selectedNode.untriedMoves.length === 0 && selectedNode.children.length > 0) {
            selectedNode = select(selectedNode);
        }

        while (selectedNode.untriedMoves.length > 0) {
            selectedNode = expand(selectedNode);
        }

        // Simulate a random playout from the expanded node
        const playoutResult = who_won(selectedNode.boardState);

        // Update the tree with the playout result
        backpropagate(selectedNode, playoutResult);
    }

    // Choose the best move based on the tree search results
    return getBestMove(rootNode);
}

// function to get the root node based on the boardState parameter. 
// If rootNode is null, create a new TreeNode with the boardState parameter as the boardState. 
// If it is not null, then do a breadth first search of rootNode to find the board state matching 
// the hash of the parameter
function getRootNode(boardState) {
    if (rootNode !== null) {
        let newHash = boardState.hash();
        // for each grandchild of rootNode, if the hash of the grandchild's boardState matches the hash of the parameter, return the grandchild node
        for (let i = 0; i < rootNode.children.length; i++) {
            for (let j = 0; j < rootNode.children[i].children.length; j++) {
                if (rootNode.children[i].children[j].boardState.hash() === newHash) {
                    return rootNode.children[i].children[j];
                }
            }
        }
    }

    return new TreeNode(boardState, null, null);
}


// Select the best child node using the UCT formula
function select(node) {
    const explorationFactor = 4; // Exploration factor (adjust as needed)

    let selectedChild = null;
    let bestScore = Number.NEGATIVE_INFINITY;

    // Iterate over each child node and calculate their UCT scores
    for (const child of node.children) {
        const exploitation = child.wins / child.visits;
        const exploration = Math.sqrt(Math.log(node.visits) / child.visits);
        const score = exploitation + explorationFactor * exploration;

        if (score > bestScore) {
            bestScore = score;
            selectedChild = child;
        }
    }

    return selectedChild;
}

// Expand the selected node by adding a child node for each legal move
function expand(node) {
    const untriedMoves = node.untriedMoves;

    if (untriedMoves.length > 0) {
        const randomIndex = Math.floor(Math.random() * untriedMoves.length);
        const selectedMove = untriedMoves[randomIndex];

        // remove selectedMove from untriedMoves
        untriedMoves.splice(randomIndex, 1);

        let newState = clone_board_state(node.boardState);

        // let x = the integer of selectedMove
        let x = Math.log2(parseInt(selectedMove));
        make_move(newState, x + 1);

        const newNode = new TreeNode(newState, node, x + 1);
        node.children.push(newNode);

        return newNode;
    }

    return null;
}

// Simulate a random playout from the expanded node until the game ends
function simulate(node) {
    let passes = 0;
    const localBoardState = clone_board_state(node.boardState);

    while (passes < 2) {
        let position = chooseRandomMove(localBoardState);
        if (position === null) {
            passes++;
        } else {
            passes = 0;
            make_move(localBoardState, position);
        }
    }

    return who_won(localBoardState);
}

// Update the tree with the playout result by backpropagating the result to ancestors
function backpropagate(node, result) {
    if (node === null) {
        return;
    }

    let localBoardState = node.boardState;

    ++node.visits;

    if (!localBoardState.isBlackTurn && result > 0) {
        ++node.wins;
    } else if (localBoardState.isBlackTurn && result < 0) {
        ++node.wins;
    }

    backpropagate(node.parent, result);
}

// Choose the best move based on the tree search results
function getBestMove(node) {
    // get max wins from children
    let maxWins = Number.NEGATIVE_INFINITY;
    let bestMove = null;
    let bestNode = null;
    for (const child of node.children) {
        if (child.wins > maxWins) {
            maxWins = child.wins;
            bestMove = child.move;
            bestNode = child;
        }
    }
    console.log("Best move: " + bestMove + " with " + maxWins + " wins out of " + bestNode.visits + " visits");
    return bestMove;
}

