from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class CounterApp(App):
    def build(self):
        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Create title label
        title = Label(
            text='Simple Kivy Counter App',
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        
        # Create counter display
        self.counter_label = Label(
            text='0',
            font_size='48sp',
            size_hint_y=None,
            height=80
        )
        
        # Create button layout
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        # Create buttons
        increment_btn = Button(
            text='+',
            font_size='20sp',
            on_press=self.increment_counter
        )
        
        decrement_btn = Button(
            text='-',
            font_size='20sp',
            on_press=self.decrement_counter
        )
        
        reset_btn = Button(
            text='Reset',
            font_size='16sp',
            on_press=self.reset_counter
        )
        
        # Add buttons to button layout
        button_layout.add_widget(decrement_btn)
        button_layout.add_widget(reset_btn)
        button_layout.add_widget(increment_btn)
        
        # Add all widgets to main layout
        layout.add_widget(title)
        layout.add_widget(self.counter_label)
        layout.add_widget(button_layout)
        
        return layout
    
    def increment_counter(self, instance):
        try:
            current = int(self.counter_label.text)
            self.counter_label.text = str(current + 1)
        except ValueError:
            self.counter_label.text = '1'
    
    def decrement_counter(self, instance):
        try:
            current = int(self.counter_label.text)
            self.counter_label.text = str(current - 1)
        except ValueError:
            self.counter_label.text = '-1'
    
    def reset_counter(self, instance):
        self.counter_label.text = '0'

if __name__ == '__main__':
    CounterApp().run()