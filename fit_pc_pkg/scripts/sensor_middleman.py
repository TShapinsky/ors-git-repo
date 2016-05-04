#!/usr/bin/env python
import rospy
import math
from std_msgs.msg import Float32
from geometry_msgs.msg import Pose2D, Vector3

knots = 0.514444  # 1 knot in m/s


def angle_range(a):
    """ limit angles to range of -180 to 180 """
    return (a + 180) % 360 - 180


def subtract_angles(a, b):
    """ subtract angles while keeping them in range -180 to 180 """
    return angle_range(a - b)


class Arbiter:
    def __init__(self, home=(42.293441, -71.263970)):
        """home defines the center of translation. It should
        be within a few hundred km of our location. Default is the center
        of the Oval"""

        self.home = home
        self.heading = 0.0
        self.speed = 0.0
        self.track = 0.0

        self.relwind = (0, 0)  # (direction, speed)
        self.truewind = (0, 0)  # (direction, speed)

        self.initScalars()

        self.pos = self.transformLocation(home[0], home[1])

        self.initSubscribers()
        self.initPublishers()

    def transformLocation(self, lat, longitude):
        return ((lat - self.home[0]) * self.latscalar,
                (longitude - self.home[1]) * self.longscalar)

    def initScalars(self):
        earth_circumference = 40.075 * 10**6  # meters
        self.latscalar = earth_circumference / 360  # meters per degree

        # the length of the line of latitude that we are on in meters
        longdistance = math.cos(math.radians(self.home[0])) * earth_circumference

        self.longscalar = longdistance / 360  # meters per degree

    def initPublishers(self):
        queue = 1

        self.posPub = rospy.Publisher('location', Pose2D, queue_size=queue)
        self.velPub = rospy.Publisher('velocity', Pose2D, queue_size=queue)

        self.relWindPub = rospy.Publisher(
            'relative_wind', Pose2D, queue_size=queue)
        self.trueWindPub = rospy.Publisher(
            'true_wind', Pose2D, queue_size=queue)
        self.globalWindPub = rospy.Publisher(
            'global_wind', Pose2D, queue_size=queue)

    def initSubscribers(self):
        # Hemisphere subscribers
        self.positionSub = rospy.Subscriber('/hemisphere/position', Pose2D,
                                            self.onPosition)
        self.speedSub = rospy.Subscriber('/hemisphere/speed', Float32,
                                         self.onSpeed)
        self.trackSub = rospy.Subscriber('/hemisphere/track', Float32,
                                         self.onTrack)

        # Airmar subscribers
        self.relWindSub = rospy.Subscriber('airmar/relative_wind', Vector3,
                                           self.onRelWind)
        self.trueWindSub = rospy.Subscriber('airmar/true_wind', Vector3,
                                            self.onTrueWind)

    def onRelWind(self, msg):
        self.relwind[0] = msg.x
        self.relwind[1] = msg.y * knots

    def onTrueWind(self, msg):
        self.truewind[0] = msg.x
        self.truewind[1] = msg.y * knots

    def onPosition(self, msg):
        # Incomming messages are in decimal degrees
        self.pos = self.transformLocation(msg.x, msg.y)
        self.heading = msg.theta

    def onSpeed(self, msg):
        # Incomming messages are in decimal minutes
        self.speed = msg.data

    def onTrack(self, msg):
        # Incomming messages are in degrees clockwise of North
        self.track = msg.data

    def publish(self):
        self.posPub.publish(Pose2D(self.pos[1], self.pos[0], self.heading))
        self.velPub.publish(Pose2D(self.speed, 0.0, self.track))

        self.relWindPub.publish(
            Pose2D(self.relwind[1], 0.0, self.relwind[0]))
        self.trueWindPub.publish(
            Pose2D(self.truewind[1], 0.0, self.truewind[0]))

        # Be warned, there could be a negative mistake in the following code.
        # Review needed.
        self.globalWindPub.publish(
            Pose2D(self.relwind[1], 0.0,
                   subtract_angles(self.relwind[0], self.heading)))

    def run(self):
        rate = rospy.Rate(10)  # 10hz
        while not rospy.is_shutdown():
            self.publish()

            rate.sleep()

if __name__ == '__main__':
    rospy.init_node('arbiter', anonymous=True)
    arbiter = Arbiter()
    arbiter.run()
    # do something
