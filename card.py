# -*- coding: utf-8 -*-
import copy
import random
from itertools import groupby, chain

from utils import JSONParserMixin


class CardBase(JSONParserMixin):
    fields = (
        'code',
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
        'cost',
    )

    class UnrecognizedFormat(Exception):
        """Raised when an invalid format is being passed as initializer."""
        pass

    def __init__(self, card=None, *args, **kwargs):
        super(CardBase, self).__init__(*args, **kwargs)

        if not card:
            self._faux = True
            return

        self._faux = False

        if isinstance(card, CardBase):
            self = copy.deepcopy(card)
            return

        card = self.parsed_json or card
        del self.parsed_json

        if not isinstance(card, dict):
            raise CardBase.UnrecognizedFormat(
                ('Expecting a json string or a serialized json representing'
                 ' a card. Got {}'.format(type(card)))
            )
        # TODO: set these fields as read-only
        for field in self.fields:
            setattr(self, field, card.get(field, None))

    def __unicode__(self):
        return u'{}'.format(self.title)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.title)

    @property
    def faux(self):
        return self._faux

    @property
    def is_identity(self):
        return self.type_code == 'identity'

    @property
    def is_runner(self):
        return self.side_code == 'runner'

    @property
    def is_corp(self):
        return self.side_code == 'corp'

    def costs(self, card):
        """Returns the cost of a card to a given identity card."""
        if not self.cost:
            return 0
        elif not card.is_identity or self.is_identity:
            return 0
        elif self.side_code == card.side_code or self.side_code == 'neutral':
            return 0
        return self.cost

    def __eq__(self, other):
        if not isinstance(other, CardBase):
            return False
        if self.faux and other.faux:
            return True
        return all([self_field == other_field
                    for self_field, other_field in zip(self.fields, other.fields)])


class Card(object):
    class UnrecognizedFormat(Exception):
        """Raised when an unrecognized format is passed in as a card."""
        pass

    def __init__(self, card=None, faceup=False):
        self._faceup = faceup
        if card:
            if isinstance(card, Card):
                self._card = card.card
                return

            self._card = card if isinstance(card, CardBase) else CardBase(card)

    def __unicode__(self):
        return u'{}'.format(self.card.title)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.card.title)

    @property
    def is_faceup(self):
        return self._faceup

    def flip(self):
        self._faceup = ~self._faceup

    def view(self):
        if not self.is_faceup:
            return CardBase()
        return self._card

    @property
    def card(self):
        return self._card

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError(attr)

        for obj in chain([self, self.card], self.__class__.mro(), self.card.__class__.mro()):
            if attr in obj.__dict__:
                result = obj.__dict__[attr]
                if isinstance(result, property):
                    return result.__get__(self, obj.__class__)
                return obj.__dict__[attr]
        raise AttributeError(
            'Neither {} nor {} has attribute {}'.format(self.__class__, self.card.__class__, attr)
        )


class CardContainer(JSONParserMixin):
    def __init__(self, cards=None, *args, **kwargs):
        super(CardContainer, self).__init__(*args, **kwargs)

        if isinstance(cards, CardContainer):
            self.frozen_cards = cards.frozen_cards
            return

        self.frozen_cards = []

        cards = self.parsed_json or cards
        del self.parsed_json

        if cards and hasattr(cards, '__iter__'):
            for card in cards:
                try:
                    card = Card(card)
                except Card.UnrecognizedFormat:
                    raise
                self.frozen_cards.append(card)
        self.cards = copy.deepcopy(self.frozen_cards)
        self.frozen_cards = sorted(self.frozen_cards, key=lambda c: c.title)

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def pretty_print(self):
        """Pretty prints the deck list."""
        grouped = groupby(self.frozen_cards, lambda c: c.title)
        output = u''
        for title, group in grouped:
            output += u'{}x {}\n'.format(len(list(group)), unicode(title))
        return output

    def __unicode__(self):
        return unicode(self.pretty_print())

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, '...' )

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


class Deck(CardContainer):
    class NoIdentityFound(Exception):
        """No Identity found for this deck."""
        pass

    def __init__(self, *args, **kwargs):
        super(Deck, self).__init__(*args, **kwargs)
        self._valid = self.validate()
        self._identity = self.find_identity()
        self._influence_limit = self._identity.influencelimit
        self._side = self._identity.side_code
        self._min_deck_size = self._identity.minimumdecksize

    def __unicode__(self):
        output = 'Identity: {}\n'.format(self.identity)
        output += '-' * (len(output) - 1) + '\n'
        output += super(Deck, self).__unicode__()
        return output

    @property
    def valid(self):
        return self._valid

    @property
    def identity(self):
        return self._identity

    @property
    def influence_limit(self):
        return self._influence_limit

    @property
    def min_deck_size(self):
        return self._min_deck_size

    def find_identity(self):
        for card in self.frozen_cards:
            if card.is_identity:
                return card
        else:
            raise Deck.NoIdentityFound

    def validate(self):
        """Introspect all validate_* methods and run them."""
        valid = True
        for attr_key, attr_value in self.__dict__.iteritems():
            if 'validate_' in attr_key:
                valid &= attr_value()

        return valid

    def validate_deck_size(self):
        return len(self.frozen_cards) >= self.min_deck_size

    def validate_agenda_points(self):
        return True

    def validate_has_only_one_identity(self):
        identities = [card for card in self.frozen_cards if card.is_identity]
        return len(identities) == 1

    def validate_composition(self):
        """Validate deck has only cards from one side."""
        sides = set([card.side_code for card in self.frozen_cards])
        return len(sides) == 1

    def validate_influence(self):
        """Validate influence is within identity's limit."""
        influence_total = sum([card.costs(self.identity)
                               for card in self.frozen_cards])
        return influence_total <= self.influence_limit
