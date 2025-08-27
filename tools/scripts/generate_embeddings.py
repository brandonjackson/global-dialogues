#!/usr/bin/env python3
"""
Generate embeddings for Global Dialogues responses.

This script generates embeddings for all open-ended responses in a Global Dialogue dataset
using OpenAI's text-embedding-3-small model. It reads the raw aggregate CSV file exported
directly from Remesh and saves embeddings in the same format as the notebook.

The process typically takes ~2 minutes per 1000 responses (approximately 30-50 minutes 
for a full dataset).

Usage:
    python generate_embeddings.py --gd_number <N>
"""

import argparse
import logging
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from dotenv import load_dotenv
from lib.analysis_utils import parse_gd_identifier, validate_gd_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress HTTP request logs from OpenAI/httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

# Try to import OpenAI
try:
    from openai import OpenAI
except ImportError:
    logger.error("OpenAI library not installed. Please run: pip install openai")
    sys.exit(1)


class EmbeddingGenerator:
    """Handles the generation of embeddings for Global Dialogues responses."""
    
    def __init__(self, gd_identifier: str):
        self.gd_identifier = gd_identifier
        self.data_dir = Path("Data") / gd_identifier
        self.aggregate_file = self.data_dir / f"{gd_identifier}_aggregate.csv"
        self.embeddings_file = self.data_dir / f"{gd_identifier}_embeddings.json"
        self.checkpoint_file = self.data_dir / f"{gd_identifier}_embeddings_checkpoint.json"
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
        # Embedding parameters (matching the notebook)
        self.model = "text-embedding-3-small"
        self.dimensions = 1024
        
        # Cost estimation for text-embedding-3-small (as of 2024)
        # OpenAI pricing: $0.02 per 1M tokens = $0.00002 per 1K tokens
        self.cost_per_1k_tokens = 0.00002  
        # Average response length is typically 100-200 tokens for dialogue responses
        self.avg_tokens_per_response = 150  # More realistic estimate
        
        # Progress tracking
        self.total_responses = 0
        self.processed_responses = 0
        self.start_time = None
        self.checkpoint_data = None
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        if not self.aggregate_file.exists():
            logger.error(f"Aggregate file not found: {self.aggregate_file}")
            logger.info(f"Please ensure you have exported the aggregate CSV from Remesh")
            logger.info(f"Expected file: {self.aggregate_file}")
            return False
        
        return True
    
    def check_existing_embeddings(self) -> bool:
        """Check if embeddings file already exists."""
        if self.embeddings_file.exists():
            file_size = self.embeddings_file.stat().st_size / (1024 * 1024)  # MB
            logger.warning(f"Embeddings file already exists: {self.embeddings_file} ({file_size:.1f} MB)")
            
            response = input("\nDo you want to overwrite the existing embeddings? (yes/no): ").strip().lower()
            return response == 'yes'
        
        return True
    
    def check_checkpoint(self) -> Dict[str, Any]:
        """Check if a checkpoint exists and load it."""
        if self.checkpoint_file.exists():
            logger.info(f"Found checkpoint file: {self.checkpoint_file}")
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                completed_questions = checkpoint.get('completed_questions', [])
                total_processed = checkpoint.get('total_processed', 0)
                
                logger.info(f"Checkpoint contains {len(completed_questions)} completed questions")
                logger.info(f"Total responses processed: {total_processed}")
                
                return checkpoint
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
                return None
        return None
    
    def save_checkpoint(self, qs: List[pd.DataFrame], completed_questions: List[int], 
                       question_indices: List[int]) -> None:
        """Save current progress to checkpoint file."""
        checkpoint = {
            'completed_questions': completed_questions,
            'total_processed': self.processed_responses,
            'timestamp': datetime.now().isoformat(),
            'total_questions': len(question_indices),
            'question_indices': question_indices
        }
        
        # Save partial results
        qs_checkpoint = []
        for i, df in enumerate(qs):
            if i in completed_questions:
                # Save with embeddings
                df_dict = df.to_dict('records')
            else:
                # Save without embeddings for uncompleted questions
                df_without_embeddings = df.drop('embedding', axis=1) if 'embedding' in df.columns else df
                df_dict = df_without_embeddings.to_dict('records')
            qs_checkpoint.append(df_dict)
        
        checkpoint['partial_qs'] = qs_checkpoint
        
        # Write checkpoint
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f)
            # Silent save - no logging to keep terminal clean
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def load_aggregate_data(self) -> List[pd.DataFrame]:
        """Load the raw aggregate CSV file (direct Remesh export) and parse it into the qs structure."""
        logger.info(f"Loading raw aggregate data from {self.aggregate_file}")
        
        # This mimics the notebook's CSV loading logic
        with open(self.aggregate_file, 'r') as file:
            import csv
            csvreader = csv.reader(file)
            
            # Skip padding rows (metadata at the top)
            PADDING_ROWS = 9
            for _ in range(PADDING_ROWS):
                next(csvreader)
            
            data = []
            qdata = []
            
            for row in csvreader:
                if len(row) == 0 or not row[0].strip():
                    if qdata:
                        data.append(qdata)
                        qdata = []
                else:
                    qdata.append(row)
            
            if qdata:
                data.append(qdata)
        
        # Process the data into DataFrames
        qs = []
        for i in range(len(data)):
            if not data[i]:
                continue
                
            # Create DataFrame from the question data
            df = pd.DataFrame(data[i][1:], columns=data[i][0])
            
            # Convert percentage strings to float for Poll questions
            if len(df) > 0 and 'Question Type' in df.columns:
                if df['Question Type'].iloc[0] == 'Poll Single Select':
                    for col in df.columns[4:]:
                        df[col] = df[col].apply(self._percent_to_float)
                elif df['Question Type'].iloc[0] == 'Ask Opinion':
                    for col in df.columns[6:-3]:
                        df[col] = df[col].apply(self._percent_to_float)
            
            qs.append(df)
        
        logger.info(f"Loaded {len(qs)} questions from aggregate file")
        return qs
    
    @staticmethod
    def _percent_to_float(x):
        """Convert percentage string to float."""
        try:
            if x == ' - ':
                return float("nan")
            else:
                return float(x.strip('%')) / 100
        except:
            return x
    
    def count_responses_to_embed(self, qs: List[pd.DataFrame]) -> Tuple[int, List[int]]:
        """Count total responses that need embedding and identify question indices."""
        total_responses = 0
        question_indices = []
        
        for i in range(len(qs)):
            if len(qs[i]) > 0 and 'Question Type' in qs[i].columns:
                # Check if it's an open-ended question (Ask Opinion or Ask Experience)
                if "Ask" in qs[i]['Question Type'].iloc[0]:
                    total_responses += len(qs[i])
                    question_indices.append(i)
        
        return total_responses, question_indices
    
    def estimate_cost_and_time(self, total_responses: int) -> Tuple[float, float]:
        """Estimate the cost and time for generating embeddings."""
        # Estimate tokens
        total_tokens = total_responses * self.avg_tokens_per_response
        
        # Estimate cost
        estimated_cost = (total_tokens / 1000) * self.cost_per_1k_tokens
        
        # Estimate time (2 minutes per 1000 responses from notebook comment)
        estimated_minutes = (total_responses / 1000) * 2
        
        return estimated_cost, estimated_minutes
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using OpenAI API."""
        text = text.replace("\n", " ")
        response = self.client.embeddings.create(
            input=[text],
            model=self.model,
            dimensions=self.dimensions
        )
        return response.data[0].embedding
    
    def embed_responses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add embeddings to all responses in a DataFrame."""
        df = df.copy()
        embeddings = []
        
        for idx, row in df.iterrows():
            if pd.notna(row.get('English Responses')):
                try:
                    embedding = self.get_embedding(str(row['English Responses']))
                    embeddings.append(embedding)
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for response {idx}: {e}")
                    embeddings.append(None)
            else:
                embeddings.append(None)
            
            self.processed_responses += 1
        
        df['embedding'] = embeddings
        return df
    
    def generate_embeddings(self, qs: List[pd.DataFrame], question_indices: List[int], 
                          completed_questions: List[int] = None) -> List[pd.DataFrame]:
        """Generate embeddings for all open-ended responses."""
        if completed_questions is None:
            completed_questions = []
            
        logger.info("Starting embedding generation...")
        if completed_questions:
            logger.info(f"Resuming from checkpoint - {len(completed_questions)} questions already completed")
            
        self.start_time = time.time()
        
        # Calculate already processed responses for progress bar
        already_processed = sum(len(qs[i]) for i in completed_questions if i in question_indices)
        self.processed_responses = already_processed
        
        # Create progress bar with better formatting
        pbar = tqdm(total=self.total_responses, initial=already_processed, 
                   desc="Generating embeddings", unit=" responses",
                   bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
        
        try:
            # Log how many questions we're skipping if resuming
            if completed_questions:
                skip_count = len([i for i in question_indices if i in completed_questions])
                logger.info(f"Skipping {skip_count} already completed questions")
            
            for idx, i in enumerate(question_indices):
                # Skip if already completed
                if i in completed_questions:
                    continue
                    
                # Only log every 5th question to reduce clutter
                if idx % 5 == 0:
                    logger.info(f"Processing questions {i+1}-{min(i+5, len(qs))}/{len(qs)}...")
                
                # Update progress bar description
                pbar.set_description(f"Question {i+1}/{len(qs)}")
                
                # Generate embeddings for this question
                qs[i] = self.embed_responses(qs[i])
                
                # Update progress
                pbar.update(len(qs[i]))
                
                # Mark question as completed and save checkpoint
                completed_questions.append(i)
                self.save_checkpoint(qs, completed_questions, question_indices)
                
                # Log progress every 5 questions or at milestones
                if idx % 5 == 0 or idx == len(question_indices) - 1:
                    elapsed = time.time() - self.start_time
                    rate = (self.processed_responses - already_processed) / elapsed if elapsed > 0 else 0
                    remaining = (self.total_responses - self.processed_responses) / rate if rate > 0 else 0
                    
                    logger.info(f"Checkpoint saved | {self.processed_responses}/{self.total_responses} responses "
                              f"({self.processed_responses/self.total_responses*100:.1f}%) | "
                              f"Est. remaining: {timedelta(seconds=int(remaining))}")
        
        finally:
            pbar.close()
        
        return qs
    
    def save_embeddings(self, qs: List[pd.DataFrame]) -> None:
        """Save the qs structure with embeddings to JSON file."""
        logger.info(f"Saving embeddings to {self.embeddings_file}")
        
        # Convert DataFrames to dictionaries for JSON serialization
        qs_dicts = []
        for df in qs:
            # Convert DataFrame to dictionary
            df_dict = df.to_dict('records')
            qs_dicts.append(df_dict)
        
        # Save to JSON
        with open(self.embeddings_file, 'w') as f:
            json.dump(qs_dicts, f)
        
        file_size = self.embeddings_file.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"Embeddings saved successfully ({file_size:.1f} MB)")
    
    def run(self) -> None:
        """Run the complete embedding generation process."""
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        # Check for existing checkpoint
        checkpoint = self.check_checkpoint()
        completed_questions = []
        qs = None
        
        if checkpoint:
            response = input("\nA previous run was interrupted. Do you want to resume from checkpoint? (yes/no): ").strip().lower()
            if response == 'yes':
                completed_questions = checkpoint.get('completed_questions', [])
                # Try to restore the partial qs data structure
                if 'partial_qs' in checkpoint:
                    logger.info("Restoring data from checkpoint...")
                    qs = []
                    for df_dict in checkpoint['partial_qs']:
                        qs.append(pd.DataFrame(df_dict))
                else:
                    logger.info("No partial data in checkpoint, reloading from scratch...")
                    qs = self.load_aggregate_data()
            else:
                # User chose not to resume, delete checkpoint
                try:
                    self.checkpoint_file.unlink()
                    logger.info("Checkpoint deleted, starting fresh...")
                except Exception as e:
                    logger.warning(f"Failed to delete checkpoint: {e}")
        
        # Check existing embeddings only if not resuming
        if not completed_questions and not self.check_existing_embeddings():
            logger.info("Embedding generation cancelled by user")
            return
        
        # Load data if not already loaded from checkpoint
        if qs is None:
            qs = self.load_aggregate_data()
        
        # Count responses and estimate cost/time
        self.total_responses, question_indices = self.count_responses_to_embed(qs)
        
        if self.total_responses == 0:
            logger.warning("No open-ended responses found to embed")
            return
        
        # Calculate remaining work
        completed_responses = sum(len(qs[i]) for i in completed_questions if i in question_indices)
        remaining_responses = self.total_responses - completed_responses
        remaining_questions = len([i for i in question_indices if i not in completed_questions])
        
        # Estimate cost and time for remaining work
        estimated_cost, estimated_minutes = self.estimate_cost_and_time(remaining_responses)
        
        # Display summary and get confirmation
        total_tokens = remaining_responses * self.avg_tokens_per_response
        print("\n" + "="*60)
        print(f"EMBEDDING GENERATION SUMMARY FOR GD{self.gd_number}")
        print("="*60)
        print(f"Total responses to embed: {self.total_responses:,}")
        if completed_questions:
            print(f"Already completed: {completed_responses:,} responses")
            print(f"Remaining to process: {remaining_responses:,} responses")
            print(f"Questions completed: {len(completed_questions)}/{len(question_indices)}")
        print(f"Open-ended questions: {len(question_indices)} (remaining: {remaining_questions})")
        print(f"Estimated time: {timedelta(minutes=int(estimated_minutes))}")
        print(f"Estimated cost: ${estimated_cost:.2f}")
        print(f"Model: {self.model}")
        print(f"Dimensions: {self.dimensions}")
        print("="*60)
        print("\nNOTE: Progress is saved after each question. If interrupted, you can resume later.")
        
        response = input("\nDo you want to proceed with embedding generation? (yes/no): ").strip().lower()
        if response != 'yes':
            logger.info("Embedding generation cancelled by user")
            return
        
        # Generate embeddings
        qs = self.generate_embeddings(qs, question_indices, completed_questions)
        
        # Save results
        self.save_embeddings(qs)
        
        # Clean up checkpoint file on successful completion
        if self.checkpoint_file.exists():
            try:
                self.checkpoint_file.unlink()
                logger.info("Checkpoint file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to delete checkpoint file: {e}")
        
        # Final summary
        total_time = time.time() - self.start_time
        actual_processed = self.processed_responses - completed_responses
        print("\n" + "="*60)
        print(f"✓ EMBEDDING GENERATION COMPLETE")
        print("="*60)
        print(f"Total time: {timedelta(seconds=int(total_time))}")
        if actual_processed > 0:
            print(f"Processing rate: {actual_processed/total_time:.1f} responses/second")
        print(f"Output saved to: {self.embeddings_file}")
        file_size = self.embeddings_file.stat().st_size / (1024 * 1024)  # MB
        print(f"File size: {file_size:.1f} MB")
        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate embeddings for Global Dialogues responses"
    )
    parser.add_argument(
        "--gd_number",
        type=str,
        required=True,
        help="Global Dialogue identifier (e.g., '5', '6UK', '6_UK')"
    )
    
    args = parser.parse_args()
    
    try:
        gd_identifier = parse_gd_identifier(args.gd_number)
        validate_gd_directory(gd_identifier)
        
        generator = EmbeddingGenerator(gd_identifier)
        generator.run()
    except KeyboardInterrupt:
        logger.warning("\nEmbedding generation interrupted by user")
        logger.info("Progress has been saved. You can resume by running the same command again.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}")
        logger.info("Progress has been saved. You can resume by running the same command again.")
        sys.exit(1)


if __name__ == "__main__":
    main()