#!/usr/bin/env python3
#
# iChing_Modified_3_coins.py
#
#   see https://github.com/kwccoin/I-Ching-Modified-3-Coin-Method
#
#   Create (two) I Ching hexagrams: present > future (might be same).
#
# With both "3-coin method" and "modified 3-coin method" (see <nowiki>https://en.wikipedia.org/wiki/I_Ching_divination</nowiki>).
#
# 3-coins Probabilities:
#   old/changing/moving yin    "6 : == x ==" = 1/8
#   (young/stable/static) yang "7 : =======" = 3/8
#   (young/stable/static) yin  "8 : ==   ==" = 3/8
#   old/changing/moving yang   "9 : == o ==" = 1/8
#
# 3-coins Probabilities:
#   old/changing/moving yin    "6 : === x ===" = 1/8
#   (young/stable/static) yang "7 : =========" = 3/8
#   (young/stable/static) yin  "8 : ===   ===" = 3/8
#   old/changing/moving yang   "9 : ====o====" = 1/8
#
# Modified 3-coins Probabilities:
#   old/changing/moving yin    "6 : === x ===" = 1/8 * 1/2     = 1/16
#   (young/stable/static) yang "7 : =========" = 3/8 - 1/8*1/2 = 5/16
#   (young/stable/static) yin  "8 : ===   ===" = 3/8 - P[6]    = 7/16
#   old/changing/moving yang   "9 : ====o====" = 1/8 - p[7]    = 3/16

# see
# https://aleadeum.com/2013/07/12/the-i-ching-random-numbers-and-why-you-are-doing-it-wrong/
# especially see the remark why 1st round are 1/4-3/4 whilst 2nd and 3rd round are 1/2-1/2

import random


def toss(method: str = "yarrow") -> int:
    "Toss."""
    rng = random.SystemRandom()  # Auto-seeded, with os.urandom()

    special_coin = 0
    val = 0

    for flip in range(3):  # Three simulated coin flips i.e. coin 0, 1, 2
        val += rng.randint(2, 3)  # tail=2, head=3 for each coin
        if flip == 0:
            special_coin = val  # Coin 0 as the special coin

    if method == "coin":  # Coin method note tth or 223 is 7 or young yang
        return val  # Probability of 6/7/8/9 is 1/8 3/8 3/8 1/8

    elif method == "modified 3 coins":
        # method similar to "yarrow-stick" need to have prob.
        # for 6/7/8/9 as 1/16  5/16  7/16  3/16

        # now coin method is
        # for 6/7/8/9 as 2/16  6/16  6/16  2/16

        # modified to change
        #               -1/16 -1/16 +1/16 + 1/16
        #                   6     7     8      9
        if ((val == 6) and (special_coin == 2)):
            special_coin = rng.randint(2, 3)
            if (special_coin == 2):
                val = 6
            else:
                val = 8
        elif ((val == 7) and (special_coin == 3)):
            special_coin = rng.randint(2, 3)
            if (special_coin == 3):
                val = 7
            else:
                val = 9

        return val  # probability of 6/7/8/9 is 1/16 5/16 7/16 3/16

    else:  # yarrow-stick method as effectively default
        # start_sticks, sky-left, sky-reminder, human,  earth-right, earth-reminder, bin
        # value->   49         0             0      0             0            0      0
        # index->    0         1             2      3             4            5      6
        # on table:
        #               heaven
        # heaven-left   human    earth-right
        #               earth
        #
        # sometimes use finger to hold above

        def printys(ys, remark):
            # String format example: f"Result: {value:{width}.{precision}}"
            width = 3
            print(f'[{ys[0]}, \t{ys[1]}, \t{ys[2]}, \t{ys[3]}, \t{ys[4]}, \t{ys[5]}, \t{ys[6]}] \t{remark}')
            return

        def ys_round(ys, round, debug="no"):
            if debug == "yes": print("Round is", round)
            if debug == "yes": print("===============")
            if debug == "yes": print(
                f'[{"src"}, \t{"sky"}, \t{"left"}, \t{"human"}, \t{"earth"}, \t{"right"}, \t{"bin"}] \t{"remark"}')
            # Generate a number somewhere in between 1/3 to 2/3 as human do not trick
            if debug == "yes": printys(ys, "Starting")
            ys[1] = rng.randint(ys[0] // 3, ys[0] * 2 // 3)
            ys[4] = ys[0] - ys[1]
            ys[0] = ys[0] - ys[1] - ys[4]
            if debug == "yes": printys(ys, "Separate into two")
            ys[3] = 1
            ys[1] = ys[1] - ys[3]
            if debug == "yes": printys(ys, "and with one as human")
            ys[2] = ys[1] % 4
            if ys[2] == 0:
                ys[2] = 4
            ys[1] = ys[1] - ys[2]
            if debug == "yes": printys(ys, "then 4 by 4 and sky behind ...")
            ys[5] = ys[4] % 4
            if ys[5] == 0:
                ys[5] = 4
            ys[4] = ys[4] - ys[5]
            if debug == "yes": printys(ys, "then 4 by 4 and earth behind ...")
            ys[6] += ys[2] + ys[3] + ys[5]
            ys[2] = 0
            ys[3] = 0
            ys[5] = 0
            ys[0] = ys[1] + ys[4]
            ys[1] = 0
            ys[4] = 0
            if debug == "yes": printys(ys, "complete the cycle ...")
            return ys

        ys = [0, 0, 0, 0, 0, 0, 0]  # May be better use dictionary
        ys[0] = 55
        # printys(ys, "The number of heaven and earth is 55")
        ys[0] = 49
        # printys(ys, "only 49 is used")

        # Round 1 need to ensure mod 4 cannot return 0 and cannot have 0
        # wiki said cannot have 1 as well not sure about that

        ys = ys_round(ys, 1, "no")  # "yes")
        ys = ys_round(ys, 2, "no")  # "yes")
        ys = ys_round(ys, 3, "no")  # "yes")
        return (ys[0] // 4)


# We build in bottom to top

print("Method is yarrow by default\n")
toss_array = [0, 0, 0, 0, 0, 0]

for line in range(0, 6, 1):
    toss_array[line] = toss()
    print("Line is ", line + 1, "; toss is ", toss_array[line], "\n")


# Hence we print in reverse

def print_lines_in_reverse(toss_array):
    for line in range(5, -1, -1):
        val = toss_array[line]  # The changing line/hexagram need another program
        if val == 6:
            print('6  :  == x ==')  # ||   ==   ==  >  -------')
        elif val == 7:
            print('7  :  -------')  # ||   -------  >  -------')
        elif val == 8:
            print('8  :  ==   ==')  # ||   ==   ==  >  ==   ==')
        elif val == 9:
            print('9  :  -- o --')  # ||   -------  >  ==   ==')


print_lines_in_reverse(toss_array)

print("\n\n")
