import unittest

import monopoly

class MonopolyTests(unittest.TestCase):

    def testPlayerInitialCapital(self):
        player = monopoly.Player()
        self.assertEqual(player.capital, 1500)

    def testDiceRoll(self):
        TRIALS = 1000
        max_roll = max(sum(monopoly.dice_roll()) for _ in range(TRIALS))
        self.assertEqual(max_roll, 12)
        min_roll = min(sum(monopoly.dice_roll()) for _ in range(TRIALS))
        self.assertEqual(min_roll, 0)

    def testPlayerStartsInSquareZero(self):
        player = monopoly.Player()
        self.assertEqual(player.square, 0)

    def testPlayerAdvance(self):
        player = monopoly.Player()
        player.square = 0
        player.capital = 0
        player.advance(10)  # jail just visiting
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 0)

    def testPlayerAdvancePassGo(self):
        player = monopoly.Player()
        player.square = 35
        player.capital = 0
        player.advance(15)  # jail just visiting
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 200)

    def testIsDouble(self):
        roll = (6, 6)
        self.assertTrue(monopoly.is_double(roll))
        roll = (4, 6)
        self.assertFalse(monopoly.is_double(roll))

    def testDontStartInJail(self):
        player = monopoly.Player()
        self.assertFalse(player.in_jail)

    @unittest.mock.patch('monopoly.dice_roll')
    def testRollNormalDontRollAgain(self, mock_roll):
        mock_roll.side_effect = [(5, 3), (3, 5), (2, 4)]
        player = monopoly.Player()
        player.square = 0
        player.take_turn()
        self.assertEqual(player.square, 8)
        self.assertFalse(player.in_jail)

    @unittest.mock.patch('monopoly.dice_roll')
    def testRollDoubleOnceRollAgain(self, mock_roll):
        mock_roll.side_effect = [(5, 5), (3, 5), (2, 4)]
        player = monopoly.Player()
        player.square = 0
        player.take_turn()
        self.assertEqual(player.square, 18)
        self.assertFalse(player.in_jail)

    @unittest.mock.patch('monopoly.dice_roll')
    def testRollDoubleTwiceRollAgain(self, mock_roll):
        mock_roll.side_effect = [(5, 5), (5, 5), (2, 4)]
        player = monopoly.Player()
        player.square = 0
        player.take_turn()
        self.assertEqual(player.square, 26)
        self.assertFalse(player.in_jail)

    @unittest.mock.patch('monopoly.dice_roll')
    def testRollDoubleThreeTimesGoToJail(self, mock_roll):
        mock_roll.side_effect = [(5, 5), (5, 5), (2, 2)]
        player = monopoly.Player()
        player.square = 0
        player.take_turn()
        self.assertEqual(player.square, 10)
        self.assertTrue(player.in_jail)

    def testLandOnGoToJail(self):
        player = monopoly.Player()
        player.capital = 0
        player.square = 25
        player.advance(5)
        self.assertEqual(player.square, 10)
        self.assertTrue(player.in_jail)

    def testDaysInJailWorks(self):
        player = monopoly.Player()
        with self.assertRaises(ValueError):
            player.in_jail = True
        player.in_jail = False
        self.assertEqual(player.days_in_jail, 0)
        player.days_in_jail = 2
        self.assertTrue(player.in_jail)
        player.in_jail = False
        self.assertFalse(player.in_jail)
        self.assertEqual(player.days_in_jail, 0)

    @unittest.mock.patch('monopoly.dice_roll', autospec=True)
    def testGetOutOfJailOnFirstDouble(self, mock_roll):
        mock_roll.side_effect = [(5, 5), (3, 2), (6, 4)]
        player = monopoly.Player()
        player.capital = 100
        player.square = 10
        player.days_in_jail = 1
        player.take_turn()
        # Note that you don't roll again after getting out of jail
        self.assertEqual(player.square, 20)  # free parking
        self.assertEqual(player.capital, 100)
        self.assertFalse(player.in_jail)

    @unittest.mock.patch('monopoly.dice_roll', autospec=True)
    def testGetOutOfJailOnSecondDouble(self, mock_roll):
        mock_roll.side_effect = [(2, 5), (5, 5), (6, 4)]
        player = monopoly.Player()
        player.capital = 100
        player.square = 10
        player.days_in_jail = 1
        player.take_turn()
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 100)
        self.assertEqual(player.days_in_jail, 2)
        player.take_turn()
        # Note that you don't roll again after getting out of jail
        self.assertEqual(player.square, 20)  # free parking
        self.assertEqual(player.capital, 100)

    @unittest.mock.patch('monopoly.dice_roll', autospec=True)
    def testGetOutOfJailOnThirdDouble(self, mock_roll):
        mock_roll.side_effect = [(2, 5), (4, 5), (5, 5)]
        player = monopoly.Player()
        player.capital = 100
        player.square = 10
        player.days_in_jail = 1
        player.take_turn()
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 100)
        self.assertEqual(player.days_in_jail, 2)
        player.take_turn()
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 100)
        self.assertEqual(player.days_in_jail, 3)
        player.take_turn()
        # Note that you don't roll again after getting out of jail
        self.assertEqual(player.square, 20)  # free parking
        self.assertEqual(player.capital, 100)

    @unittest.mock.patch('monopoly.dice_roll', autospec=True)
    def testStayInJailIfNoDoubleThenPay50AfterThird(self, mock_roll):
        mock_roll.side_effect = [(5, 3), (3, 2), (6, 4)]
        player = monopoly.Player()
        player.capital = 100
        player.square = 10
        player.days_in_jail = 1
        player.take_turn()
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 100)
        self.assertEqual(player.days_in_jail, 2)
        player.take_turn()
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 100)
        self.assertEqual(player.days_in_jail, 3)
        player.take_turn()
        self.assertFalse(player.in_jail)
        self.assertEqual(player.square, 20)  # free parking
        self.assertEqual(player.capital, 50)

    @unittest.mock.patch('monopoly.take_a_chance', autospec=True)
    def testEachOfTheChanceSquares(self, mock_chance):
        player = monopoly.Player()
        player.square = 0
        player.advance(7)
        mock_chance.assert_called_once_with()
        mock_chance.reset_mock()
        player = monopoly.Player()
        player.square = 0
        player.advance(22)
        mock_chance.assert_called_once_with()
        mock_chance.reset_mock()
        player = monopoly.Player()
        player.square = 0
        player.advance(36)
        mock_chance.assert_called_once_with()

    @unittest.mock.patch('monopoly.take_a_chest', autospec=True)
    def testEachOfTheCommunityChestSquares(self, mock_chest):
        player = monopoly.Player()
        player.square = 0
        player.advance(2)
        mock_chest.assert_called_once_with()
        mock_chest.reset_mock()
        player.square = 0
        player.advance(17)
        mock_chest.assert_called_once_with()
        mock_chest.reset_mock()
        player.square = 0
        player.advance(33)
        mock_chest.assert_called_once_with()

    def testAdvanceToWithGo(self):
        player = monopoly.Player()
        player.capital = 200
        player.square = 38
        player.advance_to(0)
        self.assertEqual(player.capital, 400)
        player.advance_to(2)
        self.assertEqual(player.capital, 400)
        player.advance_to(1)
        self.assertEqual(player.capital, 600)

    def testGoToGo(self):
        player = monopoly.Player()
        player.capital = 200
        player.square = 38
        monopoly.go_to_go(player)
        self.assertEqual(player.capital, 400)
        self.assertEqual(player.square, 0)
        monopoly.go_to_go(player)
        self.assertEqual(player.capital, 600)
        self.assertEqual(player.square, 0)

    def testIncreaseCapital(self):
        player = monopoly.Player()
        player.capital = 200
        monopoly.increase_capital(player, 40)
        self.assertEqual(player.capital, 240)

    def testGoDirectlyToJail(self):
        player = monopoly.Player()
        player.capital = 200
        player.square = 35
        monopoly.go_to_jail(player)
        self.assertEqual(player.square, 10)
        self.assertEqual(player.capital, 200)
        self.assertEqual(player.days_in_jail, 1)

    def testGoBack(self):
        player = monopoly.Player()
        player.capital = 200
        player.square = 2
        monopoly.go_back(player, 3)
        self.assertEqual(player.square, 39)
        self.assertEqual(player.capital, 200)
        monopoly.go_back(player, 3)
        self.assertEqual(player.square, 36)
        self.assertEqual(player.capital, 200)

    def testNearestUtility(self):
        self.assertEqual(monopoly.nearest_utility(10), 12)
        self.assertEqual(monopoly.nearest_utility(12), 12)
        self.assertEqual(monopoly.nearest_utility(13), 28)
        self.assertEqual(monopoly.nearest_utility(29), 12)


if __name__ == "__main__":
    unittest.main()
