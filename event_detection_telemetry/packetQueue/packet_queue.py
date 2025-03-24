# # import queue

# # class PacketQueue:
# #     """Thread-safe queue to pass telemetry packets between threads."""
    
# #     queues = {}

# #     @staticmethod
# #     def add_queue(packet_type):
# #         """Adds a new queue for a specific packet type."""
# #         if packet_type not in PacketQueue.queues:
# #             PacketQueue.queues[packet_type] = queue.Queue()

# #     @staticmethod
# #     def put(packet_type, packet):
# #         """Adds a packet to the queue."""
# #         if packet_type in PacketQueue.queues:
# #             PacketQueue.queues[packet_type].put(packet)

# #     @staticmethod
# #     def get(packet_type):
# #         """Retrieves the next packet from the queue."""
# #         if packet_type in PacketQueue.queues:
# #             return PacketQueue.queues[packet_type].get()

# import queue

# class PacketQueue:
#     """Thread-safe queue to pass telemetry packets between threads."""
    
#     queues = {}

#     @staticmethod
#     def add_queue(packet_type, max_size=1000):
#         """
#         Adds a new queue for a specific packet type.
        
#         Args:
#             packet_type (str): The type of telemetry packet.
#             max_size (int): The maximum size of the queue (default: 1000).
#         """
#         if packet_type not in PacketQueue.queues:
#             PacketQueue.queues[packet_type] = queue.Queue(maxsize=max_size)

#     @staticmethod
#     def put(packet_type, packet, player_indexes):
#         """
#         Adds a packet to the queue. If the queue is full, it drops the oldest packet.
        
#         Args:
#             packet_type (str): The type of telemetry packet.
#             packet: The telemetry packet to add.
#         """
#         if packet_type in PacketQueue.queues:
#             q = PacketQueue.queues[packet_type]
#             if q.full():
#                 q.get_nowait()  # Remove the oldest packet if the queue is full
#             q.put(packet,player_indexes)  # Add the new packet

#     @staticmethod
#     def get(packet_type, timeout=1):
#         """
#         Retrieves the next packet from the queue with a timeout.

#         Args:
#             packet_type (str): The type of telemetry packet.
#             timeout (int): Timeout in seconds to wait for a packet (default: 1).

#         Returns:
#             The retrieved telemetry packet, or None if no packet is available.
#         """
#         if packet_type in PacketQueue.queues:
#             q = PacketQueue.queues[packet_type]
#             try:
#                 return q.get(timeout=timeout)
#             except queue.Empty:
#                 return None  # Return None instead of raising an error
#         return None  # Return None if queue does not exist

import queue

class PacketQueue:
    """Thread-safe queue to pass telemetry packets between threads."""
    
    queues = {}

    @staticmethod
    def add_queue(packet_type):
        """Adds a new queue for a specific packet type."""
        if packet_type not in PacketQueue.queues:
            PacketQueue.queues[packet_type] = queue.Queue()

    @staticmethod
    def put(packet_type, packet_data):  # packet_data is a tuple (packet, player_indexes)
        """
        Adds a packet to the queue.

        Args:
            packet_type (str): The type of telemetry packet.
            packet_data (tuple): (packet, player_indexes)
        """
        if packet_type in PacketQueue.queues:
            PacketQueue.queues[packet_type].put(packet_data)

    @staticmethod
    def get(packet_type):
        """Retrieves the next packet from the queue."""
        if packet_type in PacketQueue.queues:
            try:
                return PacketQueue.queues[packet_type].get(timeout=1)  # Returns (packet, player_indexes)
            except queue.Empty:
                return None  # Return None if queue is empty
        return None  # Return None if queue does not exist
