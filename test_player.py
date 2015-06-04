from test_helper import TestHelper


class PlayerTests(TestHelper):
    def setUp(self):
        self.player = Player()

    def test_player_starts_with_empty_hand(self):
        self.assertEmpty(self.player.hand)

    def test_player_starts_with_empty_deck(self):
        self.assertEqual(self.player.remaining_cards, 0)

    def test_player_starts_with_0_agenda_points(self):
        self.assertEqual(self.player.agenda_points, 0)

    def test_player_can_score_agenda_points_directly(self):
        self.player.scores(3)
        self.assertEqual(self.player.agenda_points, 3)

        self.player.scores(2)
        self.assertEqual(self.player.agenda_points, 5)

    def test_player_wins_if_agenda_points_gte_7(self):
        self.assertFalse(self.player.is_winning)

        self.player.scores(2)
        self.assertFalse(self.player.is_winning)

        self.player.scores(4)
        self.assertFalse(self.player.is_winning)

        self.player.scores(1)
        self.assertTrue(self.player.is_winning)

        self.player.scores(5)
        self.assertTrue(self.player.is_winning)

    def test_player_starts_with_0_credits(self):
        self.assertEqual(self.player.credits, 0)

    def test_player_can_gain_credits(self):
        self.player.gains(5)
        self.assertEqual(self.player.credits, 5)

        self.player.gains(4)
        self.assertEqual(self.player.credits, 9)

    def test_player_can_lose_credits(self):
        self.player.gains(10)
        self.assertEqual(self.player.credits, 10)

        self.player.loses(4)
        self.assertEqual(self.player.credits, 6)


class CorporationTests(PlayerTests):
    def setUp(self):
        self.player = Corporation()

    def test_corporation_loses_if_can_no_longer_draw_cards(self):
        with self.assertRaises(Corporation.Lost):
            self.player.draw()


class RunnerTests(PlayerTests):
    def setUp(self):
        self.player = Runner()

    def test_runner_does_not_lose_if_can_no_longer_draw_cards(self):
        card = self.player.draw()
        self.assertIsNone(card)

    def test_runner_loses_if_hand_is_empty_and_takes_meat_or_net_damage(self):
        self.assertEmpty(self.player.hand)
        with self.assertRaises(Runner.Lost):
            self.player.take(meat_damage=1)

        with self.assertRaises(Runner.Lost):
            self.player.take(net_damage=1)
