# A few baseline players for Checkers including a keyboard player
from __future__ import absolute_import, division, print_function

import numpy as np

from checkers.game import Checkers
from checkers.agents import Player
from copy import deepcopy

# A random player
class RandomPlayer(Player):
    """A player that makes random legal moves."""

    def next_move(self, board, last_moved_piece):
        state = (board, self.color, last_moved_piece)
        self.simulator.restore_state(state)
        legal_moves = self.simulator.legal_moves()
        move = self.random.choice(np.asarray(legal_moves, dtype="int,int"))
        return move


# Human keyboard player
def keyboard_player_move(board, last_moved_piece):
    """A player that uses keyboard to select moves."""
    if last_moved_piece is None:
        input_str = input("* move `from_square, to_square`: ")
    else:
        input_str = input("* move `%i, to_square`: " % last_moved_piece)
    from_sq, to_sq = map(int, input_str.strip().split(","))
    return from_sq, to_sq


def play_a_game(
    checkers,
    black_player_move,
    white_player_move,
    max_plies=float("inf"),
    is_show_detail=True,
    black_player=None,
    white_player=None,
):
    # Play a quick game
    players = {
        "black": black_player_move,
        "white": white_player_move,
    }
    ply = 0
    tot_moves = 0
    board, turn, last_moved_piece = checkers.save_state()
    moves = checkers.legal_moves()
    winner = None
    killed = None
    while winner is None and ply < max_plies:
        tot_moves += len(moves)
        # The current game state
        if is_show_detail:
            checkers.print_board()
            print(ply, "turn:", turn, "last_moved_piece:", last_moved_piece)
            print("%i legal moves %r" % (len(moves), moves))
        # Select a legal move for the current player
        from_sq, to_sq = players[turn](board, last_moved_piece)
        if is_show_detail:
            print(turn, "moved %i, %i" % (from_sq, to_sq))
        # Update the game
        board, turn, last_moved_piece, moves, winner, num_captured = checkers.move(from_sq, to_sq)
        
        being_captured_penalty = -150
        if hasattr(black_player, "modelName") and turn == "white": # if turn == white then fill black state
            if black_player.modelName == "DeepKILLme":
                rewardToFill = 0
                if num_captured == 1:
                    rewardToFill = 100
                black_player.memory[-1][2] = deepcopy(board) # fill board next (idx 2) step in the latest timestamp
                if black_player.memory[-1][3] is None:
                    black_player.memory[-1][3] = rewardToFill # fill reward (idx 3) in the latest timestamp

        if hasattr(white_player, "modelName") and turn == "black":
            if white_player.modelName == "DeepKILLme":
                rewardToFill = 0
                if num_captured == 1:
                    rewardToFill = 100
                white_player.memory[-1][2] = deepcopy(board) # fill board next (idx 2) step in the latest timestamp
                if white_player.memory[-1][3] is None:
                    white_player.memory[-1][3] = rewardToFill # fill reward (idx 3) in the latest timestamp

        if hasattr(white_player, "modelName") and turn == "white":
            if white_player.modelName == "DeepKILLme":
                if num_captured > 0:
                    white_player.memory[-1][3] = being_captured_penalty # if black capture white, then the latest move of white sucks, so we penalize them
        
        if hasattr(black_player, "modelName") and turn == "black":
            if black_player.modelName == "DeepKILLme":
                if num_captured > 0:
                    black_player.memory[-1][3] = being_captured_penalty # if black capture white, then the latest move of white sucks, so we penalize them
                        
        if is_show_detail and hasattr(white_player, "modelName"):
            if len(white_player.memory): print("whitePlayer Memory", white_player.memory[-1])
            print()
        ply += 1
    if is_show_detail:
        if winner is None:
            print("draw")
        else:
            print("%s player wins" % winner)
        print("total legal moves", tot_moves, "avg branching factor", tot_moves / ply)
    return winner


if __name__ == "__main__":
    ch = Checkers()
    ch.print_empty_board()

    black_random_player = RandomPlayer("black", seed=0)
    white_random_player = RandomPlayer("white", seed=1)
    play_a_game(ch, black_random_player.next_move, white_random_player.next_move)
    # play_a_game(ch, keyboard_player_move, keyboard_player_move)
