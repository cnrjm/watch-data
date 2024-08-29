from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt, QSignalBlocker
from PyQt6.QtGui import QColor
from database import get_unique_values, query_watches, get_all_watches, clear_database, get_watch_statistics, format_price, get_filtered_values

class WatchDatabaseGUI(QMainWindow):
    def __init__(self, db_connection, initial_scrape_function):
        super().__init__()
        self.db_connection = db_connection
        self.initial_scrape_function = initial_scrape_function
        self.setWindowTitle("Watch Database Query")
        self.setGeometry(100, 100, 1000, 600)

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

        self.dropdowns = [self.brand_dropdown, self.model_dropdown, self.condition_dropdown, self.ref_dropdown, self.year_dropdown]

        # Connect dropdown change events
        for dropdown in self.dropdowns:
            dropdown.currentTextChanged.connect(self.update_dropdowns)

        # Create buttons
        query_button = QPushButton("Query Database")
        query_button.clicked.connect(self.query_database)
        
        print_all_button = QPushButton("Print All Watches")
        print_all_button.clicked.connect(self.print_all_watches)

        clear_button = QPushButton("Clear Database")
        clear_button.clicked.connect(self.clear_database)

        initial_scrape_button = QPushButton("Initial Scrape")
        initial_scrape_button.clicked.connect(self.perform_initial_scrape)

        # Create table for results
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(8)
        self.result_table.setHorizontalHeaderLabels(["ID", "Brand", "Model", "Ref", "Price", "Currency", "Condition", "Year"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable sorting
        self.result_table.setSortingEnabled(True)
        self.result_table.horizontalHeader().sectionClicked.connect(self.header_clicked)

        # Create label for statistics
        self.stats_label = QLabel()

        # Add widgets to layout
        dropdown_layout = QHBoxLayout()
        for dropdown in self.dropdowns:
            dropdown_layout.addWidget(dropdown)

        button_layout = QHBoxLayout()
        button_layout.addWidget(query_button)
        button_layout.addWidget(print_all_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(initial_scrape_button)

        self.layout.addLayout(dropdown_layout)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.stats_label)
        self.layout.addWidget(self.result_table)

        # Populate dropdowns
        self.populate_dropdowns()

    def create_dropdown(self, label):
        dropdown = QComboBox()
        dropdown.addItem(f"All {label}s")
        return dropdown

    def populate_dropdowns(self):
        for dropdown, column in zip(self.dropdowns, ['brand', 'model', 'condition', 'ref', 'year']):
            self.update_dropdown(dropdown, column)

    def update_dropdowns(self):
        sender = self.sender()
        for dropdown, column in zip(self.dropdowns, ['brand', 'model', 'condition', 'ref', 'year']):
            if dropdown != sender:
                self.update_dropdown(dropdown, column)

    def update_dropdown(self, dropdown, column):
        current_text = dropdown.currentText()
        
        with QSignalBlocker(dropdown):
            dropdown.clear()
            dropdown.addItem(f"All {column.capitalize()}s")
            
            filters = {
                'brand': self.brand_dropdown.currentText(),
                'model': self.model_dropdown.currentText(),
                'condition': self.condition_dropdown.currentText(),
                'ref': self.ref_dropdown.currentText(),
                'year': self.year_dropdown.currentText()
            }
            
            # Remove the current column from filters and "All X" values
            filters.pop(column)
            filters = {k: v for k, v in filters.items() if not v.startswith('All ')}

            values = get_filtered_values(self.db_connection, column, **filters)
            dropdown.addItems(values)

            if current_text in values or current_text == f"All {column.capitalize()}s":
                dropdown.setCurrentText(current_text)
            else:
                dropdown.setCurrentIndex(0)

    def query_database(self):
        filters = {
            'brand': self.brand_dropdown.currentText(),
            'model': self.model_dropdown.currentText(),
            'condition': self.condition_dropdown.currentText(),
            'ref': self.ref_dropdown.currentText(),
            'year': self.year_dropdown.currentText()
        }
        filters = {k: v for k, v in filters.items() if not v.startswith('All ')}

        results = query_watches(self.db_connection, **filters)
        stats = get_watch_statistics(self.db_connection, **filters)

        self.display_results(results, stats)

    def display_results(self, results, stats):
        if not results:
            self.result_table.setRowCount(0)
            self.stats_label.setText("No matches found.")
            return

        avg_price, max_price, min_price = stats
        stats_text = f"Total watches found: {len(results)}\n"
        
        if avg_price is not None:
            stats_text += f"Average Price: {format_price(avg_price)}\n"
            stats_text += f"Highest Price: {format_price(max_price)}\n"
            stats_text += f"Lowest Price: {format_price(min_price)}"
        else:
            stats_text += "No price data available for the selected criteria."
        
        self.stats_label.setText(stats_text)

        self.result_table.setSortingEnabled(False)  # Disable sorting while updating
        self.result_table.setRowCount(len(results))
        for row, watch in enumerate(results):
            for col, item in enumerate(watch):
                table_item = QTableWidgetItem()
                if col == 0:  # ID column
                    table_item.setData(Qt.ItemDataRole.DisplayRole, int(item))
                elif col == 4:  # Price column
                    try:
                        table_item.setData(Qt.ItemDataRole.DisplayRole, float(item))
                    except ValueError:
                        table_item.setData(Qt.ItemDataRole.DisplayRole, item)
                    table_item.setText(format_price(item))
                elif col == 7:  # Year column
                    try:
                        table_item.setData(Qt.ItemDataRole.DisplayRole, int(item))
                    except ValueError:
                        table_item.setData(Qt.ItemDataRole.DisplayRole, item)
                else:
                    table_item.setData(Qt.ItemDataRole.DisplayRole, str(item))
                self.result_table.setItem(row, col, table_item)

        self.result_table.resizeColumnsToContents()
        self.result_table.setSortingEnabled(True)  # Re-enable sorting

    def header_clicked(self, logical_index):
        header = self.result_table.horizontalHeader()
        order = Qt.SortOrder.AscendingOrder if header.sortIndicatorSection() != logical_index or header.sortIndicatorOrder() == Qt.SortOrder.DescendingOrder else Qt.SortOrder.DescendingOrder
        self.result_table.sortItems(logical_index, order)

        # Update header colors
        for i in range(self.result_table.columnCount()):
            if i == logical_index:
                self.result_table.horizontalHeaderItem(i).setBackground(QColor(200, 200, 255))
            else:
                self.result_table.horizontalHeaderItem(i).setBackground(QColor(240, 240, 240))

    def print_all_watches(self):
        results = get_all_watches(self.db_connection)
        stats = get_watch_statistics(self.db_connection)
        self.display_results(results, stats)

    def clear_database(self):
        reply = QMessageBox.question(self, 'Clear Database', 'Are you sure you want to clear the entire database?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            clear_database(self.db_connection)
            self.result_table.setRowCount(0)
            self.stats_label.setText("Database cleared.")
            self.populate_dropdowns()  # Refresh dropdowns after clearing

    def perform_initial_scrape(self):
        reply = QMessageBox.question(self, 'Initial Scrape', 'This will perform an initial scrape of multiple brands. Continue?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.stats_label.setText("Performing initial scrape... This may take a while.")
            self.initial_scrape_function(self.db_connection)
            self.stats_label.setText("Initial scrape completed.")
            self.populate_dropdowns()  # Refresh dropdowns after scraping