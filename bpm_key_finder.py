import librosa
from madmom.features import CNNKeyRecognitionProcessor
from madmom.features.key import key_prediction_to_label
from pydub import AudioSegment
import os
import filetype
from scipy.io import wavfile
import bpm_detection_wave
import mutagen
from mutagen.easyid3 import EasyID3


# 判断给定文件是否为音频文件
def is_audio(filename):
    if not os.path.exists(filename):
        return False, '指定路径不存在！'
    else:
        file_type = filetype.guess(filename)
        if file_type is not None:
            if file_type.mime.split('/')[0] == 'audio':
                return True, file_type.extension
        else:
            return False, '指定文件不是音频！'


# 将音频转换为.wav格式（16bit）
def convert_any_to_wav(filename):
    # 创建目录
    if not os.path.exists('data/temp'):
        os.makedirs('data/temp')

    audio_flag, log = is_audio(filename)
    convert_flag = False
    if audio_flag:
        if log == 'wav':
            samplerate, data = wavfile.read(filename)
            # wav格式         numpy数据类型
            # 64位浮点         float64
            # 64 位整数 PCM    int64
            # 32位浮点         float32
            # 32 位整数 PCM    int32
            # 24 位整数 PCM    int32
            # 16 位整数 PCM    int16
            # 8 位整数 PCM     uint8
            if data.dtype == 'float32' or data.dtype == 'float64':  # 此处只对浮点类型进行转换
                convert_flag = True
        else:
            convert_flag = True

        if convert_flag:
            # 设置转换后文件的路径
            converted_path = get_new_file_name(filename) + '.wav'
            converted_path = 'data/temp/' + converted_path

            # 读取音频文件
            audio = AudioSegment.from_file(filename)
            # 转换为 16bit 的 wav文件
            audio.export(converted_path, format='wav', parameters=['-acodec', 'pcm_s16le'])

            return True, '转换成功！', converted_path
        else:
            return True, '无需转换！', filename
    else:
        return audio_flag, log, ''


# 检测BPM（使用wave库）
def find_bpm_wave(filename):
    flag, log, path = convert_any_to_wav(filename)
    if flag:
        return_list = bpm_detection_wave.detect(path)
        # 删除临时文件
        if path.find('temp') > 0:
            os.remove(path)
        return True, '测速成功', str(round(return_list[2]))
    else:
        return flag, log, ''


# 检测BPM（使用librosa库）
def find_bpm_librosa(filename):
    audio_flag, log = is_audio(filename)
    if audio_flag:
        # 读取音频文件
        audio = AudioSegment.from_file(filename)
        sample_rate = audio.frame_rate

        # Load the audio as a waveform `y` Store the sampling rate as `sr` loads and decodes the audio as a time
        # series y, represented as a one-dimensional NumPy floating point array. The variable sr contains the
        # sampling rate of y, that is, the number of samples per second of audio
        y, sr = librosa.load(filename, sr=sample_rate)

        # 获取bpm
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        return True, '测速成功！', str(round(tempo))
    else:
        return False, log, ''


# 获取文件名（去除路径和后缀）
def get_new_file_name(filename):
    # 将路径的符号统一
    new_path = filename.replace('\\', '/')
    # 如果文件名中含有路径
    if new_path.find('/') > 0:
        new_filename = new_path.split('/')[-1].split('.')[0]
    else:
        new_filename = filename.split('.')[0]
    return new_filename


# 依次返回成功标志，标题，艺术家，专辑
def get_audio_info(filename):
    audio_flag, log = is_audio(filename)
    if audio_flag:
        if log == 'mp3':
            audio = EasyID3(filename)
            title, artist, album = '', '', ''
            if 'title' in audio:
                title = audio['title'][0]
            else:
                title = get_new_file_name(filename)
            if 'artist' in audio:
                artist = audio['artist'][0]
            if 'album' in audio:
                album = audio['album'][0]
            return True, title, artist, album
        elif log == 'flac':
            audio = mutagen.File(filename)
            tags = audio.tags.pprint()
            tags_split = tags.split('\n')  # 0:album,1:artist,2:description,3:title,4:tracknumber
            title, album, artist = '', '', ''
            for tag in tags_split:
                if 'TITLE' in tag:
                    title = tag.split('=')[-1]
                elif 'ALBUM' in tag:
                    album = tag.split('=')[-1]
                elif 'ARTIST' in tag:
                    artist = tag.split('=')[-1]
            return True, title, artist, album
        elif log == 'm4a':
            audio = mutagen.File(filename)
            tags = audio.tags.pprint()
            tags_split = tags.split('\n')  # 0:ART,1:alb,2:nam,3:too
            title, artist, album = '', '', ''
            if tags.find('ART') > 0 and tags.find('alb') > 0 and tags.find('nam') > 0:
                artist = tags_split[0].split('=')[-1]
                album = tags_split[1].split('=')[-1]
                title = tags_split[2].split('=')[-1]
            return True, title, artist, album
        # 如果是.wav/.ogg文件，由于这些文件无歌曲信息，直接返回文件名
        else:
            new_filename = get_new_file_name(filename)
            return True, new_filename, '', ''
    else:
        return False, log, '', ''


# 检测调性
def find_key(filename):
    audio_flag, log = is_audio(filename)

    if audio_flag:
        processor = CNNKeyRecognitionProcessor()
        key = key_prediction_to_label(processor(filename))
        return True, '测调成功！', key
    else:
        return audio_flag, log, ''
