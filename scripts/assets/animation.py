class Animation:
    def __init__(self, images, duration=5, is_loop=True):
        self.images = images
        self.duration = duration
        self.is_loop = is_loop

        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.duration, self.is_loop)

    def update(self, dt):
        if self.is_loop:
            self.frame = (self.frame + 1) % (self.duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.duration * len(self.images) - 1)
            if self.frame >= self.duration * len(self.images) - 1:
                self.done = True

    def get_img(self):
        return self.images[int(self.frame / self.duration)]