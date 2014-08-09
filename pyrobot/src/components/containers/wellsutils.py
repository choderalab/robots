'''
Created on 04.08.2014

@author: jan-hendrikprinz
'''

import math

class WellUtils(object):
    '''
    Mixin that allows a container to compute lots of useful properties for wells
    '''

    @property
    def well_volume_total (self):
        well_volume_total = self.well_volume_at_depth(0.0)
        return well_volume_total
    
    @staticmethod
    def _rounddepth(r, h, d):
        rad = (r*r + h*h) / 2.0 / h
        return rad - math.sqrt(rad * rad - (rad - d)*(rad - d))
    
    @staticmethod
    def _roundvolume(r, h, d):
        a = WellUtils._rounddepth(r, h, d)
        return h * math.pi / 6.0  (3* a*a + h*h)
    
    def well_volume_at_depth(self, depth):
        
        if self.well_shape == 'rectangle' and self.well_bottom_shape != 'flat':
            # Dont know what to do
            return 0.0
        
        headheight = self._headheight()
        fulldepth = self.well_depth
        area = self._areafactor

        if fulldepth > 0:                
            if depth > fulldepth - headheight:
                #inside head
                head = self._headvolume(fulldepth - depth)     
                tail = 0.0
            else:
                head = self._headvolume(headheight)
                tail = (fulldepth - headheight - depth) * self._radius(headheight) * self._radius(headheight)
        else:
            head = - self._headvolume(- depth)     
            tail = 0.0
        
        well_volume_total = (head + tail) * area
        
        return well_volume_total
    
    def well_surface_at_depth(self, depth):
        
        if self.well_shape == 'rectangle' and self.well_bottom_shape != 'flat':
            # Dont know what to do
            return 0.0
        
        headheight = self._headheight()
        fulldepth = self.well_depth
        umfang = self._areafactor
                        
        if depth > fulldepth - headheight:
            #inside head
            head = self._headsurface(fulldepth - depth)     
            tail = 0.0
        else:
            head = self._headsurface(headheight)
            tail = (fulldepth - headheight - depth) * self._radius(headheight)

        well_volume_total = (head + tail) * umfang
        
        return well_volume_total

    def well_depth_safe(self, limit_radius = 1.5):
        '''returns the save pipetting limit within the limit region
        
        NOTES
        -----
        The size of the dispense head is not taken into account and needs to be present in the limit. Default is a 2mm dispense head diameter plut 1 mm error all divided by two. So a radius if 1.5mm
        '''

        return self.well_depth - self._head_iradius(limit_radius)

    def well_dead_volume(self, limit_radius = 1.5):
        return self.well_volume_at_depth(self.well_depth_safe(limit_radius))

    @property
    def _areafactor(self):
        if self.well_shape == 'round':   
            factor = math.pi
        elif self.well_shape == 'square':
            factor = 4.0
        elif self.well_shape == 'rectangle':
            factor = self.well_size_y / self.well_size_x
        elif self.well_shape == 'unknown':
            # smallest possible which is round
            factor = math.pi
        else:
            factor = 0.0
        
        return factor
    
    def _head_iradius(self, radius):
        w = self.well_size_x / 2.0
        d = self.well_depth
        
        if radius > w:
            return 0.0
        
        if self.well_bottom_shape == 'vshape':
            height = radius 

        if self.well_bottom_shape == 'ushape':
            # half sphere
            sec = 1.0
            height = w * sec - math.sqrt(-radius*radius + w*w * sec*sec)
        
        if self.well_bottom_shape == 'round':
            # half a half sphere ending at 45 degrees
            sec = math.sqrt(2.0)
            height = w * sec - math.sqrt(-radius*radius + w*w * sec*sec)
            
        if self.well_bottom_shape == 'bubble':
            if self.well_shape == 'round':
                height = (w*w - d*d + math.sqrt(w*w*w*w + 2.0 * w*w * d*d + d*d*d*d - 4.0 * w*w * radius*radius))/(2.0 * w)
            else:
                height = 0.0
                
        if self.well_bottom_shape == 'flat':
            height = 0.0
                
        if self.well_bottom_shape == 'unknown':
            # unknown is treated as flat, but at the point where the a vshape or round would start
            height = 0.0        
            
        return height
    
    def height_by_volume(self, volume):
        w = self.well_size_x / 2.0
        d = self.well_depth
        area = self._areafactor
        r = self._radius(self._headheight())
        
        HV = self.well_volume_at_depth(self._headheight()) / area
        
        Q = volume / area
        
        
        if Q < HV:
            if self.well_bottom_shape == 'vshape':
                height = (3.0 * Q)** (1 / 3.0)
    
            if self.well_bottom_shape == 'ushape':
                # half sphere
                sec = 1.0
                height = (-((3.0 * Q)/2) + w*w*w * sec*sec*sec + 1.0 / 2.0 * math.sqrt(3) * math.sqrt(Q (3.0 * Q - 4.0 * w*w*w * sec*sec*sec)))** (1 / 3.0)
            
            if self.well_bottom_shape == 'round':
                # half a half sphere ending at 45 degrees
                sec = math.sqrt(2.0)
                height = (-((3.0 * Q)/2) + w*w*w * sec*sec*sec + 1.0 / 2.0 * math.sqrt(3) * math.sqrt(Q (3.0 * Q - 4.0 * w*w*w * sec*sec*sec)))** (1 / 3.0)
        else:
            height = (Q - HV) / r / r
                
        if self.well_bottom_shape == 'bubble':
            if self.well_shape == 'round':
                height = - (w*w / (3.0 * Q + math.sqrt(w**6.0 + 9.0 * Q*Q))**(1/3.0)) + (3.0 * Q + math.sqrt(w**6.0 + 9.0 * Q*Q))**(1/3.0)
            else:
                height = 0.0
                                
        if self.well_bottom_shape == 'unknown':
            # unknown is treated as flat, but at the point where the a vshape or round would start
            height = 0.0
                
        return height
