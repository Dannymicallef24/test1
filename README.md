# test1
# Daniel Micallef Project 1. Vending Machine.
# TPRG2131 Fall 2023
# Produced for Phil J (Fall 2023)
# November 15th, 2023


import PySimpleGUI as sg
from gpiozero import Button, Servo
import time
from time import sleep
import RPi.GPIO


#Where am I?
hardware_present = False
try:
    servo = Servo(17)
    key1 = Button(5)
    hardware_present = True
except ModuleNotFoundError:
    print("Not on a Raspberry Pi or gpiozero not installed.")


# Set it to False for normal operation
TESTING = True

# Print a debug log string if TESTING is True, ensure use of Docstring, in definition
def log(s):
    
    if TESTING:
        print(s)

class VendingMachine(object):
    
    PRODUCTS = {"suprise $0.05": ("SURPRISE", 5),
                "chocolate $0.10": ("CHOCOLATE", 10),
                "chips $0.25": ("CHIPS", 25),
                "gummy worms $1.00": ("GUMMY WORMS", 100),
                "beer $2.00": ("BEER", 200),

                }

    # List of coins: each tuple is ("VALUE", value in cents)
    COINS = {"5": ("5", 5),
             "10": ("10", 10),
             "25": ("25", 25),
             "100": ("100", 100),
             "200": ("200", 200),
            }


    def __init__(self):
        self.state = None  # current state
        self.states = {}  # dictionary of states
        self.event = ""  # no event detected
        self.amount = 0  # amount from coins inserted so far
        self.change_due = 0  # change due after vending
        # Build a list of coins in descending order of value
        values = []
        for k in self.COINS:
            values.append(self.COINS[k][1])
        self.coin_values = sorted(values, reverse=True)
        log(str(self.coin_values))

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            log('Exiting %s' % (self.state.name))
            self.state.on_exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.on_entry(self)

    def update(self):
        if self.state:
            #log('Updating %s' % (self.state.name))
            self.state.update(self)

    def add_coin(self, coin):
        """Look up the value of the coin given by the key and add it in."""
        self.amount += self.COINS[coin][1]

    def button_action(self):
        """Callback function for Raspberry Pi button."""
        self.event = 'RETURN'
        self.update()

class State(object):
    """Superclass for states. Override the methods as required."""
    _NAME = ""
    def __init__(self):
        pass
    @property
    def name(self):
        return self._NAME
    def on_entry(self, machine):
        pass
    def on_exit(self, machine):
        pass
    def update(self, machine):
        pass

# In the waiting state, the machine waits for the first coin
class WaitingState(State):
    _NAME = "waiting"
    def update(self, machine):
        if machine.event in machine.COINS:
            machine.add_coin(machine.event)
            machine.go_to_state('add_coins')

# Additional coins, until a product button is pressed
class AddCoinsState(State):
    _NAME = "add_coins"
    def update(self, machine):
        if machine.event == "RETURN":
            machine.change_due = machine.amount  # return entire amount
            machine.amount = 0
            machine.go_to_state('count_change')
        elif machine.event in machine.COINS:
            machine.add_coin(machine.event)
        elif machine.event in machine.PRODUCTS:
            if machine.amount >= machine.PRODUCTS[machine.event][1]:
                machine.go_to_state('deliver_product')
        else:
            pass  # else ignore the event, not enough money for product

# Print the product being delivered
class DeliverProductState(State):
    _NAME = "deliver_product"
    def on_entry(self, machine):
        machine.change_due = machine.amount - machine.PRODUCTS[machine.event][1]
        machine.amount = 0
        
        # Controling the servo 
        servo.value = 1  # Full servo movement
        sleep(2)  # Wait for 2 seconds to simulate product dispensing
        servo.value = 0  # Stop servo movement
        
        # Deliver the product and change state
        machine.change_due = machine.amount - machine.PRODUCTS[machine.event][1]
        machine.amount = 0
        
        print("Buzz... Whir... Click...", machine.PRODUCTS[machine.event][0])
        if machine.change_due > 0:
            machine.go_to_state('count_change')
        else:
            machine.go_to_state('waiting')

# Count out the change in coins 
class CountChangeState(State):
    _NAME = "count_change"
    def on_entry(self, machine):
        # Return the change due and change state
        print("Change due: $%0.2f" % (machine.change_due / 100))
        log("Returning change: " + str(machine.change_due))
    def update(self, machine):
        for coin_index in range(0, 5):
            #print("working with", machine.coin_values[coin_index])
            while machine.change_due >= machine.coin_values[coin_index]:
                print("Returning %d" % machine.coin_values[coin_index])
                machine.change_due -= machine.coin_values[coin_index]
        if machine.change_due == 0:
            machine.go_to_state('waiting') # No more change due


# MAIN PROGRAM
if __name__ == "__main__":
    sg.theme('RedSilver') 

    coin_col = []
    coin_col.append([sg.Text("ENTER COINS", font=("Helvetica", 24))])
    for item in VendingMachine.COINS:
        log(item)
        button = sg.Button(item, font=("Helvetica", 18))
        row = [button]
        coin_col.append(row)

    select_col = []
    select_col.append([sg.Text("SELECT ITEM", font=("Helvetica", 24))])
    for item in VendingMachine.PRODUCTS:
        log(item)
        button = sg.Button(item, font=("Helvetica", 18))
        row = [button]
        select_col.append(row)

    layout = [ [sg.Column(coin_col, vertical_alignment="TOP"),
                     sg.VSeparator(),
                     sg.Column(select_col, vertical_alignment="TOP")
                    ] ]
    layout.append([sg.Button("RETURN", font=("Helvetica", 12))])
    window = sg.Window('Vending Machine', layout)

    # new machine object
    vending = VendingMachine()

    # Add the states
    vending.add_state(WaitingState())
    vending.add_state(AddCoinsState())
    vending.add_state(DeliverProductState())
    vending.add_state(CountChangeState())

    # Reset state is "waiting for coins"
    vending.go_to_state('waiting')

   # Checks if being used on Pi
    if hardware_present:
        # Set up the hardware button callback
        key1.when_pressed = vending.button_action

    # Now that all the states have been defined this is the
    # main portion of the main program.
    while True:
        event, values = window.read(timeout=10)
        if event != '__TIMEOUT__':
            log((event, values))
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        vending.event = event
        vending.update()

    window.close()
    print("Normal exit")

