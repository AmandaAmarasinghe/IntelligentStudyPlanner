import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from logic import StudyPlannerLogic


class IntelligentStudyPlannerUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent Study Planner")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f4ff")

        # Initialize logic layer
        self.logic = StudyPlannerLogic()

        # Create main container
        self.create_widgets()

        # Start reminder checks
        self.check_reminders()

        # Show subjects tab by default
        self.show_subjects_tab()

    # UI setup

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(
            self.root,
            bg="#8B008B",
            height=100
        )
        header_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        title_label = tk.Label(
            header_frame,
            text="🧠 Intelligent Study Planner",
            font=("Arial", 24, "bold"),
            bg="#8B008B",
            fg="white",
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="AI-powered scheduling with conflict detection",
            font=("Arial", 12),
            bg="#8B008B",
            fg="#e0e7ff",
        )
        subtitle_label.pack()

        # Tab buttons
        tab_frame = tk.Frame(
            self.root,
            bg="#f0f4ff"
        )
        tab_frame.pack(
            fill="x",
            padx=20
        )

        btn_style = {
            "font": ("Arial", 12, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 20,
            "pady": 10,
            "cursor": "hand2",
        }

        self.subjects_btn = tk.Button(
            tab_frame,
            text="📚 Subjects",
            command=self.show_subjects_tab,
            **btn_style
        )
        self.subjects_btn.pack(
            side="left",
            padx=5
        )

        self.schedule_btn = tk.Button(
            tab_frame,
            text="📅 Schedule",
            command=self.show_schedule_tab,
            **btn_style
        )
        self.schedule_btn.pack(
            side="left",
            padx=5
        )

        self.dashboard_btn = tk.Button(
            tab_frame,
            text="📊 Dashboard",
            command=self.show_dashboard_tab,
            **btn_style
        )
        self.dashboard_btn.pack(
            side="left",
            padx=5
        )

        # Content frame
        self.content_frame = tk.Frame(
            self.root,
            bg="#f0f4ff"
        )
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

    def highlight_tab(self, active_btn):
        # Highlight active tab
        for btn in [
            self.subjects_btn,
            self.schedule_btn,
            self.dashboard_btn
        ]:
            btn.config(
                bg="#D8B9FF",
                fg="#8B008B"
            )

        active_btn.config(
            bg="#8B008B",
            fg="white"
        )

    def clear_content(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # Subjects Tab

    def show_subjects_tab(self):
        self.highlight_tab(self.subjects_btn)
        self.clear_content()

        conflicts = self.logic.detect_conflicts()

        if conflicts:
            self.show_conflict_alert(conflicts)

        header = tk.Frame(
            self.content_frame,
            bg="#f0f4ff"
        )
        header.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            header,
            text="Your Subjects",
            font=("Arial", 18, "bold"),
            bg="#f0f4ff",
            fg="#1a202c",
        ).pack(side="left")

        tk.Button(
            header,
            text="➕ Add Subject",
            command=self.show_add_subject_dialog,
            bg="#8B008B",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(side="right")

        canvas = tk.Canvas(
            self.content_frame,
            bg="#f0f4ff",
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            self.content_frame,
            orient="vertical",
            command=canvas.yview
        )

        scrollable_frame = tk.Frame(
            canvas,
            bg="#f0f4ff"
        )

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )

        canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        if not self.logic.subjects:
            tk.Label(
                scrollable_frame,
                text="No subjects added yet. Click 'Add Subject' to get started!",
                font=("Arial", 12),
                bg="#f0f4ff",
                fg="#718096",
            ).pack(pady=50)

        else:
            row, col = 0, 0

            for idx, subject in enumerate(
                self.logic.subjects
            ):
                self.create_subject_card(
                    scrollable_frame,
                    subject,
                    idx,
                    row,
                    col
                )

                col += 1

                if col > 1:
                    col = 0
                    row += 1

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    def create_subject_card(
        self,
        parent,
        subject,
        idx,
        row,
        col
    ):
        card = tk.Frame(
            parent,
            bg="#ECD9FF",
            relief="solid",
            bd=1
        )

        card.grid(
            row=row,
            column=col,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        parent.columnconfigure(
            col,
            weight=1
        )

        header = tk.Frame(
            card,
            bg="#ECD9FF"
        )

        header.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            header,
            text=subject["name"],
            font=("Arial", 16, "bold"),
            bg="#ECD9FF",
            fg="#1a202c",
        ).pack(side="left")

        tk.Button(
            header,
            text="🗑️",
            command=lambda: self.delete_subject(idx),
            bg="#ECD9FF",
            fg="#e53e3e",
            font=("Arial", 14),
            relief="flat",
            cursor="hand2",
        ).pack(side="right")

        details_frame = tk.Frame(
            card,
            bg="#ECD9FF"
        )

        details_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )

        details = [
            ("Exam Date:", subject["exam_date"]),
            (
                "Days Until Exam:",
                f"{self.logic.get_days_until_exam(subject['exam_date'])} days"
            ),
            (
                "Difficulty:",
                "⭐" * subject["difficulty"]
            ),
            (
                "Past Score:",
                f"{subject['past_score']}%"
            ),
            (
                "Total Study Hours:",
                f"{subject['recommended_hours']}h"
            ),
            (
                "Daily Study Hours:",
                f"{subject.get('daily_study_hours', 'N/A')}h"
            ),
        ]

        for label, value in details:
            row_frame = tk.Frame(
                details_frame,
                bg="#ECD9FF"
            )

            row_frame.pack(
                fill="x",
                pady=2
            )

            tk.Label(
                row_frame,
                text=label,
                font=("Arial", 10),
                bg="#ECD9FF",
                fg="#4a5568",
            ).pack(side="left")

            tk.Label(
                row_frame,
                text=value,
                font=("Arial", 10, "bold"),
                bg="#ECD9FF",
                fg="#2d3748",
            ).pack(side="right")

        progress_frame = tk.Frame(
            card,
            bg="#ECD9FF"
        )

        progress_frame.pack(
            fill="x",
            padx=15,
            pady=(10, 15)
        )

        progress = self.logic.calculate_subject_progress(
            subject
        )

        progress_bg = tk.Canvas(
            progress_frame,
            height=20,
            bg="#f5f5f5",
            highlightthickness=0
        )

        progress_bg.pack(
            fill="x"
        )

        progress_bar = tk.Canvas(
            progress_frame,
            height=20,
            bg="#8B008B",
            highlightthickness=0
        )

        progress_bar.place(
            x=0,
            y=0,
            relwidth=progress / 100,
            height=20
        )

        tk.Label(
            progress_frame,
            text=f"{int(progress)}% Complete",
            font=("Arial", 9),
            bg="#ECD9FF",
            fg="#4a5568",
        ).pack(
            pady=(5, 0)
        )

    def show_add_subject_dialog(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Subject")
        dialog.geometry("450x450")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Add New Subject",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1a202c",
        ).pack(pady=20)

        form_frame = tk.Frame(
            dialog,
            bg="white"
        )

        form_frame.pack(
            padx=30,
            fill="both",
            expand=True
        )

        tk.Label(
            form_frame,
            text="Subject Name:",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        name_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        name_entry.pack(fill="x")

        tk.Label(
            form_frame,
            text="Exam Date (YYYY-MM-DD):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        date_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        date_entry.pack(fill="x")

        tk.Label(
            form_frame,
            text="Difficulty (1-5):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        difficulty_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=10
        )

        difficulty_entry.insert(0, "3")
        difficulty_entry.pack(fill="x")

        tk.Label(
            form_frame,
            text="Past Score (%) - Required (0-100):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        score_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        score_entry.insert(0, "75")
        score_entry.pack(fill="x")

        tk.Label(
            form_frame,
            text="Daily Study Hours:",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        daily_study_hours_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11)
        )

        daily_study_hours_entry.insert(0, "3")
        daily_study_hours_entry.pack(fill="x")

        btn_frame = tk.Frame(
            dialog,
            bg="white"
        )

        btn_frame.pack(pady=20)

        def add_subject():

            name = name_entry.get().strip()
            exam_date = date_entry.get().strip()

            if not name:
                messagebox.showerror(
                    "Invalid Input",
                    "Subject name is required."
                )
                return

            is_valid, error, difficulty = (
                self.logic.validate_difficulty(
                    difficulty_entry.get()
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Input",
                    error
                )
                return

            is_valid, error, past_score = (
                self.logic.validate_past_score(
                    score_entry.get().strip()
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Input",
                    error
                )
                return

            is_valid, date_obj_or_error = (
                self.logic.validate_date_format(
                    exam_date
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Date",
                    date_obj_or_error
                )
                return

            date_obj = date_obj_or_error

            is_valid, error = (
                self.logic.validate_future_date(
                    date_obj
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Date",
                    error
                )
                return

            is_valid, error, daily_study_hours = (
                self.logic.validate_daily_study_hours(
                    daily_study_hours_entry.get()
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Input",
                    error
                )
                return

            recommended_hours = (
                self.logic.add_subject(
                    name,
                    exam_date,
                    difficulty,
                    past_score,
                    daily_study_hours
                )
            )

            dialog.destroy()

            self.show_subjects_tab()

            messagebox.showinfo(
                "Success",
                f"Subject added! Recommended study time: "
                f"{recommended_hours} hours"
            )

        tk.Button(
            btn_frame,
            text="Add Subject",
            command=add_subject,
            bg="#48bb78",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#cbd5e0",
            fg="#2d3748",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

    def delete_subject(self, idx):

        if messagebox.askyesno(
            "Confirm Delete",
            "Delete this subject and all its sessions?"
        ):
            self.logic.delete_subject(idx)
            self.show_subjects_tab()

    # Schedule Tab

    def show_schedule_tab(self):

        self.highlight_tab(
            self.schedule_btn
        )

        self.clear_content()

        conflicts = self.logic.detect_conflicts()

        if conflicts:
            self.show_conflict_alert(
                conflicts
            )

        header = tk.Frame(
            self.content_frame,
            bg="#f0f4ff"
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            header,
            text="Study Schedule",
            font=("Arial", 18, "bold"),
            bg="#f0f4ff",
            fg="#1a202c",
        ).pack(side="left")

        btn_container = tk.Frame(
            header,
            bg="#f0f4ff"
        )

        btn_container.pack(
            side="right"
        )

        tk.Button(
            btn_container,
            text="📅 Add Session",
            command=self.show_add_session_dialog,
            bg="#8B008B",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            btn_container,
            text="🤖 Auto-Schedule",
            command=self.show_auto_schedule_settings,
            bg="#38b2ac",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

        canvas = tk.Canvas(
            self.content_frame,
            bg="#f0f4ff",
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            self.content_frame,
            orient="vertical",
            command=canvas.yview
        )

        scrollable_frame = tk.Frame(
            canvas,
            bg="#f0f4ff"
        )

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )

        canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        if not self.logic.study_sessions:

            tk.Label(
                scrollable_frame,
                text="No study sessions scheduled. "
                     "Click 'Add Session' or 'Auto-Schedule'!",
                font=("Arial", 12),
                bg="#f0f4ff",
                fg="#718096",
            ).pack(pady=50)

        else:

            sessions_by_date = (
                self.logic.get_sessions_by_date()
            )

            for date, sessions in (
                sessions_by_date.items()
            ):
                self.create_date_section(
                    scrollable_frame,
                    date,
                    sessions
                )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    def create_date_section(
        self,
        parent,
        date,
        sessions
    ):

        date_frame = tk.Frame(
            parent,
            bg="#f0f4ff"
        )

        date_frame.pack(
            fill="x",
            pady=(20, 10),
            padx=20
        )

        date_text = (
            self.logic.format_date_display(
                date
            )
        )

        tk.Label(
            date_frame,
            text=date_text,
            font=("Arial", 14, "bold"),
            bg="#f0f4ff",
            fg="#2d3748",
        ).pack(side="left")

        for session in sessions:
            self.create_session_card(
                parent,
                session,
                self.logic.get_session_index(
                    session
                )
            )

    def create_session_card(
        self,
        parent,
        session,
        idx
    ):

        card = tk.Frame(
            parent,
            bg="white",
            relief="solid",
            bd=1
        )

        card.pack(
            fill="x",
            pady=5,
            padx=20
        )

        left_frame = tk.Frame(
            card,
            bg="white"
        )

        left_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        time_text = (
            f"{session['start_time']} - "
            f"{session['end_time']}"
        )

        tk.Label(
            left_frame,
            text=time_text,
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#8B008B",
        ).pack(anchor="w")

        tk.Label(
            left_frame,
            text=session["subject"],
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#1a202c",
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        if session.get("notes"):

            tk.Label(
                left_frame,
                text=f"📝 {session['notes']}",
                font=("Arial", 10),
                bg="white",
                fg="#718096",
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

        right_frame = tk.Frame(
            card,
            bg="white"
        )

        right_frame.pack(
            side="right",
            padx=15,
            pady=15
        )

        if not session.get(
            "completed",
            False
        ):

            # The Complete button remains available.
            # Validation happens when it is clicked.
            tk.Button(
                right_frame,
                text="✓ Complete",
                command=lambda: self.complete_session(idx),
                bg="#48bb78",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5,
                relief="flat",
                cursor="hand2",
                width=12,
            ).pack(pady=2)

        else:

            tk.Label(
                right_frame,
                text="✓ Completed",
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#48bb78",
                width=12,
            ).pack(pady=2)

        tk.Button(
            right_frame,
            text="🗑️ Delete",
            command=lambda: self.delete_session(idx),
            bg="#e53e3e",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2",
            width=12,
        ).pack(pady=2)

    def show_add_session_dialog(self):

        if not self.logic.subjects:
            messagebox.showwarning(
                "No Subjects",
                "Please add subjects first!"
            )
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Study Session")
        dialog.geometry("450x450")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Schedule Study Session",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1a202c",
        ).pack(pady=20)

        form_frame = tk.Frame(
            dialog,
            bg="white"
        )

        form_frame.pack(
            padx=30,
            fill="both",
            expand=True
        )

        tk.Label(
            form_frame,
            text="Subject:",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        subject_var = tk.StringVar()

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Custom.TCombobox",
            fieldbackground="#f0f0f0",
            bg="#f0f0f0"
        )

        subject_combo = ttk.Combobox(
            form_frame,
            textvariable=subject_var,
            values=self.logic.get_subject_names(),
            font=("Arial", 11),
            state="readonly",
            style="Custom.TCombobox",
        )

        subject_combo.pack(
            fill="x"
        )

        if self.logic.subjects:
            subject_combo.current(0)

        tk.Label(
            form_frame,
            text="Date (YYYY-MM-DD):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        date_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        date_entry.insert(
            0,
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        date_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="Start Time (HH:MM):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        start_time_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        start_time_entry.insert(
            0,
            "09:00"
        )

        start_time_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="End Time (HH:MM):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        end_time_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        end_time_entry.insert(
            0,
            "11:00"
        )

        end_time_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="Notes (optional):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        notes_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        notes_entry.pack(
            fill="x"
        )

        btn_frame = tk.Frame(
            dialog,
            bg="white"
        )

        btn_frame.pack(
            pady=20
        )

        def add_session():

            subject = subject_var.get()
            date = date_entry.get().strip()
            start_time = start_time_entry.get().strip()
            end_time = end_time_entry.get().strip()
            notes = notes_entry.get().strip()

            # Validate date format
            is_valid, date_obj_or_error = (
                self.logic.validate_date_format(
                    date
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Date",
                    date_obj_or_error
                )
                return

            date_obj = date_obj_or_error

            # Check if date is in the past
            is_valid, error = (
                self.logic.validate_date_not_past(
                    date_obj
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Date",
                    error
                )
                return

            # Check exam date
            is_valid, error = (
                self.logic.check_exam_date_conflict(
                    date_obj
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Date",
                    error
                )
                return

            # Validate time format
            is_valid, error, start, end = (
                self.logic.validate_time_format(
                    start_time,
                    end_time
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Time",
                    error
                )
                return

            # Prevent past times when scheduling for today
            is_valid, error = (
                self.logic.validate_session_not_in_past(
                    date,
                    start_time,
                    end_time
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Past Time Not Allowed",
                    error
                )
                return

            # Check daily study hours
            session_hours = (
                end - start
            ).seconds / 3600

            is_valid, error = (
                self.logic.validate_session_duration(
                    subject,
                    session_hours
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Session Duration",
                    error
                )
                return

            self.logic.add_session(
                subject,
                date,
                start_time,
                end_time,
                notes
            )

            dialog.destroy()

            self.show_schedule_tab()

        tk.Button(
            btn_frame,
            text="Add Session",
            command=add_session,
            bg="#48bb78",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#cbd5e0",
            fg="#2d3748",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

    def complete_session(self, idx):

        # Check whether the session is allowed to be completed.
        is_valid, error = (
            self.logic.validate_session_completion(idx)
        )

        if not is_valid:

            messagebox.showwarning(
                "Session Not Available",
                error
            )

            return

        hours, subject_name = (
            self.logic.complete_session(idx)
        )

        if hours > 0:

            self.show_schedule_tab()

            messagebox.showinfo(
                "Session Completed",
                f"Great job! {hours:.1f} hours added "
                f"to {subject_name}"
            )

    def delete_session(self, idx):

        if messagebox.askyesno(
            "Confirm Delete",
            "Delete this study session?"
        ):
            self.logic.delete_session(idx)
            self.show_schedule_tab()

    # Auto Schedule

    def show_auto_schedule_settings(self):

        if not self.logic.subjects:
            messagebox.showwarning(
                "No Subjects",
                "Please add subjects first!"
            )
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Auto-Schedule Settings")
        dialog.geometry("450x500")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="⚙️ Auto-Schedule Settings",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1a202c",
        ).pack(pady=20)

        form_frame = tk.Frame(
            dialog,
            bg="white"
        )

        form_frame.pack(
            padx=30,
            fill="both",
            expand=True
        )

        tk.Label(
            form_frame,
            text="Available From (HH:MM):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        start_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        start_entry.insert(
            0,
            "09:00"
        )

        start_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="Available Until (HH:MM):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        end_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        end_entry.insert(
            0,
            "21:00"
        )

        end_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="Preferred Session Duration (hours):",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        duration_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        duration_entry.insert(
            0,
            "2"
        )

        duration_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="Break Between Sessions (hours) - Optional:",
            font=("Arial", 10),
            bg="white"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        break_entry = tk.Entry(
            form_frame,
            bg="#f0f0f0",
            font=("Arial", 11),
            width=40
        )

        break_entry.insert(
            0,
            "0"
        )

        break_entry.pack(
            fill="x"
        )

        tk.Label(
            form_frame,
            text="💡 Tip: These settings will be used to generate your study schedule automatically.",
            font=("Arial", 9),
            bg="white",
            fg="#718096",
            wraplength=350,
            justify="left"
        ).pack(
            anchor="w",
            pady=(20, 0)
        )

        btn_frame = tk.Frame(
            dialog,
            bg="white"
        )

        btn_frame.pack(
            pady=20
        )

        def proceed():

            start_time = start_entry.get().strip()
            end_time = end_entry.get().strip()
            duration = duration_entry.get()
            break_time = break_entry.get()

            is_valid, error = (
                self.logic.validate_auto_schedule_params(
                    start_time,
                    end_time,
                    duration,
                    break_time
                )
            )

            if not is_valid:
                messagebox.showerror(
                    "Invalid Input",
                    error
                )
                return

            dialog.destroy()

            self.auto_schedule_with_settings(
                start_time,
                end_time,
                float(duration),
                float(break_time)
            )

        tk.Button(
            btn_frame,
            text="Generate Schedule",
            command=proceed,
            bg="#48bb78",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#cbd5e0",
            fg="#2d3748",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
        ).pack(
            side="left",
            padx=5
        )

    def auto_schedule_with_settings(
        self,
        start_time,
        end_time,
        session_duration,
        break_time
    ):

        if self.logic.study_sessions:

            if not messagebox.askyesno(
                "Auto-Schedule",
                "This will clear existing sessions. Continue?"
            ):
                return

        success, result = (
            self.logic.auto_schedule(
                start_time,
                end_time,
                session_duration,
                break_time
            )
        )

        if not success:
            messagebox.showerror(
                "Auto-Schedule Failed",
                result
            )
            return

        scheduled_count = result[
            "scheduled_count"
        ]

        incomplete_subjects = result[
            "incomplete_subjects"
        ]

        self.show_schedule_tab()

        if incomplete_subjects:

            warning_msg = (
                f"Successfully scheduled "
                f"{scheduled_count} study sessions!\n\n"
            )

            warning_msg += (
                "⚠️ Some subjects couldn't be fully scheduled:\n"
            )

            warning_msg += "\n".join(
                f"  • {subj}"
                for subj in incomplete_subjects
            )

            warning_msg += (
                "\n\nTip: Try increasing daily study hours "
                "or extending your available time window."
            )

            messagebox.showwarning(
                "Auto-Schedule Complete",
                warning_msg
            )

        else:

            messagebox.showinfo(
                "Auto-Schedule Complete",
                f"🎉 Successfully scheduled "
                f"{scheduled_count} study sessions!\n\n"
                f"All subjects scheduled to 100% completion "
                f"with proper daily limits!"
            )

    # Dashboard

    def show_dashboard_tab(self):

        self.highlight_tab(
            self.dashboard_btn
        )

        self.clear_content()

        stats_frame = tk.Frame(
            self.content_frame,
            bg="#f0f4ff"
        )

        stats_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        stats = self.logic.get_statistics()

        stat_items = [
            (
                "Total Subjects",
                stats["total_subjects"],
                "#667eea"
            ),
            (
                "Total Hours Needed",
                f"{stats['total_hours_needed']}h",
                "#f56565"
            ),
            (
                "Hours Completed",
                f"{stats['total_hours_completed']:.1f}h",
                "#48bb78"
            ),
            (
                "Study Sessions",
                stats["total_sessions"],
                "#ed8936"
            ),
            (
                "Completed Sessions",
                stats["completed_sessions"],
                "#38b2ac"
            ),
        ]

        for label, value, color in stat_items:

            self.create_stat_card(
                stats_frame,
                label,
                value,
                color
            ).pack(
                side="left",
                padx=10,
                fill="both",
                expand=True
            )

        tk.Label(
            self.content_frame,
            text="Subject Progress",
            font=("Arial", 18, "bold"),
            bg="#f0f4ff",
            fg="#1a202c",
        ).pack(
            anchor="w",
            pady=(20, 10)
        )

        canvas = tk.Canvas(
            self.content_frame,
            bg="#f0f4ff",
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            self.content_frame,
            orient="vertical",
            command=canvas.yview
        )

        scrollable_frame = tk.Frame(
            canvas,
            bg="#f0f4ff"
        )

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )

        canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        if not self.logic.subjects:

            tk.Label(
                scrollable_frame,
                text="No subjects to display",
                font=("Arial", 12),
                bg="#f0f4ff",
                fg="#718096",
            ).pack(
                pady=50
            )

        else:

            for subject in self.logic.subjects:
                self.create_progress_row(
                    scrollable_frame,
                    subject
                )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    def create_stat_card(
        self,
        parent,
        label,
        value,
        color
    ):

        card = tk.Frame(
            parent,
            bg="white",
            relief="solid",
            bd=1
        )

        tk.Label(
            card,
            text=str(value),
            font=("Arial", 24, "bold"),
            bg="white",
            fg=color,
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            card,
            text=label,
            font=("Arial", 11),
            bg="white",
            fg="#718096",
        ).pack(
            pady=(0, 20)
        )

        return card

    def create_progress_row(
        self,
        parent,
        subject
    ):

        row = tk.Frame(
            parent,
            bg="white",
            relief="solid",
            bd=1
        )

        row.pack(
            fill="x",
            pady=10,
            padx=20
        )

        left_frame = tk.Frame(
            row,
            bg="white"
        )

        left_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        tk.Label(
            left_frame,
            text=subject["name"],
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#1a202c",
        ).pack(
            anchor="w"
        )

        info_frame = tk.Frame(
            left_frame,
            bg="white"
        )

        info_frame.pack(
            anchor="w",
            pady=(5, 0)
        )

        days_left = self.logic.get_days_until_exam(
            subject["exam_date"]
        )

        tk.Label(
            info_frame,
            text=f"⏰ {days_left} days left",
            font=("Arial", 10),
            bg="white",
            fg="#718096",
        ).pack(
            side="left",
            padx=(0, 15)
        )

        tk.Label(
            info_frame,
            text=(
                f"📚 {subject['hours_completed']:.1f}/"
                f"{subject['recommended_hours']}h"
            ),
            font=("Arial", 10),
            bg="white",
            fg="#718096",
        ).pack(
            side="left"
        )

        right_frame = tk.Frame(
            row,
            bg="white",
            width=300
        )

        right_frame.pack(
            side="right",
            padx=20,
            pady=15
        )

        progress = self.logic.calculate_subject_progress(
            subject
        )

        color = self.logic.get_progress_color(
            progress
        )

        progress_bg = tk.Canvas(
            right_frame,
            height=25,
            bg="#e2e8f0",
            highlightthickness=0,
            width=300
        )

        progress_bg.pack()

        progress_bar = tk.Canvas(
            right_frame,
            height=25,
            bg=color,
            highlightthickness=0
        )

        progress_bar.place(
            x=0,
            y=0,
            width=300 * (
                progress / 100
            ),
            height=25
        )

        tk.Label(
            progress_bg,
            text=f"{int(progress)}%",
            font=("Arial", 11, "bold"),
            bg="#e2e8f0",
            fg="#4a5568",
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # Conflict handling

    def show_conflict_alert(
        self,
        conflicts
    ):

        if not conflicts:
            return

        msg_lines = (
            self.logic.format_conflict_messages(
                conflicts
            )
        )

        all_msg = "\n".join(
            msg_lines
        )

        messagebox.showwarning(
            "Scheduling Conflicts Detected",
            all_msg
        )

    # Reminder system

    def check_reminders(self):

        upcoming = (
            self.logic.get_upcoming_sessions_today()
        )

        for idx, session in upcoming:

            messagebox.showinfo(
                "Study Reminder",
                f"📚 Reminder: "
                f"{session['subject']} session starts "
                f"in 15 minutes at "
                f"{session['start_time']}!"
            )

            self.logic.mark_session_reminded(
                idx
            )

        self.root.after(
            120000,
            self.check_reminders
        )