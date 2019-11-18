#!/usr/bin/python
import threading
from threading import Thread
from time import sleep

class Vehicle:
  ''' speed in 0..100% '''
  def __init__(self,speed_control_motor, steering_control_motor):
    self.speed_control_motor = speed_control_motor
    self.steering_control_motor = steering_control_motor
    self.cv = threading.Condition()

  def moveForward(self,speed,active_time_sec):
    ''' simple method to check the wiring of Raspberry Pi, motors and H-bridge '''
    self.speed_control_motor.rotate(speed,True)
    sleep(active_time_sec)
    self.speed_control_motor.stop()

  def moveBackward(self,speed,active_time_sec):
    ''' simple method to check the wiring of Raspberry Pi, motors and H-bridge '''
    self.speed_control_motor.rotate(speed,False)
    sleep(active_time_sec)
    self.speed_control_motor.stop()

  def turnLeft(self,speed, active_time_sec):
    ''' simple method to check the wiring of Raspberry Pi, motors and H-bridge '''
    self.speed_control_motor.rotate(speed,True)
    self.steering_control_motor.rotate(speed,True)
    sleep(active_time_sec)
    self.speed_control_motor.stop()
    self.steering_control_motor.stop()

  def turnRight(self,speed, active_time_sec):
    ''' simple method to check the wiring of Raspberry Pi, motors and H-bridge '''
    self.speed_control_motor.rotate(speed,True)
    self.steering_control_motor.rotate(speed,False)
    sleep(active_time_sec)
    self.speed_control_motor.stop()
    self.steering_control_motor.stop()

  def stop(self):
    ''' soft stop, wheels can move'''
    self.speed_control_motor.stop()
    self.steering_control_motor.stop()
    self.stopAnotherCommands()

  def hardBreak(self):
    ''' hard stop - wheels are blocked'''
    self.speed_control_motor.emergency_stop()
    self.steering_control_motor.emergency_stop()
    self.stopAnotherCommands()

  ## for more precise control 
  def moveForwardPrecise(self, speed_dc, steer_dc, active_time_sec):
    '''
      use this methods for understanding vehicle dynamics
      if steer_dc > 0 - move right, else - left 
    '''
    try:
      self.speed_control_motor.rotate(speed_dc,True)
      if(steer_dc >= 0):
        # right
        self.steering_control_motor.rotate(steer_dc,False)
      else:
        # left
        self.steering_control_motor.rotate(abs(steer_dc),True)

      #sleep(active_time_sec)
      self.cv.acquire()
      self.cv.wait(active_time_sec)
    
      self.speed_control_motor.stop()
      self.steering_control_motor.stop()
      self.cv.release() 
    except Exception as e:
      print "Forward"
      print str(e)

  def moveBackwardPrecise(self, speed_dc, steer_dc, active_time_sec):
    '''
      use this methods for understanding vehicle dynamics
      if steer_dc > 0 - move right, else - left 
    '''
    try:
      self.speed_control_motor.rotate(speed_dc,False)
      if(steer_dc >= 0):
        # right
        self.steering_control_motor.rotate(steer_dc,False)
      else:
        # left
        self.steering_control_motor.rotate(abs(steer_dc),True)

      #sleep(active_time_sec)
      self.cv.acquire()
      self.cv.wait(active_time_sec)

      self.speed_control_motor.stop()
      self.steering_control_motor.stop()
      self.cv.release()
    except Exception as e:
      print "Backward"
      print str(e)


  # Asynch (to be able to interrupt commands by new commands 
  # (for ex. for collision avoidance, when new object suddenly appears in front of us)
  def stopAnotherCommands(self):
    self.cv.acquire()
    self.cv.notifyAll()
    self.cv.release()

  def moveForwardAsync(self, speed_dc, steer_dc, active_time_sec):
    self.stopAnotherCommands()
    cmdThread = threading.Thread(target=self.moveForwardPrecise, args=(float(speed_dc), float(steer_dc), float(active_time_sec)))
    cmdThread.daemon = True
    cmdThread.start()
    
 
  def moveBackwardAsync(self, speed_dc, steer_dc, active_time_sec):
    self.stopAnotherCommands()
    cmdThread = threading.Thread(target=self.moveBackwardPrecise, args=(speed_dc, steer_dc, active_time_sec))
    cmdThread.daemon = True
    cmdThread.start()