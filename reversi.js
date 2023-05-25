// BoardState prototype
function BoardState(mask, board, isBlackTurn) {
    this.mask = mask;
    this.board = board;
    this.isBlackTurn = isBlackTurn;
    this.game_over = false;
}

function clone_board_state(boardState) {
    var bs = new BoardState(boardState.mask, boardState.board, boardState.isBlackTurn);
    bs.game_over = boardState.game_over;
    return bs;
}

function new_game() {
    var startingMask = (0b11n << 27n) | (0b11n << 35n); // Starting mask
    var startingBoard = (0b10n << 27n) | (0b01n << 35n); // Starting board
    var isBlackTurn = true; // Starting turn indicator

    return new BoardState(startingMask, startingBoard, isBlackTurn);
}

var boardState = new_game();

function updateTurnIndicator(localBoardState) {
    var turnIndicator = document.getElementById("turn_indicator");

    setInterval(function () {
        if (localBoardState.game_over) {
            turnIndicator.textContent = "Game over!\n" + win_text(localBoardState);
        } else if (localBoardState.isBlackTurn) {
            turnIndicator.textContent = "Black to move";
        } else {
            turnIndicator.textContent = "White moving randomly...";
            move = chooseRandomMove(localBoardState);
            if (move) {
                make_move(localBoardState, move);
                renderBoard(localBoardState);
            }
        }
    }, 1000);
}

function win_text(localBoardState) {
    const n = who_won(localBoardState);

    if (n > 0) {
        return "Black Won!";
    } else if (n < 0) {
        return "White Won!";
    } else {
        return "It's a Draw!";
    }
}

function who_won(localBoardState) {
    const totalPieces = countSetBits(localBoardState.mask);
    const blackPieces = countSetBits(localBoardState.board);
    const whitePieces = totalPieces - blackPieces;

    return blackPieces - whitePieces;
}

// Helper function to count the number of set bits in a value
function countSetBits(value) {
    let count = 0n;

    while (value > 0n) {
        count += value & 1n;
        value >>= 1n;
    }

    return count;
}


function removePieceSpaces() {
    var pieceSpaces = document.querySelectorAll(".piece-white, .piece-black");

    for (var i = 0; i < pieceSpaces.length; i++) {
        var space = pieceSpaces[i];
        space.parentNode.removeChild(space);
    }
}

function getLegalMoves(boardState) {
    const legalMoves = [];

    const emptySpaces = ~(boardState.mask);

    for (let i = 0; i < 64; i++) {
        const pointer = 1n << BigInt(i);

        if (emptySpaces & pointer) {
            const flips = getFlipsForMove(boardState, BigInt(i));

            if (flips.length > 0) {
                legalMoves.push(pointer);
            }
        }
    }

    return legalMoves;
}

function getFlipsForMove(boardState, move) {
    const board = boardState.board;
    const mask = boardState.mask;
    const flips = [];
    const directions = [-9n, -8n, -7n, -1n, 1n, 7n, 8n, 9n];

    for (const direction of directions) {
        let current = move;
        let flip = 0n;

        while (true) {
            current += direction;

            if (current < 0n || current >= 64n) {
                break;
            }

            // Check for wrapping around the board edges
            if (
                (direction === -1n && current % 8n === 7n) ||
                (direction === 1n && current % 8n === 0n) ||
                (direction === -9n && current % 8n === 7n) ||
                (direction === -7n && current % 8n === 0n) ||
                (direction === 7n && current % 8n === 7n) ||
                (direction === 9n && current % 8n === 0n)
            ) {
                break;
            }

            var pointer = 1n << current;
            if (!(mask & pointer)) {
                break;
            }

            var playerMask = boardState.isBlackTurn ? pointer : 0n;
            var opponentMask = boardState.isBlackTurn ? 0n : pointer;

            if ((board & pointer) === opponentMask) {
                flip |= pointer;
            } else if ((board & pointer) === playerMask) {
                if (flip) {
                    flips.push(flip);
                }
                break;
            } else {
                break;
            }
        }
    }

    return flips;
}

function chooseRandomMove(localBoardState) {
    const legalMoves = getLegalMoves(localBoardState);

    if (legalMoves.length === 0) {
        return null;
    }

    const randomIndex = Math.floor(Math.random() * legalMoves.length);
    const chosenMove = legalMoves[randomIndex];

    // what power of 2 is chosenMove?
    const position = Math.log2(parseInt(chosenMove));

    return position + 1;
}

function choose_mcts(boardState) {
    // Create a tree node for the current state
    const rootNode = new TreeNode(boardState, null);

    // Perform Monte Carlo Tree Search
    const numSimulations = 1000; // Adjust the number of simulations as needed

    for (let i = 0; i < numSimulations; i++) {
        // Select the best child node using UCT (Upper Confidence Bound for Trees)
        const selectedNode = select(rootNode);

        // return null if no selectedNode
        if (!selectedNode) {
            return null;
        }

        // Expand the selected node by adding a child node
        const expandedNode = expand(selectedNode);

        // Simulate a random playout from the expanded node
        const playoutResult = simulate(expandedNode);

        // Update the tree with the playout result
        backpropagate(expandedNode, playoutResult);
    }

    // Choose the best move based on the tree search results
    const bestMove = getBestMove(rootNode);

    // Extract the position from the best move
    const position = Math.log2(parseInt(bestMove));

    return position + 1;
}

