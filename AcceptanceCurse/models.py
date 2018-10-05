from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random
import numpy



author = 'Jacopo Magnani'

doc = """
Matching Game with noisy signals
"""


class Constants(BaseConstants):
    name_in_url = 'game'
    players_per_group = 2
    num_rounds = 3
    game_sequence = [0, 2, 4]
    type_space = [1, 2, 3]
    type_labels = ["X", "Y", "Z"]
    status_space = [0, 1]
    status_labels = ["active", "passive"]
    match_value = [160, 80, 40]
    reservation_value = [100, 75, 25]
    signal_space = [1, 2, 3]
    signal_names = ["red", "yellow", "blue"]
    pL = [0, 1/2, 1/2]
    pM = [0, 1, 0]
    pH = [[0.5, 0.5, 0], [0.625, 0.375, 0], [0.75, 0.25, 0], [0.875, 0.125, 0], [1, 0, 0]]
    game_space = [0, 1, 2, 3, 4]
    game_labels= ["A", "B", "C", "D", "E"]

class Subsession(BaseSubsession):

    game = models.IntegerField()
    game_name = models.StringField()

    def creating_session(self):
        if self.round_number == 1:
            paying_round = random.randint(1, Constants.num_rounds)
            self.session.vars['paying_round'] = paying_round
            self.in_round(2).game = 1
            for t in range(1, Constants.num_rounds+1):
                self.in_round(t).game = Constants.game_sequence[t-1]
                self.in_round(t).game_name = Constants.game_labels[self.in_round(t).game]


class Group(BaseGroup):

    def initialize_group(self):
        # assign types
        for p in self.get_players():
            p.type = random.choice(Constants.type_space)
        # form random pairs, assign status, reassign type=M to active player (p1) and assign choice to passive player (p2)
        id_list = list(range(1, Constants.players_per_group + 1))
        while id_list:
            idx1 = random.randrange(0, len(id_list))
            p1 = id_list.pop(idx1)
            idx2 = random.randrange(0, len(id_list))
            p2 = id_list.pop(idx2)
            for p in self.get_players():
                if p.id_in_group == p1:
                    p.partner_id = p2
                    p.status = Constants.status_space[0]
                    p.status_name = Constants.status_labels[Constants.status_space.index(p.status)]
                    p.type = 2
                elif p.id_in_group == p2:
                    p.partner_id = p1
                    p.status = Constants.status_space[1]
                    p.status_name = Constants.status_labels[p.status]
                    p.choice = 1
        #  generate signals
        for p in self.get_players():
            for q in self.get_players():
                if p.partner_id == q.id_in_group:
                    p.partner_type = q.type
                    if q.type == 1:
                        p.signal = numpy.random.choice(Constants.signal_space, p=Constants.pH[self.subsession.game])
                    elif q.type == 2:
                        p.signal = numpy.random.choice(Constants.signal_space, p=Constants.pM)
                    elif q.type == 3:
                        p.signal = numpy.random.choice(Constants.signal_space, p=Constants.pL)

    def get_outcome(self):
        match_value = Constants.match_value
        reservation_value = Constants.reservation_value
        for p in self.get_players():
            for q in self.get_players():
                if p.partner_id == q.id_in_group:
                    p.partner_choice = q.choice
            p.match = p.choice * p.partner_choice
            p.points = p.match * match_value[p.partner_type - 1] + (1 - p.match) * reservation_value[p.type - 1]
            if self.subsession.round_number == self.session.vars['paying_round']:
                p.payoff = p.points
            else:
                p.payoff = c(0)


class Player(BasePlayer):
    type = models.IntegerField()
    status = models.IntegerField()
    status_name = models.StringField()
    partner_id = models.IntegerField()
    partner_type = models.IntegerField()
    signal = models.IntegerField()
    choice = models.IntegerField(
        choices=[
            [1, 'Yes'],
            [0, 'No'],
        ],
        widget=widgets.RadioSelectHorizontal
    )
    partner_choice = models.IntegerField()
    match = models.IntegerField()
    late = models.IntegerField()
    points = models.IntegerField()