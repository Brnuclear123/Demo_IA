import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import config
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, concatenate_videoclips
import os
import random
import cv2
import math

conf = config['development']

# ======================================================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================================================
FONT_PATH = conf.FONT_PATH
FUNDO_IMAGEM_PATH = conf.FUNDO_IMAGEM_PATH
IMAGEM_FINAL_PATH = conf.IMAGEM_FINAL_PATH
BG_VIDEO_PATH = conf.BG_VIDEO_PATH
BG_VIDEO_LOGO_PATH = conf.BG_VIDEO_LOGO_PATH
TARGET_PATH = conf.TARGET_PATH

class SloganVideoGenerator:
    """
    Classe responsável por gerar imagens estáticas com slogans para diferentes marcas.
    """
    
    def __init__(self, brand_name):
        """
        Inicializa o gerador com as configurações específicas da marca.
        
        Args:
            brand_name (str): Nome da marca (Corona, Lacta, Bauducco)
        """
        self.brand_name = brand_name
        self._load_brand_config()
        
    def _load_brand_config(self):
        """Carrega as configurações específicas da marca."""
        if self.brand_name == "Corona":
            self.bg_video = BG_VIDEO_PATH['corona']
            self.bg_video_logo = BG_VIDEO_LOGO_PATH['corona']
            self.path_font = FONT_PATH['corona']
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH['corona']
            self.path_imagem_final = IMAGEM_FINAL_PATH['corona']
            self.target_path = TARGET_PATH['corona']
            self.bg_color = "#333333"
            self.text_color = "white"
            self.text_color_hex = "#FFFFFF"
            self.font_size = 73.68
            self.horizontal_margin = 0.05 # 0.5%
            self.left_margin = 0.05 # 0.5%
            self.vertical_offset = 0.05 # 0.5%
        elif self.brand_name == "Lacta":
            self.bg_video = BG_VIDEO_PATH['lacta']
            self.bg_video_logo = BG_VIDEO_LOGO_PATH['lacta']
            self.path_font = FONT_PATH['lacta']
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH['lacta']
            self.path_imagem_final = IMAGEM_FINAL_PATH['lacta']
            self.target_path = TARGET_PATH['lacta']
            self.bg_color = "#333333"
            self.text_color = "white"
            self.text_color_hex = "#FFFFFF"
            self.font_size = 55
            self.horizontal_margin = 0.03 # 0.05%
            self.left_margin = None
            self.vertical_offset = 0.10 # 10%
        elif self.brand_name == "Bauducco":
            self.bg_video = BG_VIDEO_PATH['bauducco']
            self.bg_video_logo = BG_VIDEO_LOGO_PATH['bauducco']
            self.path_font = FONT_PATH['bauducco']
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH['bauducco']
            self.path_imagem_final = IMAGEM_FINAL_PATH['bauducco']
            self.target_path = TARGET_PATH['bauducco']
            self.bg_color = "#333333"
            self.text_color = "white"
            self.text_color_hex = "#FFEE70"
            self.font_size = 55
            self.horizontal_margin = 0.03 # 0.05%
            self.left_margin = None
            self.vertical_offset = 0.10 # 10%
        else:
            self.path_font = FONT_PATH.get('default', 'static/fonte/default.ttf')
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH.get('default', 'static/frames/default.png')
            self.path_imagem_final = IMAGEM_FINAL_PATH.get('default', 'static/frames/default_final.png')
            self.bg_color = "#FFFFFF"
            self.text_color = "black"

    def process_and_add_text(
            self, 
            slogan_text, 
            clean_temp_files=True):    
        """
        This function processes the background video and adds text to it.

        Args:
            bg_clip: The background video clip to process.
            slogan_text: The text to add to the video.
            output_dir: The directory to save the output video.
            font_path: The path to the font to use for the text.
            clean_temp_files: Whether to clean temporary files after processing.
        """

        output_dir = self.target_path
        os.makedirs(output_dir, exist_ok=True)

        bg_clip = self.bg_video
        # REMOVER DEPOIS DE DEBUG
        abspath = os.path.abspath(bg_clip)
        print("→ tentando abrir vídeo em:", abspath, "existe?", os.path.isfile(abspath))
        
        
        # Create a temp directory inside the output_dir
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique output filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_output_path = f"{temp_dir}/video_with_text_{timestamp}.avi"  # Use .avi for FFV1
        final_output_path = f"{output_dir}/processed_video_{timestamp}.mp4"
        
        # Use the font path from the parameter or the class attribute
        font_path = self.path_font
        
        # Open the video
        cap = cv2.VideoCapture(bg_clip)
        if not cap.isOpened():
            print(f"Error: Could not open video file {bg_clip}")
            return bg_clip  # Return original path if can't process
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video dimensions: {width}x{height}")
        
        # Configure output video with high quality and compatibility
        # Use FFV1 codec for lossless temp file (requires ffmpeg support)
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # Lossless, best for gradients
        
        # Create VideoWriter with standard settings
        out = cv2.VideoWriter(
            temp_output_path, 
            fourcc, 
            fps, 
            (width, height), 
            isColor=True
        )
        
        if not out.isOpened():
            print("Error: Could not create output video writer")
            return bg_clip
        
        # For a 1920x158 video, we want to ensure text is centered
        # Define border spacing (margin from edges)
        horizontal_margin = int(width * self.horizontal_margin)  # 5% margin on each side
        
        # Calculate maximum available space for text width
        max_text_width = width - (2 * horizontal_margin)
        
        # For height, we'll use a percentage of the video height
        # but ensure we calculate vertical position precisely
        max_text_height = int(height * 0.7)  # Reduced from 80% to 70% of height
        
        # Find the optimal font size that fits the text within the available space
        # For a narrow banner video (1920x158), we need to be careful with height
        font_size = height // 3  # Start with a smaller initial guess (1/3 instead of 1/2)
        font = None
        text_width = width + 1  # Initialize larger than max to enter the loop
        text_height = height + 1
        
        # Binary search to find optimal font size
        min_size = 10
        max_size = self.font_size
        
        while min_size <= max_size:
            mid_size = (min_size + max_size) // 2
            try:
                test_font = ImageFont.truetype(font_path, mid_size)
                # Create a temporary image to measure text
                temp_img = Image.new("RGB", (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                bbox = temp_draw.textbbox((0, 0), slogan_text, font=test_font)
                current_width = bbox[2] - bbox[0]
                current_height = bbox[3] - bbox[1]
                
                if current_width <= max_text_width and current_height <= max_text_height:
                    # This size fits, try a larger one
                    font = test_font
                    font_size = mid_size
                    text_width = current_width
                    text_height = current_height
                    min_size = mid_size + 1
                else:
                    # Too big, try smaller
                    max_size = mid_size - 1
            except Exception as e:
                print(f"Error loading font at size {mid_size}, trying smaller")
                print(f"Error: {e}")
                max_size = mid_size - 1
        
        # If we couldn't find a suitable font, use the default
        if font is None:
            print(f"Could not find suitable font size, using default")
            font = ImageFont.load_default()
            # Measure the default font
            temp_img = Image.new("RGB", (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), slogan_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Reduce the font size by 25% to make it significantly smaller than the maximum possible
        # This ensures better visual balance in a narrow banner
        if font_size > 10:
            reduced_font_size = int(font_size * 1)  # Reduced from 85% to 75%
            try:
                # Only try to load the font if we have a valid font path
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, reduced_font_size)
                    # Recalculate text dimensions with the reduced font
                    temp_img = Image.new("RGB", (1, 1))
                    temp_draw = ImageDraw.Draw(temp_img)
                    bbox = temp_draw.textbbox((0, 0), slogan_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    font_size = reduced_font_size
                else:
                    print(f"Font file not found for reduced size: {font_path}")
            except Exception as e:
                print(f"Error loading reduced font size: {e}")
                # Keep the original font if there's an error
        
        print(f"Selected font size: {font_size} for text dimensions: {text_width}x{text_height}")
        
        # Calculate how many frames to show text (10 seconds or entire video if shorter)
        text_duration_seconds = 10
        max_text_frames = min(int(fps * text_duration_seconds), total_frames)
        
        # Calculate the exact center position for the text
        text_x_center = width // 2
        text_y_center = height // 2
        
        # Move the text slightly upwards (by 15% of the height)
        vertical_offset = int(height * self.vertical_offset)
        text_y_center -= vertical_offset
        
        # Calculate text position to center it
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), slogan_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if (self.left_margin is not None):
            # Position text to left
            left_margin = int(width * self.left_margin)     
            text_x = left_margin
        else:
            # Position text to center
            text_x = text_x_center - (text_width // 2)
        text_y = text_y_center - (text_height // 2)
        
        print(f"Text position: x={text_x}, y={text_y}")
        
        # Animation parameters
        word_delay_frames = 3  # Reduced from 15 to make words appear more quickly after each other
        word_animation_frames = 12  # Keep the same animation duration
        rise_distance = 45  # Keep the same rise distance
        
        # Split the text into words and calculate positions
        words = slogan_text.split()
        word_positions = []
        
        # Create a temporary image to measure text
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate each word's position starting from the left position
        current_x = text_x
        for word in words:
            # Get the width of this specific word
            word_bbox = temp_draw.textbbox((0, 0), word, font=font)
            word_width = word_bbox[2] - word_bbox[0]
            word_height = word_bbox[3] - word_bbox[1]
            
            # Store the position for this word
            word_positions.append((current_x, word, word_width, word_height))
            
            # Add the width of this word plus a space
            space_width = temp_draw.textbbox((0, 0), ' ', font=font)[2]
            current_x += word_width + space_width
        
        # Calculate buffer zone to prevent words from being cut off
        buffer_height = rise_distance + 20  # Extra buffer to ensure words aren't cut off
        
        frame_number = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Add text only for the first 10 seconds
            if frame_number < max_text_frames:
                # Convert OpenCV frame to PIL Image for better text rendering
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Create a larger canvas with buffer zone to prevent clipping
                canvas = Image.new("RGBA", (width, height + buffer_height * 2), (0, 0, 0, 0))
                canvas_draw = ImageDraw.Draw(canvas)
                
                # Draw each word with its animation
                for i, word_info in enumerate(word_positions):
                    # Calculate when this word should start appearing
                    word_start_frame = i * word_delay_frames
                    
                    # Only draw words that should be visible by now
                    if frame_number >= word_start_frame:
                        word_x, word, word_width, word_height = word_info
                        
                        # Calculate animation progress (0.0 to 1.0)
                        frames_since_word_start = frame_number - word_start_frame
                        if frames_since_word_start < word_animation_frames:
                            # Calculate progress with floating point precision
                            progress = frames_since_word_start / word_animation_frames
                            
                            # Simplified movement with focus on fade-in
                            # Use a simple ease-out for the vertical movement
                            ease_progress = 1 - (1 - progress) * (1 - progress)
                            
                            # Calculate vertical offset with floating point precision
                            y_offset = rise_distance * (1 - ease_progress)
                            
                            # Enhanced fade-in effect with extra smooth start
                            # Use a more dramatic fade-in curve that starts very slowly
                            # and then accelerates more noticeably
                            
                            # First half of animation has very subtle opacity increase
                            if progress < 0.4:
                                # Very slow start to opacity (cubic function)
                                fade_progress = 2.5 * progress * progress * progress
                            else:
                                # Accelerated increase in second half (smoothstep mapped to 0.4-1.0 range)
                                p = (progress - 0.4) / 0.6  # Normalize to 0-1 range for the second part
                                # Math function to make the fade-in more dramatic
                                # This creates a more pronounced fade-in effect
                                fade_progress = 0.1 + 0.9 * (p * p * (3 - 2 * p))
                            
                            # Apply the enhanced fade-in effect
                            opacity = int(255 * fade_progress)
                            
                            # Draw word with current animation state
                            word_y_animated = text_y + y_offset + buffer_height
                            
                            # Convert hex color to RGB with opacity
                            text_color_hex = self.text_color_hex
                            
                            # Parse the hex color
                            if text_color_hex.startswith('#'):
                                text_color_hex = text_color_hex[1:]
                            
                            # Convert hex to RGB
                            r = int(text_color_hex[0:2], 16)
                            g = int(text_color_hex[2:4], 16)
                            b = int(text_color_hex[4:6], 16)
                            
                            # Create color tuple with opacity
                            color_with_opacity = (r, g, b, opacity)
                            
                            # Draw the full word at once with the current opacity and color
                            canvas_draw.text((word_x, word_y_animated), word, font=font, fill=color_with_opacity)
                        else:
                            # Word animation complete, draw at final position
                            # Use full opacity for completed words
                            color_with_full_opacity = (r, g, b, 255)
                            canvas_draw.text((word_x, text_y + buffer_height), word, font=font, fill=color_with_full_opacity)
                
                # Crop the canvas to the original frame size, removing the buffer zone
                final_img = canvas.crop((0, buffer_height, width, height + buffer_height))
                
                # Composite the animated text onto the original frame
                pil_img = Image.alpha_composite(pil_img.convert("RGBA"), final_img)
                
                # Convert back to OpenCV format
                frame = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
            
            # Write the frame
            out.write(frame)
            frame_number += 1
        
        # Release resources
        cap.release()
        out.release()
        
        print(f"✅ Video with text successfully generated: {temp_output_path}")
        
        # Convert to a more compatible format using moviepy
        try:
            print("Converting to a more compatible format (preserving quality)...")
            
            # Load the video we just created
            temp_clip = VideoFileClip(temp_output_path)
            
            # Write with moviepy's settings to maximize quality and reduce pixelation
            temp_clip.write_videofile(
                final_output_path,
                codec='libx264',
                audio_codec='aac',  # Include this even if there's no audio
                preset='veryslow',  # Best quality, slowest encoding
                ffmpeg_params=[
                    '-crf', '14',             # Lower CRF for higher quality (try 12 for even better)
                    '-pix_fmt', 'yuv420p',    # Match original pixel format
                    '-profile:v', 'high',     # Match original H.264 profile
                    '-level', '4.1'           # Match original H.264 level
                ],
                threads=4
            )
            
            # Close the clip
            temp_clip.close()
            
            print(f"✅ Converted to high quality format: {final_output_path}")
        except Exception as e:
            print(f"Warning: Could not convert to more compatible format: {e}")
            print("Using the original output file instead.")
            # If conversion fails, copy the temp file to the final location
            import shutil
            shutil.copy2(temp_output_path, final_output_path)
    
        first_clip = VideoFileClip(final_output_path)
        second_clip = VideoFileClip(self.bg_video_logo)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        final_output_path_processed = os.path.join(self.target_path, f"final_{timestamp}.mp4")
        print(f"Final output path: {final_output_path_processed}")

        final_clip = concatenate_videoclips([first_clip, second_clip], method="compose")

        # Write the result to a file
        final_clip.write_videofile(final_output_path_processed, codec="libx264", audio_codec="aac")
        
        # Close the clips to free up resources
        final_clip.close()
        second_clip.close()
        first_clip.close()

        # Clean temporary files if requested
        if clean_temp_files:
            self.clean_temp_dir(temp_dir)
            
        return final_output_path_processed

    def clean_temp_dir(self, temp_dir):
        """
        Remove all files in the temporary directory.
        
        Args:
            temp_dir: Path to the temporary directory
        """
        if not os.path.exists(temp_dir):
            return
            
        # Get all files in the directory
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Removed temporary file: {file_path}")
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
            
            print(f"Temporary directory cleaned: {temp_dir}")
        except Exception as e:
            print(f"Error cleaning temporary directory {temp_dir}: {e}")
            
    def generate_static_images(self, slogans):
        """
        Generate static images for a list of slogans.
        
        Args:
            slogans (list): List of slogan texts to generate images for.
            
        Returns:
            list: List of paths to the generated images.
        """
        # Implementation for generating static images
        # This is a placeholder - implement the actual image generation logic here
        image_paths = []
        
        for slogan in slogans:
            # Create a unique filename for this slogan
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = f"static/generated/{self.brand_name.lower()}/slogan_{timestamp}.png"
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create a simple image with the slogan text
            # This is a basic implementation - enhance as needed
            img = Image.new("RGB", (800, 400), self.bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load the font, fall back to default if not available
            try:
                font = ImageFont.truetype(self.path_font, 36)
            except IOError:
                font = ImageFont.load_default()
            
            # Draw the text
            draw.text((400, 200), slogan, font=font, fill=self.text_color, anchor="mm")
            
            # Save the image
            img.save(output_path)
            
            # Add the path to our list
            image_paths.append(output_path)
            
        return image_paths

    