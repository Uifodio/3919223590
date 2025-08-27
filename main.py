from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

class CounterApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
    
    def build(self):
        # Set window size for better visibility
        Window.size = (400, 300)
        Window.minimum_width = 300
        Window.minimum_height = 200
        
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
        self.counter += 1
        self.counter_label.text = str(self.counter)
    
    def decrement_counter(self, instance):
        self.counter -= 1
        self.counter_label.text = str(self.counter)
    
    def reset_counter(self, instance):
        self.counter = 0
        self.counter_label.text = str(self.counter)

if __name__ == '__main__':
    CounterApp().run()