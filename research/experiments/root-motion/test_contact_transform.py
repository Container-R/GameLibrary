"""Original planar rigid-transform model; not an engine/IK implementation."""
import math
import unittest

def rotate(v, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (c*v[0]-s*v[1], s*v[0]+c*v[1])

def world(root_position, root_angle, local_foot):
    x, y = rotate(local_foot, root_angle)
    return (x+root_position[0], y+root_position[1])

def local_from_anchor(root_position, root_angle, anchor):
    return rotate((anchor[0]-root_position[0], anchor[1]-root_position[1]), -root_angle)

class ContactTests(unittest.TestCase):
    def assertPoint(self, a, b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=10)

    def test_authored_contact_compensates_root_turn(self):
        anchor=(1,0); angle=math.pi/2
        local=local_from_anchor((0,0),angle,anchor)
        self.assertPoint(world((0,0),angle,local),anchor)

    def test_second_writer_breaks_contact(self):
        anchor=(1,0); authored=math.pi/2
        local=local_from_anchor((0,0),authored,anchor)
        slipped=world((0,0),authored*2,local)
        self.assertAlmostEqual(math.dist(slipped,anchor),math.sqrt(2))

    def test_blending_local_feet_need_not_preserve_contact(self):
        anchor=(1,0)
        a=local_from_anchor((0,0),0,anchor)
        b=local_from_anchor((0,0),math.pi/2,anchor)
        midpoint=tuple((x+y)/2 for x,y in zip(a,b))
        foot=world((0,0),math.pi/4,midpoint)
        self.assertAlmostEqual(math.dist(foot,anchor),1-1/math.sqrt(2))

    def test_world_anchor_requires_new_local_target(self):
        anchor=(1,0); root=(2,3); angle=math.pi/3
        local=local_from_anchor(root,angle,anchor)
        self.assertPoint(world(root,angle,local),anchor)

if __name__=='__main__': unittest.main(verbosity=2)
