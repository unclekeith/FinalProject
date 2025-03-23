from datetime import datetime, timedelta

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from libs.applibs.generated_connection_manager import EventsRoutes


class CalendarScreen(MDScreen):
    month_label = StringProperty("")
    days = ListProperty([])
    current_date = datetime.now()
    events = {}  # Dictionary to store events for each day
    monthly_events = {}  # Dictionary to store monthly events
    selected_day_labels = []  # List to keep track of currently selected day labels
    currently_selected_date = None  # Store the currently selected date

    def __init__(self, **kwargs):
        super(CalendarScreen, self).__init__(**kwargs)
        self.update_calendar()  # Ensure this is called to initialize the calendar

    def on_enter(self):
        Clock.schedule_once(self.get_all_events, 0)

    def update_calendar(self):
        first_day_of_month = self.current_date.replace(day=1)
        self.month_label = self.current_date.strftime("%B %Y")

        # Calculate the number of days in the month and the first weekday
        next_month = first_day_of_month.replace(
            month=first_day_of_month.month % 12 + 1,
            year=first_day_of_month.year + first_day_of_month.month // 12,
        )
        num_days = (next_month - timedelta(days=1)).day
        first_weekday = first_day_of_month.weekday()  # Monday is 0

        # Fill the days
        days = [""] * first_weekday + [str(day) for day in range(1, num_days + 1)]
        days += [""] * (42 - len(days))  # Ensure 6 rows of 7 days

        self.days = days
        self.update_calendar_grid()

    def update_calendar_grid(self):
        grid = self.ids.calendar_grid
        grid.clear_widgets()

        # Add weekday headers
        self.add_weekday_headers(grid)

        for day in self.days:
            day_label = MDBoxLayout(
                orientation="vertical", size_hint_y=None, height=dp(40), radius=dp(0)
            )

            day_number = MDLabel(
                text=day,
                halign="center",
                valign="middle",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
            day_label.add_widget(day_number)

            if day:
                full_date = self.current_date.replace(day=int(day))
                # Add a small label below the day to show event count
                event_count = len(self.events.get(full_date, []))
                if event_count > 0:
                    event_label = MDLabel(
                        text=f"{event_count} event(s)",
                        halign="center",
                        size_hint_y=None,
                        height=dp(20),
                    )
                    day_label.add_widget(event_label)

                day_label.bind(on_touch_down=self.on_day_click)

            grid.add_widget(day_label)

    def add_weekday_headers(self, grid):
        for day in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]:
            if day == "Su":
                label = MDLabel(
                    text=f"[b][color=#FF0000]{day}[/color][/b]",
                    markup=True,
                    halign="center",
                    valign="middle",
                    size_hint_y=None,
                    height=dp(30),
                    color=self.get_theme_color(),
                )
            else:
                label = MDLabel(
                    text=f"[b]{day}[/b]",
                    markup=True,
                    halign="center",
                    valign="middle",
                    size_hint_y=None,
                    height=dp(30),
                    color=self.get_theme_color(),
                )
            grid.add_widget(label)

    def on_day_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Deselect previous selections
            for selected_label in self.selected_day_labels:
                selected_label.md_bg_color = (
                    self.theme_cls.backgroundColor
                )  # Reset background to default

            self.selected_day_labels.clear()

            # Highlight selected day
            instance.md_bg_color = [
                0.2,
                0.6,
                0.8,
                1,
            ]  # Example blue color for selected day
            self.selected_day_labels.append(instance)

            # Extract day text and set the selected day
            for child in instance.children:
                if isinstance(child, MDLabel):
                    day_text = child.text
                    break

            selected_day = int(day_text) if day_text.isdigit() else None
            if selected_day:
                self.currently_selected_date = self.current_date.replace(
                    day=selected_day
                )

            # Fetch events for the selected day and populate the daily events section
            if self.currently_selected_date:
                self.show_events(self.currently_selected_date)

    def on_day_drag(self, instance, touch):
        if (
            instance.collide_point(*touch.pos) and instance.text
        ):  # Check if day is not empty
            self.select_day(instance)

    def on_day_release(self, instance, touch):
        # Reset the selected days list when the touch is released
        self.selected_day_labels = []

    def select_day(self, instance):
        # Reset the previously selected day labels' color
        for label in self.selected_day_labels:
            label.md_bg_color = [1, 1, 1, 1]  # Reset to default color

        selected_day = int(instance.text)
        full_date = self.current_date.replace(day=selected_day)

        # Check if any event exists for the selected date
        has_event = full_date in self.events

        # Highlight selected day with a border and color
        instance.md_bg_color = [0.2, 0.6, 0.8, 1]  # Blue background
        if has_event:
            instance.md_bg_color = [0.2, 0.8, 0.2, 1]  # Green for days with events

        self.selected_day_labels.append(instance)
        print(f"Selected date: {full_date.strftime('%Y-%m-%d')}")
        self.show_events(full_date)

    def add_event(self, *args, **kwargs):
        if not self.currently_selected_date:
            print("No day selected to add an event.")
            return

        event_date = self.currently_selected_date

        # Show the selected date in the dialog as well
        self.show_event_dialog(
            selected_date=event_date.date()
        )  # Pass the date to the dialog

    def show_events(self, date):
        # Clear the current daily events
        self.ids.daily_events.clear_widgets()

        # Retrieve events for the selected date (dummy data for now)
        events_for_day = self.events.get(date.strftime("%Y-%m-%d"), [])

        if events_for_day:
            # Populate the daily_events MDList with items
            for event in events_for_day:
                list_item = MDBoxLayout(
                    MDLabel(text=event),
                    radius=[10],
                    size_hint_y=None,
                    height=dp(48),
                    md_bg_color="#00FFF0",
                    padding=dp(4),
                )
                self.ids.daily_events.add_widget(list_item)
        # else:
        #     # If no events, show a placeholder message
        #     no_event_item = MDListItem(
        #         MDListItemHeadlineText(text="No events for this day"), radius=[10]
        #     )
        #     self.ids.daily_events.add_widget(no_event_item)

    def show_monthly_events(self, month):
        # Update the monthly events display
        monthly_events = self.ids.monthly_events
        monthly_events.clear_widgets()  # Clear existing monthly events
        monthly_events.add_widget(
            MDLabel(
                markup=True,
                text=f"[size=16sp][b]Events for Month {month}[/b][/size]",
                halign="center",
            )
        )

        # Display a maximum of three events for the month
        for event in self.monthly_events.get(month, [])[:3]:
            monthly_events.add_widget(
                MDLabel(markup=True, text=f"[size=14sp]{event}[/size]", halign="left")
            )

    def previous_month(self):
        # Animate the calendar while switching
        self.animate_calendar_change(direction="left")
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.update_calendar()

    def next_month(self):
        # Animate the calendar while switching
        self.animate_calendar_change(direction="right")
        self.current_date = self.current_date.replace(day=28) + timedelta(days=5)
        self.current_date = self.current_date.replace(day=1)
        self.update_calendar()

    def animate_calendar_change(self, direction):
        fade_out = Animation(opacity=0, duration=0.2)
        fade_in = Animation(opacity=1, duration=0.2)
        fade_out.start(self.ids.calendar_grid)
        fade_out.bind(on_complete=lambda *args: self.update_calendar())
        fade_in.start(self.ids.calendar_grid)

    def get_theme_color(self):
        # Determine the theme color based on the app's theme
        if self.theme_cls.theme_style == "Light":
            return (0, 0, 0, 1)  # Black for dark theme (opposite of white)
        else:
            return (1, 1, 1, 1)  # White for light theme (opposite of black)

    def show_event_dialog(self, selected_date=None):
        # If no date is passed, use the currently selected date
        if not selected_date:
            selected_date = (
                self.currently_selected_date
                if self.currently_selected_date
                else "No date selected"
            )
        self.event_name_field = MDTextField(
            hint_text="Enter event name",
            pos_hint={"center_y": 0.5},
        )

        dialog = MDDialog(
            MDDialogContentContainer(
                MDLabel(
                    markup=True,
                    text=f"[size=30sp][b]ADD EVENT FOR {selected_date}:[/b][/size]",
                    size_hint_x=None,
                    width=dp(200),
                    valign="middle",
                    adaptive_height=True,
                    pos_hint={"top": 1},
                ),
                MDBoxLayout(
                    MDLabel(
                        markup=True,
                        text="[size=16sp][b]Event Name:[/b][/size]",
                        size_hint_x=None,
                        width=dp(150),
                        valign="middle",
                        adaptive_height=True,
                        pos_hint={"center_y": 0.5},
                    ),
                    self.event_name_field,  # Attach the text field for event name
                    adaptive_height=True,
                ),
                orientation="vertical",
                spacing=10,
            ),
            # ---------------------Button container------------------------
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Create Event"),
                    style="text",
                    on_release=lambda x: self.create_new_event(dialog),
                    # Bind to the on_accept_button function
                ),
                spacing="8dp",
            ),
            size_hint_x=0.9,
            # size_hint_y=0.6,
            # size_hint_x=9,
            # height=500,
            adaptive_height=True,
            # -------------------------------------------------------------
        )
        dialog.open()

    def create_new_event(
        self,
        dialog,
    ):
        event_name = self.event_name_field.text.strip()  # Get the event name
        
        # Basic validation to ensure no field is empty
        if not event_name:
            print("Event name is empty. Please enter a valid event name.")

        else:
            event_form = {
                "name": event_name,
                "date": self.currently_selected_date.date(),
            }
            # Send the the event to the server
            print(event_form)
            response = EventsRoutes(self.manager.connection_client).post_create_event(
                data=event_form
            )
            print(response.status_code)

            dialog.dismiss()  # Close the dialog

    def get_all_events(self, *args):
        """Fetch all events for the current month and populate the events dictionary."""
        # Example: Fetch events from your API or database
        response = EventsRoutes(self.manager.connection_client).get_events()

        if response and response.status_code == 200:
            data = response.json()  # Assuming the response is in JSON format

            for event in data:
                # Extract date and event description (this will depend on your data structure)
                event_date_str = event.get("date")  # Format: 'YYYY-MM-DD'
                event_name = event.get("name")  # Description of the event

                if event_date_str:
                    if event_date_str not in self.events:
                        self.events[event_date_str] = []

                    # Check if the event name is already in the list for this date
                    if event_name not in self.events[event_date_str]:
                        # Append the event name to the list for that date if it's not already present
                        self.events[event_date_str].append(event_name)

        print(self.events)

    def add_recurring_event(self, event_description, recurrence_rule):
        if not self.currently_selected_date:
            print("No day selected to add a recurring event.")
            return

        if recurrence_rule == "monthly":
            # Add the event for the same day in every upcoming month
            for month in range(1, 13):
                try:
                    event_date = self.currently_selected_date.replace(month=month)
                    self.add_event(event_description)
                except ValueError:
                    # This handles cases like when the day doesn't exist in some months (e.g., 31st February)
                    print(f"Skipping invalid date for month: {month}")
        else:
            print(f"Unsupported recurrence rule: {recurrence_rule}")

    def add_event_to_date(self, event_date, event_description):
        if event_date not in self.events:
            self.events[event_date] = []
        self.events[event_date].append(event_description)
