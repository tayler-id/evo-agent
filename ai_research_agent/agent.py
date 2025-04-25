from typing import List, Dict, Any
import logging
from datetime import datetime
import openai  # Import the openai library
import json # Import json library
import os # Import os library
import matplotlib.pyplot as plt # Import plotting library
import sqlite3 # Import SQLite library

class AIResearchAgent:
    def __init__(self, name: str, openai_api_key: str, db_filepath: str):
        self.name = name
        self.openai_api_key = openai_api_key
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.db_filepath = db_filepath
        self.logger = self._setup_logger()
        self.conn = None
        self.cursor = None

        try:
            # Establish DB connection and cursor
            self.conn = sqlite3.connect(self.db_filepath)
            # Use Row factory for dictionary-like access
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.logger.info(f"Connected to database: {self.db_filepath}")
            # Initialize database tables
            self._initialize_db()
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error to {self.db_filepath}: {e}")
            raise e # Re-raise for now

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f"research_logs_{datetime.now().strftime('%Y%m%d')}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _initialize_db(self):
        """Create database tables if they don't exist."""
        try:
            # Experiments Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    prompt TEXT,
                    parameters_json TEXT,
                    result_content TEXT,
                    result_usage_json TEXT,
                    error TEXT
                )
            ''')
            # Evaluations Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id INTEGER NOT NULL UNIQUE,
                    timestamp TEXT NOT NULL,
                    score REAL,
                    notes TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                )
            ''')
            # TODO: Add tables for observations and evaluation_metrics if needed later
            self.conn.commit()
            self.logger.info("Database tables initialized successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database tables: {e}")
            raise e

    def close_db(self):
        """Close the database connection."""
        if self.conn:
            try:
                self.conn.close()
                self.logger.info("Database connection closed.")
            except sqlite3.Error as e:
                self.logger.error(f"Error closing database connection: {e}")

    def conduct_experiment(self, model_name: str, prompt: str, parameters: Dict[Any, Any]) -> Dict:
        """
        Conduct an experiment, record results in the database, and return the experiment ID.
        """
        timestamp = datetime.now()
        result_content = None
        result_usage_json = None
        error_str = None

        try:
            # Interact with the AI model
            result = self._interact_with_model(model_name, prompt, parameters)
            result_content = result.get('content')
            result_usage_json = json.dumps(result.get('usage')) if result.get('usage') else None
        except Exception as e:
            self.logger.error(f"Experiment interaction failed: {str(e)}")
            error_str = str(e)

        parameters_json = json.dumps(parameters)

        try:
            self.cursor.execute('''
                INSERT INTO experiments (timestamp, model_name, prompt, parameters_json, result_content, result_usage_json, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp.isoformat(), model_name, prompt, parameters_json, result_content, result_usage_json, error_str))
            self.conn.commit()
            experiment_id = self.cursor.lastrowid
            self.logger.info(f"Experiment {experiment_id} saved to database.")
            return {'id': experiment_id, 'error': error_str, 'result_content': result_content, 'usage': json.loads(result_usage_json) if result_usage_json else None} # Return more info
        except sqlite3.Error as e:
            self.logger.error(f"Database error saving experiment: {e}")
            return {'id': None, 'error': f"Database error: {e}"}

    def _interact_with_model(self, model_name: str, prompt: str, parameters: Dict) -> Dict:
        """Interact with the OpenAI model."""
        self.logger.info(f"Interacting with model: {model_name} with prompt: '{prompt[:50]}...'")
        try:
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                **parameters
            )
            result_content = response.choices[0].message.content
            usage = response.usage.to_dict()
            self.logger.info(f"Model interaction successful. Usage: {usage}")
            return {"content": result_content, "usage": usage}
        except openai.APIError as e:
            self.logger.error(f"OpenAI API Error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during model interaction: {e}")
            raise

    def add_observation(self, experiment_id: int, observation: str):
        """Add observations (Not implemented for DB yet)."""
        self.logger.warning(f"add_observation is not implemented for database storage yet (exp_id: {experiment_id}).")
        pass

    def evaluate_experiment(self, experiment_id: int, score: float, metrics: Dict[str, Any], notes: str):
        """Add evaluation data to the database."""
        timestamp = datetime.now().isoformat()
        # TODO: Store metrics properly (e.g., JSON column or separate table)
        # metrics_json = json.dumps(metrics)
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO evaluations (experiment_id, timestamp, score, notes)
                VALUES (?, ?, ?, ?)
            ''', (experiment_id, timestamp, score, notes))
            self.conn.commit()
            self.logger.info(f"Evaluation for experiment {experiment_id} saved to database.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error saving evaluation for experiment {experiment_id}: {e}")

    def analyze_capabilities(self) -> Dict:
        """Analyze capabilities based on data in the database."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM experiments")
            total_experiments = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT DISTINCT model_name FROM experiments")
            models_tested = set(row['model_name'] for row in self.cursor.fetchall())
            analysis = {
                'total_experiments': total_experiments,
                'models_tested': list(models_tested), # Convert set to list for JSON compatibility if needed later
                'success_rate': self._calculate_success_rate(),
                'capability_summary': self._generate_capability_summary()
            }
            return analysis
        except sqlite3.Error as e:
            self.logger.error(f"Database error during analysis: {e}")
            return {'total_experiments': 0, 'models_tested': [], 'success_rate': 0.0, 'capability_summary': {}}

    def _calculate_success_rate(self) -> float:
        """Calculate success rate from the database."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM experiments")
            total = self.cursor.fetchone()[0]
            if total == 0: return 0.0
            self.cursor.execute("SELECT COUNT(*) FROM experiments WHERE error IS NULL")
            successful = self.cursor.fetchone()[0]
            return successful / total
        except sqlite3.Error as e:
            self.logger.error(f"Database error calculating success rate: {e}")
            return 0.0

    def _generate_capability_summary(self) -> Dict:
        """Generate capability summary from the database."""
        summary = {}
        try:
            self.cursor.execute("SELECT DISTINCT model_name FROM experiments")
            all_models = [row['model_name'] for row in self.cursor.fetchall()]
            for model in all_models:
                summary[model] = {'experiment_count': 0, 'evaluated_count': 0, 'average_score': None, 'metrics_summary': {}, 'evaluation_notes': []}

            self.cursor.execute('''
                SELECT e.model_name, ev.score, ev.notes
                FROM experiments e LEFT JOIN evaluations ev ON e.id = ev.experiment_id
            ''')
            results = self.cursor.fetchall()
            model_scores = {model: [] for model in all_models}
            model_notes = {model: [] for model in all_models}
            model_counts = {model: 0 for model in all_models}

            for row in results:
                model = row['model_name']
                model_counts[model] += 1
                if row['score'] is not None: model_scores[model].append(row['score'])
                if row['notes']: model_notes[model].append(row['notes'])

            for model in all_models:
                summary[model]['experiment_count'] = model_counts[model]
                scores = model_scores[model]
                if scores:
                    summary[model]['evaluated_count'] = len(scores)
                    summary[model]['average_score'] = round(sum(scores) / len(scores), 3)
                summary[model]['evaluation_notes'] = model_notes[model]
                # TODO: Aggregate metrics from DB if stored

            return summary
        except sqlite3.Error as e:
            self.logger.error(f"Database error generating capability summary: {e}")
            return {}

    def visualize_results(self, output_dir: str):
        """Generate visualizations based on experiment results."""
        self.logger.info(f"Generating visualizations in directory: {output_dir}")
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Error creating output directory {output_dir}: {e}")
            return

        analysis = self.analyze_capabilities()
        summary = analysis.get('capability_summary', {})
        if not summary:
            self.logger.warning("No capability summary data to visualize.")
            return

        models, avg_scores, evaluated_counts = [], [], []
        for model, data in summary.items():
            if data.get('average_score') is not None:
                models.append(model)
                avg_scores.append(data['average_score'])
                evaluated_counts.append(data.get('evaluated_count', 0))

        if not models:
            self.logger.info("No models with average scores found to plot.")
            return

        try:
            plt.figure(figsize=(10, 6))
            bars = plt.bar(models, avg_scores, color='skyblue')
            plt.xlabel("Model Name")
            plt.ylabel("Average Score")
            plt.title("Average Experiment Score per Model")
            plt.ylim(0, 1)
            plt.xticks(rotation=45, ha='right')
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2., height, f'n={evaluated_counts[i]}', ha='center', va='bottom')
            plt.tight_layout()
            plot_filepath = os.path.join(output_dir, "average_scores.png")
            plt.savefig(plot_filepath)
            self.logger.info(f"Saved average scores plot to {plot_filepath}")
            plt.close()
        except Exception as e:
             self.logger.error(f"Error generating or saving average scores plot: {e}")
