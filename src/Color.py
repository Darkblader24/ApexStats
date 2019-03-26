
class Color:
    hue = 0
    sat = 0
    val = 0

    def __init__(self, *args):
        if len(args) == 3:
            self.hue, self.sat, self.val = args
            return
        if len(args) == 1:
            self.hue, self.sat, self.val = args[0]
            return
        raise ValueError("Invalid Number of Arguments given to Color Constructor.")

    def __iter__(self):
        yield self.hue
        yield self.sat
        yield self.val
        return

    def __eq__(self, other):
        return self.hue == other.hue and self.sat == other.sat and self.val == other.val

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return "Color: ({h},{s},{v}) HSV".format(h=self.hue, s=self.sat, v=self.val)
