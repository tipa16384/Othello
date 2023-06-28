let computerPlayer = null;
let computerStrategy = null;
let whitePlayer = null;

let strategyList = [{ id: "human", strategy: chooseHumanMove, name: "manually" },
{ id: "random", strategy: chooseRandomMove, name: "randomly" },
{ id: "greedy", strategy: chooseGreedyMove, name: "greedily" },
{ id: "mcts", strategy: choose_mcts, name: "using MCTS" },
{ id: "mobility", strategy: chooseMobility, name: "using mobility" }]
let playerList = [{ id: "human", name: "You", isHuman: true, eloRating: 1000 },
{ id: "random", name: "Randy", isHuman: false, eloRating: 1000 },
{ id: "greedy", name: "Dietrich", isHuman: false, eloRating: 1000 },
{ id: "mcts", name: "Monita", isHuman: false, eloRating: 1000 },
{ id: "mobility", name: "Mabel", isHuman: false, eloRating: 1000 }]

function write_player_list_to_cookies() {
    var playerListString = JSON.stringify(playerList);
    document.cookie = "playerList=" + playerListString;
}

function read_player_list_from_cookies() {
    var playerListString = document.cookie.replace(/(?:(?:^|.*;\s*)playerList\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    if (playerListString) {
        let tempPlayerList = JSON.parse(playerListString);

        // set the eloRating in playerList to the one in tempPlayerList
        for (var i = 0; i < playerList.length; i++) {
            for (var j = 0; j < tempPlayerList.length; j++) {
                if (playerList[i].id == tempPlayerList[j].id) {
                    playerList[i].eloRating = tempPlayerList[j].eloRating;
                }
            }
        }
    }
}

function clone_board_state(boardState) {
    var bs = new BoardState(boardState.mask, boardState.board, boardState.isBlackTurn);
    bs.game_over = boardState.game_over;
    return bs;
}

function new_game() {
    read_player_list_from_cookies();
    write_player_list_to_cookies();

    var startingMask = (0b11n << 27n) | (0b11n << 35n); // Starting mask
    var startingBoard = (0b10n << 27n) | (0b01n << 35n); // Starting board
    var isBlackTurn = true; // Starting turn indicator

    // choose strategy randomly from strategyList
    let strategy = strategyList[Math.floor(Math.random() * strategyList.length)];

    // choose a player from the players in playerList where isHuman is false
    whitePlayer = playerList[Math.floor(Math.random() * playerList.length)];
    while (whitePlayer.isHuman) {
        whitePlayer = playerList[Math.floor(Math.random() * playerList.length)];
    }

    whitePlayer = playerList[3];

    // choose strategy from strategyList with same ID as whitePlayer
    for (var i = 0; i < strategyList.length; i++) {
        if (strategyList[i].id == whitePlayer.id) {
            strategy = strategyList[i];
            break;
        }
    }

    computerStrategy = strategy.name;
    computerPlayer = strategy.strategy;
    rootNode = null;

    return new BoardState(startingMask, startingBoard, isBlackTurn);
}

var boardState = new_game();

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function game_loop() {
    boardState = new_game();

    var turnIndicator = document.getElementById("turn_indicator");

    while (!boardState.game_over) {
        // see if any legal moves
        if (getLegalMoves(boardState).length === 0) {
            console.log("No legal moves for " + (boardState.isBlackTurn ? "black" : "white") + " player, skipping turn.");
            boardState.isBlackTurn = !boardState.isBlackTurn;
            // any legal moves for other player?
            if (getLegalMoves(boardState).length === 0) {
                console.log("No legal moves for " + (boardState.isBlackTurn ? "black" : "white") + " player, game over.");
                boardState.game_over = true;
                renderBoard(boardState);
                break;
            }
        }

        if (boardState.isBlackTurn) {
            renderBoard(boardState);
            turnIndicator.textContent = "Black to move";
            // pause until boardState.isBlackTurn is false
            while (boardState.isBlackTurn) {
                await(sleep(100));
            }
        } else {
            turnIndicator.textContent = "White to move";
            renderBoard(boardState);
            await(sleep(100));
            move = computerPlayer(boardState);
            if (move) {
                make_move(boardState, move);
            }
        }
    }

    turnIndicator.textContent = "Game over!\n" + win_text(boardState);
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

function chooseHumanMove(boardState) {
    const legalMoves = getLegalMoves(boardState);
}

function addMoveListeners() {
    const legalMoves = document.querySelectorAll('.legal-move');

    legalMoves.forEach(move => {
        move.addEventListener('click', function () {
            const position = parseInt(move.id.split('_')[1]);
            make_move(boardState, position);
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

    // set #computer_player to the name of the computer player
    document.getElementById("computer_player").textContent = whitePlayer.name;

    removePieceSpaces();

    var moves = getLegalMoves(boardState);

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

    if (boardState.isBlackTurn) {
        addMoveListeners();
    }
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

        reversiBoard.appendChild(space);
    }

    game_loop();
});
