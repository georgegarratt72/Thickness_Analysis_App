import threading
import time
import base64
import concurrent.futures
import streamlit as st
from utils.ui import fig_to_base64
from utils.helpers import generate_lot_analysis_report_html, generate_simple_report_html

class BackgroundReportGenerator:
    """Handles background generation of HTML reports with chart images."""
    
    def __init__(self):
        self.threads = {}
        self.progress = {}
        self.completed_reports = {}
    
    def start_background_generation(self, analysis_type, title, scores_data, plot_objects, target_mean, input_filename):
        """Start background generation of HTML report with chart images."""
        thread_key = f"{analysis_type}_report"
        
        # If already processing, don't start again
        if thread_key in self.threads and self.threads[thread_key].is_alive():
            return
        
        # Initialize progress
        self.progress[thread_key] = {
            'status': 'Starting...',
            'percentage': 0,
            'completed': False,
            'error': None,
            'start_time': time.time()
        }
        
        # Start background thread
        thread = threading.Thread(
            target=self._generate_report_with_images,
            args=(thread_key, title, scores_data, plot_objects, target_mean, input_filename)
        )
        thread.daemon = True
        thread.start()
        self.threads[thread_key] = thread
    
    def _generate_report_with_images(self, thread_key, title, scores_data, plot_objects, target_mean, input_filename):
        """Background function to generate report with chart images - OPTIMIZED VERSION."""
        try:
            # Update progress
            self.progress[thread_key]['status'] = 'Converting charts to images...'
            self.progress[thread_key]['percentage'] = 10
            
            # OPTIMIZATION 1: Parallel chart conversion using ThreadPoolExecutor
            chart_images = {}
            valid_plots = {k: v for k, v in plot_objects.items() if v is not None}
            
            if valid_plots:
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    # Submit all chart conversion tasks simultaneously
                    future_to_key = {
                        executor.submit(self._fast_convert_figure, plot_fig, plot_key): plot_key 
                        for plot_key, plot_fig in valid_plots.items()
                    }
                    
                    completed = 0
                    total_charts = len(valid_plots)
                    
                    for future in concurrent.futures.as_completed(future_to_key):
                        plot_key = future_to_key[future]
                        try:
                            chart_images[plot_key] = future.result()
                            completed += 1
                            
                            # Update progress with time estimation
                            progress_percent = 10 + (completed * 70 // total_charts)
                            elapsed = time.time() - self.progress[thread_key]['start_time']
                            if completed > 0:
                                estimated_total = elapsed * total_charts / completed
                                remaining = max(0, estimated_total - elapsed)
                                self.progress[thread_key]['status'] = f'Converted {completed}/{total_charts} charts... (~{remaining:.0f}s remaining)'
                            else:
                                self.progress[thread_key]['status'] = f'Converted {completed}/{total_charts} charts...'
                            self.progress[thread_key]['percentage'] = progress_percent
                            
                        except Exception as e:
                            chart_images[plot_key] = ""
                            completed += 1
            
            # Generate final report
            self.progress[thread_key]['status'] = 'Generating final report...'
            self.progress[thread_key]['percentage'] = 90
            
            # Create plot objects dict with base64 images
            plot_objects_with_images = {}
            for key, fig in plot_objects.items():
                if key in chart_images and chart_images[key]:
                    plot_objects_with_images[key] = fig
                else:
                    plot_objects_with_images[key] = None
            
            # Generate the complete report
            html_report = generate_lot_analysis_report_html(
                title, scores_data, plot_objects_with_images, target_mean, input_filename
            )
            
            # Store completed report
            self.completed_reports[thread_key] = html_report
            
            # Mark as completed
            self.progress[thread_key]['status'] = 'Report ready for download!'
            self.progress[thread_key]['percentage'] = 100
            self.progress[thread_key]['completed'] = True
            
        except Exception as e:
            self.progress[thread_key]['error'] = str(e)
            self.progress[thread_key]['status'] = f'Error: {str(e)}'
            self.progress[thread_key]['completed'] = True
    
    def _fast_convert_figure(self, fig, plot_key):
        """OPTIMIZED: Fast figure conversion with smaller images and better kaleido usage."""
        if fig is None:
            return ""
        
        try:
            import kaleido
        except ImportError:
            return ""
        
        try:
            from io import BytesIO
            
            buf = BytesIO()
            
            # OPTIMIZATION 2: Smaller image sizes for faster processing
            width = 800  # Reduced from 1000
            height = fig.layout.height if fig.layout.height else 500  # Reduced from 600
            
            # OPTIMIZATION 3: Direct conversion without additional threading
            fig.write_image(buf, format="png", width=width, height=height, engine="kaleido")
            return base64.b64encode(buf.getvalue()).decode("utf-8")
            
        except Exception as e:
            return ""
    
    def get_progress(self, analysis_type):
        """Get progress of background report generation."""
        thread_key = f"{analysis_type}_report"
        return self.progress.get(thread_key, {
            'status': 'Not started',
            'percentage': 0,
            'completed': False,
            'error': None
        })
    
    def get_completed_report(self, analysis_type):
        """Get completed report if available."""
        thread_key = f"{analysis_type}_report"
        return self.completed_reports.get(thread_key, None)
    
    def is_processing(self, analysis_type):
        """Check if background processing is active."""
        thread_key = f"{analysis_type}_report"
        return (thread_key in self.threads and 
                self.threads[thread_key].is_alive() and 
                not self.progress.get(thread_key, {}).get('completed', False))

# Global instance
background_generator = BackgroundReportGenerator() 