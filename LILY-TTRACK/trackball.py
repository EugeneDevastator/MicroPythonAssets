# trackball.py
from machine import Pin
from time import ticks_ms, ticks_diff

class Trackball:
    def __init__(self):
        self._pins = {
            'gs1': Pin(1, Pin.IN, Pin.PULL_DOWN),  # y down
            'gs2': Pin(2, Pin.IN, Pin.PULL_DOWN),  # x right
            'gs3': Pin(3, Pin.IN, Pin.PULL_DOWN),  # y up
            'gs4': Pin(10, Pin.IN, Pin.PULL_DOWN), # x left
            'gsKey': Pin(0, Pin.IN, Pin.PULL_UP),
        }

        self._delta_x = 0
        self._delta_y = 0
        self._last_poll = 0
        self._last_aggregation = 0
        self._poll_interval = 0
        self._aggregation_interval = 0

        self._on_move_callback = None
        self._on_button_callback = None

        # Store previous pin states
        self._prev_states = {
            'gs1': self._pins['gs1'].value(),
            'gs2': self._pins['gs2'].value(),
            'gs3': self._pins['gs3'].value(),
            'gs4': self._pins['gs4'].value(),
        }
        self._last_button_state = self._pins['gsKey'].value()

    def init(self, poll_interval_ms=10, aggregation_interval_ms=100):
        """Initialize trackball with specified intervals"""
        self._poll_interval = poll_interval_ms
        self._aggregation_interval = aggregation_interval_ms
        self._last_poll = ticks_ms()
        self._last_aggregation = ticks_ms()

    def on_move(self, callback):
        """Set callback for movement events"""
        self._on_move_callback = callback

    def on_button(self, callback):
        """Set callback for button events"""
        self._on_button_callback = callback

    def get_delta(self):
        """Get current accumulated delta"""
        return (self._delta_x, self._delta_y)

    def _update_delta(self):
        """Update delta based on pin state changes"""
        current_states = {
            'gs1': self._pins['gs1'].value(),
            'gs2': self._pins['gs2'].value(),
            'gs3': self._pins['gs3'].value(),
            'gs4': self._pins['gs4'].value(),
        }

        # Only update delta when there's a change from 0 to 1
        if current_states['gs2'] and not self._prev_states['gs2']:  # x right
            self._delta_x += 1
        if current_states['gs4'] and not self._prev_states['gs4']:  # x left
            self._delta_x -= 1
        if current_states['gs3'] and not self._prev_states['gs3']:  # y down
            self._delta_y -= 1
        if current_states['gs1'] and not self._prev_states['gs1']:  # y up
            self._delta_y += 1

        # Update previous states
        self._prev_states = current_states

    def _check_button(self):
        """Check button state and trigger callback if changed"""
        current_state = self._pins['gsKey'].value()
        if current_state != self._last_button_state:
            if self._on_button_callback:
                self._on_button_callback(current_state)
            self._last_button_state = current_state

    def update(self):
        """Main update function - should be called in the main loop"""
        current_time = ticks_ms()

        # Check if it's time to poll inputs
        if ticks_diff(current_time, self._last_poll) >= self._poll_interval:
            self._update_delta()
            self._check_button()
            self._last_poll = current_time

        # Check if it's time to trigger movement callback
        if ticks_diff(current_time, self._last_aggregation) >= self._aggregation_interval:
            if (self._delta_x != 0 or self._delta_y != 0) and self._on_move_callback:
                self._on_move_callback((self._delta_x, self._delta_y))
                self._delta_x = 0
                self._delta_y = 0
            self._last_aggregation = current_time
