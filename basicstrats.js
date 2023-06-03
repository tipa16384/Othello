/**
 * Chooses a random move from the list of legal moves.
 * @param {BoardState} localBoardState - The current board state.
 * @returns {number|null} - The position (1-64) of the chosen move, or null if no moves are available.
 */
function chooseRandomMove(localBoardState) {
    const legalMoves = getLegalMoves(localBoardState);

    // If no legal moves are available, return null
    if (legalMoves.length === 0) {
        return null;
    }

    // Generate a random index within the legalMoves array
    const randomIndex = Math.floor(Math.random() * legalMoves.length);
    const chosenMove = legalMoves[randomIndex];

    // Calculate the position of the chosen move (power of 2)
    const position = Math.log2(parseInt(chosenMove));

    return position + 1;
}

/**
 * Chooses the move with the most flips.
 * @param {BoardState} localBoardState - The current board state.
 * @returns {number|null} - The position (1-64) of the chosen move, or null if no moves are available.
 */
function chooseGreedyMove(localBoardState) {
    const legalMoves = getLegalMoves(localBoardState);

    // If no legal moves are available, return null
    if (legalMoves.length === 0) {
        return null;
    }

    let bestFlips = 0n;
    let bestMove = null;

    // For each move in legalMoves, call getFlipsForMove and calculate the total number of flips
    for (let i = 0; i < legalMoves.length; i++) {
        const move = Math.log2(parseInt(legalMoves[i]));
        const flips = getFlipsForMove(localBoardState, BigInt(move));

        // Calculate the total number of flips by summing the count of set bits in each flip
        let totalFlips = 0n;
        for (let j = 0; j < flips.length; j++) {
            totalFlips += countSetBits(flips[j]);
        }

        // Update the best move if the current move has more flips
        if (totalFlips > bestFlips) {
            bestFlips = totalFlips;
            bestMove = move;
        }
    }

    return bestMove + 1;
}
