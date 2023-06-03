/**
 * Chooses a move that leaves the opponent with the fewest possible moves on their turn.
 * @param {BoardState} boardState - The current board state.
 * @returns {number|null} - The position (1-64) of the chosen move, or null if no moves are available.
 */
function chooseMobility(boardState) {
    const legalMoves = getLegalMoves(boardState);
  
    // If no legal moves are available, return null
    if (legalMoves.length === 0) {
      return null;
    }
  
    let maxMyMoves = -Infinity;
    let chosenMove = null;
  
    for (const move of legalMoves) {
      // Create a next state by making the move
      const nextState = clone_board_state(boardState);
      const selectedMove = Math.log2(parseInt(move)) + 1;
      make_move(nextState, selectedMove);
  
      const opponentMoves = getLegalMoves(nextState);
  
      if (opponentMoves.length !== 0) {
        for (const omove of opponentMoves) {
          // Create the opponent's next state by making their move
          const oNextState = clone_board_state(nextState);
          const opponentMove = Math.log2(parseInt(omove)) + 1;
          make_move(oNextState, opponentMove);
  
          const myNextMoves = getLegalMoves(oNextState).length;
  
          // Calculate the move ratio: myNextMoves / opponentMoves.length
          const moveRatio = myNextMoves / opponentMoves.length;
  
          if (moveRatio > maxMyMoves) {
            maxMyMoves = moveRatio;
            chosenMove = move;
          }
        }
      }
    }
  
    // If no move is chosen, select a random move from legalMoves
    if (chosenMove === null) {
      chosenMove = legalMoves[Math.floor(Math.random() * legalMoves.length)];
    }
  
    // Find the position of the chosen move
    const position = Math.log2(parseInt(chosenMove)) + 1;
  
    return position;
  }
  
