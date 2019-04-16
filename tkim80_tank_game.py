# Final Project: Tank Game
# Tae Jin Kim (tkim80)

import math
import pygame as pg
import random as rand

BLK = (0, 0, 0)
RED = (255, 0, 0)
GRN = (0, 255, 0)
BLU = (0, 0, 255)
YLW = (255, 255, 0)
WHT = (255, 255, 255)
SKY = (135, 206, 235)

WIDTH = 1400
HEIGHT = 700

MAX_VEL = 200
MAX_DIS = 200


class Tank(object):
    def __init__(self, screen, player_num, wind):
        self.wind = wind
        self.screen = screen
        self.p_num = player_num
        self.t_img = pg.image.load('img/tank.png').convert()
        #self.t_img = pg.transform.scale(self.t_img,(100, 100))      
        
        # tank
        self.dir = 'r'
        self.done = 0
        self.t_w = self.t_img.get_width()
        self.t_h = self.t_img.get_height()
        if self.p_num == 1:
            pos = rand.randint(10,250)
            self.x_pos = pos
            self.r_ang = 360
            self.y_pos = int(3*HEIGHT/4)
        elif self.p_num == 2:
            self.dir = 'l'
            self.r_ang = 540
            self.t_img = pg.transform.flip(self.t_img, True, False)
            pos = rand.randint(WIDTH-(250+self.t_w),WIDTH-(10+self.t_w))
            self.x_pos = pos
            self.y_pos = int(3*HEIGHT/4)
            
        self.ground = self.y_pos + self.t_h - 20
        
        # radar
        self.r_l = 100
        self.r_ang_change = 0
        self.r_beg_pos = (int(self.x_pos+self.t_w/2), int(self.y_pos+self.t_h/2))
        self.r_end_pos = (int(self.r_beg_pos[0] + math.cos(math.radians(self.r_ang)) * self.r_l),
                          int(self.r_beg_pos[1] + math.sin(math.radians(self.r_ang)) * self.r_l))
        pg.draw.line(self.screen, BLK, self.r_beg_pos, self.r_end_pos, 1)
        
        # missile
        self.shooting = 0
        self.beg_tick = 0
        self.m_vel = (0, 0)
        self.m_pos0 = (int(self.x_pos+self.t_w/2), int(self.y_pos+self.t_h/2))
        self.m_pos = self.m_pos0
        pg.draw.circle(self.screen, RED, self.m_pos, 5, 0)
        
        # necessary variiables
        self.pow = 0
        self.dist = 0
        self.dead = 0
        self.x_vel = 0
        self.alpha = 255
        self.health = 1.0
        self.pow_change = 0
        self.alpha_change = 0
        self.health_change = 0
        
        # font
        self.t_font = pg.font.Font('txt/arcade.ttf', 25)
        self.t_font_small = pg.font.Font('txt/arcade.ttf', 20)

    def get_pos(self):
        return (self.x_pos, self.y_pos)
    
    def get_m_pos(self):
        return self.m_pos
    
    def get_dim(self):
        return (self.t_w, self.t_h)

    def move(self, key):
        # angle radar
        if key == pg.K_w or key == pg.K_UP:
            self.r_ang_change = -2
        elif key == pg.K_s or key == pg.K_DOWN:
            self.r_ang_change = 2
        # move tank
        elif key == pg.K_a or key == pg.K_LEFT:
            self.x_vel = -2
            if self.dir == 'r':
                self.dir = 'l'
                self.r_ang = 900 - self.r_ang
                self.t_img = pg.transform.flip(self.t_img, True, False)  
        elif key == pg.K_d or key == pg.K_RIGHT:
            self.x_vel = 2
            if self.dir == 'l':
                self.dir = 'r'
                self.r_ang = 900 - self.r_ang
                self.t_img = pg.transform.flip(self.t_img, True, False)
        # shoot a missile
        elif key == pg.K_SPACE:
            self.pow_change = 0.01
            
    def shoot(self, start_tick):
        self.shooting = 1
        self.beg_tick = start_tick
        if self.dir == 'r':
            self.m_vel = (self.pow*MAX_VEL*math.cos(math.radians(360-self.r_ang))+self.wind, self.pow*MAX_VEL*math.sin(math.radians(360-self.r_ang)))
        else:
            self.m_vel = (self.pow*-MAX_VEL*math.cos(math.radians(self.r_ang-540))+self.wind, self.pow*MAX_VEL*math.sin(math.radians(self.r_ang-540)))
    
    def stop(self, instruct):
        if instruct == 'm':
            self.x_vel = 0
        elif instruct == 'a':
            self.r_ang_change = 0
            
    def reset(self):
        self.pow = 0
        self.dist = 0
        self.done = 1
        self.health = 1
        self.shooting = 0
        if self.dir == 'r':
            self.r_ang = 360
        else:
            self.r_ang = 540
            
    def die(self):
        self.dead = 1
        self.health_change = -0.01
    
    def update_bars(self):
        # initialize variables
        self.pow = min(1,self.pow)
        fuel = max(0, 1-self.dist/MAX_DIS)
        fuel_color = (255, round(255*fuel), 0)
        pow_color = (0, 255, round(255*self.pow))
        
        if fuel == 0:
             self.reset()
             self.stop('a')
             self.stop('m')
        
        if self.health > 0.5:
            health_color = (round(255*2*(1-self.health)), 255, 0)
        else:
            health_color = (255, round(255*2*(self.health)), 0)
        
        # player 1
        if self.p_num == 1:
            # health
            pg.draw.rect(self.screen, WHT, (10, 10, 200, 20), 2)
            pg.draw.rect(self.screen, health_color, (12, 12, 197*self.health, 17), 0)
            health_txt = self.t_font.render("P1 : HP", True, BLU)
            self.screen.blit(health_txt, (110-health_txt.get_width()/2, 25-health_txt.get_height()/2))
            # fuel
            pg.draw.rect(self.screen, WHT, (10, 34, 200, 20), 2)
            pg.draw.rect(self.screen, fuel_color, (12, 36, 197*fuel, 17), 0)
            fuel_txt = self.t_font.render("P1 : FUEL", True, BLU)
            self.screen.blit(fuel_txt, (110-fuel_txt.get_width()/2, 49-fuel_txt.get_height()/2))
        
        # player 2
        if self.p_num == 2:
            # health
            pg.draw.rect(self.screen, WHT, (WIDTH-214, 10, 200, 20), 2)
            pg.draw.rect(self.screen, health_color, (WIDTH-212, 12, 197*self.health, 17), 0)
            health_txt = self.t_font.render("P2 : HP", True, RED)
            self.screen.blit(health_txt, (WIDTH-110-health_txt.get_width()/2, 25-health_txt.get_height()/2))
            # fuel
            pg.draw.rect(self.screen, WHT, (WIDTH-214, 34, 200, 20), 2)
            pg.draw.rect(self.screen, fuel_color, (WIDTH-212, 36, 197*fuel, 17), 0)
            fuel_txt = self.t_font.render("P2 : FUEL", True, RED)
            self.screen.blit(fuel_txt, (WIDTH-110-fuel_txt.get_width()/2, 49-fuel_txt.get_height()/2))
            
        if self.dead == 0:
            # power
            pg.draw.rect(self.screen, WHT, (self.x_pos, self.y_pos+self.t_h-20, self.t_w, 20), 2)
            pg.draw.rect(self.screen, pow_color, (self.x_pos+2, self.y_pos+self.t_h+2-20, (self.t_w-3)*self.pow, 17), 0)
            pow_txt = self.t_font_small.render("Shot Power", True, WHT)
            self.screen.blit(pow_txt, (self.x_pos+self.t_w/2-pow_txt.get_width()/2, self.y_pos+self.t_h-17))
    
    def update_radar(self):
        # limit angle of radar
        if self.dir == 'r':
            self.r_ang += self.r_ang_change
            if self.r_ang <= 270:
                self.r_ang = 270
            elif self.r_ang >= 360:
                self.r_ang = 360
        elif self.dir == 'l':
            self.r_ang -= self.r_ang_change
            if self.r_ang <= 540:
                self.r_ang = 540
            elif self.r_ang >= 630:
                self.r_ang = 630
        if self.dir == 'r':
            self.r_beg_pos = (int(self.x_pos+self.t_w/2-17), int(self.y_pos+self.t_h/2-20))
        else:
            self.r_beg_pos = (int(self.x_pos+self.t_w/2+17), int(self.y_pos+self.t_h/2-20))
        self.r_end_pos = (int(self.r_beg_pos[0] + math.cos(math.radians(self.r_ang)) * self.r_l),
                          int(self.r_beg_pos[1] + math.sin(math.radians(self.r_ang)) * self.r_l))
        if self.dead == 0:
            pg.draw.line(self.screen, RED, self.r_beg_pos, self.r_end_pos, 2)
    
    def update_missile(self):
        self.stop('a')
        self.stop('m')
        self.pow_change = 0
        
        sec = (pg.time.get_ticks()-self.beg_tick)/100
        self.m_pos = (int(self.m_vel[0]*sec + self.r_beg_pos[0]), int(5*sec**2 - self.m_vel[1]*sec + self.r_beg_pos[1]))
        pg.draw.circle(self.screen, RED, self.m_pos, 5, 0)            
        
        if self.m_pos[1] > self.ground:
            self.reset()
    
    def update(self):
        self.pow += self.pow_change
        self.dist += abs(self.x_vel)
        self.health = max(0,self.health+self.health_change)
        
        if self.shooting:
            self.update_missile()
            
        if self.dead:
            self.stop('a')
            self.stop('m')
        
        if self.dist > MAX_DIS:
            self.x_vel = 0

        self.x_pos += self.x_vel
        
        if self.x_pos < 0:
            self.x_pos = 0
        elif (self.x_pos + self.t_w) > WIDTH:
            self.x_pos = WIDTH - self.t_w
        
        self.alpha = max(0, self.alpha + self.alpha_change)
        self.t_img.set_alpha(self.alpha)
        
        self.screen.blit(self.t_img, (self.x_pos, self.y_pos))
        
        self.update_bars()
        self.update_radar()
        
        if self.dead:
            self.alpha_change = -5
        

