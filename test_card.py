from test_helper import TestHelper
from card import Card, CardContainer
from utils import parse_json


class CardContainerTests(TestHelper):
    def setUp(self):
        self.container = CardContainer()

    def init_all_cards(self):
        self.container = CardContainer('cards.json')

    def test_container_starts_off_empty(self):
        self.assertEmpty(self.container)

    def test_init_container_from_json(self):
        self.init_all_cards()
        cards = parse_json('cards.json')
        self.assertLength(self.container, len(cards))

    def test_init_container_from_other_container(self):
        num_cards = 5
        self.init_all_cards()
        random_cards = self.container.choice(num=num_cards)
        other_container = CardContainer(random_cards)
        self.assertLength(other_container, num_cards)
        self.assertIsInstance(other_container, CardContainer)

    def test_container_iterable(self):
        self.init_all_cards()
        for card in self.container:
            self.assertIsInstance(card, Card)

    def test_choice_from_container(self):
        num_cards = 40
        self.init_all_cards()
        original_size = len(self.container)
        random_cards = self.container.choice(num=num_cards)
        self.assertIsInstance(random_cards, list)
        self.assertLength(random_cards, num_cards)
        self.assertLength(self.container, original_size-num_cards)

    def test_shuffle_reorders_container(self):
        self.init_all_cards()
        card_list = list(self.container)
        self.container.shuffle()
        new_card_list = list(self.container)
        diff = [card != new_card
                for card, new_card in zip(card_list, new_card_list)]
        num_diff = diff.count(True)
        self.assertNotEqual(num_diff, 0) # very very low prob. of being unchanged


class DeckTests(TestHelper):
    def test_validate_incorrect_agenda_points(self):
        self.container = Deck('weyland1.json')
        self.assertFalse(self.container.valid)

    def test_validate_composition(self):
        self.container = Deck('mixed.json')
        self.assertFalse(self.container.validate_composition())
        self.assertFalse(self.container.valid)

    def test_validate_influence_limit(self):
        self.container = Deck('over_influence.json')
        self.assertFalse(self.container.validate_influence())
        self.assertFalse(self.container.valid)
