import tkinter as tk
from ui import IntelligentStudyPlannerUI


def main():
    root = tk.Tk()
    app = IntelligentStudyPlannerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()