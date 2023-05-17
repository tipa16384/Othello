// BoardState prototype
function BoardState(mask, board, isBlackTurn) {
    this.mask = mask;
    this.board = board;
    this.isBlackTurn = isBlackTurn;
    this.game_over = false;
}

function new_game() {
    var startingMask = (0b11n << 27n) | (0b11n << 35n); // Starting mask
    var startingBoard = (0b10n << 27n) | (0b01n << 35n); // Starting board
    var isBlackTurn = true; // Starting turn indicator

    return new BoardState(startingMask, startingBoard, isBlackTurn);
}

var boardState = new_game();

function updateTurnIndicator() {
    var turnIndicator = document.getElementById("turn_indicator");

    setInterval(function () {
        if (boardState.game_over) {
            turnIndicator.textContent = "Game over!";
        } else if (boardState.isBlackTurn) {
            turnIndicator.textContent = "Black to move";
        } else {
            turnIndicator.textContent = "White to move";
            chooseRandomMove(boardState);
        }
    }, 1000);
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

function chooseRandomMove(boardState) {
    const legalMoves = getLegalMoves(boardState);

    if (legalMoves.length === 0) {
        console.log("No legal moves available.");
        return;
    }

    const randomIndex = Math.floor(Math.random() * legalMoves.length);
    const chosenMove = legalMoves[randomIndex];

    // what power of 2 is chosenMove?
    const position = Math.log2(parseInt(chosenMove));

    make_move(position + 1);
}

function addMoveListeners() {
    const legalMoves = document.querySelectorAll('.legal-move');

    legalMoves.forEach(move => {
        move.addEventListener('click', function () {
            const position = parseInt(move.id.split('_')[1]);
            make_move(position);
        });
    });
}

function make_move(position) {
    const pointer = 1n << BigInt(position - 1);

    const flips = getFlipsForMove(boardState, BigInt(position - 1));

    if (flips.length > 0) {
        boardState.board ^= flips.reduce((a, b) => a | b);
        boardState.mask |= pointer;
        if (boardState.isBlackTurn) {
            boardState.board |= pointer;
        }
        boardState.isBlackTurn = !boardState.isBlackTurn;

        renderBoard(boardState);
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
            console.log("Clicked space mask:", maskPosition.toString(2));
        });

        reversiBoard.appendChild(space);
    }

    renderBoard(boardState);
    updateTurnIndicator();
});
