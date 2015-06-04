import copy
import random

from utils import parse_json


class Card(object):
    fields = (
        'title',
        'type',
        'type_code',
        'subtype',
        'subtype_code',
        'text',
        'baselink',
        'faction',
        'faction_code',
        'faction_letter',
        'flavor',
        'illustrator',
        'influencelimit',
        'minimumdecksize',
        'setname',
        'set_code',
        'side',
        'side_code',
        'uniqueness',
        'limited',
        'cyclenumber',
    )

    class UnrecognizedFormat(Exception):
        """Raised when an unrecognized format is passed in as a card."""
        pass

    def __init__(self, card):
        if isinstance(card, Card):
            self = copy.deepcopy(card)
            return

        try:
            card = parse_json(card) or card
        except ValueError:
            raise Card.UnrecognizedFormat(
                'Could not parse {} as a json.'.format(card)
            )

        if not isinstance(card, dict):
            raise Card.UnrecognizedFormat(
                ('Expecting a json string or a serialized json representing'
                 ' a card. Got {}'.format(type(card)))
            )
        # TODO: set these fields as read-only
        for field in self.fields:
            setattr(self, field, card.get(field, None))


class CardContainer(object):
    class UnrecognizedFormat(Exception):
        """Raised when an unrecognized format is passed in as a card container."""
        pass

    def __init__(self, cards=None):
        if isinstance(cards, CardContainer):
            self.frozen_cards = cards.frozen_cards
            return

        self.frozen_cards = []

        try:
            cards = parse_json(cards) or cards
        except ValueError:
            raise CardContainer.UnrecognizedFormat(
                'Could not parse {} as a json.'.format(cards)
            )

        if cards and hasattr(cards, '__iter__'):
            for card in cards:
                try:
                    card = Card(card)
                except Card.UnrecognizedFormat:
                    raise
                self.frozen_cards.append(card)
        self.cards = copy.deepcopy(self.frozen_cards)

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def choice(self, num=1):
        """
        Randomly draws N cards from the card container. This reduces the
        size of the container by the number of cards drawn.
        """
        draws = random.sample(self.cards, num)
        for draw in draws:
            self.cards.remove(draw)
        return draws

    def shuffle(self):
        random.shuffle(self.cards)
