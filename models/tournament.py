from datetime import datetime

from models.round import Round
from models.player import Player
from models.storage import Model


class Tournament(Model):
    def __init__(
            self,
            name,
            location,
            tournament_players_id,
            time_control,
            description,
            total_round_number=4):
        # super().__init__()
        self.name = name
        self.location = location
        self.begin_date = datetime.now().strftime("%d/%m/%Y")
        self.end_date = None
        self.rounds = []
        self.total_round_number = total_round_number
        self.players_id = tournament_players_id
        # self.players_elo_ranking = []
        self.time_control = time_control
        self.description = description
        self.id = None

    _table = 'tournaments'

    def __repr__(self):
        return repr(
            f"Nom : {self.name} | "
            f"Lieu : {self.location} | "
            f"Date de début : {self.begin_date} | "
            f"Date de fin : {self.end_date} |"
            f"Nombre de Rounds : {self.total_round_number} | "
            f"Contrôle du temps : {self.time_control} | "
            f"Description : {self.description}"
        )

    # def get_tournament_players(self, database_file):
    #     return [Player.get(player_id, database_file) for player_id in self.players_id]

    # def get_players_elo_ranking(self):
    #     return [player.elo_ranking for player in self.get_tournament_players()]

    def sort_players_id_by_rank(self):  # todo à corriger ?
        players = [Player.get(player_id) for player_id in self.players_id]
        players_score = self.players_tournament_score()
        for player in players:
            player.tournament_score = players_score.pop(0)
            print(player.tournament_score)
        input()
        players.sort(key=lambda chess_player: chess_player.elo_ranking, reverse=True)
        players.sort(key=lambda chess_player: chess_player.tournament_score, reverse=True)
        self.players_id = [player.id for player in players]

    def players_tournament_score(self):
        players_score = []
        for player_id in self.players_id:
            score = 0.0
            for chess_round in self.rounds:
                for match in chess_round.matches:
                    if match[0][1] is not None:
                        if player_id == match[0][0]:
                            score += match[0][1]
                        elif player_id == match[1][0]:
                            score += match[1][1]
            players_score.append(score)
        return players_score

    def generate_first_round(self):
        self.rounds.append(Round("Round 1"))
        self.rounds[0].pair_by_elo(self.players_id)

    def generate_following_round(self):
        self.rounds.append(Round(f"Round {len(self.rounds) + 1}"))
        self.rounds[-1].pair_by_score(self.players_id.copy(), self.rounds)

    def end_tournament(self):
        self.end_date = datetime.now().strftime("%d/%m/%Y")

    def serialize(self):
        serialized_rounds = []
        for chess_round in self.rounds:
            serialized_rounds.append(chess_round.serialize())

        serialized_tournament = {
            'name': self.name,
            'location': self.location,
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'rounds': serialized_rounds,
            'total_round_number': self.total_round_number,
            'players_id': self.players_id,
            'time_control': self.time_control,
            'description': self.description
        }
        return serialized_tournament

    @classmethod
    def deserialize(cls, serialized_tournament):
        deserialized_rounds = []
        for chess_round in serialized_tournament['rounds']:
            deserialized_rounds.append(Round.deserialize(chess_round))

        tournament = cls(
            serialized_tournament['name'],
            serialized_tournament['location'],
            serialized_tournament['players_id'],
            serialized_tournament['time_control'],
            serialized_tournament['description'],
            serialized_tournament['total_round_number']
        )
        tournament.begin_date = serialized_tournament['begin_date']
        tournament.end_date = serialized_tournament['end_date']
        tournament.rounds = deserialized_rounds
        return tournament

