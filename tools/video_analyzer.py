from smolagents import Tool
import os
import time
import tempfile
from transformers import pipeline
from typing import List, Dict
from PIL import Image
import io

# Import required browser automation libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import helium

class WebVideoAnalyzerTool(Tool):
    name = "web_video_analyzer"
    description = "Analyzes a video on a webpage (YouTube, Vimeo, etc.) by taking screenshots at intervals and counting objects of a specified type in each frame."
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL of the web page containing the video to analyze.",
        },
        "label": {
            "type": "string",
            "description": "The type of object to count (e.g., 'bird', 'person', 'car', 'dog'). Use common object names recognized by standard object detection models.",
        },
        "duration": {
            "type": "integer",
            "description": "How many seconds of the video to analyze (default: 30)",
        },
        "interval": {
            "type": "integer",
            "description": "How often to take screenshots (in seconds, default: 1)",
        }
    }
    output_type = "string"

    def _setup_browser(self):
        """Initialize the browser with appropriate settings."""
        if self.driver is not None:
            return self.driver
            
        print("Setting up browser...")
        
        # Configure Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument("--disable-pdf-viewer")
        chrome_options.add_argument("--window-position=0,0")
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
        
        # Initialize the driver
        self.driver = helium.start_chrome(headless=False, options=chrome_options)
        return self.driver

    def _navigate_to_video(self, url: str) -> bool:
        """Navigate to the video URL and prepare for playback."""
        try:
            print(f"Navigating to {url}...")
            helium.go_to(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Handle YouTube-specific interactions
            if "youtube.com" in url:
                try:
                    # Accept cookies if prompted
                    if helium.Button("Accept all").exists():
                        helium.click("Accept all")
                    elif helium.Button("I agree").exists():
                        helium.click("I agree")
                    
                    # Click on the video to ensure it's playing
                    try:
                        # Find the video player element
                        video_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "video"))
                        )
                        video_element.click()
                        
                        # Ensure the video is playing by trying to click the play button if visible
                        try:
                            play_button = self.driver.find_element(By.CLASS_NAME, "ytp-play-button")
                            if "Play" in play_button.get_attribute("aria-label"):
                                play_button.click()
                        except:
                            pass
                            
                    except:
                        print("Could not locate video element to click")
                
                except Exception as e:
                    print(f"Error during YouTube setup: {str(e)}")
                    
            # General approach - try to find and click on any video element
            else:
                try:
                    # Try to find video element
                    video_elements = self.driver.find_elements(By.TAG_NAME, "video")
                    if video_elements:
                        video_elements[0].click()
                except Exception as e:
                    print(f"Could not find or click video element: {str(e)}")
            
            # Allow video to start
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error navigating to {url}: {str(e)}")
            return False

    def _close_popups(self):
        """Attempt to close any popups or overlays."""
        try:
            # Try pressing Escape key to close general popups
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            
            # YouTube-specific: try to close any visible dialog or popup
            if "youtube.com" in self.driver.current_url:
                # Try to find and click close buttons on popups
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                                             "button.ytp-ad-overlay-close-button, button.ytp-ad-skip-button")
                    for button in close_buttons:
                        button.click()
                except:
                    pass
        except Exception as e:
            print(f"Error closing popups: {str(e)}")

    def _take_screenshot(self) -> Image.Image:
        """Take a screenshot of the current browser window."""
        png_bytes = self.driver.get_screenshot_as_png()
        return Image.open(io.BytesIO(png_bytes))

    def _analyze_screenshot(self, image: Image.Image, label: str) -> int:
        """Count objects of the specified label in a screenshot."""
        detector = pipeline("object-detection", model="facebook/detr-resnet-50")
        
        try:
            # Run detection on the image
            results = detector(image)
            
            # Count objects matching the label
            object_count = sum(1 for result in results if label.lower() in result["label"].lower())
            
            # Debug: print detected classes
            detected_classes = [result["label"] for result in results]
            if detected_classes:
                print(f"Detected classes: {', '.join(detected_classes)}")
                
            return object_count
            
        except Exception as e:
            print(f"Error detecting objects in screenshot: {str(e)}")
            return 0

    def _capture_video_frames(self, duration: int = 30, interval: int = 1, label: str = "") -> List[Dict]:
        """Capture frames from the video at regular intervals."""
        results = []
        
        print(f"Starting frame capture for {duration} seconds with {interval} second intervals...")
        temp_dir = tempfile.mkdtemp()
        
        for seconds_elapsed in range(0, duration, interval):
            # Take screenshot
            try:
                print(f"Capturing frame at {seconds_elapsed} seconds...")
                screenshot = self._take_screenshot()
                
                # Save screenshot for debugging (optional)
                screenshot_path = os.path.join(temp_dir, f"frame_{seconds_elapsed}.jpg")
                screenshot.save(screenshot_path)
                
                # Analyze screenshot
                object_count = self._analyze_screenshot(screenshot, label)
                
                # Store results
                results.append({
                    "time": seconds_elapsed,
                    "object_count": object_count,
                    "screenshot_path": screenshot_path
                })
                
                # Wait for next interval
                if seconds_elapsed + interval < duration:
                    time.sleep(interval)
                    
            except Exception as e:
                print(f"Error capturing frame at {seconds_elapsed} seconds: {str(e)}")
        
        return results

    def forward(self, url: str, label: str, duration: int = 30, interval: int = 1) -> str:
        """
        Analyzes a video on a webpage by taking screenshots and counting objects.
        
        Args:
            url (str): The URL of the webpage containing the video.
            label (str): The type of object to count (e.g., 'bird', 'person', 'car', 'dog').
            duration (int): How many seconds of the video to analyze.
            interval (int): How often to take screenshots (in seconds).
        
        Returns:
            str: A detailed report of object counts over time.
        """
        try:
            # Setup the browser
            self._setup_browser()
            
            # Navigate to the video
            if not self._navigate_to_video(url):
                return f"Error: Could not navigate to or play the video at {url}"
            
            # Close any popups or overlays
            self._close_popups()
            
            # Capture and analyze frames
            frame_results = self._capture_video_frames(duration, interval, label)
            
            # Calculate summary statistics
            if not frame_results:
                return f"Error: No frames were successfully captured and analyzed"
                
            total_objects = sum(result["object_count"] for result in frame_results)
            avg_objects = total_objects / len(frame_results)
            max_objects = max(frame_results, key=lambda x: x["object_count"])
            
            # Generate a report
            report = [
                f"# {label.title()} Count Analysis for Video",
                f"Video URL: {url}",
                f"Analysis duration: {duration} seconds",
                f"Screenshots taken: {len(frame_results)} (every {interval} second(s))",
                "",
                "## Summary",
                f"Total {label}s detected: {total_objects}",
                f"Average {label}s per screenshot: {avg_objects:.2f}",
                f"Maximum {label}s in a single screenshot: {max_objects['object_count']} (at {max_objects['time']} seconds)",
                "",
                "## Time-based Analysis"
            ]
            
            # Add frame-by-frame details
            for result in frame_results:
                report.append(f"Time {result['time']} seconds: {result['object_count']} {label}s")
            
            # Clean up
            try:
                helium.kill_browser()
                self.driver = None
            except:
                print("Warning: Could not properly close the browser")
                
            return "\n".join(report)
            
        except Exception as e:
            # Ensure browser is closed on error
            try:
                if self.driver:
                    helium.kill_browser()
                    self.driver = None
            except:
                pass
                
            return f"Error analyzing video: {str(e)}"
    
