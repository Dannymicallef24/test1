# Resistor class models a resistor that behaves according to Ohm's law.

# MODIFIED TUE FEB 6: fix the PyLint warnings in the unit test code.

# Accessors return value of electrical properties and state variables.

# Mutators set_voltage(), set_current() keep electrical state variables
# voltage, current and power in a self consistent state.

# Series-parallel:
 # Resistor.series(other) returns new Resistor sum of resistances
 # Resistor.parallel(other) returns new Resistor resistances in parallel

#Model a resistor that behaves according to Ohm's law.
class Resistor (object):
    #Constructor for Resistor.
    #
    # res = resistance in Ohms (default 1000 ohms)
    # tol = tolerance as a percentage (default 5%)
    # pwr = power rating in Watts (default 1/4W)
    # Must also initialize the electrical state variables to zero.
    def __init__(self, res=1000.0, tol=5.0, pwr=0.25):
            # Initialize the properties from parameters
            self.resistance = float(res)
            self.tolerance = float(tol)
            self.rating = float(pwr)

            # Initialize the state variables as zero
            self._voltage = 0.0
            self._current = 0.0
            self._power = 0.0
            return

    #
    # Mutator methods
    #
    def set_voltage(self, v):
        """Set the voltage, update current and power accordingly."""
        self._voltage = v
        self._current = v / self.resistance
        self._power = abs(self._voltage * self._current)
        return

    def set_current(self, amps):
        """Set the current, update voltage and power accordingly."""
        self._current = amps
        self._voltage = amps * self.resistance
        self._power = abs(self._voltage * self._current)
        return

    #
    # Accessor methods
    #
    def get_resistance(self):
        return self.resistance
    def get_tolerance(self):
        return self.tolerance
    def get_rating(self):
        return self.rating

    def get_voltage(self):
        return self._voltage
    def get_current(self):
        return self._current
    def get_power(self):
        return self._power

    #
    # Series and parallel combinations
    #

    # Returns a Resistor with resistance equal to self + other.
    #
    # parameter other is an instance of Resistor.
    # The combined tolerances and ratings are the more pessimistic:
    # tolerance is the wider of the two e.g. 5% and 10% --> 10%;
    # ratings is the lesser of the two, e.g. 1/4 W and 1/2 W --> 1/4 W

    def series(self, other):
        rs = self.resistance + other.resistance
        # new tolerance is the larger of the two
        if self.tolerance >= other.tolerance :
            newtol = self.tolerance
        else :
            newtol = other.tolerance
        # new power rating is the smaller of the two
        if self.rating <= other.rating :
            newrating = self.rating
        else :
            newrating = other.rating
        return Resistor( rs, tol=newtol, pwr=newrating)

    def __add__( self, other) :
        """Overload the addition + operator for series resistances."""
        return self.series(other)

    def parallel( self, other) :
        """Returns a Resistor with resistance equal to self // other.
        
        parameter other is an instance of Resistor.
        The combined tolerances and ratings are the more pessimistic:
        tolerance is the wider of the two e.g. 5% and 10% --> 10%;
        ratings is the lesser of the two, e.g. 1/4 W and 1/2 W --> 1/4 W
        """
        rp = 1.0 / (1.0/self.resistance + 1.0/other.resistance)
        # new tolerance is the larger of the two
        if self.tolerance >= other.tolerance :
            newtol = self.tolerance
        else :
            newtol = other.tolerance
        # new power rating is the smaller of the two
        if self.rating <= other.rating :
            newrating = self.rating
        else :
            newrating = other.rating
        return Resistor( rp, tol=newtol, pwr=newrating)

    def __floordiv__( self, other) :
        """Redefine floor division // operator for parallel resistances."""
        return self.parallel(other)

    def __str__(self) :
        """Return a string describing this instance.
        
        Uses Unicode numbers: Omega \x03A9 and Plus-Minus \x00B1.
        """
        return str(self.resistance) + "\u03a9 " \
            + "\u00b1" + str(self.tolerance) + "%" \
            + " (" + str(self.rating) + "W)"


