# Pong done with kivy (https://kivy.org/docs/tutorials/pong.html)
###

# TO-DO:
##
"""
-Add sound effects to paddle bounce, wall bounce, scoring of point, beginning of game
-See if paddle controls can/should(?) be tweaked further
"""

# imports
##
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader


# globals
##
paddle_height = 200


# classes
##
class PongPaddle(Widget):
	# for tracking the score
	score = NumericProperty(0)

	# velocity of the paddle on y-axis
	paddle_vel = NumericProperty(0)

	snd_pbouce = ObjectProperty(None, allownone=True)
	

	def bounce_ball(self, ball):
		if self.collide_widget(ball):
			vx, vy = ball.velocity
			offset = (ball.center_y - self.center_y) / (self.height / 2)
			bounced = Vector(-1 * vx, vy)
			vel = bounced * 1.2			
			ball.velocity = vel.x, vel.y + offset
			self.snd_pbounce = SoundLoader.load('paddle_bounce.wav')
			self.snd_pbounce.play()


class PongBall(Widget):
	# velocity of the ball on x and y axis
	velocity_x = NumericProperty(0)
	velocity_y = NumericProperty(0)
	velocity = ReferenceListProperty(velocity_x, velocity_y)

	def move(self):
		self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):
	global paddle_height

	ball = ObjectProperty(None)
	player1 = ObjectProperty(None)
	player2 = ObjectProperty(None)
	snd_serve = ObjectProperty(None, allownone=True)
	snd_wbounce = ObjectProperty(None, allownone=True)
		
	def __init__(self, **kwargs):
		super(PongGame, self).__init__(**kwargs)
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self._keyboard.bind(on_key_up=self._on_keyboard_up)
		

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	# modify this to adjust paddle velocity instead of position in order
	#   to smooth out movement.  Will require resetting each paddle's
	#   velocity to zero on keyboard_up.
	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		accel = 2

		if keycode[1] == 'w':
			if accel < 3:
				self.player1.paddle_vel += accel
		elif keycode[1] == 's':
			if accel < 3:
				self.player1.paddle_vel -= accel
		elif keycode[1] == 'up':
			if accel < 3:
				self.player2.paddle_vel += accel
		elif keycode[1] == 'down':
			if accel < 3:
				self.player2.paddle_vel -= accel
		return True

	# I kept getting an error that only 3 arguments were being supplied but 
	#  that 5 were needed for on_keyboard_up and so I removed the last two...  
	#  seems like a total hack, but it fixed the problem and it seems like a 
	#  bug in kivy and there are no Google results to rely on so I'm ok with 
	#  that.
	def _on_keyboard_up(self, keyboard, keycode):
		if keycode[1] == 'w':
			self.player1.paddle_vel = 0
		elif keycode[1] == 's':
			self.player1.paddle_vel = 0
		elif keycode[1] == 'up':
			self.player2.paddle_vel = 0
		elif keycode[1] == 'down':
			self.player2.paddle_vel = 0
		return True

	def serve_ball(self, vel=(3, -1)):
		self.ball.center= self.center
		self.ball.velocity = vel
		if self.snd_serve is None:
			self.snd_serve = SoundLoader.load('sound1.wav')
		self.snd_serve.play()
		
	def update(self, dt):
		# call ball.move, etc.
		self.ball.move()

		# bounce off paddles
		self.player1.bounce_ball(self.ball)
		self.player2.bounce_ball(self.ball)

		# bounce off top and bottom
		if(self.ball.y < 0) or (self.ball.top > self.height):
			self.ball.velocity_y *= -1
			if self.snd_wbounce is None:
				self.snd_wbounce = SoundLoader.load('wall_bounce.wav')
			self.snd_wbounce.play()

		# gutters for points
		if self.ball.x < self.x:
			self.player2.score += 1
			if self.snd_score is None:
				self.snd_score = SoundLoader.load('score.wav')
			self.snd_score.play()
			self.serve_ball(vel=(3, 1))
		if self.ball.x > self.width:
			self.player1.score += 1
			self.snd_score = SoundLoader.load('score.wav')
			self.snd_score.play()
			self.serve_ball(vel=(-3, 1))

		# Update players' paddle positions based on velocity,
		#   which is modified with keyboard events, above, and
		#   and keep paddle from going off the screen. 
		if self.player1.center_y + self.player1.paddle_vel - (0.5 * paddle_height) > 0 and (0.5 * paddle_height) + self.player1.center_y + self.player1.paddle_vel < self.height:
			self.player1.center_y += self.player1.paddle_vel
		if self.player2.center_y + self.player2.paddle_vel - (0.5 * paddle_height) > 0 and (0.5 * paddle_height) + self.player2.center_y + self.player2.paddle_vel < self.height:
			self.player2.center_y += self.player2.paddle_vel

		# controls for a touch screen
		def on_touch_move(self, touch):
			if touch.x < self.width / 3:
				self.player1.center_y = touch.y
			if touch.x > self.width - self.width / 3:
				self.player2.center_y = touch.y

		

class PongApp(App):
	def build(self):
		game = PongGame()
		game.serve_ball()
		Clock.schedule_interval(game.update, 1.0 / 60.0)
		self.snd_serve = SoundLoader.load('sound1.wav')
		self.snd_serve.play()		
		return game


# game loop
##
if __name__ == '__main__':
	PongApp().run()
