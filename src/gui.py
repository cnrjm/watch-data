import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QTextEdit
from PyQt6.QtCore import Qt
import sqlite3  # Assuming you're using SQLite for your database

class WatchDatabaseGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watch Database Query")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_ui()

    def init_ui(self):
        # Create dropdown menus
        self.brand_dropdown = self.create_dropdown("Brand")
        self.model_dropdown = self.create_dropdown("Model")
        self.condition_dropdown = self.create_dropdown("Condition")
        self.ref_dropdown = self.create_dropdown("Reference")
        self.year_dropdown = self.create_dropdown("Year")

        # Create buttons
        query_button = QPushButton("Query Database")
        query_button.clicked.connect(self.query_database)
        
        print_all_button = QPushButton("Print All Watches")
        print_all_button.clicked.connect(self.print_all_watches)

        clear_button = QPushButton("Clear Database")
        clear_button.clicked.connect(self.clear_database)

        # Create result area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)

        # Add widgets to layout
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(self.brand_dropdown)
        dropdown_layout.addWidget(self.model_dropdown)
        dropdown_layout.addWidget(self.condition_dropdown)
        dropdown_layout.addWidget(self.ref_dropdown)
        dropdown_layout.addWidget(self.year_dropdown)

        button_layout = QHBoxLayout()
        button_layout.addWidget(query_button)
        button_layout.addWidget(print_all_button)
        button_layout.addWidget(clear_button)

        self.layout.addLayout(dropdown_layout)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.result_area)

        # Populate dropdowns
        self.populate_dropdowns()

    def create_dropdown(self, label):
        dropdown = QComboBox()
        dropdown.addItem(f"All {label}s")
        return dropdown

    def populate_dropdowns(self):
        # Connect to your database and populate the dropdowns
        # This is a placeholder - you'll need to replace it with actual database queries
        conn = sqlite3.connect('your_database.db')
        cursor = conn.cursor()

        # Populate brand dropdown
        cursor.execute("SELECT DISTINCT brand FROM watches")
        brands = [row[0] for row in cursor.fetchall()]
        self.brand_dropdown.addItems(brands)

        # Repeat for other dropdowns...

        conn.close()

    def query_database(self):
        # Implement your database query logic here
        # Use the selected values from dropdowns
        brand = self.brand_dropdown.currentText()
        model = self.model_dropdown.currentText()
        condition = self.condition_dropdown.currentText()
        ref = self.ref_dropdown.currentText()
        year = self.year_dropdown.currentText()

        # Perform the query and display results
        # This is a placeholder - replace with actual query logic
        query_result = f"Querying for:\nBrand: {brand}\nModel: {model}\nCondition: {condition}\nRef: {ref}\nYear: {year}"
        self.result_area.setText(query_result)

    def print_all_watches(self):
        # Implement logic to print all watches
        self.result_area.setText("Printing all watches...")

    def clear_database(self):
        # Implement logic to clear the database
        self.result_area.setText("Clearing database...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WatchDatabaseGUI()
    window.show()
    sys.exit(app.exec())