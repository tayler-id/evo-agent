import os
from agent import AIResearchAgent
from dotenv import load_dotenv # Use python-dotenv to load .env file
import json # Import json for pretty printing analysis

# Load environment variables from .env file
load_dotenv()

# Define the path for the SQLite database
DB_FILEPATH = "ai_research.db"
# Define the directory for saving plots
PLOTS_OUTPUT_DIR = "research_plots"

def main():
    # Retrieve OpenAI API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file in the ai_research_agent directory with OPENAI_API_KEY=your_key")
        return

    agent = None # Initialize agent to None for finally block
    try:
        # Initialize the research agent with the database path
        print(f"Initializing agent and connecting to database: {DB_FILEPATH}...")
        agent = AIResearchAgent(
            "AI_Capability_Researcher",
            openai_api_key=openai_api_key,
            db_filepath=DB_FILEPATH # Pass the DB filepath
        )
        # DB connection/init messages handled by agent logger

        # Example experiment
        print("Conducting experiment...")
        experiment_result = agent.conduct_experiment(
            model_name="gpt-3.5-turbo",
            prompt="Explain quantum computing in simple terms",
            parameters={
                "temperature": 0.7,
                "max_tokens": 150
            }
        )

        # Check if experiment was successful and get ID
        if experiment_result and experiment_result.get('id') is not None:
            current_experiment_id = experiment_result['id']
            print(f"Experiment completed with ID: {current_experiment_id}")

            # Add observations (currently logs a warning)
            agent.add_observation(current_experiment_id, "Model provided coherent explanation with accurate technical details")
            agent.add_observation(current_experiment_id, "Response maintained simplicity while covering key concepts")

            # Add evaluation using the database ID
            print("\nEvaluating experiment...")
            # Extract usage info if available from the conduct_experiment return value
            usage_info = experiment_result.get('usage', {})
            token_cost = usage_info.get('total_tokens', 0) if usage_info else 0
            agent.evaluate_experiment(
                experiment_id=current_experiment_id,
                score=0.85, # Example score
                metrics={'clarity': 0.9, 'completeness': 0.8, 'token_cost': token_cost},
                notes="Good explanation, could be slightly more concise."
            )

            # Print the result content if available
            if experiment_result.get('result_content'):
                 print("\nExperiment Result Content:")
                 print(experiment_result['result_content'])
            if experiment_result.get('usage'):
                 print("\nUsage:", experiment_result['usage'])

        elif experiment_result and experiment_result.get('error'):
            print("\nExperiment failed:", experiment_result['error'])
        else:
            print("\nExperiment failed for an unknown reason.")


        # Analyze capabilities (reads from DB now)
        print("\nAnalyzing capabilities...")
        analysis = agent.analyze_capabilities()
        # Use json.dumps for pretty printing the analysis dictionary
        print("Research Analysis:")
        print(json.dumps(analysis, indent=4))

        # Generate visualizations
        print(f"\nGenerating visualizations in {PLOTS_OUTPUT_DIR}...")
        if agent: # Ensure agent was initialized
            agent.visualize_results(PLOTS_OUTPUT_DIR)

        # JSON saving is removed, data is saved per experiment/evaluation in DB

    finally:
        # Ensure database connection is closed
        if agent and agent.conn:
            print("\nClosing database connection...")
            agent.close_db()

if __name__ == "__main__":
    main()
