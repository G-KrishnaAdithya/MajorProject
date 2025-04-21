import os
import requests
import hashlib
import openai
from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip, CompositeVideoClip, concatenate_audioclips, ImageClip
from config import OPENAI_API_KEY  # Replace with your OpenAI API key import or set inline
from PIL import Image, ImageEnhance

# Function to darken the image
def darken_image(image_path):
    """
    Darkens the image by adjusting its brightness.
    
    Args:
        image_path (str): Path to the image to be darkened.
    
    Returns:
        str: Path to the darkened image.
    """
    try:
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.4)  # Reduce brightness to make the image darker
        darkened_image_path = image_path.replace(".png", "_darkened.png")
        img.save(darkened_image_path)
        return darkened_image_path
    except Exception as e:
        print(f"Error darkening image: {e}")
        return image_path

# Function to generate custom background image using OpenAI's API
def get_custom_background_image(sentence):
    """
    Generate a custom background image for a given sentence using OpenAI's API.
    
    Args:
        sentence (str): The input sentence.
        
    Returns:
        str: The path to the generated image.
    """
    # Define the output directory for saving images
    output_directory = "generated_images"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Generate a unique filename for the image
    hash_object = hashlib.md5(sentence.encode())
    image_filename = f"background_{hash_object.hexdigest()[:8]}.png"
    image_path = os.path.join(output_directory, image_filename)

    # Check if the image already exists to avoid regenerating
    if os.path.exists(image_path):
        return darken_image(image_path)  # Apply darkening if the image exists

    try:
        # Set up OpenAI API
        openai.api_key = OPENAI_API_KEY

        # Generate the image using OpenAI API
        response = openai.Image.create(
            prompt="Give me an image of " + sentence,
            n=1,
            size="512x512"
        )

        # Fetch the generated image URL from the response
        image_url = response["data"][0]["url"]
        response_image = requests.get(image_url)

        if response_image.status_code == 200:
            # Save the image locally
            with open(image_path, "wb") as f:
                f.write(response_image.content)
            return darken_image(image_path)  # Darken the image after saving it
        else:
            raise Exception(f"Failed to fetch image: {response_image.status_code}")

    except Exception as e:
        print(f"Error generating image: {e}")
        return None

# Function to generate video with OpenAI-generated images
def generate_sentence_by_sentence_video(text, output_filename="output_sentence_by_sentence.mp4"):
    """
    Generate a video with text appearing sentence by sentence and synchronized with audio narration,
    each with a custom background image.
    Args:
        text (str): The input text.
        output_filename (str): The output video file.
    """
    # Split text into sentences and filter out empty strings
    sentences = text.split(".")
    sentences = [sentence.strip() + ("." if not sentence.endswith(".") else "") for sentence in sentences if sentence.strip()]
    print(sentences)

    # Initialize lists for audio files, durations, and valid sentences
    audio_files = []
    sentence_durations = []
    valid_sentences = []
    background_images = []

    for i, sentence in enumerate(sentences):
        try:
            # Generate audio for each valid sentence
            tts = gTTS(sentence)
            audio_file = f"audio_{i}.mp3"
            tts.save(audio_file)
            audio_files.append(audio_file)

            # Get the duration of the audio
            audio_clip = AudioFileClip(audio_file)
            sentence_durations.append(audio_clip.duration)
            valid_sentences.append(sentence)  # Only include valid sentences
            audio_clip.close()

            # Generate or fetch a custom background image
            background_image = get_custom_background_image(sentence)
            if background_image:
                background_images.append(background_image)
            else:
                # Use a fallback image or black background if image generation fails
                print(f"Image generation failed for sentence: {sentence}")
                background_images.append("fallback_image.png")  # Replace with an actual fallback image path
        except Exception as e:
            print(f"Skipping sentence {i}: '{sentence}' due to error - {e}")

    # If no valid audio generated, exit gracefully
    if not audio_files:
        print("No valid sentences to process. Exiting.")
        return

    # Calculate the start times for each sentence
    start_times = [0] + [sum(sentence_durations[:i + 1]) for i in range(len(sentence_durations) - 1)]

    # Create a list of TextClip objects, one for each valid sentence
    clips = []

    for i, sentence in enumerate(valid_sentences):
        # Create an ImageClip for the background
        bg_clip = ImageClip(background_images[i], duration=sentence_durations[i])
        bg_clip = bg_clip.set_position(("center", "center"))

        # Create a TextClip for the sentence
        text_clip = TextClip(sentence, fontsize=25, color='white', size=(512, 512), method="caption")
        text_clip = text_clip.set_position(("center", "bottom")).set_duration(sentence_durations[i])

        # Overlay the text on the background image
        final_clip = CompositeVideoClip([bg_clip, text_clip]).set_start(start_times[i])
        clips.append(final_clip)

    # Combine all video clips into a single video
    video = CompositeVideoClip(clips, size=(512, 512))

    # Combine all audio files into a single AudioFileClip
    audio_clips = [AudioFileClip(audio_file) for audio_file in audio_files]
    combined_audio = concatenate_audioclips(audio_clips)

    # Add the combined audio to the video
    video = video.set_audio(combined_audio)

    # Write the final video to file
    video.write_videofile(output_filename, fps=24)

    # Cleanup
    for audio_file in audio_files:
        os.remove(audio_file)

# Wrapper function as requested
def generate_storyboard_video(text):
    """
    Wrapper to generate a storyboard video from input text, storing it in generated_videos and returning its path.
    Args:
        text (str): Input story text (sentences separated by periods).
    Returns:
        str: Path to the generated video.
    """
    # Ensure output directory exists
    output_dir = "frontend/generated_videos"
    os.makedirs(output_dir, exist_ok=True)

    # Generate a unique filename based on the input text
    hash_object = hashlib.md5(text.encode())
    video_filename = f"storyboard_{hash_object.hexdigest()[:8]}.mp4"
    output_path = os.path.join(output_dir, video_filename)
    final_output_path = output_path.replace("/frontend", "")  # Adjust path for serving
    # Generate the video using the existing function
    generate_sentence_by_sentence_video(text, output_filename=output_path)
    return final_output_path
