"""
Thread management utilities

This module provides utilities for managing background threads safely.
"""
import threading
import logging
import time
import random
from queue import Queue

# Set up logging
logger = logging.getLogger(__name__)

# Maximum number of worker threads
MAX_WORKERS = 3

# Thread-safe queue for tasks
task_queue = Queue()

# List of active workers
workers = []

# Flag to control worker threads
should_stop = False


def add_task(func, *args, **kwargs):
    """
    Add a task to the background task queue
    
    Args:
        func: The function to call
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    """
    task_queue.put((func, args, kwargs))
    ensure_workers()


def worker_thread():
    """
    Worker thread that processes tasks from the queue
    """
    global should_stop
    
    logger.info("Starting worker thread")
    
    while not should_stop:
        try:
            # Get a task with a 1-second timeout
            try:
                task, args, kwargs = task_queue.get(timeout=1)
            except:
                # No task available, continue the loop
                continue
            
            # Execute the task
            try:
                logger.info(f"Executing background task: {task.__name__}")
                task(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in background task {task.__name__}: {str(e)}")
            
            # Mark the task as done
            task_queue.task_done()
            
        except Exception as e:
            logger.error(f"Error in worker thread: {str(e)}")
            # Add a small delay to prevent busy-waiting in case of repeated errors
            time.sleep(0.1)
    
    logger.info("Worker thread stopping")


def ensure_workers():
    """
    Ensure that worker threads are running
    """
    global workers
    
    # Clean up any dead workers
    workers = [w for w in workers if w.is_alive()]
    
    # Start new workers if needed
    while len(workers) < MAX_WORKERS:
        thread = threading.Thread(target=worker_thread, daemon=True)
        thread.start()
        workers.append(thread)
        logger.info(f"Started new worker thread (total: {len(workers)})")


def stop_workers():
    """
    Stop all worker threads
    """
    global should_stop, workers
    
    logger.info("Stopping all worker threads")
    
    # Set the stop flag
    should_stop = True
    
    # Wait for all threads to stop
    for worker in workers:
        if worker.is_alive():
            worker.join(timeout=2)
    
    # Clear the workers list
    workers = []
    
    # Reset the stop flag
    should_stop = False
    
    logger.info("All worker threads stopped")


def preload_questions_in_background(get_random_topic_func, generate_mcq_func, 
                                    generate_subj_func, generate_coding_func):
    """
    Preload various question types in the background
    
    Args:
        get_random_topic_func: Function to get a random topic
        generate_mcq_func: Function to generate MCQ questions
        generate_subj_func: Function to generate subjective questions
        generate_coding_func: Function to generate coding questions
    """
    difficulties = ["Easy", "Medium", "Hard", "Expert"]
    
    # Preload one of each type
    topic = get_random_topic_func()
    
    if topic:
        difficulty = random.choice(difficulties)
        
        # Add tasks to the queue with a 50% chance for each type
        if random.random() < 0.5:
            add_task(generate_mcq_func, topic, difficulty)
            
        if random.random() < 0.5:
            add_task(generate_subj_func, topic, difficulty)
    
    # Always preload one coding question
    add_task(generate_coding_func, None, random.choice(difficulties)) 