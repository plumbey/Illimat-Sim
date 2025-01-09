import random

class Card:
    def __init__(self, rank, suit) -> None:
        self.rank = rank
        self.suit = suit

class Field:
    def __init__(self, season, lum="down") -> None:
        self.season = season
        self.luminary = lum

class Player:
    def __init__(self, hand, score=0) -> None:
        self.hand = hand
        self.score = score
        self.harvest_pile = []
        self.luminaries = []
        self.tokens = []
        self.fools = []
    # TODO Like everything

class Game:
    seasons = ['summer', 'spring', 'winter', 'autumn']
    cards = []
    ranks = [i for i in range(2,14)]
    suits = [
            'summer',
            'winter',
            'spring',
            'autumn',
            'stars'
            ]
    for suit in suits:
        for rank in ranks:
            cards.append(Card(rank, suit))
        cards.append(Card("F", suit))

    def __init__(self, players):
        self.players = players

    def draw(self, hand, num_cards) -> None:
        for _ in range(num_cards):
            hand += self.cards.pop

    def count_score(self, players, type="bumpercrop") -> int:
        # Returns the index of the player with the most amount of cards of type type
        # Returns -1 if player not found
        def season_count(type):
            season_cards = [0] * len(players)
            for i in range(len(players)):
                for card in players[i].harvest_pile:
                    if card.suit == type:
                        season_cards[i] += 1
            return season_cards

        max = 0
        highest_player = -1 
        match type:
            case "bumpercrop":
                for i in range(len(players)):
                    if players[i].harvest_pile > max:
                        max = players[i].harvest_pile
                        highest_player = i
                    if players[i].harvest_pile == max:
                        if len(players[i].luminaries) > len(players[highest_player].luminaries):
                            highest_player = i
            case "frostbitten":
                winters = season_count('winter')
                for i in range(len(winters)):
                    if winters[i] > max:
                        max = winters[i]
                        highest_player = i
                    if winters[i] == max:
                        if len(players[i].luminaries) < len(players[highest_player].luminaries):
                            highest_player = i
            case "sunkissed":
                summers = season_count('summer')
                for i in range(len(summers)):
                    if summers[i] > max:
                        max = summers[i]
                        highest_player = i
                    if summers[i] == max:
                        if len(players[i].luminaries) > len(players[highest_player].luminaries):
                            highest_player = i
            case "score":
                for i in range(len(players)):
                    if players[i].score >= 17 and players[i].score > max:
                        max = 0
                        highest_player = i 
                    if players[i].score >= 17 and players[i].score == max:
                        if len(players[i].luminaries) > len(players[highest_player].luminaries):
                            highest_player = i
                        if len(players[i].tokens) > len(players[highest_player].tokens):
                            highest_player = i
                        if len(players[i].fools) > len(players[highest_player].fools):
                            highest_player = i
        return highest_player

    def next_round(self) -> bool:
        # Reset the board
        for suit in self.suits:
            for rank in self.ranks:
                self.cards.append(Card(rank, suit))
            self.cards.append(Card("F", suit))
        self.fields = []
        for season in self.seasons:
            self.fields.append(Field(season))
        self.points = self.points or [0 * self.players]
        self.tokens = len(self.players)

        random.shuffle(self.cards)
        # Deal cards
        for i in range(len(self.players)):
            if i == 1:
                self.draw(self.players[i].hand, 3)
            else:
                self.draw(self.players[i].hand, 4)

        ended = False
        lums_cleared = False
        false_amt = 0
        while not ended:
            # Clear luminaries when there are 3 or less cards in the draw pile
            if len(self.cards) <= 3 and not lums_cleared:
                for field in self.fields:
                    if field.luminary != "down":
                        field.luminary = None
                lums_cleared = True

            # Mark round as ended if all players are unable to play
            for player in self.players:
                false_amt = false_amt if player.turn(self.fields) else false_amt + 1
            if false_amt == len(self.players):
                ended = True 
        # Subtract 2 for person with highest winters 
        fb_index = self.count_score(self.players, 'frostbitten')
        self.players[fb_index].score = 1 if self.players[fb_index].score <= 3 else self.players[fb_index].score - 2
        # Bumpercrop
        self.players[self.count_score(self.players)].score += 4
        # Sunkissed
        self.players[self.count_score(self.players, 'sunkissed')].score += 2
        # Others
        scores = [0] * len(self.players)
        for i in range(len(self.players)):
            self.players[i].score += len(self.players[i].fools)
            self.players[i].score += len(self.players[i].luminaries)
            self.players[i].score += len(self.players[i].tokens)
            scores[i] = self.players[i].score
        end_score = self.count_score(self.players, 'score')
        if end_score != -1:
            self.players[end_score].win_count += 1
            return True
        return False