#
    
    def _radius(self, height):
        w = self.well_size_x / 2.0
        d = self.well_depth
        
        h = self._headheight()
        radius = 0.0
        
        if height < h:
            if self.well_bottom_shape == 'vshape':
                radius = height 
    
            if self.well_bottom_shape == 'ushape':
                # half sphere
                sec = 1.0
                radius = math.sqrt((w * sec)**2 - (w * sec - height)**2)
    
            
            if self.well_bottom_shape == 'round':
                # half a half sphere ending at 45 degrees
                sec = math.sqrt(2.0)
                radius = math.sqrt((w * sec)**2 - (w * sec - height)**2)
                
            if self.well_bottom_shape == 'bubble':
                if self.well_shape == 'round':
                    radius = math.sqrt(((d*d + w*w)/(2.0 * d))**2.0 - (height - (d*d - w*w)/(2.0 * d))**2.0)
                else:
                    height = 0.0
                    
            if self.well_bottom_shape == 'flat':
                radius = w
                    
            if self.well_bottom_shape == 'unknown':
                # unknown is treated as flat, but at the point where the a vshape or round would start
                radius = 0       
        else:
            radius = w
            
        return radius
    
    def _headvolume(self, q):
        w = self.well_size_x / 2.0
        d = self.well_depth
        
        if self.well_bottom_shape == 'vshape':
            volume = q*q*q / 3.0  

        if self.well_bottom_shape == 'ushape':
            # half sphere
            sec = 1.0
            volume = -(q*q*q / 3.0) + w * q*q * sec  
        
        if self.well_bottom_shape == 'round':
            # half a half sphere ending at 45 degrees
            sec = math.sqrt(2.0)
            volume = -(q*q*q / 3.0) + w * q * q * sec  
            
        if self.well_bottom_shape == 'bubble':
            if self.well_shape == 'round':
                volume = w*w*q + d*q*q / 2.0 - (w*w * q*q)/(2.0 * d) - q*q*q/3.0
            else:
                volume = 0.0
                
        if self.well_bottom_shape == 'flat':
            volume = 0.0
                
        if self.well_bottom_shape == 'unknown':
            # unknown is treated as flat, but at the point where the a vshape or round would start
            volume = 0.0
                
        return volume

    def _headsurface(self, q):
        w = self.well_size_x / 2.0
        d = self.well_depth
               
        if self.well_bottom_shape == 'vshape':
            surface = q * q * math.sqrt(2)  

        if self.well_bottom_shape == 'ushape':
            # half sphere
            sec = 1.0
            surface = 2.0 * w * q * sec  
        
        if self.well_bottom_shape == 'round':
            # half a half sphere ending at 45 degrees
            sec = math.sqrt(2.0)
            surface = 2.0 * w * q * sec  
            
        if self.well_bottom_shape == 'bubble':
            if self.well_shape == 'round':
#                surface = (w + d*d/w) * q
#               Surface is just the paper nothing else
                surface = w * w
            else:
                surface = 0.0
                
        if self.well_bottom_shape == 'flat':
            surface = 0.0
                
        if self.well_bottom_shape == 'unknown':
            # unknown is treated as flat, but at the point where the a vshape or round would start
            surface = 0.0
                
        return surface

    def _headheight(self):
        if self.well_shape == 'rectangle' and self.well_bottom_shape != 'flat':
            # Dont know what to do
            return 0.0
        
        w = self.well_size_x / 2.0
        d = self.well_depth
        
        if self.well_bottom_shape == 'vshape':
            # half a half sphere ending at 45 degrees
            height = w

        if self.well_bottom_shape == 'ushape':
            # half a half sphere ending at 45 degrees
            height = w
                            
        if self.well_bottom_shape == 'round':
            # half a half sphere ending at 45 degrees
            sec = math.sqrt(2.0)
            height = w * sec - w * math.sqrt(-1.0 + sec*sec)
            
        if self.well_bottom_shape == 'bubble':
            height = -d
                                
        if self.well_bottom_shape == 'flat':
            height = 0
            
        if self.well_bottom_shape == 'unknown':
            height = w
        
        return height
    
    @property
    def well_area (self):
        print self.well_shape
        if self.well_shape == 'round':   
            well_area = math.pi / 4.0 * self.well_size_x * self.well_size_x
            return well_area
        elif self.well_shape == 'square':
            well_area = self.well_size_x * self.well_size_x
        elif self.well_shape == 'rectangle':
            well_area = self.well_size_x * self.well_size_x
        elif self.well_shape == 'unknown':
            # smallest possible which is round
            well_area = math.pi / 4.0 * self.well_size_x * self.well_size_x
        else:
            well_area = 0.0

        return well_area