import tkinter as tk
from ui import IntelligentStudyPlannerUI


def main():
    root = tk.Tk()
    app = IntelligentStudyPlannerUI(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()


if __name__ == "__main__":
    main()