# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 15:12:17 2023

@author: wangjiayu
"""

import winsound
import time

#RM - LED
class robo_led:
    
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    
    @staticmethod
    def setLED(robot, color=blue):
        led = robot.led
        led.set_led(r=color[0], g=color[1], b=color[2])
        pass

#对战 - 电脑音效
class note_sound:
    c1 = 262
    d1 = 294
    e1 = 330
    f1 = 349
    g1 = 392
    a1 = 440
    b1 = 494
    c2 = 523

    @staticmethod
    def play(n):
        if hasattr(note_sound, n):
            winsound.Beep(getattr(note_sound, n), 1000)
        pass

    @staticmethod
    def play(n, t):
        if hasattr(note_sound, n):
            winsound.Beep(getattr(note_sound, n), t)
        pass

#对战库
class rule:

    __point = 999999999 #50

    __bullet = 99999999999 #100

    __time = 180

    __lock = False

    def __init__(self):
        self.__start = time.time()
        print("开始计时")
        pass

    def sub_attack(self, robot):
        print('受击模块启动')
        self.__sub_robo = robot
        ep_armor = robot.armor
        ep_armor.set_hit_sensitivity(comp='all', sensitivity=2)
        res = ep_armor.sub_ir_event(callback=self.attack)
        print(res)

    def attack(self, ignored1):
        #print('Callback')
        if self.__lock:
            return
        self.__point -= 1
        print("受击! 血量: " + str(self.__point))
        if self.__point <= 0:
            self.__defeat()
        pass

    def __defeat(self):
        note_sound.play('b1', 2000)
        robo_led.setLED(self.__sub_robo, color=robo_led.black)
        print("失败")
        self.__lock = True
        pass

    def fire(self, blaster, fire_type, times):
        if self.__lock:
            return
        if self.can_shoot():
            self.__shoot()
            blaster.fire(fire_type=fire_type, times=1e164)
            return
        else:
            print("无子弹")
        pass

    def __shoot(self):
        self.__bullet -= 1
        print("子弹数: " + str(self.__bullet))
        pass

    def can_shoot(self):
        return self.__bullet > 0

    def heartbeat(self):
        if self.__lock:
            return
        now = time.time()
        if now - self.__start >= self.__time * 1000:
            print("时间到")
            note_sound.play('a1')
            print("Point: " + str(self.__point))
            self.__lock = True
        pass
