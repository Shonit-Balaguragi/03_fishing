from game.hook import Hook, IDLE
from game.fish import Fish
from game.catch import check_catch
from game.renderer import WIDTH, HEIGHT, SURFACE_Y, MAX_DEPTH_Y


class GameEngine:
    def __init__(self):
        self.hook = Hook(
            x=WIDTH / 2,
            surface_y=SURFACE_Y,
            max_depth_y=MAX_DEPTH_Y,
            speed=5
        )

        self.fish_list = [
            # Slow, low-value fish
            Fish(
                x=100,
                y=180,
                speed=1,
                width=36,
                height=18,
                point_value=10,
                color=(80, 180, 220),
            ),

            # Fast, high-value fish
            Fish(
                x=400,
                y=280,
                speed=-4,
                width=50,
                height=24,
                point_value=25,
                color=(220, 80, 80),
            ),

            # Another slow, low-value fish
            Fish(
                x=250,
                y=380,
                speed=1,
                width=36,
                height=18,
                point_value=10,
                color=(80, 180, 220),
            ),
        ]

        self.hooked_fish = None
        self.score = 0

    def try_cast(self):
        """
        Start a new cast only if the hook is currently idle.
        """
        if self.hook.state == IDLE:
            self.hook.start_cast()

    def update(self):
        """
        Update the hook, fish, catching, and scoring.
        """

        # Update hook movement
        self.hook.update()

        # Update all fish movement
        for fish in self.fish_list:
            fish.update(WIDTH)

        # If a fish is currently hooked, keep it attached to the hook
        if self.hooked_fish is not None:
            self.hooked_fish.x = self.hook.x
            self.hooked_fish.y = self.hook.y

            # When the hook returns to the surface,
            # add the fish's points to the score
            if self.hook.state == IDLE:
                self.score += self.hooked_fish.point_value
                self.hooked_fish = None

        # Otherwise, check whether the hook catches a fish
        else:
            caught = check_catch(self.hook, self.fish_list)

            if caught is not None:
                self.fish_list.remove(caught)
                self.hooked_fish = caught

                # Attach fish to hook
                self.hooked_fish.x = self.hook.x
                self.hooked_fish.y = self.hook.y

                # Immediately start retracting
                self.hook.catch_fish()

    def draw(self, surface, font):
        """
        Draw the game scene and score.
        """
        from game import renderer

        draw_list = list(self.fish_list)

        # Draw hooked fish as well
        if self.hooked_fish is not None:
            draw_list.append(self.hooked_fish)

        renderer.draw_scene(
            surface,
            self.hook,
            draw_list
        )

        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 10)
        )