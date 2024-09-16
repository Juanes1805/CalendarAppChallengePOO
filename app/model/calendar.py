from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import ClassVar

from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error


@dataclass
class Reminder:
    date_time: datetime
    EMAIL: str = "email"
    SYSTEM: str = "system"
    type: str = EMAIL

    def __str__(self) -> str:
        f"Reminder on {self.date_time} of type {self.type}"


@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time
    reminders: list[Reminder] = field(init=False, default_factory=list)
    id: str = field(default_factory=generate_unique_id)

    def add_reminder(self, date_time: datetime, type_: str):
        self.reminders.append(Reminder(date_time, type_))

    def delete_reminder(self, reminder_index: int):
        if 0 <= reminder_index < len(self.reminders):
            self.reminders.pop(reminder_index)
        else:
            reminder_not_found_error()

    def __str__(self) -> str:
        return (f"ID: {self.id}\n"
                f"Event title: {self.title}\n"
                f"Description: {self.description}\n"
                f"Time: {self.start_at} - {self.end_at}")


class Day:

    def __init__(self, date_: date):
        self.date_: date = date_
        self.slots: dict[time, str | None] = {}
        self._init_slots()
        
    def _init_slots(self):
        for h in range(24):
            for m in range(0, 60, 15):
                self.slots[time(h, m)] = None

    def add_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot] is not None:
                    slot_not_available_error()
                else:
                self.slots[slot] = event_id

    def delete_event(self, event_id: str):
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if self.slots[slot] == event_id:
                self.slots[slot] = None

        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot]:
                    slot_not_available_error()
                else:
                    self.slots[slot] = event_id


class Calendar:

    def __init__(self):
        self.days: dict[date, Day] = {}
        self.events: dict[str, Event] = {}

    def add_event(self, title: str, description:str, date_: date, start_at: time, end_at: time):
        if date_ < datetime.now().date():
            date_lower_than_today_error()
            
        if date_ not in self.days:
            self.days[date_] = Day(date_)

        event = Event(title, description, date_, start_at, end_at)
        self.days[date_].add_event(event.id, start_at, end_at)
        self.events[event.id] = event

        return event.id

    def add_reminder(self, event_id: str, date_time: datetime, type_: str):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        event.add_reminder(date_time, type_)

    def find_available_slots(self, date_: date) -> list[time]:
        available_slots = []
        day = self.days.get(date_)
        if day:
            for slot, event in day.slots.items():
                if not event:
                    available_slots.append(slot)
        else:
            day: Day(date_)
            available_slots = list(day.slots.keys())

        return available_slots
                                
