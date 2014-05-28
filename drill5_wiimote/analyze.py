import wiimote


def main():
    node = WiimoteNode()


class WiimoteNode(object):
    def __init__(self, n=20):
        self.coordinates = {'x': [], 'y': [], 'z': []}
        self.limit = n

    def add(self, x, y, z):
        if len(self.coordinates['x']) > self.limit:
            self.coordinates['x'].pop(0)
            self.coordinates['y'].pop(0)
            self.coordinates['z'].pop(0)
        self.coordinates['x'].append(x)
        self.coordinates['y'].append(y)
        self.coordinates['z'].append(z)

    def get(self):
        if len(self.coordinates['x']) == 0:
            return None
        else:
            x = self.coordinates['x'][len(self.coordinates['x'] - 1)]
            y = self.coordinates['y'][len(self.coordinates['y'] - 1)]
            z = self.coordinates['z'][len(self.coordinates['z'] - 1)]
            return {'x': x, 'y': y, 'z': z}

if __name__ == "__main__":
    main()
