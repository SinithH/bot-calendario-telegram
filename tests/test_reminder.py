#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Tests functions from Reminder Class.

Copyright 2017, Luis Liñán (luislivilla@gmail.com)

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""

# External imports
import unittest
import peewee
import json
import sqlite3
import os

# Local imports
import context
from bot_calendario_telegram.settings import TESTING_VARS
import bot_calendario_telegram.reminder as rem
assert TESTING_VARS, context


# === Clase test ===
class ReminderTest(unittest.TestCase):
    """Reminder test class."""

    def test_save_update_delete_event(self):
        """Check for exceptions in the insertion/update/deletion."""
        # Insert a new event
        result_insert = reminder_object.save_event('test_event',
                                                   '2000/01/01 00:00:00')
        # Update the previuosly inserted event
        result_update = reminder_object.update_event('test_event',
                                                     '2049/01/01 00:00:00')

        # Check if the returning of the inserti is the event in essence
        self.assertEqual(result_insert, {'test_event': '2000/01/01 00:00:00'},
                         'Not the correct return')
        # Check if there was one line updated
        self.assertEqual(result_update, 1, 'No event updated')

        # Check if it is possible to insert another event with the same ID
        with self.assertRaises(peewee.IntegrityError):
            reminder_object.save_event('test_event', '2049/01/01 00:00:00')

        # Delete the previous inserted event
        result = reminder_object.delete_event('test_event')
        self.assertEqual(result, 1, 'Not one row deleted')

        # Try to delete inexistent event
        result = reminder_object.delete_event('non_existent_event')
        self.assertEqual(result, 0, 'Should not delete nothing')

    def test_get_event(self):
        """Check if it returns a correct event."""
        # Test existing event
        result = reminder_object.get_event('1')
        # Test non existing event
        retult_2 = reminder_object.get_event('non_existent_event')

        # Check if it returns the expected event
        self.assertEqual(result, {'1': '2017/10/18 12:30'},
                         'Didn\'t return the correct event')
        # Check if it returns an empty dictionary
        self.assertEqual(retult_2, {}, 'Non existent event is not empty')

    def test_next_event(self):
        """Check if the next event is the first on a sorted list."""
        # Test next event
        result = reminder_object.next_event()

        # Should return the next event order by date
        self.assertEqual(result, {'4': '2016/03/25 16:45'}, 'Incorrect output')

    def test_get_all_events(self):
        """Check if there are any exceptions in the select."""
        # The expected output
        all_events_json = {
            "4": "2016/03/25 16:45",
            "5": "2017/10/05 10:40",
            "1": "2017/10/18 12:30",
            "2": "2017/10/20 14:15",
            "3": "2017/10/25 16:45"
        }

        # Test get all events
        result = reminder_object.get_all_events()

        # Should return the same as `all_events_json`
        self.assertEqual(result, all_events_json,
                         'Date sorting is not correct')


def setUpModule():
    """Set up Module method."""
    global reminder_object

    # Conexión
    conn = sqlite3.connect(TESTING_VARS['DB_NAME'])

    # Cursor
    c = conn.cursor()

    # Drop table if already exists
    c.execute("DROP TABLE IF EXISTS 'event'")

    # Create table
    c.execute('''
    CREATE TABLE event(
        id INTEGER PRIMARY KEY,
        id_event varchar(255) NOT NULL UNIQUE,
        date_event datetime NOT NULL
    );
    ''')

    # Larger example that inserts many records at a time
    with open(TESTING_VARS['REMINDER_DATA_FILE'], 'r') as fp:
        test_data = json.load(fp)

    test_data = [(k['id_event'], k['date_event']) for k in test_data['event']]

    # Insert the test data into the database
    c.executemany('INSERT INTO event (id_event, date_event) VALUES (?, ?)',
                  test_data)

    # Save (commit) the changes
    conn.commit()

    # Close the connection if everything is done
    conn.close()

    # Create Reminder object, init it and connect to the database
    reminder_object = rem.Reminder()
    reminder_object.initialize(TESTING_VARS['DB_NAME'])
    reminder_object.connect()


def tearDownModule():
    """Tear down Module method."""
    global reminder_object

    # Close the database connection of reminder_object
    reminder_object.close()

    # Remove the testing database if it is not in memory
    if TESTING_VARS['DB_NAME'] != ':memory:':
        os.remove(TESTING_VARS['DB_NAME'])


if __name__ == '__main__':
    unittest.main()