## Test code (place at bottom of the file)
if __name__ == "__main__":
    # Note: for the purpose of the PyLint exercise, the invalid name
    # warnings in the unit test code are disabled. The warnings refer
    # to attribute names r1, r2, rs and rp. They are too short.
    # (eschew foolish consistency...)
    # pylint: disable=invalid-name

    # Import the testing framework (Python standard library section 26.4)
    import unittest

    class TestResistorMethods(unittest.TestCase):
        """This class runs several tests with Resistor objects."""
        def setUp(self):
            """initialize test objects"""
            self.r1 = Resistor(1000.0, tol=10.0, pwr=0.25)
            self.r2 = Resistor(2000.0, tol=5.0, pwr=0.50)
            self.r_default = Resistor()
            self.rs = None
            self.rp = None

        def test_get_resistance(self):
            """test get_resistance"""
            self.assertEqual(
                self.r1.get_resistance(), 1000.0,
                "Incorrectly set resistance in constructor, R1 != 1000")
            self.assertEqual(
                self.r2.get_resistance(), 2000.0,
                "Incorrectly set resistance in constructor, R2 != 2000")
            self.assertEqual(
                self.r_default.get_resistance(), 1000.0,
                "Incorrect default resistance in constructor, R != 1000")

        def test_get_tolerance(self):
            """test get_tolerance"""
            self.assertEqual(
                self.r1.get_tolerance(), 10.0,
                "Incorrectly set tolerance in constructor, tolerance != 10%.")
            self.assertEqual(
                self.r2.get_tolerance(), 5.0,
                "Incorrectly set tolerance in constructor, tolerance != 5%.")
            self.assertEqual(
                self.r_default.get_tolerance(), 5.0,
                "Incorrect default tolerance, tolerance != 5%.")

        def test_get_rating(self):
            """test get_rating"""
            self.assertEqual(
                self.r1.get_rating(), 0.25,
                "Incorrectly set power rating in constructor != 1/4 W.")
            self.assertEqual(
                self.r2.get_rating(), 0.5,
                "Incorrectly set power rating in constructor != 1/2 W.")
            self.assertEqual(
                self.r_default.get_rating(), 0.25,
                "Incorrect default power rating != 1/4 W.")

        def test_initial_state_variables(self):
            """test initial value of state variables"""
            self.assertEqual(
                self.r1.get_voltage(), 0.0,
                "Incorrect initial voltage != 0.")
            self.assertEqual(
                self.r1.get_current(), 0.0,
                "Incorrect initial current != 0.")
            self.assertEqual(
                self.r1.get_power(), 0.0,
                "Incorrect initial power != 0.")

        def test_set_current(self):
            """test set_current"""
            self.r1.set_current(1.0e-3)  # 1mA --> 1V
            self.assertEqual(
                self.r1.get_voltage(), 1.0,
                "Incorrect voltage: I = 1mA, V != 1.0")
            self.assertEqual(
                self.r1.get_power(), 1.0e-3,
                "Incorrect power: I = 1mA, P != 1mW")
            self.r1.set_current(-1.0e-3)  # -1mA --> -1V
            self.assertEqual(
                self.r1.get_voltage(), -1.0,
                "Incorrect voltage: I = -1mA, V != -1.0")
            self.assertEqual(
                self.r1.get_power(), 1.0e-3,
                "Incorrect power: I = -1mA, P != 1mW")

        def test_string(self):
            """test __str__ method"""
            self.assertEqual(
                str(self.r1), "1000.0\u03a9 \u00b110.0% (0.25W)",
                "Incorrect __str__ method.")

        def test_series(self):
            """test series"""
            self.rs = self.r1.series(self.r2)
            self.assertEqual(
                self.rs.get_resistance(), 3000.0,
                "Incorrect series resistance: 1k + 2k != 3k")
            self.assertEqual(
                self.rs.get_tolerance(), 10.0,
                "Incorrect series tolerance: 5% + 10% != 10%")
            self.assertEqual(
                self.rs.get_rating(), 0.25,
                "Incorrect series power rating: 1/4 W + 1/2W != 1/4 W")
            self.assertEqual(
                (self.rs.get_voltage(), self.rs.get_current(), self.rs.get_power()),
                (0.0, 0.0, 0.0),
                "Incorrect series initial state; should be 0,0,0 from init.")

        def test_parallel(self):
            """test parallel"""
            self.rp = self.r1.parallel(self.r2)
            self.assertEqual(
                round(self.rp.get_resistance(), 2), 666.67,
                "Incorrect parallel resistance: 1k // 2k != 666.67")
            self.assertEqual(
                self.rp.get_tolerance(), 10.0,
                "Incorrect series tolerance: 5% // 10% != 10%")
            self.assertEqual(
                self.rp.get_rating(), 0.25,
                "Incorrect series power rating: 1/4 W // 1/2W != 1/4 W")
            self.assertEqual(
                (self.rp.get_voltage(), self.rp.get_current(), self.rp.get_power()),
                (0.0, 0.0, 0.0),
                "Incorrect parallel initial state; should be 0,0,0 from init.")


    # Run the tests that were just defined.
    print("Running unit testing on class Resistor:")
    unittest.main()

# done
