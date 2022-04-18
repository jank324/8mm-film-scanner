import pigpio

from filmscanner import Light


def main():
    pi = pigpio.pi()
    l = Light(pi, 6)
    l.turn_on()


if __name__ == "__main__":
    main()
