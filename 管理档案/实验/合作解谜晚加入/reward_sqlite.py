"""Run with python3 reward_sqlite.py. Uses two independent SQLite connections."""

import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

RUN = 'run19'
REWARD = 'door2'
AMOUNT = 25


def connect(path):
    return sqlite3.connect(path, timeout=5, isolation_level=None)


def grant(db, player, *, fail_before_commit=False):
    # player represents an authenticated stable player ID, not a client-supplied claim.
    db.execute('BEGIN IMMEDIATE')
    try:
        allowed = db.execute(
            'SELECT 1 FROM eligible WHERE run=? AND kind=? AND player=?',
            (RUN, REWARD, player),
        ).fetchone()
        if allowed is None:
            db.execute('ROLLBACK')
            return ('ineligible', None)
        inserted = db.execute(
            'INSERT INTO receipts(run, kind, player, amount) VALUES (?, ?, ?, ?) '
            'ON CONFLICT(run, kind, player) DO NOTHING',
            (RUN, REWARD, player, AMOUNT),
        ).rowcount
        if inserted:
            updated = db.execute(
                'UPDATE wallets SET balance=balance+? WHERE player=?',
                (AMOUNT, player),
            )
            assert updated.rowcount == 1
        receipt = db.execute(
            'SELECT id, amount FROM receipts WHERE run=? AND kind=? AND player=?',
            (RUN, REWARD, player),
        ).fetchone()
        if fail_before_commit:
            raise RuntimeError('injected before COMMIT')
        db.execute('COMMIT')
    except BaseException:
        if db.in_transaction:
            db.execute('ROLLBACK')
        raise
    return ('granted' if inserted else 'already_granted', receipt)


def check(db, expected):
    assert db.execute('SELECT player,balance FROM wallets ORDER BY player').fetchall() == [
        ('A', AMOUNT * expected), ('B', 0)
    ]
    assert db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0] == expected


def main():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'puzzle.sqlite'
        setup = connect(path)
        try:
            setup.executescript('''
                CREATE TABLE wallets (
                    player TEXT PRIMARY KEY,
                    balance INTEGER NOT NULL
                );
                CREATE TABLE eligible (
                    run TEXT NOT NULL, kind TEXT NOT NULL, player TEXT NOT NULL,
                    PRIMARY KEY (run, kind, player)
                );
                CREATE TABLE receipts (
                    id INTEGER PRIMARY KEY,
                    run TEXT NOT NULL, kind TEXT NOT NULL, player TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    UNIQUE (run, kind, player)
                );
                INSERT INTO wallets VALUES ('A', 0), ('B', 0);
            ''')
            # Product rule for this example: only A was eligible at completion.
            setup.execute('INSERT INTO eligible VALUES (?, ?, ?)', (RUN, REWARD, 'A'))

            try:
                grant(setup, 'A', fail_before_commit=True)
            except RuntimeError as exc:
                assert str(exc) == 'injected before COMMIT'
            else:
                raise AssertionError('fault was not injected')
            check(setup, 0)

            starters = Barrier(2)

            def writer(_):
                db = connect(path)
                try:
                    starters.wait(timeout=5)
                    return grant(db, 'A')
                finally:
                    db.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(writer, range(2)))
            assert sorted(status for status, _ in results) == ['already_granted', 'granted']
            assert results[0][1] == results[1][1]
            check(setup, 1)

            # The successful response above was not delivered to the client.
            # Test the retry via a fresh connection as for a reconnected A.
            retry = connect(path)
            try:
                assert grant(retry, 'A') == ('already_granted', results[0][1])
                assert grant(retry, 'B') == ('ineligible', None)
                check(retry, 1)
            finally:
                retry.close()
        finally:
            setup.close()
    print(f'SQLite {sqlite3.sqlite_version}: rollback=0; writers=1 receipt + 1 credit; '
          'ACK-lost retry=same receipt; B=ineligible')


if __name__ == '__main__':
    main()
