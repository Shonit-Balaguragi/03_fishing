import pygame

from game.hook import Hook, IDLE
from game.fish import Fish
from game.catch import check_catch
from game.renderer import WIDTH, HEIGHT, SURFACE_Y, MAX_DEPTH_Y


class GameEngine:
    ROUND_DURATION = 30  # seconds

    def __init__(self):
        self.reset_round()

    def create_fish(self):
        return [
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

    def reset_round(self):
        """
        Reset the game for a new 30-second round.
        """
        self.hook = Hook(
            x=WIDTH / 2,
            surface_y=SURFACE_Y,
            max_depth_y=MAX_DEPTH_Y,
            speed=5
        )

        self.fish_list = self.create_fish()

        self.hooked_fish = None
        self.score = 0

        self.round_start_time = pygame.time.get_ticks()
        self.round_active = True

    def get_time_remaining(self):
        """
        Return the number of seconds remaining in the round.
        """
        elapsed_time = (pygame.time.get_ticks() - self.round_start_time) / 1000
        remaining_time = self.ROUND_DURATION - elapsed_time

        return max(0, int(remaining_time + 0.999))

    def try_cast(self):
        """
        Start a new cast only if the round is active
        and the hook is currently idle.
        """
        if self.round_active and self.hook.state == IDLE:
            self.hook.start_cast()

    def update(self):
        """
        Update the game state.
        """

        # Check whether the round has ended
        if self.get_time_remaining() <= 0:
            self.round_active = False

            # Stop the hook
            self.hook.state = IDLE
            self.hook.y = self.hook.surface_y

            # Do not allow a hooked fish to score after time expires
            self.hooked_fish = None

            return

        # Update hook movement
        self.hook.update()

        # Update fish movement
        for fish in self.fish_list:
            fish.update(WIDTH)

        # If a fish is currently hooked
        if self.hooked_fish is not None:
            self.hooked_fish.x = self.hook.x
            self.hooked_fish.y = self.hook.y

            # When the hook returns to the surface,
            # add the fish's points
            if self.hook.state == IDLE:
                self.score += self.hooked_fish.point_value
                self.hooked_fish = None

        # Otherwise, check for a new catch
        else:
            caught = check_catch(self.hook, self.fish_list)

            if caught is not None:
                self.fish_list.remove(caught)
                self.hooked_fish = caught

                self.hooked_fish.x = self.hook.x
                self.hooked_fish.y = self.hook.y

                # Immediately retract the hook
                self.hook.catch_fish()

    def draw(self, surface, font):
        """
        Draw the game scene, score, timer, and round-end message.
        """
        from game import renderer

        draw_list = list(self.fish_list)

        if self.hooked_fish is not None:
            draw_list.append(self.hooked_fish)

        renderer.draw_scene(
            surface,
            self.hook,
            draw_list
        )

        # Score
        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 10)
        )

        # Timer
        renderer.draw_text(
            surface,
            font,
            f"Time: {self.get_time_remaining()}",
            (WIDTH - 130, 10)
        )

        # Round finished message
        if not self.round_active:
            renderer.draw_banner(
                surface,
                font,
                f"TIME UP! Final Score: {self.score} | Press R to Restart"
            )