from machine import Pin, PWM, I2C,
from ssd1306 import SSD1306_I2C
import time
import random
import machine
 
 
# Define the pins for the ultrasonic sensor
trig_pin = machine.Pin(18, machine.Pin.OUT)
echo_pin = machine.Pin(17, machine.Pin.IN)
# Define the pin for the LED
led_pin = machine.Pin(25, machine.Pin.OUT)
led_y = machine.Pin(16, machine.Pin.OUT)
vib   = machine.Pin(20, machine.Pin.OUT)

# Function to measure the distance
def distance():
    # Send a 10us pulse to trigger the ultrasonic sensor
    trig_pin.low()
    time.sleep_us(2)
    trig_pin.high()
    time.sleep_us(10)
    trig_pin.low()
    
    # Measure the duration of the echo signal
    duration = machine.time_pulse_us(echo_pin, 1, 5000)
    
    # Convert the duration to distance (cm)
    distance = (duration / 58.0)
    print("The distance from object is ",distance,"cm")
    d = distance
    print("T ffffffffffffffffffffffffffffffffffffffff ",d,"cm")
    
    return distance
 

def pico_pong_main():
    
        
    # Game parameters
    SCREEN_WIDTH = 128                       # size of the screen
    SCREEN_HEIGHT = 64
    BALL_SIZE = int(SCREEN_WIDTH/32)         # size of the ball size in pixels
    PADDLE_WIDTH = int(SCREEN_WIDTH/8)       # size of the paddle in pixels
    PADDLE_HEIGHT = int(SCREEN_HEIGHT/16)
    PADDLE_Y = SCREEN_HEIGHT-2*PADDLE_HEIGHT # Vertical position of the paddle

    # Buttons
    # Left button connected to GP4
    # Right button connected to GP5
    up = Pin(3, Pin.IN, Pin.PULL_UP)
    down = Pin(4, Pin.IN, Pin.PULL_UP)
    left = Pin(5, Pin.IN, Pin.PULL_UP)
    right = Pin(2, Pin.IN, Pin.PULL_UP)
    button1 = Pin(6, Pin.IN, Pin.PULL_UP)
    button2 = Pin(7, Pin.IN, Pin.PULL_UP)

    # Buzzer connected to GP18
    buzzer = PWM(Pin(19))

    # OLED Screen connected to GP14 (SDA) and GP15 (SCL)
    i2c = I2C(1, sda = Pin(14), scl = Pin(15), freq = 400000)
    oled = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)

    # variables
    ballX = 64     # ball position in pixels
    ballY = 0
    ballVX = 1.0    # ball velocity along x in pixels per frame
    ballVY = 1.0    # ball velocity along y in pixels per frame

    paddleX = int(SCREEN_WIDTH/2) # paddle  position in pixels
    paddleVX = 6                  # paddle velocity in pixels per frame

    soundFreq = 400 # Sound frequency in Hz when the ball hits something
    score = 0

    while True:
        dist = distance()
        # move the paddle when a button is pressed
        if right.value() == 0 or dist >= 20:
            # right button pressed
            paddleX += paddleVX
            led_y.high()
            led_pin.low()
            if paddleX + PADDLE_WIDTH > SCREEN_WIDTH:
                paddleX = SCREEN_WIDTH - PADDLE_WIDTH
        elif left.value() == 0 or (dist < 10 and dist >= 0) :
            # left button pressed
            paddleX -= paddleVX
            led_y.low()
            led_pin.high()
            if paddleX < 0:
                paddleX = 0
        elif (dist >=10 and dist < 20) or dist < 0:
            led_y.low()
            led_pin.low()
        
        # move the ball
        if abs(ballVX) < 1:
            # do not allow an infinite vertical trajectory for the ball
            ballVX = 1

        ballX = int(ballX + ballVX)
        ballY = int(ballY + ballVY)
        
        # collision detection
        collision=False
        if ballX < 0:
            # collision with the left edge of the screen 
            ballX = 0
            ballVX = -ballVX
            collision = True
        
        if ballX + BALL_SIZE > SCREEN_WIDTH:
            # collision with the right edge of the screen
            ballX = SCREEN_WIDTH-BALL_SIZE
            ballVX = -ballVX
            collision = True

        if ballY+BALL_SIZE>PADDLE_Y and ballX > paddleX-BALL_SIZE and ballX<paddleX+PADDLE_WIDTH+BALL_SIZE:
            # collision with the paddle
            # => change ball direction
            ballVY = -ballVY
            ballY = PADDLE_Y-BALL_SIZE
            # increase speed!
            ballVY -= 0.2
            ballVX += (ballX - (paddleX + PADDLE_WIDTH/2))/10
            collision = True
            score += 10
            
        if ballY < 0:
            # collision with the top of the screen
            ballY = 0
            ballVY = -ballVY
            collision = True
            
        if ballY + BALL_SIZE > SCREEN_HEIGHT:
            # collision with the bottom of the screen
            # => Display Game Over
            oled.fill(0)
            oled.text("GAME OVER", int(SCREEN_WIDTH/2)-int(len("Game Over!")/2 * 8), int(SCREEN_HEIGHT/2) - 8)
            oled.text(str(score), SCREEN_WIDTH-int(len(str(score))*8), 0)
            oled.show()
            # play an ugly sound
            buzzer.freq(200)
            buzzer.duty_u16(2000)
            time.sleep(0.5)
            buzzer.duty_u16(0)
            # wait for a button
            while right.value()!=0 and left.value()!=0 and button1.value()!=0 and button2.value()!=0:
                time.sleep(0.001)
            # exit the loop
            break
            
        # Make a sound if the ball hits something
        # Alternate between 2 sounds
        if collision:
            if soundFreq==400:
                soundFreq=800
            else:
                soundFreq=400
        
            buzzer.freq(soundFreq)
            buzzer.duty_u16(2000)
            vib.high()
            time.sleep(0.09)
            vib.low()
            
        
        # clear the screen
        oled.fill(0)
        
        # display the paddle
        oled.fill_rect(paddleX, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 1)
        
        # display the ball
        oled.fill_rect(ballX, ballY, BALL_SIZE, BALL_SIZE, 1)
        
        # display the score
        oled.text(str(score), SCREEN_WIDTH-int(len(str(score))*8), 0)
        
        oled.show()
        
        time.sleep(0.001)
        buzzer.duty_u16(0)
        
if _name_ == "_main_":
    pico_pong_main()
