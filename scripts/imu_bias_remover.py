#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from rclpy.qos import qos_profile_sensor_data

class SimpleImuBiasRemover(Node):
    def __init__(self):
        super().__init__('imu_bias_remover_node')
        
        self.bias_z = 0.0056  
        
        self.first_msg_received = False

        # iscrizione in modalità sensore per essere compatibili con imu_transformer
        self.subscription = self.create_subscription(
            Imu, 
            'imu_in', 
            self.imu_callback, 
            qos_profile_sensor_data)
            
        # pubblicazione in modalità 10(reliable) per farsi leggere da EKF
        self.publisher = self.create_publisher(
            Imu, 
            'imu_out', 
            10)
            
        self.get_logger().info(f"Bias remover attivo, sto sottraendo {self.bias_z} rad/s dall'asse Z.")

    def imu_callback(self, msg):
        # per debug QoS
        if not self.first_msg_received:
            self.get_logger().info("QoS corretto, i dati passano.")
            self.first_msg_received = True

        # sottrazione bias
        msg.angular_velocity.z -= self.bias_z
        
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SimpleImuBiasRemover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()