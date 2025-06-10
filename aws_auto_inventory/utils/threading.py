"""
Threading utilities for AWS Auto Inventory.
"""
import os
import logging
import concurrent.futures
from typing import List, Callable, TypeVar, Generic, Any, Dict, Optional

# Set up logger
logger = logging.getLogger(__name__)

# Type variables for generic functions
T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type


class ThreadingManager(Generic[T, R]):
    """
    Manager for concurrent execution of tasks.
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize threading manager.
        
        Args:
            max_workers: Maximum number of worker threads. If None, uses the default
                        from concurrent.futures.ThreadPoolExecutor.
        """
        self.max_workers = max_workers or min(32, os.cpu_count() * 5)
    
    def execute(
        self, 
        func: Callable[[T], R], 
        items: List[T]
    ) -> List[Dict[str, Any]]:
        """
        Execute a function concurrently for each item in a list.
        
        Args:
            func: Function to execute for each item.
            items: List of items to process.
            
        Returns:
            List of dictionaries containing the item, result, success flag, and error message.
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a future for each item
            future_to_item = {executor.submit(func, item): item for item in items}
            
            # Process completed futures
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append({
                        "item": item,
                        "result": result,
                        "success": True,
                        "error": None
                    })
                except Exception as e:
                    logger.error(f"Error processing item {item}: {str(e)}")
                    results.append({
                        "item": item,
                        "result": None,
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def execute_with_progress(
        self, 
        func: Callable[[T], R], 
        items: List[T], 
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a function concurrently for each item in a list with progress reporting.
        
        Args:
            func: Function to execute for each item.
            items: List of items to process.
            progress_callback: Callback function to report progress. Takes two arguments:
                              completed_count and total_count.
            
        Returns:
            List of dictionaries containing the item, result, success flag, and error message.
        """
        results = []
        total_count = len(items)
        completed_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a future for each item
            future_to_item = {executor.submit(func, item): item for item in items}
            
            # Process completed futures
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append({
                        "item": item,
                        "result": result,
                        "success": True,
                        "error": None
                    })
                except Exception as e:
                    logger.error(f"Error processing item {item}: {str(e)}")
                    results.append({
                        "item": item,
                        "result": None,
                        "success": False,
                        "error": str(e)
                    })
                
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, total_count)
        
        return results