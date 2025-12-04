from pico2d import *

# 배경음악
bgm = None
title_bgm = None

# 캐릭터별 효과음 딕셔너리
character_sounds = {}

# 초기화 플래그
initialized = False

def init():
    """사운드 초기화"""
    global bgm, title_bgm, initialized

    # 이미 초기화되었으면 다시 초기화하지 않음
    if initialized:
        return

    initialized = True

    # 배경음악 로드
    try:
        title_bgm = load_music('./Background/bgm.mp3')
        title_bgm.set_volume(32)
    except:
        print("배경음악 로드 실패")

def load_character_sounds(character_name):
    """특정 캐릭터의 효과음 로드"""
    global character_sounds

    if character_name in character_sounds:
        return character_sounds[character_name]

    sounds = {
        'attack': None,
        'skill': None,
        'ult': None
    }

    try:
        # 각 캐릭터별 사운드 파일 경로
        base_path = f'./Character/{character_name}/sounds/'

        # 공격 사운드
        try:
            sounds['attack'] = load_wav(base_path + 'attack.wav')
            sounds['attack'].set_volume(32)
        except:
            print(f"{character_name} 공격 사운드 로드 실패")

        # 스킬 사운드
        try:
            sounds['skill'] = load_wav(base_path + 'skill.wav')
            sounds['skill'].set_volume(32)
        except:
            print(f"{character_name} 스킬 사운드 로드 실패")

        # 궁극기 사운드
        try:
            sounds['ult'] = load_wav(base_path + 'ult.wav')
            sounds['ult'].set_volume(32)
        except:
            print(f"{character_name} 궁극기 사운드 로드 실패")

        character_sounds[character_name] = sounds

    except Exception as e:
        print(f"{character_name} 사운드 로드 중 오류: {e}")

    return sounds

def play_character_sound(character_name, sound_type):
    """캐릭터의 특정 효과음 재생

    Args:
        character_name: 'Rooks' 또는 'Murloc'
        sound_type: 'attack', 'skill', 'ult'
    """
    if character_name not in character_sounds:
        load_character_sounds(character_name)

    sounds = character_sounds.get(character_name, {})
    sound = sounds.get(sound_type)

    if sound:
        sound.play()

def finish():
    """사운드 리소스 해제"""
    global bgm, title_bgm, character_sounds, initialized

    if title_bgm:
        title_bgm.stop()
        del title_bgm

    # 캐릭터 사운드 해제
    for char_name, sounds in character_sounds.items():
        for sound_type, sound in sounds.items():
            if sound:
                del sound

    character_sounds.clear()
    initialized = False

def play_title_bgm():
    """타이틀 화면 BGM 재생"""
    if title_bgm:
        title_bgm.repeat_play()

def stop_bgm():
    """BGM 정지"""
    if title_bgm:
        title_bgm.stop()

def set_bgm_volume(volume):
    """BGM 볼륨 설정 (0-128)"""
    if title_bgm:
        title_bgm.set_volume(volume)

def set_character_volume(character_name, volume):
    """특정 캐릭터의 효과음 볼륨 설정 (0-128)"""
    if character_name in character_sounds:
        sounds = character_sounds[character_name]
        for sound in sounds.values():
            if sound:
                sound.set_volume(volume)
