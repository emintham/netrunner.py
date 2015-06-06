from test_helper import TestHelper
from card import CardBase, Card, CardContainer, Deck
from utils import parse_json


class CardTests(TestHelper):
    def setUp(self):
        self.card = Card()

    def test_card_starts_facedown(self):
        self.assertFalse(self.card.is_faceup)

    def test_flip(self):
        self.assertFalse(self.card.is_faceup)
        self.card.flip()
        self.assertTrue(self.card.is_faceup)
        self.card.flip()
        self.assertFalse(self.card.is_faceup)

    def test_view_facedown_card_returns_faux_card(self):
        self.assertFalse(self.card.is_faceup)
        self.assertEqual(self.card.view(), CardBase())


class CardContainerTests(TestHelper):
    def setUp(self):
        self.container = CardContainer()

    def init_all_cards(self):
        self.container = CardContainer(json='all_cards.json')

    def test_container_starts_off_empty(self):
        self.assertEmpty(self.container)

    def test_init_container_from_json(self):
        self.init_all_cards()
        cards = parse_json('all_cards.json')
        self.assertLength(self.container, len(cards))

    def test_init_container_from_other_container(self):
        num_cards = 5
        self.init_all_cards()
        random_cards = self.container.choice(num=num_cards)
        print random_cards
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
    def test_validate_agenda_points(self):
        self.container = Deck(json='missing_agenda.json')
        self.assertFalse(self.container.validate_agenda_points())

        self.container = Deck(json='correct_agenda.json')
        self.assertTrue(self.container.validate_agenda_points())

    def test_validate_composition(self):
        self.container = Deck(json='mixed.json')
        self.assertFalse(self.container.validate_composition())

        self.container = Deck(json='only_weyland.json')
        self.assertTrue(self.container.validate_composition())

    def test_validate_only_one_identity(self):
        self.container = Deck(json='two_identities.json')
        self.assertFalse(self.container.validate_has_only_one_identity())

        self.container = Deck(json='one_identity.json')
        self.assertTrue(self.container.validate_has_only_one_identity())

    def test_validate_influence(self):
        self.container = Deck(json='over_influence.json')
        self.assertFalse(self.container.validate_influence())

        self.container = Deck(json='at_influence.json')
        self.assertTrue(self.container.validate_influence())

        self.container = Deck(json='under_influence.json')
        self.assertTrue(self.container.validate_influence())

    def test_validate_gte_minimum_deck_size(self):
        self.container = Deck(json='under_minimum_deck_size.json')
        self.assertFalse(self.container.validate_deck_size())

        self.container = Deck(json='at_minimum_deck_size.json')
        self.assertTrue(self.container.validate_deck_size())

        self.container = Deck(json='above_minimum_deck_size.json')
        self.assertTrue(self.container.validate_deck_size())
