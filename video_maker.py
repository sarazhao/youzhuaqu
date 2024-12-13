from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import os
from typing import List
from PIL import Image

# 在新版本的Pillow中，ANTIALIAS被废弃，改用LANCZOS
ANTIALIAS = Image.Resampling.LANCZOS  

def get_image_files(directory: str) -> List[str]:
    """获取目录下所有图片文件路径
    
    Args:
        directory: 图片所在目录的路径
        
    Returns:
        List[str]: 所有图片文件的完整路径列表，按文件名排序
    """
    # 定义支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png')
    image_files = []
    
    # 遍历目录，获取所有图片文件
    for file in sorted(os.listdir(directory)):  # sorted确保文件按名称排序
        if file.lower().endswith(image_extensions):  # 检查文件扩展名
            image_files.append(os.path.join(directory, file))  # 构建完整路径
            
    return image_files

def create_clip_with_zoom(image_path: str, duration: int = 2) -> ImageClip:
    """创建带缩放效果的视频片段
    
    Args:
        image_path: 图片文件路径
        duration: 视频片段持续时间（秒）
        
    Returns:
        ImageClip: 处理后的视频片段，包含缩放效果
    """
    # 读取图片创建视频片段
    clip = ImageClip(image_path)
    
    # 获取原始图片尺寸，用于计算缩放和裁剪
    w, h = clip.size
    
    def zoom(t):
        """定义缩放函数，用于实现放大效果
        
        Args:
            t: 当前时间点(0-duration)
            
        Returns:
            tuple: (新宽度, 新高度)
        """
        # 计算缩放比例：从1.0逐渐变化到1.2
        zoom_factor = 1.0 + (0.2 * t/duration)
        
        # 根据缩放比例计算新的尺寸
        new_w = int(w * zoom_factor)
        new_h = int(h * zoom_factor)
        
        return (new_w, new_h)
    
    # 应用缩放效果
    clip = clip.resize(zoom)
    
    # 设置片段持续时间
    clip = clip.set_duration(duration)
    
    # 居中裁剪，确保画面始终填充满视频
    # x_center和y_center指定裁剪中心点，width和height指定裁剪后的尺寸
    clip = clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
    
    return clip

def create_video(image_dir: str, audio_path: str, output_dir: str, batch_size: int = 10, max_videos: int = None):
    """创建视频主函数
    
    Args:
        image_dir: 图片目录路径
        audio_path: 背景音乐文件路径
        output_dir: 输出视频保存目录
        batch_size: 每个视频包含的图片数量
        max_videos: 最大生成视频数量，None表示不限制
    """
    # 检查输入路径是否存在
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"图片目录不存在: {image_dir}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有图片文件路径
    image_files = get_image_files(image_dir)
    if not image_files:
        raise FileNotFoundError(f"在目录 {image_dir} 中没有找到图片文件")
    
    # 如果指定了最大视频数量，限制处理的图片数量
    if max_videos:
        image_files = image_files[:max_videos * batch_size]
    
    # 按batch_size分组处理图片
    for i in range(0, len(image_files), batch_size):
        batch_files = image_files[i:i+batch_size]  # 获取当前批次的图片
        
        # 创建视频片段列表
        clips = []
        for image_path in batch_files:
            try:
                # 处理每张图片，创建视频片段
                clip = create_clip_with_zoom(image_path)
                clips.append(clip)
            except Exception as e:
                # 如果处理某张图片出错，打印错误信息并继续处理下一张
                print(f"处理图片 {image_path} 时出错: {str(e)}")
                continue
        
        # 如果当前批次没有成功处理的图片，跳过该视频
        if not clips:
            print(f"没有可用的图片片段，跳过视频 {i//batch_size + 1}")
            continue
            
        # 将所有片段拼接成一个视频
        # method="compose"参数确保更好的过渡效果
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # 添加背景音乐
        audio = AudioFileClip(audio_path)
        # 将音频裁剪至与视频相同长度
        audio = audio.subclip(0, final_clip.duration)
        final_clip = final_clip.set_audio(audio)
        
        # 生成输出文件名
        output_filename = os.path.join(output_dir, f"output_video_{i//batch_size + 1}.mp4")
        
        print(f"正在生成视频 {i//batch_size + 1}...")
        
        # 导出视频文件
        # fps=24: 设置视频帧率
        # codec='libx264': 使用H.264编码
        # audio_codec='aac': 使用AAC音频编码
        final_clip.write_videofile(
            output_filename,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )
        
        # 释放资源，避免内存泄漏
        final_clip.close()
        audio.close()
        for clip in clips:
            clip.close()

if __name__ == "__main__":
    # 设置输入输出路径
    image_dir = r"J:\youzhuaqu\pics"  # 图片目录
    audio_path = r"J:\youzhuaqu\pics\biubiubiu.m4a"  # 音频文件
    output_dir = os.path.join(os.path.dirname(__file__), "output")  # 输出目录
    
    try:
        # 打印路径信息，方便调试
        print(f"图片目录: {image_dir}")
        print(f"音频文件: {audio_path}")
        print(f"输出目录: {output_dir}")
        
        # 生成视频（这里设置max_videos=2用于测试）
        create_video(image_dir, audio_path, output_dir, max_videos=None)
        print("视频生成完成!")
    except FileNotFoundError as e:
        print(f"文件路径错误: {str(e)}")
    except Exception as e:
        print(f"发生错误: {str(e)}") 