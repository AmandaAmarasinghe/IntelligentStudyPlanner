import json
import os
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np


class StudyPlannerLogic:

    def __init__(self, data_file="study_planner_data.json"):
        self.data_file = data_file
        self.subjects = []
        self.study_sessions = []
        self.load_data()

    # Data persistence

    def load_data(self):

        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.subjects = data.get("subjects", [])
                self.study_sessions = data.get("study_sessions", [])
            except Exception:
                self.subjects = []
                self.study_sessions = []
        else:
            self.subjects = []
            self.study_sessions = []

    def save_data(self):
        # Save subjects and sessions to a JSON file
        data = {
            "subjects": self.subjects,
            "study_sessions": self.study_sessions,
        }

        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            return False, str(e)

    # Subject operations

    def add_subject(self, name, exam_date, difficulty, past_score, daily_study_hours=3):
        # Add a new subject
        recommended_hours = self.predict_study_hours(
            difficulty, past_score, exam_date
        )

        subject = {
            "name": name,
            "exam_date": exam_date,
            "difficulty": difficulty,
            "past_score": past_score,
            "recommended_hours": recommended_hours,
            "hours_completed": 0,
            "daily_study_hours": daily_study_hours,
        }

        self.subjects.append(subject)
        self.save_data()
        return recommended_hours

    def delete_subject(self, idx):
        # Delete a subject and its associated sessions
        if 0 <= idx < len(self.subjects):
            subject_name = self.subjects[idx]["name"]

            del self.subjects[idx]

            self.study_sessions = [
                s for s in self.study_sessions
                if s["subject"] != subject_name
            ]

            self.save_data()
            return True

        return False

    def get_subject_by_name(self, name):
        # Get subject by name
        for subject in self.subjects:
            if subject["name"] == name:
                return subject

        return None

    def get_subject_names(self):
        # Get list of all subject names
        return [s["name"] for s in self.subjects]

    # Session operations

    def add_session(self, subject, date, start_time, end_time, notes=""):
        # Add a new study session
        session = {
            "subject": subject,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "notes": notes,
            "completed": False,
        }

        self.study_sessions.append(session)
        self.save_data()

        return True

    def delete_session(self, idx):
        # Delete a study session
        if 0 <= idx < len(self.study_sessions):
            del self.study_sessions[idx]
            self.save_data()
            return True

        return False

    def complete_session(self, idx):
        # Mark a session as completed and update subject hours
        if 0 <= idx < len(self.study_sessions):
            session = self.study_sessions[idx]

            # Prevent completing the same session twice
            if session.get("completed", False):
                return 0, None

            session["completed"] = True

            # Update subject hours
            start = datetime.strptime(session["start_time"], "%H:%M")
            end = datetime.strptime(session["end_time"], "%H:%M")

            hours = (end - start).seconds / 3600

            for subject in self.subjects:
                if subject["name"] == session["subject"]:
                    subject["hours_completed"] += hours
                    break

            self.save_data()

            return hours, session["subject"]

        return 0, None

    def get_sessions_by_date(self):
        # Group sessions by date
        sessions_by_date = {}

        for session in self.study_sessions:
            date = session["date"]

            if date not in sessions_by_date:
                sessions_by_date[date] = []

            sessions_by_date[date].append(session)

        return dict(sorted(sessions_by_date.items()))

    def get_session_index(self, session):
        # Get the index of a session
        try:
            return self.study_sessions.index(session)
        except ValueError:
            return -1

    # Validation methods

    def validate_date_format(self, date_str):
        # Validate date format (YYYY-MM-DD)
        import re

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"

        if not re.match(date_pattern, date_str):
            return (
                False,
                "Date must be in YYYY-MM-DD format with 2 digits for month and day",
            )

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return True, date_obj

        except ValueError:
            return (
                False,
                "Invalid calendar date. Please check the day/month values",
            )

    def validate_future_date(self, date_obj):
        # Check if date is in the future
        today = datetime.now()

        if date_obj.date() <= today.date():
            return False, "Exam date must be in the future"

        return True, None

    def validate_date_not_past(self, date_obj):
        # Check if date is not in the past
        today = datetime.now().date()

        if date_obj.date() < today:
            return (
                False,
                "Cannot schedule sessions for past dates. Please select today or a future date.",
            )

        return True, None

    def validate_session_not_in_past(
        self,
        date_str,
        start_time,
        end_time
    ):
        """
        Prevent scheduling a session that has already started or finished.

        For today:
        - 09:00-11:00 at 12:50 -> rejected
        - 12:00-13:00 at 12:50 -> rejected
        - 13:00-14:00 at 12:50 -> allowed

        For a future date:
        - Any valid future time is allowed.
        """

        try:
            session_date = datetime.strptime(
                date_str, "%Y-%m-%d"
            ).date()

            start_dt = datetime.strptime(
                start_time, "%H:%M"
            ).time()

            end_dt = datetime.strptime(
                end_time, "%H:%M"
            ).time()

        except ValueError:
            return False, "Invalid date or time."

        today = datetime.now().date()

        # Only check the current time when the session is today
        if session_date == today:
            now = datetime.now()

            session_start = datetime.combine(
                session_date,
                start_dt
            )

            session_end = datetime.combine(
                session_date,
                end_dt
            )

            # The whole session must be in the future
            if session_start <= now:
                return (
                    False,
                    f"Cannot schedule a session that has already started or passed.\n\n"
                    f"Current time: {now.strftime('%H:%M')}\n"
                    f"Selected session: {start_time} - {end_time}\n\n"
                    f"Please select a future time.",
                )

            if session_end <= now:
                return (
                    False,
                    f"Cannot schedule a session that has already ended.\n\n"
                    f"Current time: {now.strftime('%H:%M')}\n"
                    f"Selected session: {start_time} - {end_time}\n\n"
                    f"Please select a future time.",
                )

        return True, None

    def validate_difficulty(self, difficulty_str):
        # Validate difficulty input
        try:
            difficulty = int(difficulty_str)

            if not (1 <= difficulty <= 5):
                return False, "Difficulty must be a number between 1 and 5", None

            return True, None, difficulty

        except ValueError:
            return False, "Difficulty must be a number between 1 and 5", None

    def validate_past_score(self, score_str):
        # Validate past score input
        if not score_str:
            return (
                False,
                "Past score is required. Please enter a value between 0-100.",
                None,
            )

        try:
            score = int(score_str)

            if not (0 <= score <= 100):
                return (
                    False,
                    "Past score must be a number between 0-100",
                    None,
                )

            return True, None, score

        except ValueError:
            return (
                False,
                "Past score must be a number between 0-100",
                None,
            )

    def validate_time_format(self, start_time, end_time):
        # Validate time format and logical ordering
        try:
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")

            if start >= end:
                return (
                    False,
                    "Times must be in HH:MM format and end time must be after start time",
                    None,
                    None,
                )

            return True, None, start, end

        except ValueError:
            return (
                False,
                "Times must be in HH:MM format and end time must be after start time",
                None,
                None,
            )

    def validate_daily_study_hours(self, hours_str):
        # Validate daily study hours input
        try:
            hours = float(hours_str) if hours_str else 3

            if hours <= 0:
                return (
                    False,
                    "Daily study hours must be a positive number",
                    None,
                )

            return True, None, hours

        except ValueError:
            return False, "Daily study hours must be a number", None

    def validate_session_duration(self, subject_name, session_hours):
        # Validate if session duration is within daily limit
        subject = self.get_subject_by_name(subject_name)

        if subject:
            daily_hours = subject.get("daily_study_hours", 10)

            if session_hours > daily_hours:
                return (
                    False,
                    f"Session duration ({session_hours:.1f}h) exceeds daily study hours "
                    f"({daily_hours}h) for {subject_name}.\n\n"
                    f"Please schedule a session of {daily_hours}h or less.",
                )

            return True, None

        return False, "Subject not found"

    def check_exam_date_conflict(self, date_obj):
        # Check if the session date conflicts with any exam dates
        exam_subjects_on_date = []

        for subj in self.subjects:
            exam_date_obj = datetime.strptime(
                subj["exam_date"], "%Y-%m-%d"
            ).date()

            if date_obj.date() == exam_date_obj:
                exam_subjects_on_date.append(subj["name"])

        if exam_subjects_on_date:
            exam_list = ", ".join(exam_subjects_on_date)

            return (
                False,
                f"Cannot schedule study sessions on "
                f"{date_obj.strftime('%Y-%m-%d')}.\n\n"
                f"Exam(s) scheduled on this date: {exam_list}\n\n"
                f"Please choose a different date for studying.",
            )

        return True, None

    def validate_auto_schedule_params(
        self,
        start_time,
        end_time,
        duration_str,
        break_str
    ):
        # Validate auto-schedule parameters
        is_valid, error, start_dt, end_dt = self.validate_time_format(
            start_time,
            end_time
        )

        if not is_valid:
            return False, error

        try:
            duration = float(duration_str)
            break_time = float(break_str)

            if duration <= 0 or break_time < 0:
                return (
                    False,
                    "Duration must be positive and break time cannot be negative",
                )

            return True, None

        except ValueError:
            return (
                False,
                "Duration must be a number and break time must be a number",
            )

    # ML prediction

    def predict_study_hours(self, difficulty, past_score, exam_date):

        days_until = self.get_days_until_exam(exam_date)

        # Training data
        training_data = [
            [1, 90, 30, 8],
            [1, 70, 20, 10],
            [1, 45, 15, 13],
            [2, 85, 25, 12],
            [2, 60, 20, 15],
            [2, 40, 10, 14],
            [3, 90, 40, 15],
            [3, 75, 30, 20],
            [3, 50, 20, 26],
            [3, 30, 15, 28],
            [4, 85, 35, 25],
            [4, 70, 25, 28],
            [4, 45, 20, 35],
            [5, 90, 45, 28],
            [5, 70, 30, 35],
            [5, 40, 20, 42],
            [1, 75, 30, 10],
            [2, 75, 25, 15],
            [3, 75, 30, 20],
            [4, 75, 35, 28],
            [5, 75, 40, 35],
        ]

        X_train = np.array([
            [row[0], row[1], row[2]]
            for row in training_data
        ])

        y_train = np.array([
            row[3]
            for row in training_data
        ])

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        model = LinearRegression()
        model.fit(X_train_scaled, y_train)

        X_new = np.array([
            [difficulty, past_score, days_until]
        ])

        X_new_scaled = scaler.transform(X_new)

        predicted_hours = model.predict(X_new_scaled)[0]

        predicted_hours = max(
            8,
            min(50, predicted_hours)
        )

        return round(predicted_hours)

    # Conflict detection

    def detect_conflicts(self):
        # Rule-based conflict detection
        conflicts = []

        # Check for overlapping sessions
        for i in range(len(self.study_sessions)):
            for j in range(i + 1, len(self.study_sessions)):
                session1 = self.study_sessions[i]
                session2 = self.study_sessions[j]

                if session1["date"] == session2["date"]:
                    start1 = datetime.strptime(
                        session1["start_time"], "%H:%M"
                    )
                    end1 = datetime.strptime(
                        session1["end_time"], "%H:%M"
                    )

                    start2 = datetime.strptime(
                        session2["start_time"], "%H:%M"
                    )
                    end2 = datetime.strptime(
                        session2["end_time"], "%H:%M"
                    )

                    if start1 < end2 and end1 > start2:
                        conflicts.append({
                            "type": "overlap",
                            "session1": i,
                            "session2": j,
                            "date": session1["date"],
                        })

        # Check for multiple exams on same date
        exam_dates = {}

        for subject in self.subjects:
            exam_date = subject["exam_date"]

            if exam_date not in exam_dates:
                exam_dates[exam_date] = []

            exam_dates[exam_date].append(subject["name"])

        for date, subjects in exam_dates.items():
            if len(subjects) > 1:
                conflicts.append({
                    "type": "multiple_exams",
                    "date": date,
                    "subjects": subjects,
                })

        return conflicts

    def format_conflict_messages(self, conflicts):
        # Format conflict messages for display
        if not conflicts:
            return []

        msg_lines = []

        for c in conflicts:
            if c["type"] == "overlap":
                s1 = self.study_sessions[c["session1"]]
                s2 = self.study_sessions[c["session2"]]

                msg_lines.append(
                    f"Overlap on {c['date']}: "
                    f"{s1['subject']} ({s1['start_time']}-{s1['end_time']}) "
                    f"and "
                    f"{s2['subject']} ({s2['start_time']}-{s2['end_time']})"
                )

            elif c["type"] == "multiple_exams":
                subjects = ", ".join(c["subjects"])

                msg_lines.append(
                    f"Multiple exams on {c['date']}: {subjects}"
                )

        return msg_lines

    def auto_resolve_conflict(self, conflict):
        # Automatically resolve scheduling conflicts
        if conflict["type"] == "overlap":
            session2_idx = conflict["session2"]

            old_date = datetime.strptime(
                self.study_sessions[session2_idx]["date"],
                "%Y-%m-%d"
            )

            new_date = old_date + timedelta(days=1)

            self.study_sessions[session2_idx]["date"] = (
                new_date.strftime("%Y-%m-%d")
            )

            self.save_data()

            return True

        return False

    # Auto-scheduling

    def auto_schedule(
        self,
        start_time,
        end_time,
        session_duration,
        break_time
    ):
        # Automatically generate study schedule
        # respecting daily study hour limits

        if not self.subjects:
            return False, "No subjects available"

        # Generate time slots
        time_slots = self._generate_time_slots(
            start_time,
            end_time,
            session_duration,
            break_time
        )

        if not time_slots:
            return False, "Availability is too short"

        # Prepare subjects for scheduling
        subjects_to_schedule = (
            self._prepare_subjects_for_scheduling()
        )

        if not subjects_to_schedule:
            return False, "All subjects complete or exams passed"

        # Clear existing sessions
        self.study_sessions = []

        # Schedule sessions
        scheduled_count, incomplete_subjects = (
            self._schedule_sessions(
                subjects_to_schedule,
                time_slots,
                session_duration
            )
        )

        self.save_data()

        return True, {
            "scheduled_count": scheduled_count,
            "incomplete_subjects": incomplete_subjects,
        }

    def _generate_time_slots(
        self,
        start_time,
        end_time,
        session_duration,
        break_time
    ):
        # Generate available time slots
        time_slots = []

        start_dt = datetime.strptime(
            start_time, "%H:%M"
        )

        end_dt = datetime.strptime(
            end_time, "%H:%M"
        )

        current_time = start_dt

        while (
            current_time + timedelta(hours=session_duration)
            <= end_dt
        ):
            slot_start = current_time.strftime("%H:%M")

            slot_end = (
                current_time
                + timedelta(hours=session_duration)
            ).strftime("%H:%M")

            time_slots.append(
                (slot_start, slot_end)
            )

            if break_time > 0:
                current_time += timedelta(
                    hours=session_duration + break_time
                )
            else:
                current_time += timedelta(
                    hours=session_duration
                )

        return time_slots

    def _prepare_subjects_for_scheduling(self):
        # Prepare subjects that need scheduling
        subjects_to_schedule = []

        for subject in self.subjects:
            remaining_hours = (
                subject["recommended_hours"]
                - subject["hours_completed"]
            )

            if remaining_hours <= 0:
                continue

            exam_date = datetime.strptime(
                subject["exam_date"],
                "%Y-%m-%d"
            )

            days_until_exam = (
                exam_date.date() - datetime.now().date()
            ).days

            if days_until_exam <= 0:
                continue

            subjects_to_schedule.append({
                "name": subject["name"],
                "remaining_hours": remaining_hours,
                "daily_limit": subject.get(
                    "daily_study_hours",
                    2
                ),
                "exam_date": exam_date,
                "days_until_exam": days_until_exam,
                "hours_scheduled": 0,
            })

        # Sort by urgency
        subjects_to_schedule.sort(
            key=lambda x: x["days_until_exam"]
        )

        return subjects_to_schedule

    def _schedule_sessions(
        self,
        subjects_to_schedule,
        time_slots,
        session_duration
    ):
        # Schedule sessions for subjects
        daily_hours_tracker = {}

        scheduled_count = 0
        incomplete_subjects = []

        today_date = datetime.now().date()

        max_days = max(
            s["days_until_exam"]
            for s in subjects_to_schedule
        )

        for day_offset in range(max_days):
            schedule_date_obj = (
                today_date
                + timedelta(days=day_offset)
            )

            schedule_date = datetime.combine(
                schedule_date_obj,
                datetime.min.time()
            )

            date_str = schedule_date.strftime(
                "%Y-%m-%d"
            )

            # Skip weekends
            if schedule_date.weekday() >= 5:
                continue

            if date_str not in daily_hours_tracker:
                daily_hours_tracker[date_str] = {}

            # Schedule sessions for this day
            for slot_start, slot_end in time_slots:

                # IMPORTANT:
                # Do not create a session in the past
                # when scheduling for today.
                if schedule_date_obj == today_date:
                    now = datetime.now()

                    slot_start_datetime = datetime.combine(
                        schedule_date_obj,
                        datetime.strptime(
                            slot_start,
                            "%H:%M"
                        ).time()
                    )

                    if slot_start_datetime <= now:
                        continue

                if not self._is_slot_available(
                    date_str,
                    slot_start,
                    slot_end
                ):
                    continue

                # Find a subject to schedule
                for subject in subjects_to_schedule:

                    if (
                        subject["hours_scheduled"]
                        >= subject["remaining_hours"]
                    ):
                        continue

                    if (
                        schedule_date
                        >= subject["exam_date"]
                        - timedelta(days=1)
                    ):
                        continue

                    subject_name = subject["name"]

                    hours_today = (
                        daily_hours_tracker[
                            date_str
                        ].get(
                            subject_name,
                            0
                        )
                    )

                    if (
                        hours_today
                        >= subject["daily_limit"]
                    ):
                        continue

                    # Calculate session hours
                    hours_remaining_today = (
                        subject["daily_limit"]
                        - hours_today
                    )

                    hours_remaining_total = (
                        subject["remaining_hours"]
                        - subject["hours_scheduled"]
                    )

                    actual_session_hours = min(
                        session_duration,
                        hours_remaining_today,
                        hours_remaining_total
                    )

                    if actual_session_hours < 0.5:
                        continue

                    # Create session
                    start_dt = datetime.strptime(
                        slot_start,
                        "%H:%M"
                    )

                    end_dt = (
                        start_dt
                        + timedelta(
                            hours=actual_session_hours
                        )
                    )

                    actual_end_time = (
                        end_dt.strftime("%H:%M")
                    )

                    # Extra safety check for today
                    if schedule_date_obj == today_date:
                        actual_start_datetime = datetime.combine(
                            schedule_date_obj,
                            start_dt.time()
                        )

                        if actual_start_datetime <= datetime.now():
                            continue

                    self.add_session(
                        subject_name,
                        date_str,
                        slot_start,
                        actual_end_time,
                        "Auto-scheduled"
                    )

                    scheduled_count += 1

                    # Update trackers
                    subject["hours_scheduled"] += (
                        actual_session_hours
                    )

                    daily_hours_tracker[
                        date_str
                    ][subject_name] = (
                        hours_today
                        + actual_session_hours
                    )

                    break

        # Check for incomplete subjects
        for subject in subjects_to_schedule:
            if (
                subject["hours_scheduled"]
                < subject["remaining_hours"]
            ):
                incomplete_subjects.append(
                    f"{subject['name']} "
                    f"(scheduled "
                    f"{subject['hours_scheduled']:.1f}h / "
                    f"{subject['remaining_hours']:.1f}h needed)"
                )

        return scheduled_count, incomplete_subjects

    def _is_slot_available(
        self,
        date_str,
        slot_start,
        slot_end
    ):
        # Check if a time slot is available
        for existing_session in self.study_sessions:

            if existing_session["date"] == date_str:

                existing_start = datetime.strptime(
                    existing_session["start_time"],
                    "%H:%M"
                )

                existing_end = datetime.strptime(
                    existing_session["end_time"],
                    "%H:%M"
                )

                slot_start_dt = datetime.strptime(
                    slot_start,
                    "%H:%M"
                )

                slot_end_dt = datetime.strptime(
                    slot_end,
                    "%H:%M"
                )

                if (
                    slot_start_dt < existing_end
                    and slot_end_dt > existing_start
                ):
                    return False

        return True

    # Statistics

    def get_statistics(self):
        # Calculate dashboard statistics
        total_subjects = len(self.subjects)

        total_hours_needed = sum(
            s["recommended_hours"]
            for s in self.subjects
        )

        total_hours_completed = sum(
            s["hours_completed"]
            for s in self.subjects
        )

        total_sessions = len(
            self.study_sessions
        )

        completed_sessions = sum(
            1
            for s in self.study_sessions
            if s.get("completed", False)
        )

        return {
            "total_subjects": total_subjects,
            "total_hours_needed": total_hours_needed,
            "total_hours_completed": total_hours_completed,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
        }

    def calculate_subject_progress(self, subject):
        # Calculate progress percentage for a subject
        if subject["recommended_hours"] <= 0:
            return 0

        progress = (
            subject["hours_completed"]
            / subject["recommended_hours"]
        ) * 100

        return min(progress, 100)

    def get_progress_color(self, progress):
        # Get color based on progress percentage
        if progress >= 100:
            return "#48bb78"

        elif progress >= 50:
            return "#4c51bf"

        else:
            return "#ed8936"

    # Reminder system

    def get_upcoming_sessions_today(self):
        # Get upcoming sessions for today
        now = datetime.now()

        today = now.strftime(
            "%Y-%m-%d"
        )

        upcoming = []

        for idx, session in enumerate(
            self.study_sessions
        ):
            if (
                session["date"] == today
                and not session.get(
                    "completed",
                    False
                )
            ):
                session_time = datetime.strptime(
                    session["start_time"],
                    "%H:%M"
                )

                time_diff = (
                    session_time.hour * 60
                    + session_time.minute
                    - (
                        now.hour * 60
                        + now.minute
                    )
                )

                if (
                    14 <= time_diff <= 16
                    and not session.get(
                        "reminded",
                        False
                    )
                ):
                    upcoming.append(
                        (idx, session)
                    )

        return upcoming

    def mark_session_reminded(self, idx):
        # Mark a session as reminded
        if 0 <= idx < len(
            self.study_sessions
        ):
            self.study_sessions[
                idx
            ]["reminded"] = True

            self.save_data()

    # Utility functions

    def get_days_until_exam(self, exam_date_str):
        # Return number of days from today until exam date
        try:
            exam_date = datetime.strptime(
                exam_date_str,
                "%Y-%m-%d"
            ).date()

            today = datetime.now().date()

            delta = (
                exam_date - today
            ).days

            return max(delta, 0)

        except Exception:
            return 0

    def format_date_display(self, date_str):
        # Format date for display
        try:
            date_obj = datetime.strptime(
                date_str,
                "%Y-%m-%d"
            )

            return date_obj.strftime(
                "%A, %B %d, %Y"
            )

        except Exception:
            return date_str