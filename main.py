from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import os

class PaniniTrackerApp(App):
    def build(self):
        self.total_cards = 630
        
        # Determine secure, private storage path on Android vs Mac
        # This keeps the save file persistent and local!
        if os.environ.get('ANDROID_ARGUMENT'):
            data_dir = self.user_data_dir
        else:
            data_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.db_file = os.path.join(data_dir, "collection.txt")
        self.load_data()

        # Main Vertical Layout
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Header Metrics
        self.metrics_label = Label(
            text="Loading...", 
            size_hint_y=None, 
            height=50, 
            font_size='18sp'
        )
        main_layout.add(self.metrics_label)

        # Input Row (Text Input + Add Button)
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.card_input = TextInput(
            hint_text="Enter numbers (e.g., 5, 12, 45)", 
            multiline=False,
            input_filter='int' # Mobile keyboard helper optimization
        )
        add_btn = Button(text="Add", size_hint_x=None, width=100, background_color=(0, 0.6, 0.3, 1))
        add_btn.bind(on_press=self.add_cards)
        
        input_layout.add(self.card_input)
        input_layout.add(add_btn)
        main_layout.add(input_layout)

        # Missing Cards Label
        main_layout.add(Label(text="Missing Cards List:", size_hint_y=None, height=30, halign='left'))

        # Scrollable View for the long text string of missing numbers
        scroll = ScrollView()
        self.missing_text_label = Label(
            text="", 
            size_hint_y=None, 
            text_size=(400, None), # Wrap box setup
            halign='center', 
            valign='top'
        )
        self.missing_text_label.bind(texture_size=self.missing_text_label.setter('text_size'))
        self.missing_text_label.bind(size=self.missing_text_label.setter('size'))
        
        scroll.add_widget(self.missing_text_label)
        main_layout.add(scroll)

        self.update_ui()
        return main_layout

    def load_data(self):
        # Create a dictionary tracking cards 1 through 630
        self.collection = {i: False for i in range(1, self.total_cards + 1)}
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    for line in f:
                        num = int(line.strip())
                        if 1 <= num <= self.total_cards:
                            self.collection[num] = True
            except:
                pass

    def save_data(self):
        try:
            with open(self.db_file, "w") as f:
                for card, owned in self.collection.items():
                    if owned:
                        f.write(f"{card}\n")
        except:
            pass

    def update_ui(self):
        owned_count = sum(1 for owned in self.collection.values() if owned)
        missing_list = [str(card) for card, owned in self.collection.items() if not owned]
        
        self.metrics_label.text = f"Owned: {owned_count}/{self.total_cards}  |  Missing: {self.total_cards - owned_count}"
        self.missing_text_label.text = ", ".join(missing_list)

    def add_cards(self, instance):
        if self.card_input.text:
            try:
                tokens = self.card_input.text.split(",")
                for token in tokens:
                    clean = token.strip()
                    if clean.isdigit():
                        num = int(clean)
                        if 1 <= num <= self.total_cards:
                            self.collection[num] = True
                self.save_data()
                self.update_ui()
                self.card_input.text = ""
            except:
                pass

if __name__ == '__main__':
    PaniniTrackerApp().run()
