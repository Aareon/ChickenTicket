import random
import matplotlib.pyplot as plt
from src.chain import Blockchain
from loguru import logger

class BlockchainSimulator:
    def __init__(self, alpha_values, scaling_factors, simulation_rounds=100):
        self.alpha_values = alpha_values
        self.scaling_factors = scaling_factors
        self.simulation_rounds = simulation_rounds

    def custom_log(self, message, alpha, scaling_factor):
        """Custom logging function to include alpha and scaling factor in the log message."""
        logger.info(f"Alpha={alpha}, Scaling={scaling_factor}, {message}")

    def simulate(self):
        results = {}
        for alpha in self.alpha_values:
            for scaling_factor in self.scaling_factors:
                # Use custom_log to log the start of a simulation round
                self.custom_log("Starting simulation...", alpha, scaling_factor)
                blockchain = Blockchain()
                blockchain.alpha = alpha
                blockchain.scaling_factor = scaling_factor  # Assuming you have a way to set this in your Blockchain
                
                difficulties, block_times = self.simulate_mining(blockchain, alpha, scaling_factor)
                results[(alpha, scaling_factor)] = (difficulties, block_times)

        self.plot_results(results)

    def simulate_mining(self, blockchain, alpha, scaling_factor):
        difficulties = []
        block_times = []
        for i in range(self.simulation_rounds):
            # Directly call blockchain.mine() without simulated block time argument
            blockchain.mine()
            
            last_block = blockchain.chain[-1]
            difficulties.append(last_block.difficulty)
            simulated_block_time = random.randint(1, 200)  # This simulates variable mining times
            block_times.append(simulated_block_time)

            # Optionally, log each block's mining outcome
            self.custom_log(f"Mined block {i+1} with difficulty {last_block.difficulty} in {simulated_block_time}s", alpha, scaling_factor)

        return difficulties, block_times

    def plot_results(self, results):
        plt.figure(figsize=(14, 7))

        for params, (difficulties, block_times) in results.items():
            alpha, scaling_factor = params
            plt.plot(difficulties, label=f"Alpha={alpha}, Scaling={scaling_factor}")

        plt.xlabel('Block Number')
        plt.ylabel('Difficulty')
        plt.title('Blockchain Simulation: Difficulty Adjustments')
        plt.legend()
        plt.show()

# Example usage
alpha_values = [0.01, 0.025, 0.3, 0.5]
scaling_factors = [0.08, 0.1, 0.12]
simulator = BlockchainSimulator(alpha_values, scaling_factors, simulation_rounds=500)
simulator.simulate()
