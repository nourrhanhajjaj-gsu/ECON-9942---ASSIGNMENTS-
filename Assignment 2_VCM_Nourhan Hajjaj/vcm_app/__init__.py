from tokenize import group

from otree.api import *


doc = """
VCM PUBLIC GOOD GAME - ASSIGNMENT
"""


class C(BaseConstants):
    NAME_IN_URL = 'vcm_app'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10 #play 5 rounds with mpcr 1 and 5 rounds with mpcr 2
    ENDOWMENT = cu(10)
    MPCR_1 = 0.4
    MPCR_2 = 0.7

class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    if  subsession.round_number in [1,2,3,4,5]:
        subsession.group_like_round(1) #group is fixed until round 5
        for g in subsession.get_groups():
            g.mpcr = C.MPCR_1            #mpcr is fixed until round 5
    elif subsession.round_number in [6,7,8,9,10]:
        subsession.group_randomly()        #group is rematched starting of round 6
        for g in subsession.get_groups():
            g.mpcr = C.MPCR_2               #mpcr changes starting of round 6

class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    mpcr = models.FloatField()


class Player(BasePlayer):
    player_contribution = models.CurrencyField(
        min=0, max=C.ENDOWMENT,
        label = "please add below how much you will contribute to the group project",
    )

## FUNCTIONS

def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.player_contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = group.total_contribution * group.mpcr

    for p in players:
        p.payoff = (C.ENDOWMENT - p.player_contribution) + group.individual_share







# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Contribution(Page):
    form_model = 'player'
    form_fields = ['player_contribution']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            history=player.in_previous_rounds(),
        )
    @staticmethod
    def js_vars(player: Player):
        return dict(
            endowment=float(C.ENDOWMENT),
        )

class NewInstructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 6


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            rounds_completed=player.in_all_rounds(),
            endowment_kept=C.ENDOWMENT - player.player_contribution,
            accumulated_payoff=sum(
                (p.payoff for p in player.in_previous_rounds()),
                cu(0),) + player.payoff,
            history= player.in_previous_rounds(),
        )

class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            history=player.in_all_rounds(),
            total_payoffs = sum(
                (p.payoff for p in player.in_all_rounds()),
                cu(0),
            ),
        )

page_sequence = [Instructions, NewInstructions, Contribution, ResultsWaitPage, Results, FinalResults]
