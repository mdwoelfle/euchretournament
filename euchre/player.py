"""
Track information about a given player
"""
from typing import List, Optional, Tuple, Union

from pydantic import BaseModel


# TODO: set up logging


# TODO: Make this a pydantic object? Better serialization!
class Player(object):
    """
    Define class to track each player
    """

    # Initialize the class
    def __init__(
        self,
        name: str,
    ):
        """
        Init the class

        :param name: player name
        """
        # Name the player
        self.name = name

        # TODO: Give the player a unique id number
        self.id = 0

        # Set player's total number of byes as int
        self.n_byes = 0
        # Set opponent scores for each round as list
        self.opponent_scores = []
        # Set player's scores for each round as list
        self.round_scores = []
        # Set table player sat at for each round
        self.tables: List[Union[RoundTable, ByeTable]] = []

    def __repr__(self):
        """
        Set thing that will show up when class is called.
        Should be super detailed
        """
        # Thing to return
        s = ('playercard(\'{:s}\', {:d}, '.format(self.name,
                                                  self.id) +
             'nbyes={:d}, '.format(self.n_byes) +
             'opponents=[[\'' +
             '\'], [\''.join(['\', \''.join([k
                                             if k else 'None'
                                             for k in j])
                              for j in self.opponents]) +
             '\']], ' +
             'opponentRoundScores=[' +
             ', '.join(['{:d}'.format(j)
                        for j in self.opponent_scores]) +
             '], ' +
             'opponentscore={:d}, '.format(self.opponent_total_score()) +
             'partners=[\'' +
             '\', \''.join([j if j else 'None'
                            for j in self.partners]) +
             '\'], ' +
             'roundScores=[' +
             ', '.join(['{:d}'.format(j) for j in self.round_scores]) +
             '], ' +
             'score={:d}, '.format(self.total_score()) +
             'tables=[' + ', '.join(['{:d}'.format(j) if j else 'None'
                                     for j in self.tables]) + ']' +
             ')'
             )

        # Return the thing.
        return s

    def __str__(self):
        """
        Set other thing which should be simpler.
        """
        return f"Player card for {self.name}"

    @property
    def total_score(self):
        """
        Get own total score
        """
        return sum(self.round_scores)

    @property
    def opponent_total_score(self):
        """
        Get opponent total score
        """
        return sum(self.opponent_scores)

    @property
    def n_victories(self):
        """
        Get total number of rounds won
        """
        return sum(
            [
                self.round_scores[round_number] > self.opponent_scores[round_number]
                for round_number in range(len(self.round_scores))
            ]
        )

    @property
    def partners(self):
        return [p.get_player_partner(self) for p in self.tables]

    @property
    def opponents(self):
        return [p.get_player_opponents(self) for p in self.tables]

    def add_score(
        self,
        score: int,
        opponent_score: int,
        round_number: int,
        table: "RoundTable",
    ) -> None:
        """
        Add score for the given (current) round and update total

        :param score: player's score for this round
        :param opponent_score: opponent's score for this round
        :param round_number: round number to update; will add new round
            if round_number is expected next round number; round number
            should be indexed from 1  TODO: for now.
        :param table: Table for this score report
        :return: None
        """

        if round_number > len(self.round_scores) + 1:
            raise IndexError("round_number must not exceed number of known rounds + 1")

        rd_idx = round_number - 1

        # Add score for round to PlayerCard
        try:
            # Add score assuming it updates a previous round
            self.round_scores[rd_idx] = score
            self.opponent_scores[rd_idx] = opponent_score
            self.tables[rd_idx] = table
        except IndexError:
            # Otherwise, add scores for new round
            self.round_scores.append(score)
            self.opponent_scores.append(opponent_score)
            self.tables.append(table)

    def print_all_rounds(self):
        """
        Print round info for all logged rounds
        """
        for round_number in range(len(self.tables)):
            self.print_round(round_number + 1)

    def print_round(self,
                    round_number,
                    ):
        """
        Print info for a given round for this player
        """
        # Create header for round print out
        s = '\n---Round {:d} for {:s}---\n'.format(round_number, self.name)

        # Add details for round print out
        if self.tables[round_number - 1] is None:
            s = s + 'Bye Round'
        else:
            s = (s +
                 '      Table: {:d}\n'.format(self.tables[round_number - 1]) +
                 '    Partner: {:s}\n'.format(self.partners[round_number - 1]) +
                 '  Opponents: {:s}, {:s}\n'.format(
                     self.opponents[round_number - 1][0],
                     self.opponents[round_number - 1][1])
                 )
            # Attempt to get score for round
            try:
                s = (s +
                     'Round Score: {:d}'.format(self.round_scores[round_number - 1])
                     )
            except IndexError:
                s = (s + 'Round Score: Unreported')

        # Print round information for given round
        print
        s


class Partnership(BaseModel):

    players: Tuple[Player, Player]

    def get_partner(self, player: Player):
        if player.id == self.players[0].id:
            return self.players[1]
        elif player.id == self.players[1].id:
            return self.players[0]
        else:
            raise ValueError(f"Player {player} not in this partnership.")

    def contains(self, player: Player):
        return player.id in [p.id for p in self.players]


class ByeTable(object):
    # TODO: How to align this concept with RoundTable

    def __init__(
        self,
        players: Tuple[Player, ...]
    ):
        self.players = players

        # No real table number
        self.number = -1

    @staticmethod
    def get_partner(*args, **kwargs):
        return None

    @staticmethod
    def get_opponents(*args, **kwargs):
        return None, None


class RoundTable(object):

    def __init__(
        self,
        number: int,
        players: Tuple[Partnership, Partnership],
    ):
        """

        :param number:
        :param players:
        """
        self.number = number
        self.players = players
        self.score = (None, None)

    def _ensure_player_at_table(self, player: Player) -> None:
        if not self.is_player_here(player):
            raise ValueError(f"Player {player} not at this table")

    def is_player_here(self, player: Player) -> bool:
        return self.players[0].contains(player) or self.players[1].contains(player)

    def get_player_partner(self, player: Player) -> Player:
        # TODO: make this work
        self._ensure_player_at_table(player)

        if self.players[0].contains(player):
            return self.players[0].get_partner(player)
        else:
            return self.players[1].get_partner(player)

    def get_player_opponents(self, player: Player) -> Partnership:
        self._ensure_player_at_table(player)

        if self.players[0].contains(player):
            return self.players[1]
        else:
            return self.players[0]

    def add_score(self, score: Tuple[int, int], reporting_player: Player) -> None:
        self._ensure_player_at_table(reporting_player)

        if self.players[0].contains(reporting_player):
            self.score = score
        else:
            self.score = (score[1], score[0])

    def get_player_score(self, player: Player) -> Optional[int]:
        self._ensure_player_at_table(player)

        if self.players[0].contains(player):
            return self.score[0]
        else:
            return self.score[1]

    def get_opponent_score(self, player: Player) -> Optional[int]:
        self._ensure_player_at_table(player)

        if self.players[0].contains(player):
            return self.score[1]
        else:
            return self.score[0]
