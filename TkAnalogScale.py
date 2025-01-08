import tkinter as tk

class AnalogScale(tk.Frame):
    def __init__(self, parent, from_=0, to=1000, width=330, height=90, bg="lightgreen", scale_text="Analog_Scale", command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.from_ = from_
        self.to = to
        self.width = width
        self.height = height
        self.bg = bg
        self.command = command
        self.value = from_

        # Create a canvas to draw the scale and needle
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg=self.bg)
        self.canvas.pack()

        self._draw_scale(scale_text, to)

        # needle (initially positioned at the minimum value)
        self.needle_x = 10  # Start position
        self.needle = self.canvas.create_polygon(
            self.needle_x - 2, 50,
            self.needle_x + 2, 50,
            self.needle_x + 2, 10,
            self.needle_x, 3,
            self.needle_x - 2, 10,
            fill="black"
        )

    def _draw_scale(self, scale_text, to):
        """Draws the scale with ticks and labels."""
        for i in range(51):  #51 ticks for values 0 to 1000 in steps of 20
            x = 10 + (i * (300 / 50)) 
            if i % 5 == 0:  #Long tick and add a label
                self.canvas.create_line(x, 20, x, 50, width=2, fill="black")  # Long tick
                self.canvas.create_text(x, 60, text=f"{i * (to//50)}", font=("Arial", 10), fill="black")  # Tick label
            else:
                self.canvas.create_line(x, 30, x, 50, width=1, fill="black")  # Short tick
        # Add a label
        self.canvas.create_text(self.width // 2, self.height - 10, text=scale_text, font=("Arial", 9), fill="black")

    def _update_needle(self):
        """Updates the needle's position based on the current value."""
        needle_x = 10 + ((self.value - self.from_) / (self.to - self.from_)) * 300
        self.canvas.coords(
            self.needle,
            needle_x - 2, 50,
            needle_x + 2, 50,
            needle_x + 2, 10,
            needle_x, 23,
            needle_x - 2, 10
        )

    def set(self, value):
        """Sets the scale to a specific value."""
        self.value = max(self.from_, min(value, self.to))
        self._update_needle()
        if self.command:
            self.command(self.value)

    def get(self):
        """Gets the current value of the scale."""
        return self.value
