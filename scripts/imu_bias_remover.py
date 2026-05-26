#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from rclpy.qos import qos_profile_sensor_data


class SimpleImuBiasRemover(Node):
    # BIAS FISSO
    # def __init__(self):
    #     super().__init__('imu_bias_remover_node')

    #     self.bias_z = 0.0056

    #     self.first_msg_received = False

    #     # iscrizione in modalità sensore per essere compatibili con imu_transformer
    #     self.subscription = self.create_subscription(
    #         Imu,
    #         'imu_in',
    #         self.imu_callback,
    #         qos_profile_sensor_data)

    #     # pubblicazione in modalità 10(reliable) per farsi leggere da EKF
    #     self.publisher = self.create_publisher(
    #         Imu,
    #         'imu_out',
    #         10)

    #     self.get_logger().info(f"Bias remover attivo, sto sottraendo {self.bias_z} rad/s dall'asse Z.")

    # def imu_callback(self, msg):
    #     # per debug QoS
    #     if not self.first_msg_received:
    #         self.get_logger().info("QoS corretto, i dati passano.")
    #         self.first_msg_received = True

    #     # sottrazione bias
    #     msg.angular_velocity.z -= self.bias_z

    #     self.publisher.publish(msg)

    # BIAS CALIBRATO
    def __init__(self):
        super().__init__("imu_bias_remover_node")

        self.is_calibrated = False  # interruttore
        self.calibration_samples = 1200  # 1200 campioni a 200Hz sono ~6 secondi

        self.sample_count = 0  # contatore
        self.bias_accumulator_z = 0.0  # somma errore
        self.bias_z = 0.0  # valore finale bias

        # iscrizione in modalità sensore per essere compatibili con imu_transformer
        self.subscription = self.create_subscription(
            Imu, "imu_in", self.imu_callback, qos_profile_sensor_data
        )

        # pubblicazione in modalità 10(reliable) per farsi leggere da EKF
        self.publisher = self.create_publisher(Imu, "imu_out", 10)

        self.get_logger().info(
            f"Avvio calibrazione IMU... Acquisizione di {self.calibration_samples} campioni. MANTENERE IL ROBOT FERMO."
        )

    def imu_callback(self, msg):

        # durante calibrazione
        if not self.is_calibrated:
            self.bias_accumulator_z += msg.angular_velocity.z
            self.sample_count += 1

            # stampa per visualizzare il progresso
            if self.sample_count % 100 == 0:  # ogni 100 campioni
                self.get_logger().info(
                    f"Calibrazione in corso... [{self.sample_count}/{self.calibration_samples}]"
                )

            # finita la calibrazione, calcola il bias e attiva l'interruttore
            if self.sample_count >= self.calibration_samples:
                self.bias_z = self.bias_accumulator_z / self.calibration_samples
                self.is_calibrated = True 
                self.get_logger().info(
                    f"CALIBRAZIONE COMPLETATA! Nuovo Bias Z: {self.bias_z:.6f} rad/s."
                )

            return

        # sottrazione del bias appena calcolato
        msg.angular_velocity.z -= self.bias_z

        # invia il dato pulito all'EKF
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SimpleImuBiasRemover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
