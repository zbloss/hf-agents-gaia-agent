from smolagents import Tool
import os
import cv2
import tempfile
from yt_dlp import YoutubeDL
from transformers import pipeline
from typing import Any
from PIL import Image


class YouTubeObjectCounterTool(Tool):
    name = "youtube_object_counter"
    description = "Analyzes a YouTube video frame by frame and counts the number of objects of a specified type visible in each frame."
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL of the YouTube video to analyze.",
        },
        "label": {
            "type": "string",
            "description": "The type of object to count (e.g., 'bird', 'person', 'car', 'dog'). Use common object names recognized by standard object detection models.",
        },
    }
    output_type = "string"

    def _download_video(self, url):
        """Downloads the YouTube video to a temporary file."""
        print(f"Downloading video from {url}...")
        temp_dir = tempfile.mkdtemp()

        video_path = os.path.join(temp_dir, "video.mp4")

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": video_path,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Video downloaded to {video_path}")
            return video_path
        except Exception as e:
            error_msg = f"Error downloading video: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _count_objects_in_frame(self, frame, label: str):
        """Counts objects of specified label in a single frame using the object detection model."""

        try:
            # Convert OpenCV BGR frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(rgb_frame)

            # Load the detector
            detector = pipeline("object-detection", model="facebook/detr-resnet-50")

            # Run detection with PIL Image
            results = detector(pil_image)

            # Count objects matching the label
            object_count = sum(
                1 for result in results if label.lower() in result["label"].lower()
            )
            return object_count
        except Exception as e:
            print(f"Error detecting objects in frame: {str(e)}")
            return 0

    def _analyze_video(self, video_path: str, label: str) -> dict[str, Any]:
        """Analyzes the video frame by frame and counts objects of the specified label."""
        sample_rate = 30
        print(
            f"Analyzing video {video_path}, looking for '{label}' objects, sampling every {sample_rate} frames..."
        )

        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Error: Could not open video file {video_path}")

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        # Initialize results
        frame_results = []
        total_objects = 0
        max_objects = 0
        max_objects_frame = 0
        frame_idx = 0

        # Process frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Only process every nth frame
            if frame_idx % sample_rate == 0:
                time_point = frame_idx / fps
                print(f"Processing frame {frame_idx} at time {time_point:.2f}s...")

                object_count = self._count_objects_in_frame(frame, label)
                total_objects += object_count

                if object_count > max_objects:
                    max_objects = object_count
                    max_objects_frame = frame_idx

                frame_results.append(
                    {
                        "frame": frame_idx,
                        "time": time_point,
                        "object_count": object_count,
                    }
                )

            frame_idx += 1

        # Release resources
        cap.release()

        # Calculate statistics
        avg_objects_per_frame = (
            total_objects / len(frame_results) if frame_results else 0
        )
        max_objects_time = max_objects_frame / fps if max_objects_frame else 0

        # Clean up the temporary file
        try:
            os.remove(video_path)
            print(f"Deleted temporary video file: {video_path}")
        except Exception as e:
            print(
                f"Warning: Failed to delete temporary video file: {video_path} | {str(e)}"
            )

        return {
            "frame_results": frame_results,
            "total_frames_analyzed": len(frame_results),
            "video_duration": duration,
            "fps": fps,
            "total_frames": frame_count,
            "average_objects_per_analyzed_frame": avg_objects_per_frame,
            "max_objects_in_single_frame": max_objects,
            "max_objects_frame": max_objects_frame,
            "max_objects_time": max_objects_time,
            "label": label,
        }

    def forward(self, url: str, label: str) -> str:
        """
        Analyzes a YouTube video frame by frame and counts objects of the specified type.

        Args:
            url (str): The URL of the YouTube video to analyze.
            label (str): The type of object to count (e.g., 'bird', 'person', 'car', 'dog').

        Returns:
            str: A detailed report of object counts per frame and summary statistics.
        """

        try:
            # Download the video
            video_path = self._download_video(url)

            # Analyze the video
            results = self._analyze_video(video_path, label)

            # Generate a report
            report = [
                f"# {label.title()} Count Analysis for YouTube Video",
                f"Video URL: {url}",
                f"Video duration: {results['video_duration']:.2f} seconds",
                f"Analyzed {results['total_frames_analyzed']} frames out of {results['total_frames']} total frames",
                f"Sampling rate: 1 frame every 30 frames (approximately {results['fps'] / 30:.2f} frames per second)",
                "## Summary",
                f"Average {label}s per analyzed frame: {results['average_objects_per_analyzed_frame']:.2f}",
                f"Maximum {label}s in a single frame: {results['max_objects_in_single_frame']} (at {results['max_objects_time']:.2f} seconds)",
            ]

            # Add frame-by-frame details
            report.append("## Frame-by-Frame Analysis")
            for result in results["frame_results"]:
                report.append(
                    f"Frame {result['frame']} (Time: {result['time']:.2f}s): {result['object_count']} {label}s"
                )

            return "\n".join(report)

        except Exception as e:
            return f"Error analyzing video: {str(e)}"
