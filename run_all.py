#!/usr/bin/env python3
"""
Multi-process runner for the Flask e-commerce application with AI monitoring.
This script starts all three components:
1. Main Flask web application (app.py)
2. Log generator (log_generator.py) 
3. AI anomaly monitor (log_ai_monitor.py)
"""

import subprocess
import signal
import os
import sys
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.shutdown_requested = False
        
    def start_process(self, name, cmd, cwd=None):
        """Start a process and track it"""
        try:
            logger.info(f"Starting {name}...")
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                preexec_fn=os.setsid if os.name != 'nt' else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            self.processes[name] = process
            logger.info(f"{name} started with PID {process.pid}")
            return process
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return None
    
    def stop_processes(self, signum=None, frame=None):
        """Gracefully stop all processes"""
        if self.shutdown_requested:
            return
            
        self.shutdown_requested = True
        logger.info("Shutting down all processes...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    logger.info(f"Stopping {name} (PID: {process.pid})")
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        logger.info(f"{name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Force killing {name}")
                        if os.name != 'nt':
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        else:
                            process.kill()
                        
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")
        
        logger.info("All processes stopped")
        sys.exit(0)
    
    def check_processes(self):
        """Check if all processes are still running"""
        for name, process in self.processes.items():
            if process and process.poll() is not None:
                logger.warning(f"{name} has stopped unexpectedly")
                return False
        return True
    
    def run(self):
        """Main execution loop"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.stop_processes)
        signal.signal(signal.SIGTERM, self.stop_processes)
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Start all processes
        processes_to_start = [
            ("Flask App", ["python", "app.py"]),
            ("Log Generator", ["python", "log_generator.py"]),
            ("AI Monitor", ["python", "log_ai_monitor.py"])
        ]
        
        for name, cmd in processes_to_start:
            if not self.start_process(name, cmd):
                logger.error(f"Failed to start {name}, exiting...")
                self.stop_processes()
                return
        
        logger.info("All processes started successfully")
        logger.info("Flask App: http://localhost:5000")
        logger.info("AI Monitor: http://localhost:9000")
        logger.info("Press Ctrl+C to stop all processes")
        
        # Monitor processes
        try:
            while not self.shutdown_requested:
                if not self.check_processes():
                    logger.error("One or more processes have failed")
                    break
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_processes()

def main():
    """Entry point"""
    logger.info("Starting Flask E-commerce Application with AI Monitoring")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    manager = ProcessManager()
    manager.run()

if __name__ == "__main__":
    main()
