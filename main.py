import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FitnessTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Master Pro")
        self.root.geometry("1200x800")
        self.style = ttk.Style()
        self._configure_styles()
        self._create_widgets()
        self._init_data()
        self._setup_bindings()

    def _configure_styles(self):
        """Modern UI styling configuration"""
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Segoe UI', 11))
        self.style.configure('TButton', font=('Segoe UI', 11, 'bold'), padding=6)
        self.style.configure('TEntry', font=('Segoe UI', 11), padding=6)
        self.style.configure('Header.TFrame', background='#2c3e50')
        self.style.map('TButton', 
            foreground=[('active', 'white'), ('disabled', 'gray')],
            background=[('active', '#3498db'), ('disabled', '#bdc3c7')]
        )

    def _create_widgets(self):
        """Create modern UI components"""
        self._create_header()
        self._create_input_panel()
        self._create_stats_panel()
        self._create_status_bar()

    def _create_header(self):
        """Application header with logo"""
        header = ttk.Frame(self.root, style='Header.TFrame')
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="🏋️ FITNESS MASTER PRO", 
                font=('Segoe UI', 18, 'bold'), 
                foreground='white', 
                background='#2c3e50').pack(pady=15)

    def _create_input_panel(self):
        """Responsive input panel with modern layout"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Personal Info Section
        personal_frame = ttk.LabelFrame(main_frame, text=" Personal Information ")
        personal_frame.grid(row=0, column=0, sticky=tk.NW, padx=10, pady=10)

        self.entries = {
            'height': self._create_input_row(personal_frame, "Height (cm):", 0),
            'weight': self._create_input_row(personal_frame, "Weight (kg):", 1),
            'age': self._create_input_row(personal_frame, "Age:", 2),
            'activity': self._create_combobox(personal_frame, "Activity Level:", 
                            [1.2, 1.375, 1.55, 1.725, 1.9], 3),
            'gender': self._create_combobox(personal_frame, "Gender:", 
                            ["Male", "Female"], 4)
        }

        # Body Measurements Section
        measures_frame = ttk.LabelFrame(main_frame, text=" Body Measurements (cm) ")
        measures_frame.grid(row=0, column=1, sticky=tk.NW, padx=10, pady=10)

        self.entries.update({
            'left_arm': self._create_input_row(measures_frame, "Left Arm:", 0),
            'right_arm': self._create_input_row(measures_frame, "Right Arm:", 1),
            'left_leg': self._create_input_row(measures_frame, "Left Leg:", 2),
            'right_leg': self._create_input_row(measures_frame, "Right Leg:", 3),
            'waist': self._create_input_row(measures_frame, "Waist:", 4),
            'chest': self._create_input_row(measures_frame, "Chest:", 5)
        })

        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=20)

        self.buttons = {
            'save': ttk.Button(btn_frame, text="💾 Save Record", 
                      command=self._threaded_save),
            'stats': ttk.Button(btn_frame, text="📊 Show Stats", 
                      command=self._show_live_stats),
            'export': ttk.Button(btn_frame, text="📤 Export Data", 
                      command=self._threaded_export)
        }
        
        for btn in self.buttons.values():
            btn.pack(side=tk.LEFT, padx=8, ipadx=10)

    def _create_stats_panel(self):
        """Interactive statistics dashboard"""
        stats_frame = ttk.LabelFrame(self.root, text=" Live Statistics ")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create figure for matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=stats_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        """Modern status bar with progress"""
        self.status = ttk.Frame(self.root, height=28)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status, text="Ready", 
                                    font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.progress = ttk.Progressbar(self.status, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=10, pady=2, fill=tk.X, expand=True)

    def _create_input_row(self, parent, label, row):
        """Helper method for input rows"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        entry = ttk.Entry(parent, width=14)
        entry.grid(row=row, column=1, padx=5, pady=3)
        return entry

    def _create_combobox(self, parent, label, values, row):
        """Styled combobox creation"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        combo = ttk.Combobox(parent, values=values, state="readonly", width=12)
        combo.grid(row=row, column=1, padx=5, pady=3)
        return combo

    def _init_data(self):
        """Initialize data structures"""
        self.data = pd.DataFrame()
        self._load_data()
        
    def _load_data(self):
        """Background data loading"""
        if os.path.exists('DP/fit_clcletor/DATA/data.csv'):
            try:
                self.data = pd.read_csv('DP/fit_clcletor/DATA/data.csv', 
                                      parse_dates=['timestamp'])
                self._update_charts()
            except Exception as e:
                messagebox.showerror("Data Error", f"Cannot load data: {str(e)}")

    def _validate_inputs(self):
        """Comprehensive input validation"""
        required = {
            'height': (100, 250),  # cm
            'weight': (30, 300),   # kg
            'age': (10, 120),
            'left_arm': (10, 100),
            'right_arm': (10, 100),
            'left_leg': (20, 150),
            'right_leg': (20, 150),
            'waist': (50, 200),
            'chest': (60, 200)
        }
        
        for field, (min_val, max_val) in required.items():
            val = self.entries[field].get()
            if not val.isdigit() or not (min_val <= int(val) <= max_val):
                self._show_error(f"Invalid {field.replace('_', ' ')} value")
                return False
        return True

    def _threaded_save(self):
        """Non-blocking save operation"""
        if self._validate_inputs():
            threading.Thread(target=self._save_data, daemon=True).start()

    def _save_data(self):
        """Optimized data saving"""
        try:
            self._update_status("Saving data...", 20)
            record = self._create_record()
            
            # Append to CSV
            record_df = pd.DataFrame([record])
            header = not os.path.exists('DP/fit_clcletor/DATA/data.csv')
            record_df.to_csv('DP/fit_clcletor/DATA/data.csv', 
                            mode='a', 
                            header=header, 
                            index=False)
            
            self._update_status("Data saved successfully!", 100)
            self._clear_form()
            self._load_data()
            
        except Exception as e:
            self._show_error(f"Save failed: {str(e)}")
        finally:
            self._update_progress(0)

    def _create_record(self):
        """Create data record from inputs"""
        return {
            'timestamp': datetime.now().isoformat(),
            'gender': self.entries['gender'].get().lower(),
            'activity': float(self.entries['activity'].get()),
            'height': int(self.entries['height'].get()),
            'weight': int(self.entries['weight'].get()),
            'age': int(self.entries['age'].get()),
            'left_arm': int(self.entries['left_arm'].get()),
            'right_arm': int(self.entries['right_arm'].get()),
            'left_leg': int(self.entries['left_leg'].get()),
            'right_leg': int(self.entries['right_leg'].get()),
            'waist': int(self.entries['waist'].get()),
            'chest': int(self.entries['chest'].get()),
            'bmr': self._calculate_bmr(),
            'tdee': self._calculate_tdee()
        }

    def _calculate_bmr(self):
        """BMR calculation"""
        gender = self.entries['gender'].get().lower()
        weight = int(self.entries['weight'].get())
        height = int(self.entries['height'].get())
        age = int(self.entries['age'].get())
        
        return (10 * weight + 6.25 * height - 5 * age + 
               (5 if gender == 'male' else -161))

    def _calculate_tdee(self):
        """TDEE calculation"""
        return self._calculate_bmr() * float(self.entries['activity'].get())

    def _show_live_stats(self):
        """Update live statistics dashboard"""
        self.ax1.clear()
        self.ax2.clear()
        
        # TDEE History Plot
        self.ax1.set_title('TDEE Trend')
        if not self.data.empty:
            self.data['tdee'].plot(ax=self.ax1, color='#3498db', marker='o')
        
        # Body Measurements Radar Chart
        categories = ['Left Arm', 'Right Arm', 'Waist', 'Chest']
        values = [
            self.data['left_arm'].mean(),
            self.data['right_arm'].mean(),
            self.data['waist'].mean(),
            self.data['chest'].mean()
        ]
        
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        angles += angles[:1]
        
        self.ax2.plot(angles, values + values[:1], color='#e74c3c')
        self.ax2.fill(angles, values + values[:1], alpha=0.25, color='#e74c3c')
        self.ax2.set_xticks(angles[:-1])
        self.ax2.set_xticklabels(categories)
        self.ax2.set_title('Body Measurements')
        
        self.canvas.draw()

    def _update_status(self, message, progress=0):
        """Update status bar"""
        self.root.after(0, lambda: self.status_label.config(text=message))
        self._update_progress(progress)

    def _update_progress(self, value):
        """Update progress bar"""
        self.root.after(0, lambda: self.progress['value'] == value)

    def _show_error(self, message):
        """Show error message"""
        self.root.after(0, lambda: messagebox.showerror("Error", message))

    def _clear_form(self):
        """Clear all inputs"""
        for entry in self.entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, ttk.Combobox):
                entry.set('')

    def _threaded_export(self):
        """Export data in background"""
        threading.Thread(target=self._export_data, daemon=True).start()

    def _export_data(self):
        """Export data to Excel"""
        try:
            self._update_status("Exporting...", 50)
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            if path:
                self.data.to_excel(path, index=False)
                self._update_status("Export completed!", 100)
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
        finally:
            self._update_progress(0)

    def _setup_bindings(self):
        """Configure keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self._threaded_save())
        self.root.bind('<Control-e>', lambda e: self._threaded_export())

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessTracker(root)
    root.mainloop()