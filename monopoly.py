import random

PAY_TO_ESCAPE_JAIL = False
PLAYERS = 3
HOUSES = 0
HOTELS = 0


class Player(object):

    @property
    def in_jail(self):
        return bool(self.days_in_jail)

    @in_jail.setter
    def in_jail(self, jail_bool):
        if jail_bool is False:
            self.days_in_jail = 0
        else:
            raise ValueError('Do not set in_jail; set days_in_jail')

    def __init__(self):
        self.capital = 1500
        self.square = 0
        self.days_in_jail = 0

    def advance_to(self, square):
        return advance_to(self, square)

    def advance(self, squares):
        new_square = (self.square + squares) % 40
        self.advance_to(new_square)

    def take_turn(self):
        roll = dice_roll()
        if self.in_jail:
            # TODO - make choice on whether to buy.
            if PAY_TO_ESCAPE_JAIL:
                self.capital -= 50
                self.in_jail = False
            elif not is_double(roll):
                self.days_in_jail += 1
                if self.days_in_jail > 3:
                    self.capital -= 50
                    self.in_jail = False
                    self.advance(sum(roll))
                return
            else:
                self.in_jail = False
                self.advance(sum(roll))
                return
        self.advance(sum(roll))
        if not is_double(roll):
            return
        roll = dice_roll()
        self.advance(sum(roll))
        if not is_double(roll):
            return
        roll = dice_roll()
        if is_double(roll):
            self.days_in_jail = 1
            self.square = 10
        else:
            self.advance(sum(roll))


def dice_roll():
    return (random.randrange(7), random.randrange(7))


def take_a_chance():
    return random.sample(
    ((go_to_go,),
    (go_to_jail,),
    (advance_to, 5),  # reading railroad
    (advance_to, 11),  # st charles place
    (advance_to, 24),  # illinois avenue
    (advance_to, 39),  # boardwalk
    (increase_capital, -50 * PLAYERS),
    (increase_capital, 150),
    (increase_capital, 100),
    (increase_capital, 50),
    (increase_capital, -15),
    (go_back, 3),
    (increase_capital, -25 * HOUSES - 100 * HOTELS)), 1)[0]
    # Advance token to nearest Utility. If unowned, you may buy it from the Bank
    # If owned, throw dice and pay owner a total ten times the amount thrown.
    # Advance token to the nearest Railroad and pay owner twice the rental to
    # which he/she is otherwise entitled. If Railroad is unowned, you may buy
    # it from the Bank. (There are two of these.) 
    # TODO get out of jail card


def take_a_chest():
    return random.sample(
    ((increase_capital, 200),
    (increase_capital, 100),
    (increase_capital, 100),
    (increase_capital, 100),
    (increase_capital, 50),
    (increase_capital, 25),
    (increase_capital, 20),
    (increase_capital, 10),
    (increase_capital, -50),
    (increase_capital, -100),
    (increase_capital, -150),
    (increase_capital, 50 * PLAYERS),
    (increase_capital, 10 * PLAYERS),
    (increase_capital, -40 * HOUSES - 115 * HOTELS),
    (go_to_go,),
    (go_to_jail,)), 1)[0]
    # TODO get out of jail card


def is_double(dice_roll):
    die_1, die_2 = dice_roll
    if die_1 == die_2:
        return True
    return False


def advance_to(player, square, direct=False):
    if not direct and square <= player.square:  # passing go:
        player.capital += 200
    player.square = square
    if square == 30:  # Go to jail
        player.square = 10
        player.days_in_jail = 1
    elif square in (7, 22, 36):
        chance = take_a_chance()
        func, *args = chance
        func(player, *args)
    elif square in (2, 17, 33):
        chest = take_a_chest()
        func, *args = chest
        func(player, *args)
    elif square == 4:
        pay_income_tax(player)
    elif square == 38:
        player.capital -= 100  # Luxury Tax


def increase_capital(player, delta):
    player.capital += delta


def go_to_go(player):
    advance_to(player, 0)


def go_to_jail(player):
    advance_to(player, 30, direct=True)


def go_back(player, squares):
    new_square = (player.square - squares) % 40
    advance_to(player, new_square, direct=True)


def nearest_utility(square):
    if 12 < square <= 28:
        return 28
    return 12


def pay_income_tax(player):
    player.capital -= min(200, int(.1 * player.capital))


if __name__ == "__main__":
    player = Player()
    orig = player.capital
    count = 0
    jail_count = 0
    while True:
        count += 1
        player.take_turn()
        if player.in_jail:
            jail_count += 1
        #print(count, player.capital, player.square, jail_count)
        print((player.capital - orig) / float(count))
