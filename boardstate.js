function BoardState(mask, board, isBlackTurn) {
    this.mask = mask;
    this.board = board;
    this.isBlackTurn = isBlackTurn;
    this.game_over = false;
}

// function returning the hash of a board state
BoardState.prototype.hash = function () {
    return this.mask ^ this.board ^ (this.isBlackTurn ? 1n : 0n);
}
