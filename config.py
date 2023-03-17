
class Config:
    def __init__(self):
        # environment

        self.window_name = "Ruffle - bird.swf"

        self.image_size = [160, 300]
        self.interval_time = 0.2

        # model
        self.hidden_layer_size = 200
        self.learning_rate = 0.0005
        self.batch_size_episodes = 10
        self.load_checkpoint = "store_true"
        self.discount_factor = 0.99
        self.render = "store_true"