class App(object):
    def __init__(self):
        pg.init()
        pg.display.set_caption("Tae's Game")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.mount_img = pg.image.load('img/mountain.png')
        
        self.running = True
        self.clock = pg.time.Clock()
        self.wind = rand.randint(-14, 14)
        wind_str = ""
        
        if self.wind > 0:
            wind_str = "-> WIND : " + str(self.wind)
        elif self.wind < 0:
            wind_str = "<- WIND : " + str(-1*self.wind)
        else:
            wind_str = "No WIND"
            
        self.turn = rand.randint(0, 1)
        self.player1 = Tank(self.screen, 1, self.wind)
        self.player2 = Tank(self.screen, 2, self.wind)        
        
        self.font = pg.font.Font('txt/arcade.ttf', 25)
        self.font_big = pg.font.Font('txt/arcade.ttf', 50)
        
        self.wind_txt = self.font.render(wind_str, True, SKY)
        self.turn_txt = self.font.render("YOUR TURN", True, WHT)
        self.comm1_txt = self.font.render("move left [a] right [d], aim up [w] down [s], hold [SPACE] to shoot", True, WHT)
        self.comm2_txt = self.font.render("move left [LEFT] right [RIGHT], aim up [UP] down [DOWN], hold [SPACE] to shoot", True, WHT)
        
        self.game_over = self.font_big.render("GAME OVER", True, RED)
        self.play_again = self.font.render("Press [ENTER] to Play Again", True, WHT)
    
    def start_over(self):
        self.wind = rand.randint(-14, 14)
        wind_str = ""
        
        if self.wind > 0:
            wind_str = "-> WIND : " + str(self.wind)
        elif self.wind < 0:
            wind_str = "<- WIND : " + str(-1*self.wind)
        else:
            wind_str = "No WIND"
            
        self.wind_txt = self.font.render(wind_str, True, SKY)
            
        self.turn = rand.randint(0, 1)
        self.player1 = Tank(self.screen, 1, self.wind)
        self.player2 = Tank(self.screen, 2, self.wind)
        self.player1.reset()
        self.player2.reset()
    
    def on_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                pass
            elif event.type in (pg.KEYDOWN, pg.KEYUP):
                if event.type == pg.KEYDOWN:
                    if self.turn == 0:
                        if event.key in (pg.K_w, pg.K_s, pg.K_a, pg.K_d, pg.K_SPACE):
                            self.player1.move(event.key)
                    elif self.turn == 1:
                        if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT, pg.K_SPACE):
                            self.player2.move(event.key)
                else:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                    if event.key == pg.K_RETURN:
                        self.start_over()
                    elif event.key == pg.K_SPACE:
                        if self.player1.shooting == 0 and self.player2.shooting == 0:
                            start_ticks = pg.time.get_ticks()
                            if self.turn == 0:
                                self.player1.shoot(start_ticks)
                            else:
                                self.player2.shoot(start_ticks)
                    elif event.key in (pg.K_w, pg.K_s):
                        self.player1.stop('a')
                    elif event.key in (pg.K_a, pg.K_d):
                        self.player1.stop('m')
                    elif event.key in (pg.K_UP, pg.K_DOWN):
                        self.player2.stop('a')
                    elif event.key in (pg.K_LEFT, pg.K_RIGHT):
                        self.player2.stop('m')   
               
    def update_txt(self):
        pos = []
        dim = []
        # command txt
        if self.turn == 0:
            pos = self.player1.get_pos()
            dim = self.player1.get_dim()
            self.screen.blit(self.comm1_txt, (WIDTH/2-self.comm1_txt.get_width()/2, 36)) 
        else:
            pos = self.player2.get_pos()  
            dim = self.player2.get_dim()
            self.screen.blit(self.comm2_txt, (WIDTH/2-self.comm2_txt.get_width()/2, 36))
        # wind txt
        self.screen.blit(self.wind_txt, (WIDTH/2-self.wind_txt.get_width()/2, 12))
        # turn txt
        if self.player1.dead == 0 and self.player2.dead == 0:
            self.screen.blit(self.turn_txt, (pos[0]+dim[0]/2-self.turn_txt.get_width()/2, pos[1]-self.turn_txt.get_height()))
        
    def on_update(self):
        self.update_txt()
        self.player1.update()
        self.player2.update()
        self.screen.blit(self.mount_img, (int(WIDTH/2-self.mount_img.get_width()/2), int(HEIGHT-self.mount_img.get_height())))
        
        p1_pos = self.player1.get_pos()
        p1_dim = self.player1.get_dim()
        p2_pos = self.player2.get_pos()
        p2_dim = self.player2.get_dim()
        m1_pos = self.player1.get_m_pos()
        m2_pos = self.player2.get_m_pos()
        if m1_pos[0] in range(p2_pos[0]+10, p2_pos[0]+p2_dim[0]-10) and m1_pos[1] >= p2_pos[1]+10:
            self.player1.m_pos = self.player1.r_beg_pos
            self.player1.reset()
            self.player2.die()
        if m2_pos[0] in range(p1_pos[0]+10, p1_pos[0]+p1_dim[0]-10) and m2_pos[1] >= p1_pos[1]+10:
            self.player2.m_pos = self.player2.r_beg_pos
            self.player2.reset()
            self.player1.die()
        if m1_pos[0] in range(int(WIDTH/2-self.mount_img.get_width()/3), int(WIDTH/2+self.mount_img.get_width()/3)) and m1_pos[1] >= int(HEIGHT-self.mount_img.get_height()+20):
            self.player1.m_pos = self.player1.r_beg_pos
            self.player1.reset()
        if m2_pos[0] in range(int(WIDTH/2-self.mount_img.get_width()/3), int(WIDTH/2+self.mount_img.get_width()/3)) and m2_pos[1] >= int(HEIGHT-self.mount_img.get_height()+20):
            self.player2.m_pos = self.player2.r_beg_pos
            self.player2.reset()
        if (p1_pos[0] + p1_dim[0]) > int(WIDTH/2-self.mount_img.get_width()/2):
            self.player1.x_pos = int(WIDTH/2-self.mount_img.get_width()/2-p1_dim[0])
        if p2_pos[0] < int(WIDTH/2+self.mount_img.get_width()/2):
            self.player2.x_pos = int(WIDTH/2+self.mount_img.get_width()/2)
        
        if self.player1.done == 1:
            self.player1.done = 0
            self.turn = 1 - self.turn
        elif self.player2.done == 1:
            self.player2.done = 0
            self.turn = 1 - self.turn
            
        if self.player1.health == 0 or self.player2.health == 0:
            self.screen.blit(self.game_over, (WIDTH/2-self.game_over.get_width()/2, 180))
            self.screen.blit(self.play_again, (WIDTH/2-self.play_again.get_width()/2, 220))
            
    def on_render(self):
        pg.display.update()
        self.screen.fill(BLK)
    
    def on_execute(self):
        while self.running:
            self.on_event()
            self.on_update()
            self.on_render()
            self.clock.tick(60)
        pg.quit()
        
    
# main fuction
if __name__ == '__main__':
    game = App()
    game.on_execute()