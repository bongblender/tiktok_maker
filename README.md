# TikTok Short Video Maker  

A simple Python GUI application to create TikTok-style short videos by combining multiple clips with audio and effects.  

## Features  
- Combine multiple video clips in selected order  
- Add background music (BGM) and dialog audio  
- Apply effects: reverse, slow motion, flip, grayscale, color inversion  
- Adjust brightness/contrast  
- Add light leak overlay  
- Auto-loop videos if shorter than audio  
- Output in vertical format (1080x1920)  

## Requirements  
- Python 3.6+  
- FFmpeg  
- Required packages:  
  ```
  pip install moviepy pydub tkinter
  ```  

## Usage  
1. Run the script:  
   ```
   python tiktok_maker.py
   ```  

2. In the GUI:  
   - Select dialog audio (required)  
   - Add background music (optional)  
   - Select one or more video clips  
   - Choose effects and settings  
   - Click "Create TikTok Video"  

3. Output will be saved as `output_tiktok.mp4`  

## Notes  
- For best results, ensure your FFmpeg is properly configured  
- First run may take longer as it caches effects  

Created with ❤️ using Python + MoviePy
