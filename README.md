# 自动视频生成器

一个Python脚本，可以将图片序列自动转换为带缩放效果和背景音乐的视频。

## 主要功能

1. `get_image_files`: 获取指定目录下的所有图片文件
2. `create_clip_with_zoom`: 为单张图片创建带缩放效果的视频片段
3. `create_video`: 主函数，处理图片并生成视频
4. 支持批量处理，可以将图片按组生成多个视频

## 关键技术点

1. 使用 `moviepy` 库处理视频
   - 图片序列转视频
   - 添加缩放动画效果
   - 音频处理和合成

2. 实现平滑的缩放效果
   - 从100%逐渐放大到120%
   - 保持画面居中
   - 确保画面填充

3. 异常处理
   - 文件路径检查
   - 图片处理错误捕获
   - 资源释放保证

4. 资源管理
   - 及时释放视频和音频资源
   - 避免内存泄漏

## 使用说明

1. 安装依赖： 