// Helper functions for MCTS steps (select, expand, simulate, backpropagate, getBestMove)

// Tree node class to represent a state in the Monte Carlo Tree Search
class TreeNode {
    constructor(boardState, parent) {
        this.boardState = boardState;
        this.parent = parent;
        this.children = [];
        this.wins = 0;
        this.visits = 0;
        this.untriedMoves = getLegalMoves(boardState);
    }
}

// Select the best child node using the UCT formula
function select(node) {
    const explorationFactor = Math.sqrt(2); // Exploration factor (adjust as needed)

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
    const untriedMoves = getUntriedMoves(node);

    if (untriedMoves.length > 0) {
        const randomIndex = Math.floor(Math.random() * untriedMoves.length);
        const selectedMove = untriedMoves[randomIndex];

        // remove selectedMove from untriedMoves
        untriedMoves.splice(randomIndex, 1);
        
        let newState = clone_board_state(node.boardState);
        make_move(newState, selectedMove);

        const newNode = new TreeNode(newState, node);
        node.children.push(newNode);

        return newNode;
    }

    return null;
}

// Simulate a random playout from the expanded node until the game ends
function simulate(node) {
    // Perform a random playout from the given node until the game ends
    // ...
    // Return the playout result (e.g., +1 for a win, 0 for a draw, -1 for a loss)
    // ...
}

// Update the tree with the playout result by backpropagating the result to ancestors
function backpropagate(node, result) {
    // Update the visit count and win count of the nodes from the given node up to the root
    // ...
}

// Choose the best move based on the tree search results
function getBestMove(node) {
    // Determine the best move based on the highest win rate among child nodes
    // ...
    // Return the best move (board mask) from the selected child node
    // ...
}

function addMoveListeners() {
    const legalMoves = document.querySelectorAll('.legal-move');

    legalMoves.forEach(move => {
        move.addEventListener('click', function () {
            const position = parseInt(move.id.split('_')[1]);
            make_move(boardState, position);
            renderBoard(boardState);
        });
    });
}

function make_move(localBoardState, position) {
    const pointer = 1n << BigInt(position - 1);

    const flips = getFlipsForMove(localBoardState, BigInt(position - 1));

    if (flips.length > 0) {
        localBoardState.board ^= flips.reduce((a, b) => a | b);
        localBoardState.mask |= pointer;
        if (localBoardState.isBlackTurn) {
            localBoardState.board |= pointer;
        }
        localBoardState.isBlackTurn = !localBoardState.isBlackTurn;
    }
}

function renderBoard(boardState) {
    var board = boardState.board;
    var mask = boardState.mask;
    var reversiBoard = document.getElementById("reversi_board");

    removePieceSpaces();

    var moves = getLegalMoves(boardState);

    // if no moves, flip turn
    if (moves.length === 0) {
        boardState.isBlackTurn = !boardState.isBlackTurn;
        moves = getLegalMoves(boardState);
    }

    // if still no moves, game over
    if (moves.length === 0) {
        boardState.game_over = true;
    }

    for (var i = 1; i <= 64; i++) {
        const pointer = 1n << BigInt(i - 1);
        if ((mask & pointer) || moves.includes(pointer)) {
            var space = document.createElement("div");
            space.id = "piece_" + i;
            space.className = "space";

            // Check if the space is a legal move and add highlighting class
            if (moves.includes(pointer)) {
                space.classList.add("legal-move");
                if (boardState.isBlackTurn) {
                    space.classList.add("piece-black");
                } else {
                    space.classList.add("piece-white");
                }
            } else if (board & pointer) {
                space.classList.add("piece-black");
            } else {
                space.classList.add("piece-white");
            }

            // Calculate position based on row and column
            var row = Math.floor((i - 1) / 8);
            var col = (i - 1) % 8;
            space.style.position = "absolute";
            space.style.top = row * 50 + "px";
            space.style.left = col * 50 + "px";

            reversiBoard.appendChild(space);
        }
    }

    addMoveListeners();
}

document.addEventListener("DOMContentLoaded", function () {
    // Generate game board spaces
    var reversiBoard = document.getElementById("reversi_board");
    for (var i = 1; i <= 64; i++) {
        var space = document.createElement("div");
        space.id = "space_" + i;
        space.className = "space";

        // Calculate position based on row and column
        var row = Math.floor((i - 1) / 8);
        var col = (i - 1) % 8;
        space.style.position = "absolute";
        space.style.top = (row * 50) + "px";
        space.style.left = (col * 50) + "px";

        // Add click event listener to non-piece spaces
        space.addEventListener("click", function () {
            var maskPosition = 1n << BigInt(parseInt(this.id.split("_")[1]) - 1);
        });

        reversiBoard.appendChild(space);
    }

    renderBoard(boardState);
    updateTurnIndicator(boardState);
});
