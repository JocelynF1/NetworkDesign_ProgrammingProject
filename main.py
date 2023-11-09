# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import threading

timeout = False


# Press the green button in the gutter to run the script.

def make_packet(filename):
    pass


def toggle_timeout():
    global timeout
    timeout = not timeout


def complex_routine():
    if timeout:
        print("Timed out!")
    elif True:
        toggle_timeout()
    else:
        x = 17
        x += 1


if __name__ == '__main__':

    # This is how to set up a Timer at the beginning of time
    timer = threading.Timer(10.0, toggle_timeout)
    timer.start()

    while True:
        complex_routine()
        if timeout:
            # This is how to set the timer after it has been set once.
            # Will handle both cases where the application code and the timer set the timeout
            # if the application code sets it, must ensure that the timer does not toggle before the code gets here
            toggle_timeout()
            timer.join()
            timer = threading.Timer(1.0, toggle_timeout)
            timer.start()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
