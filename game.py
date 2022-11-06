import random
import sqlite3
from datetime import datetime
import pickle
import os

lowercase = 'abcdefghijklmnopqrstuvwxyz'

words = [word for word in open('words.txt').read().split() if len(word) > 4 and '-' not in word]


class Game(object):
    def __init__(self):
        if os.path.exists('game.pickle'):
            d = pickle.load(open('game.pickle'))
            self.word = d['word']
            self.missed = d['missed']
            self.guessed = d['guessed']
            print(self.word)
        else:
            self.start()

    def start(self):
        self.word = random.choice(words)
        print(self.word)
        self.missed = []
        self.guessed = []
        if len(self.word) > 4:
            self.guessed = list(set([self.word[0], self.word[-1]]))

    def play(self, letter='', ident='', name='', country=''):
        res = ''
        status = None
        if letter:
            res = self.guess(letter)
        img = 'hangman/Hangman-%d.png' % len(self.missed)
        text = 'Word: %s' % (' '.join(l if l in self.guessed else '_' for l in self.word))
        if self.missed: text += '\nMissed: %s' % (','.join(self.missed))
        if res: text += '\n%s' % res
        if res.startswith('You lose') or res.startswith('You won'):
            status = "lost"
            self.start()
        if res.startswith('You won'):
            status = "won"
            img = 'hangman/victory.jpg'
        if res.startswith('Correct'):
            status = "hit"
        if res.startswith('Wrong'):
            status = "miss"
        if status:
            d = {'word': self.word, 'missed': self.missed, 'guessed': self.guessed}
            pickle.dump(d, open('game.pickle', 'w'))
            with sqlite3.connect('lb.sqlite') as conn:
                conn.execute('INSERT INTO games(ident,status,date,name,country) VALUES(?,?,?,?,?);',
                             (ident, status, datetime.now(), name, country))
        return (text, img)

    def guess(self, letter):
        letter = letter.lower().strip()
        if self.word == letter:
            self.guessed = list(set(self.word))
            return 'You won'
        if len(letter) > 1:
            return 'Wrong'
        if letter not in lowercase:
            return 'Not a letter'
        if letter in self.guessed:
            return 'You already guessed that letter'
        if letter in self.missed:
            return 'You already tried that letter'
        if letter in self.word:
            self.guessed.append(letter)
            if all(l in self.guessed for l in self.word):
                return 'You won'
            return 'Correct'
        else:
            self.missed.append(letter)
            if len(self.missed) == 6:
                return 'You lose(word was %s)' % self.word
            return 'Wrong'

    def stats(self):
        res = ''
        with sqlite3.connect('lb.sqlite') as conn:
            cur = conn.execute(
                'SELECT name,country,count(id) as c FROM games WHERE status="won" GROUP BY ident ORDER BY c DESC LIMIT 20')
            res = 'Games won:\n'
            res += '\n'.join('%s | %s | %s' % row for row in cur.fetchall())
            cur = conn.execute(
                'SELECT name,country,count(id) as c FROM games WHERE status="lost" GROUP BY ident ORDER BY c DESC LIMIT 20')
            res += '\n\nGames lost:\n'
            res += '\n'.join('%s | %s | %s' % row for row in cur.fetchall())
            cur = conn.execute(
                'SELECT name,country,count(id) as c FROM games WHERE status="hit" GROUP BY ident ORDER BY c DESC LIMIT 20')
            res += '\n\nLetters guessed:\n'
            res += '\n'.join('%s | %s | %s' % row for row in cur.fetchall())
            cur = conn.execute(
                'SELECT name,country,count(id) as c FROM games WHERE status="miss" GROUP BY ident ORDER BY c DESC LIMIT 20')
            res += '\n\nLetters missed:\n'
            res += '\n'.join('%s | %s | %s' % row for row in cur.fetchall())
        return res
