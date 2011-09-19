#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Frederic'

from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup
from utils import split_weeks, convert_time, convert_week_number_to_date
from basecalendar import BaseCalendar

class StudentSetCalendar(BaseCalendar):
    def __init__(self, markup):
        super(StudentSetCalendar, self).__init__()
        if self._is_file_type_object(markup):
            markup = markup.read()
        self.html_content = markup
        soup = BeautifulSoup(self.html_content, fromEncoding='iso-8859-1')
        self.header_data = {'student_profile':None, 'faculty':None}
        self._load_content_from_soup(soup)


    @property
    def description(self):
        descr = "[%s] %s" % (self.header_data['faculty'],
                             self.header_data['student_profile'])
        return descr.replace(':', '-')


    @property
    def name(self):
        return  self.header_data['student_profile'].replace(':', '-')


    def _load_content_from_soup(self, soup):
        try:
            top_level_tables = soup.html.body.findAll(name="table", recursive=False)
            # Take only the first 3 top-level tables. Sometimes the html is
            # broken and we don't get the 4th.
            # We also don't get the closing tags. This piece of software is
            # pretty brilliant
            header, event_grid, footer = top_level_tables[:3]

            self._load_header_data(header)
            self._load_events(event_grid)
        except AttributeError,e:
            self._guess_query_error(self.html_content)
        except ValueError,e:
            self._guess_query_error(self.html_content)
            
    def _load_header_data(self, header):
        all_entries = header.findAll(name='table')
        faculty_table = all_entries[4]
        profile_table = all_entries[6]
        self.header_data['faculty'] = self._extract_data_from_header_table(faculty_table)
        self.header_data['student_profile'] = self._extract_data_from_header_table(profile_table)


    @staticmethod
    def _extract_data_from_header_table(table):
        t = table.td.getText()
        return t


    @staticmethod
    def _insert_halfhour_slots_and_convert_to_datetime(hour_cells):
        hours = []
        for h in hour_cells:
            if h.string:
                hours.append(convert_time(h.string))
            else:
                last_added_hour = hours[-1]
                hours.append(datetime(last_added_hour.year,
                                           last_added_hour.month,
                                           last_added_hour.day,
                                           last_added_hour.hour, 30))
        return hours


    def _load_events(self, event_table):
        all_rows = event_table.findChildren('tr', recursive=False)

        # get the column labels, save as actual hours objects
        hours_row = all_rows[0].findChildren('td', recursive=False)
        hours = self._insert_halfhour_slots_and_convert_to_datetime(hours_row[1:])

        # get the events for each day
        event_rows = all_rows[1:]
        self.events = []

        rows_per_day = self._get_num_row_per_day(event_rows)
        current_row_index = 0

        for (num_day, day_string, num_rows) in rows_per_day:
            day_events = []
            for day_subrow in range(num_rows):
                current_day_index = current_row_index + day_subrow
                events_in_row = self._load_weekday_events(event_rows[current_day_index],
                                                          num_day,
                                                          hours)
                day_events.extend(events_in_row)
            self.events.extend(day_events)
            current_row_index += num_rows


    def _get_num_row_per_day(self, event_rows):
        """
        Extracts the number of rows allocated for each day in the html table

        Params:
        - event_rows : a list of table rows. Each row contains parsed
        html data (w/ BeautifulSoup)

        Returns:
        - A list of (num_day, day_string, num_rows) tuples.
        """

        # This is a first pass on the whole table of events. We extract
        # the number of rows allocated for each day in
        # the layout algorithm. We use the 'rowspan' attribute present
        # in the first column of the first row of each day.
        # TODO: this needs work
        day_string = ['lun.', 'mar.', 'mer.' , 'jeu.', 'ven.', 'sam.']
        num_rows = []
        for row in event_rows:
            num_rows += [int(col['rowspan'])
                         for col in row.findAll('td', recursive=False)
                         if col.text in day_string]
        return zip(range(6), day_string, num_rows)


    def _load_weekday_events(self, weekday_row, num_day, hours):
        """
        Finds and load the events in one row of a day.
        - weekday_row : the parsed data (w/ BeautifulSoup) for the current day row
        - num_day : number of the current day (0 to 6)
        - hours : a list of all the timeslot hours (as datetime objects) for a day.
        """
        # At this point we should have a bunch of <td> elements.
        # Some cells are empty, some cells have an event in them.
        # First <td> is the weekday string, so we skip it.
        row = weekday_row.findChildren('td', recursive=False)
        all_day_slots = row

        events = []
        current_time_idx = 0
        for time_slot in all_day_slots:
            if self._slot_has_event(time_slot):
                new_event = self._process_event(time_slot,
                                                hours[current_time_idx],
                                                num_day)
                events.append(new_event)
                current_time_idx += new_event['num_timeslots']
            else:
                # This is tricky : in the first row of each day, the first
                # column (which contains the name of 
                # the current day) does not count as a time slot.
                # Another way to say it is, for each row, the time slots
                # go from 1 to n in the first row, and 0 to n in all the others.
                # Thus, we increment the current time slot index only if we're
                # not in the first column of the first row.
                # Thanks a lot, Scientia(r) Course Planner(tm)(c)
                if time_slot.text not in ['lun.', 'mar.', 'mer.' ,
                                          'jeu.', 'ven.', 'sam.']:
                    current_time_idx += 1
                
        return events


    def _process_event(self, object_cell, starting_hour, num_day):
        num_timeslots = int(object_cell['colspan'])
        cell_tables = object_cell.findChildren('table', recursive=False)
        # event box : 3 tables, one per line :
        #   - location/weeks
        #   - title
        #   - tutor/course type
        location_weeks_table, title_table, tutor_type_table = cell_tables

        location = location_weeks_table.tr.findChildren('td')[0].text
        course_weeks = location_weeks_table.tr.findChildren('td')[1].text

        course_title = title_table.tr.td.text

        children = tutor_type_table.findChildren('td')
        course_tutor = children[0].text
        course_group = children[1].text
        course_type = children[2].text

        return {
            'type':course_type,
            'location':location,
            'organizer':"",
            'title':course_title,
            'weeks':split_weeks(course_weeks),
            'num_timeslots':num_timeslots,
            'start_time':starting_hour,
            'stop_time':starting_hour + timedelta(hours = self._convert_num_timeslots_to_hours(num_timeslots)),
            'day':num_day,
            'lecturer':course_tutor,
            'group':course_group
        }
    

    @staticmethod
    def _convert_num_timeslots_to_hours(num_timeslots):
        # 1 timeslot = 30 minutes
        return float(num_timeslots) / 2

    @staticmethod
    def _slot_has_event(slot):
        return slot.table is not None


