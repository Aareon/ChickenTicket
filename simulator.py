import random
import matplotlib.pyplot as plt
from src.chain import Blockchain
from loguru import logger
from math import exp


def calculate_simulated_block_time(hash_power, difficulty):
    """
    Calculates simulated block time based on hash power and difficulty.
    
    This method assumes an exponential relationship where higher difficulty 
    and lower hash power exponentially increase the block time. The model 
    can be adjusted based on a deeper understanding of the relationship.
    
    Parameters:
    hash_power (float): The hash power available for mining.
    difficulty (float): The current difficulty of mining a block.
    
    Returns:
    float: The simulated time (in seconds) it takes to mine a block.
    """
    # Check to avoid division by zero
    if hash_power == 0:
        return float('inf')  # Infinite time if no hash power
    
    # Using an exponential decay model for block time calculation
    # The base of the exponential function can be adjusted to simulate different environments
    # This formula assumes that an increase in difficulty or a decrease in hash power increases the block time
    base = 2  # Adjust base to change the sensitivity of block time to hash power and difficulty
    exponent = difficulty / hash_power
    
    # Calculate block time, ensuring it doesn't fall below a minimum threshold
    min_block_time = 1  # Minimum block time in seconds

    # Introduce randomness to the block time calculation
    randomness_factor = random.uniform(0.8, 1.2)

    block_time = max(exp(exponent) * randomness_factor / base, min_block_time)
    
    return block_time


class BlockchainSimulator:
    def __init__(self, scaling_factors, simulation_rounds=100):
        self.scaling_factors = scaling_factors
        self.simulation_rounds = simulation_rounds

    def custom_log(self, message, scaling_factor):
        """Custom logging function to include scaling factor in the log message."""
        logger.info(f"Scaling={scaling_factor}, {message}")

    def simulate(self):
        results = {}
        for scaling_factor in self.scaling_factors:
            # Use custom_log to log the start of a simulation round
            self.custom_log("Starting simulation...", scaling_factor)
            blockchain = Blockchain()
            blockchain.scaling_factor = scaling_factor  # Assuming you have a way to set this in your Blockchain
                
            difficulties, block_times = self.simulate_mining(blockchain, scaling_factor)
            results[scaling_factor] = (difficulties, block_times)

        self.plot_results(results)

    def simulate_mining(self, blockchain, scaling_factor):
        difficulties = []
        block_times = []

        # Simulate initial hash power (this can be any value you choose to start with)
        hash_power = 1000
        for i in range(self.simulation_rounds):
            # Adjust hash power to simulate changes in the network's mining capacity
            # This could be more sophisticated based on your needs
            hash_power *= random.uniform(0.9, 1.1)  # Simulate fluctuating hash power

            # Simulate the mining process
            blockchain.mine()

            last_block = blockchain.chain[-1]
            difficulties.append(last_block.difficulty)
            # This simulates variable mining times based on network hash power
            difficulty = blockchain.chain[-1].difficulty
            simulated_block_time = calculate_simulated_block_time(hash_power, difficulty)
            block_times.append(simulated_block_time)

            # Log each block's mining outcome
            self.custom_log(f"Mined block {i+1} with difficulty {last_block.difficulty} in {simulated_block_time}s", scaling_factor)

        return difficulties, block_times

    def plot_results(self, results):
        plt.figure(figsize=(14, 7))

        for scaling_factor, (difficulties, block_times) in results.items():
            plt.plot(difficulties, label=f"Scaling={scaling_factor}")

        plt.xlabel('Block Number')
        plt.ylabel('Difficulty')
        plt.title('Blockchain Simulation: Difficulty Adjustments')
        plt.legend()
        plt.show()

# Example usage
scaling_factors = [0.08, 0.1, 0.12]
simulator = BlockchainSimulator(scaling_factors, simulation_rounds=500)
simulator.simulate()
